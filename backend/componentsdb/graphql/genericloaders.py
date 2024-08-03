import base64
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Generic, Optional, TypeVar
from uuid import UUID

import sqlalchemy as sa
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from ..db import models as dbm
from . import types
from .paginationtypes import (
    DEFAULT_LIMIT,
    Connection,
    Edge,
    MinMaxIds,
    PaginationParams,
)

_R = TypeVar("_R", bound=dbm.ResourceMixin)
_N = TypeVar("_N", bound="types.Node")
_K = TypeVar("_K")


def select_after_uuid(
    model: type[_R], uuid: UUID, *, base_select: Optional[sa.Select[tuple[_R]]] = None
) -> sa.Select[tuple[_R]]:
    subquery = (
        sa.select(model.id).where(model.uuid == uuid).order_by(model.id.asc()).scalar_subquery()
    )
    base_select = base_select if base_select is not None else sa.select(model)
    return base_select.where(model.id > subquery).order_by(model.id.asc())


def uuid_from_cursor(cursor: str) -> UUID:
    return UUID(bytes=base64.b64decode(cursor))


def cursor_from_uuid(uuid_: UUID) -> str:
    return base64.standard_b64encode(uuid_.bytes).decode("ascii")


class ConnectionFactory(Generic[_K, _N], metaclass=ABCMeta):
    _session: AsyncSession
    _edges_loader: DataLoader[tuple[Any, PaginationParams], list[Edge[_N]]]
    _count_loader: DataLoader[Any, int]
    _min_max_ids_loader: DataLoader[Any, MinMaxIds]

    def __init__(self, session: AsyncSession):
        self._session = session
        self._edges_loader = DataLoader(load_fn=self._load_edges)
        self._count_loader = DataLoader(load_fn=self._load_counts)
        self._min_max_ids_loader = DataLoader(load_fn=self._load_min_max_ids)

    def make_connection(self, key: _K, pagination_params: PaginationParams) -> Connection[_N]:
        return Connection[_N](
            loader_key=key,
            pagination_params=pagination_params,
            edges_loader=self._edges_loader,
            count_loader=self._count_loader,
            min_max_ids_loader=self._min_max_ids_loader,
        )

    @abstractmethod
    async def _load_edges(self, keys: list[tuple[_K, PaginationParams]]) -> list[list[Edge[_N]]]:
        pass  # pragma: no cover

    @abstractmethod
    async def _load_counts(self, keys: list[_K]) -> list[int]:
        pass  # pragma: no cover

    @abstractmethod
    async def _load_min_max_ids(self, keys: list[_K]) -> list[Optional[MinMaxIds]]:
        pass  # pragma: no cover


class OneToManyRelationshipConnectionFactory(Generic[_R, _N], ConnectionFactory[int, _N]):
    """
    A ConnectionFactory which follows one to many relationships.
    """

    relationship: sa.orm.Relationship
    entity_model: type[_R]
    foreign_key_column: sa.Column
    node_factory: Callable[[_R], _N]

    def __init__(self, session: AsyncSession, relationship: Any, node_factory: Callable[[_R], _N]):
        super().__init__(session)
        self.relationship = sa.inspect(relationship)
        assert isinstance(self.relationship, sa.orm.QueryableAttribute)
        assert isinstance(self.relationship.property, sa.orm.RelationshipProperty)
        assert self.relationship.property.direction == sa.orm.RelationshipDirection.ONETOMANY
        self.entity_model = self.relationship.property.entity.class_
        self.foreign_key_column = self.relationship.property.local_remote_pairs[0][1]
        self.node_factory = node_factory

    async def _load_edges(self, keys: list[tuple[int, PaginationParams]]) -> list[list[Edge[_N]]]:
        if len(keys) == 0:
            return []

        sub_stmts: list[sa.Select] = []
        for key_idx, (cabinet_id, p) in enumerate(keys):
            first = p.first if p.first is not None else DEFAULT_LIMIT
            stmt = (
                sa.select(self.entity_model, sa.literal(key_idx).label("key_idx"))
                .where(self.foreign_key_column == cabinet_id)
                .order_by(self.entity_model.id.asc())
            )
            if p.after is not None:
                stmt = select_after_uuid(
                    self.entity_model, uuid_from_cursor(p.after), base_select=stmt
                )
            stmt = stmt.limit(first)
            sub_stmts.append(stmt)
        stmt = sa.select(self.entity_model, sa.literal_column("key_idx")).from_statement(
            sa.union_all(*sub_stmts)
        )

        db_entities_by_key_idx = defaultdict[int, list[_R]](list)
        for d, key_idx in await self._session.execute(stmt):
            db_entities_by_key_idx[key_idx].append(d)

        return [
            [
                Edge(
                    cursor=cursor_from_uuid(scalar.uuid),
                    node=self.node_factory(scalar),
                )
                for scalar in db_entities_by_key_idx[key_idx]
            ]
            for key_idx, (cabinet_id, _) in enumerate(keys)
        ]

    async def _load_counts(self, keys: list[int]) -> list[int]:
        stmt = (
            sa.select(self.foreign_key_column, sa.func.count(self.entity_model.id))
            .group_by(self.foreign_key_column)
            .having(self.foreign_key_column.in_(keys))
        )
        counts_by_id = {id_: count for id_, count in (await self._session.execute(stmt)).all()}
        return [counts_by_id.get(id_, 0) for id_ in keys]

    async def _load_min_max_ids(self, keys: list[int]) -> list[Optional[MinMaxIds]]:
        stmt = (
            sa.select(
                self.foreign_key_column,
                sa.func.min(self.entity_model.id),
                sa.func.max(self.entity_model.id),
            )
            .group_by(self.foreign_key_column)
            .having(self.foreign_key_column.in_(keys))
        )
        min_max_by_id = {
            id_: MinMaxIds(min_, max_)
            for id_, min_, max_ in (await self._session.execute(stmt)).all()
        }
        return [min_max_by_id.get(id_, None) for id_ in keys]


class EntityConnectionFactory(Generic[_R, _N], ConnectionFactory[None, _N]):
    """
    A ConnectionFactory which can load lists of objects from the database.
    """

    node_factory: Callable[[_R], _N]

    def __init__(self, session: AsyncSession, mapper: Any, node_factory: Callable[[_R], _N]):
        super().__init__(session)
        self.model = sa.inspect(mapper).entity
        self.node_factory = node_factory

    def base_select(self) -> sa.Select[_R]:
        return sa.select(self.model).order_by(self.model.id.asc())

    async def _load_edges(self, keys: list[tuple[None, PaginationParams]]) -> list[list[Edge[_N]]]:
        rvs: list[list[Edge[_N]]] = []
        for k, p in keys:
            stmt = self.base_select()
            if p.after is not None:
                stmt = select_after_uuid(self.model, uuid_from_cursor(p.after), base_select=stmt)
            stmt = stmt.limit(p.first if p.first is not None else DEFAULT_LIMIT)
            cabinets = (await self._session.execute(stmt)).scalars().all()
            rvs.append(
                [
                    Edge(
                        cursor=cursor_from_uuid(c.uuid),
                        node=self.node_factory(c),
                    )
                    for c in cabinets
                ]
            )

        return rvs

    async def _load_counts(self, keys: list[None]) -> list[int]:
        count = (await self._session.execute(sa.select(sa.func.count(self.model.id)))).scalar_one()
        return [count] * len(keys)

    async def _load_min_max_ids(self, keys: list[None]) -> list[Optional[MinMaxIds]]:
        min_max_id_stmt = sa.select(sa.func.min(self.model.id), sa.func.max(self.model.id))
        min_id, max_id = (await self._session.execute(min_max_id_stmt)).one()
        return [MinMaxIds(min_id, max_id)] * len(keys)


class RelatedEntityLoader(Generic[_R, _N], DataLoader[int, _N]):
    """
    A DataLoader which can load database entities given the database primary key. This should only
    ever by used from objects which exist in the database and so all keys are assumed to exist.
    """

    session: AsyncSession
    node_factory: Callable[[_R], _N]

    def __init__(
        self, session: AsyncSession, mapper: Any, node_factory: Callable[[_R], _N], **kwargs
    ):
        super().__init__(load_fn=self._load, **kwargs)
        self.session = session
        self.model = sa.inspect(mapper).entity
        self.node_factory = node_factory

    async def _load(self, keys: list[int]) -> list[_N]:
        stmt = sa.select(self.model).where(self.model.id.in_(keys)).order_by(self.model.id.asc())
        entities_by_key = {o.id: o for o in (await self.session.execute(stmt)).scalars()}
        return [self.node_factory(entities_by_key[k]) for k in keys]


class EntityLoader(Generic[_R, _N], DataLoader[strawberry.ID, _N]):
    """
    A DataLoader which can load database entities given their GraphQL id. If no matching object
    exists, None is returned.
    """

    session: AsyncSession
    node_factory: Callable[[_R], _N]

    def __init__(
        self, session: AsyncSession, mapper: Any, node_factory: Callable[[_R], _N], **kwargs
    ):
        super().__init__(load_fn=self._load, **kwargs)
        self.session = session
        self.model = sa.inspect(mapper).entity
        self.node_factory = node_factory

    async def _load(self, keys: list[strawberry.ID]) -> list[Optional[_N]]:
        stmt = sa.select(self.model).where(self.model.uuid.in_(keys)).order_by(self.model.id.asc())
        entities_by_key = {str(o.uuid): o for o in (await self.session.execute(stmt)).scalars()}
        entities = [entities_by_key.get(k, None) for k in keys]
        return [self.node_factory(e) if e is not None else None for e in entities]
