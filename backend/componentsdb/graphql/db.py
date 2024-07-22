import base64
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Generic, Optional, TypeVar
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from ..db import models as dbm
from . import schema
from .pagination import DEFAULT_LIMIT, Connection, Edge, MinMaxIds, PaginationParams

_R = TypeVar("_R", bound=dbm.ResourceMixin)
_K = TypeVar("_K")
_N = TypeVar("_N", bound="schema.Node")


class ConnectionLoader(Generic[_K, _N], metaclass=ABCMeta):
    _session: AsyncSession
    _edges_loader: DataLoader[tuple[_K, PaginationParams], list[Edge[_N]]]
    _count_loader: DataLoader[_K, int]
    _min_max_ids_loader: DataLoader[_K, MinMaxIds]

    def __init__(self, session: AsyncSession):
        self._session = session
        self._edges_loader = DataLoader(load_fn=self._load_edges)
        self._count_loader = DataLoader(load_fn=self._load_counts)
        self._min_max_ids_loader = DataLoader(load_fn=self._load_min_max_ids)

    def make_connection(self, key: _K, pagination_params: PaginationParams):
        return Connection(
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


class CabinetConnectionLoader(ConnectionLoader[None, "schema.Cabinet"]):
    async def _load_edges(
        self, keys: list[tuple[None, PaginationParams]]
    ) -> list[list[Edge["schema.Cabinet"]]]:
        rvs: list[list[Edge[schema.Cabinet]]] = []
        for k, p in keys:
            if p.after is None:
                stmt = sa.select(dbm.Cabinet).order_by(dbm.Cabinet.id)
            else:
                stmt = select_after_uuid(dbm.Cabinet, uuid_from_cursor(p.after))
            stmt = stmt.limit(p.first if p.first is not None else DEFAULT_LIMIT)
            cabinets = (await self._session.execute(stmt)).scalars().all()
            rvs.append(
                [
                    Edge(
                        cursor=cursor_from_uuid(c.uuid),
                        node=schema.Cabinet(db_id=c.id, id=c.uuid, name=c.name),
                    )
                    for c in cabinets
                ]
            )

        return rvs

    async def _load_counts(self, keys: list[None]) -> list[int]:
        cabinet_count = (
            await self._session.execute(sa.select(sa.func.count(dbm.Cabinet.id)))
        ).scalar_one()
        return [cabinet_count] * len(keys)

    async def _load_min_max_ids(self, keys: list[None]) -> list[Optional[MinMaxIds]]:
        min_max_id_stmt = sa.select(sa.func.min(dbm.Cabinet.id), sa.func.max(dbm.Cabinet.id))
        min_id, max_id = (await self._session.execute(min_max_id_stmt)).one()
        return [MinMaxIds(min_id, max_id)] * len(keys)


class CabinetDrawerConnectionLoader(ConnectionLoader[int, "schema.Drawer"]):
    async def _load_edges(
        self, keys: list[tuple[int, PaginationParams]]
    ) -> list[list[Edge["schema.Drawer"]]]:
        if len(keys) == 0:
            return []

        sub_stmts: list[sa.Select] = []
        for key_idx, (cabinet_id, p) in enumerate(keys):
            first = p.first if p.first is not None else DEFAULT_LIMIT
            stmt = (
                sa.select(dbm.Drawer, sa.literal(key_idx).label("key_idx"))
                .where(dbm.Drawer.cabinet_id == cabinet_id)
                .order_by(dbm.Drawer.id.asc())
            )
            if p.after is not None:
                stmt = select_after_uuid(dbm.Drawer, uuid_from_cursor(p.after), base_select=stmt)
            stmt = stmt.limit(first)
            sub_stmts.append(stmt)
        stmt = sa.select(dbm.Drawer, sa.literal_column("key_idx")).from_statement(
            sa.union_all(*sub_stmts)
        )

        drawers_by_key_idx = defaultdict[int, list[dbm.Drawer]](list)
        for d, key_idx in await self._session.execute(stmt):
            drawers_by_key_idx[key_idx].append(d)

        return [
            [
                Edge(
                    cursor=cursor_from_uuid(d.uuid),
                    node=schema.Drawer(db_id=d.id, id=d.uuid, label=d.label),
                )
                for d in drawers_by_key_idx[key_idx]
            ]
            for key_idx, (cabinet_id, _) in enumerate(keys)
        ]

    async def _load_counts(self, keys: list[int]) -> list[int]:
        stmt = (
            sa.select(dbm.Drawer.cabinet_id, sa.func.count(dbm.Drawer.id))
            .group_by(dbm.Drawer.cabinet_id)
            .having(dbm.Drawer.cabinet_id.in_(keys))
        )
        counts_by_id = {id_: count for id_, count in (await self._session.execute(stmt)).all()}
        return [counts_by_id.get(id_, 0) for id_ in keys]

    async def _load_min_max_ids(self, keys: list[int]) -> list[Optional[MinMaxIds]]:
        stmt = (
            sa.select(
                dbm.Drawer.cabinet_id, sa.func.min(dbm.Drawer.id), sa.func.max(dbm.Drawer.id)
            )
            .group_by(dbm.Drawer.cabinet_id)
            .having(dbm.Drawer.cabinet_id.in_(keys))
        )
        min_max_by_id = {
            id_: MinMaxIds(min_, max_)
            for id_, min_, max_ in (await self._session.execute(stmt)).all()
        }
        return [min_max_by_id.get(id_, None) for id_ in keys]


def select_after_uuid(
    model: type[_R], uuid: UUID, *, base_select: Optional[sa.Select[tuple[_R]]] = None
) -> sa.Select[tuple[_R]]:
    subquery = (
        sa.select(model.id).where(model.uuid == uuid).order_by(model.id.asc()).scalar_subquery()
    )
    base_select = (
        base_select if base_select is not None else sa.select(model).order_by(model.id.asc())
    )
    return base_select.where(model.id > subquery)


def uuid_from_cursor(cursor: str) -> UUID:
    return UUID(bytes=base64.b64decode(cursor))


def cursor_from_uuid(uuid_: UUID) -> str:
    return base64.standard_b64encode(uuid_.bytes).decode("ascii")
