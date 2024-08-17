import asyncio
import base64
import enum
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar
from uuid import UUID

import sqlalchemy as sa
import strawberry
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import raiseload
from strawberry.dataloader import DataLoader

from ..db import models as dbm
from . import types
from .paginationtypes import (
    DEFAULT_LIMIT,
    Connection,
    Edge,
    LoadEdgesResult,
    PaginationParams,
)

_R = TypeVar("_R", bound=dbm.ResourceMixin)
_N = TypeVar("_N", bound="types.Node")
_K = TypeVar("_K")

LOG = structlog.get_logger()


class SelectDirection(enum.Enum):
    BEFORE = enum.auto()
    AFTER = enum.auto()


def select_beyond(
    model: type[_R],
    id: Any,
    *,
    direction: SelectDirection = SelectDirection.AFTER,
    base_select: Optional[sa.Select[tuple[_R]]] = None,
    ordering_key: Optional[sa.Numeric] = None,
    id_column: Optional[sa.Column] = None,
) -> sa.Select[tuple[_R]]:
    id_column = id_column if id_column is not None else model.uuid
    id_subquery = sa.select(model.id).where(id_column == id).scalar_subquery()
    ok_subquery = sa.select(ordering_key).where(id_column == id).scalar_subquery()
    base_select = base_select if base_select is not None else sa.select(model)
    if ordering_key is not None and ordering_key != model.id:
        # The logic here is that we generally want the rows *after* the one matching the ordering
        # key but the ordering key may not provide a total ordering so we tie-break when the
        # ordering key matches with the model id.
        if direction == SelectDirection.AFTER:
            return base_select.where(
                sa.or_(
                    ordering_key > ok_subquery,
                    sa.and_(ordering_key == ok_subquery, model.id > id_subquery),
                )
            )
        else:
            return base_select.where(
                sa.or_(
                    ordering_key < ok_subquery,
                    sa.and_(ordering_key == ok_subquery, model.id < id_subquery),
                )
            )
    else:
        if direction == SelectDirection.AFTER:
            return base_select.where(model.id > id_subquery)
        else:
            return base_select.where(model.id < id_subquery)


def uuid_from_cursor(cursor: str) -> UUID:
    return UUID(bytes=base64.b64decode(cursor))


def cursor_from_uuid(uuid_: UUID) -> str:
    return base64.standard_b64encode(uuid_.bytes).decode("ascii")


class ConnectionFactory(Generic[_K, _N], metaclass=ABCMeta):
    _session: AsyncSession
    _session_lock: asyncio.Lock
    _pagination_params: PaginationParams
    _edges_loader: DataLoader[_K, LoadEdgesResult[_N]]
    _count_loader: DataLoader[_K, int]

    def __init__(
        self,
        session: AsyncSession,
        session_lock: asyncio.Lock,
        pagination_params: PaginationParams,
    ):
        self._session = session
        self._session_lock = session_lock
        self._pagination_params = pagination_params
        self._edges_loader = DataLoader(load_fn=self._load_edges)
        self._count_loader = DataLoader(load_fn=self._load_counts)

    def cursor_from_entity(self, entity: Any) -> str:
        return cursor_from_uuid(entity.uuid)

    def entity_key_from_cursor(self, cursor: str) -> Any:
        return uuid_from_cursor(cursor)

    def make_connection(self, key: _K) -> Connection[_N]:
        return Connection[_N](
            loader_key=key,
            edges_loader=self._edges_loader,
            count_loader=self._count_loader,
        )

    @abstractmethod
    async def _load_edges(self, keys: Sequence[_K]) -> Sequence[LoadEdgesResult[_N]]:
        pass  # pragma: no cover

    @abstractmethod
    async def _load_counts(self, keys: Sequence[_K]) -> Sequence[int]:
        pass  # pragma: no cover


class OneToManyRelationshipConnectionFactory(Generic[_R, _N], ConnectionFactory[int, _N]):
    """
    A ConnectionFactory which follows one to many relationships.
    """

    relationship: sa.orm.Relationship
    entity_model: type[_R]
    foreign_key_column: sa.Column
    node_factory: Callable[[_R], _N]

    def __init__(
        self,
        session: AsyncSession,
        session_lock: asyncio.Lock,
        pagination_params: PaginationParams,
        relationship: Any,
        node_factory: Callable[[_R], _N],
    ):
        super().__init__(session, session_lock, pagination_params)
        self.relationship = sa.inspect(relationship)
        assert isinstance(self.relationship, sa.orm.QueryableAttribute)
        assert isinstance(self.relationship.property, sa.orm.RelationshipProperty)
        assert self.relationship.property.direction == sa.orm.RelationshipDirection.ONETOMANY
        self.entity_model = self.relationship.property.entity.class_
        self.foreign_key_column = self.relationship.property.local_remote_pairs[0][1]
        self.node_factory = node_factory

    async def _load_edges(self, keys: Sequence[int]) -> Sequence[LoadEdgesResult[_N]]:
        if len(keys) == 0:
            return []

        first = (
            max(1, self._pagination_params.first)
            if self._pagination_params.first is not None
            else DEFAULT_LIMIT
        )
        subq = sa.select(
            self.entity_model.id.label("entity_id"),
            self.foreign_key_column.label("key"),
            sa.func.row_number()
            .over(partition_by=self.foreign_key_column, order_by=self.entity_model.id)
            .label("rownum"),
        )
        if self._pagination_params.after is not None:
            subq = select_beyond(
                self.entity_model,
                self.entity_key_from_cursor(self._pagination_params.after),
                base_select=subq,
            )
        subq = subq.subquery()

        stmt = sa.select(self.entity_model, subq.c.key).where(
            subq.c.rownum <= first, subq.c.key.in_(keys), self.entity_model.id == subq.c.entity_id
        )
        db_entities_by_key = defaultdict[int, list[_R]](list)
        async with self._session_lock:
            for d, k in await self._session.execute(stmt):
                db_entities_by_key[k].append(d)

        db_entity_pages = [db_entities_by_key[key] for key in keys]
        has_more_stmts = [
            sa.select(
                select_beyond(
                    self.entity_model,
                    entities[0].uuid if len(entities) > 0 else None,
                    direction=SelectDirection.BEFORE,
                ).exists(),
                select_beyond(
                    self.entity_model,
                    entities[-1].uuid if len(entities) > 0 else None,
                    direction=SelectDirection.AFTER,
                ).exists(),
            )
            for entities in db_entity_pages
        ]

        async with self._session_lock:
            has_more_results = await self._session.execute(sa.union_all(*has_more_stmts))

        return [
            LoadEdgesResult(
                edges=[
                    Edge(
                        cursor=self.cursor_from_entity(scalar),
                        node=self.node_factory(scalar),
                    )
                    for scalar in page
                ],
                has_next_page=has_next_page,
                has_previous_page=has_previous_page,
            )
            for page, (has_previous_page, has_next_page) in zip(db_entity_pages, has_more_results)
        ]

    async def _load_counts(self, keys: Sequence[int]) -> Sequence[int]:
        stmt = (
            sa.select(self.foreign_key_column, sa.func.count(self.entity_model.id))
            .group_by(self.foreign_key_column)
            .having(self.foreign_key_column.in_(keys))
        )
        async with self._session_lock:
            counts_by_id = {id_: count for id_, count in (await self._session.execute(stmt)).all()}
        return [counts_by_id.get(id_, 0) for id_ in keys]


class EntityConnectionFactory(Generic[_R, _N, _K], ConnectionFactory[_K, _N]):
    """
    A ConnectionFactory which can load lists of objects from the database.
    """

    node_factory: Callable[[_R], _N]

    def __init__(
        self,
        session: AsyncSession,
        session_lock: asyncio.Lock,
        pagination_params: PaginationParams,
        mapper: Any,
        node_factory: Callable[[_R], _N],
    ):
        super().__init__(session, session_lock, pagination_params)
        self.model = sa.inspect(mapper).entity
        self.node_factory = node_factory

    def ordering_keys(self, keys: Sequence[_K]) -> Sequence[sa.Numeric]:
        """
        For each key, return the model field or expression which should be used to order results.
        Results will be order in ascending order of this expression with ties broken by ascending
        database id.
        """
        return [self.model.id for _ in keys]

    def filter(self, keys: Sequence[_K], stmt: sa.Select[_R]) -> Sequence[sa.Select[_R]]:
        "For each key, filter the select statement passed to match the required key."
        return [stmt for _ in keys]

    async def _load_edges(self, keys: Sequence[_K]) -> Sequence[LoadEdgesResult[_N]]:
        rvs: list[LoadEdgesResult[_N]] = []

        filtered_selects = self.filter(keys, sa.select(self.model))
        ordering_keys = self.ordering_keys(keys)

        for key, filtered_stmt, ordering_key in zip(keys, filtered_selects, ordering_keys):
            paginated_stmt = filtered_stmt
            if self._pagination_params.after is not None:
                paginated_stmt = select_beyond(
                    self.model,
                    self.entity_key_from_cursor(self._pagination_params.after),
                    base_select=paginated_stmt,
                    ordering_key=ordering_key,
                )
            first_limit = (
                max(1, self._pagination_params.first)
                if self._pagination_params.first is not None
                else DEFAULT_LIMIT
            )
            paginated_stmt = (
                paginated_stmt.order_by(ordering_key.asc(), self.model.id.asc())
                .limit(first_limit)
                .options(raiseload("*"))
            )

            async with self._session_lock:
                entities = list((await self._session.execute(paginated_stmt)).scalars())
                if len(entities) > 0:
                    has_previous_page, has_next_page = (
                        await self._session.execute(
                            sa.select(
                                select_beyond(
                                    self.model,
                                    entities[0].uuid,
                                    base_select=filtered_stmt,
                                    ordering_key=ordering_key,
                                    direction=SelectDirection.BEFORE,
                                ).exists(),
                                select_beyond(
                                    self.model,
                                    entities[-1].uuid,
                                    base_select=filtered_stmt,
                                    ordering_key=ordering_key,
                                    direction=SelectDirection.AFTER,
                                ).exists(),
                            )
                        )
                    ).first()
                else:
                    has_previous_page = False
                    has_next_page = False

            rvs.append(
                LoadEdgesResult(
                    edges=[
                        Edge(
                            cursor=self.cursor_from_entity(c),
                            node=self.node_factory(c),
                        )
                        for c in entities
                    ],
                    has_previous_page=has_previous_page,
                    has_next_page=has_next_page,
                )
            )

        return rvs

    async def _load_counts(self, keys: Sequence[_K]) -> Sequence[int]:
        # TODO: there may be some way to coalesce this into a single statement?
        count_stmt = sa.select(sa.func.count()).select_from(self.model)
        async with self._session_lock:
            return [
                (await self._session.execute(stmt)).scalar_one()
                for stmt in self.filter(keys, count_stmt)
            ]


class RelatedEntityLoader(Generic[_R, _N], DataLoader[int, _N]):
    """
    A DataLoader which can load database entities given the database primary key. This should only
    ever by used from objects which exist in the database and so all keys are assumed to exist.
    """

    session: AsyncSession
    session_lock: asyncio.Lock
    node_factory: Callable[[_R], _N]

    def __init__(
        self,
        session: AsyncSession,
        session_lock: asyncio.Lock,
        mapper: Any,
        node_factory: Callable[[_R], _N],
        **kwargs,
    ):
        super().__init__(load_fn=self._load, **kwargs)
        self.session = session
        self.session_lock = session_lock
        self.model = sa.inspect(mapper).entity
        self.node_factory = node_factory

    async def _load(self, keys: Sequence[int]) -> Sequence[_N]:
        stmt = (
            sa.select(self.model)
            .where(self.model.id.in_(keys))
            .order_by(self.model.id.asc())
            .options(raiseload("*"))
        )
        async with self.session_lock:
            entities_by_key = {o.id: o for o in (await self.session.execute(stmt)).scalars()}
        return [self.node_factory(entities_by_key[k]) for k in keys]


class EntityLoader(Generic[_R, _N], DataLoader[strawberry.ID, Optional[_N]]):
    """
    A DataLoader which can load database entities given their GraphQL id. If no matching object
    exists, None is returned.
    """

    session: AsyncSession
    session_lock: asyncio.Lock
    node_factory: Callable[[_R], _N]

    def __init__(
        self,
        session: AsyncSession,
        session_lock: asyncio.Lock,
        mapper: Any,
        node_factory: Callable[[_R], _N],
        **kwargs,
    ):
        super().__init__(load_fn=self._load, **kwargs)
        self.session = session
        self.session_lock = session_lock
        self.model = sa.inspect(mapper).entity
        self.node_factory = node_factory

    async def _load(self, keys: list[strawberry.ID]) -> Sequence[Optional[_N]]:
        stmt = (
            sa.select(self.model)
            .where(self.model.uuid.in_(keys))
            .order_by(self.model.id.asc())
            .options(raiseload("*"))
        )
        async with self.session_lock:
            entities_by_key = {
                str(o.uuid): o for o in (await self.session.execute(stmt)).scalars()
            }
        entities = [entities_by_key.get(k, None) for k in keys]
        return [self.node_factory(e) if e is not None else None for e in entities]
