from typing import Any, Generic, NamedTuple, Optional, TypeVar

import strawberry
from strawberry.dataloader import DataLoader

DEFAULT_LIMIT = 100


@strawberry.type
class Node:
    db_id: strawberry.Private[int]
    id: strawberry.ID


_N = TypeVar("_N", bound=Node)


class PaginationParams(NamedTuple):
    after: Optional[str] = None
    first: Optional[int] = None


class MinMaxIds(NamedTuple):
    min: int
    max: int


@strawberry.type
class Edge(Generic[_N]):
    cursor: str
    node: _N


@strawberry.type
class PageInfo:
    start_db_id: strawberry.Private[Optional[int]]
    end_db_id: strawberry.Private[Optional[int]]
    min_max_ids: strawberry.Private[Optional[MinMaxIds]]

    start_cursor: Optional[str]
    end_cursor: Optional[str]

    @strawberry.field
    async def has_previous_page(self) -> bool:
        if self.start_db_id is None:
            return False
        if self.min_max_ids is None:
            return False
        return self.min_max_ids.min < self.start_db_id

    @strawberry.field
    async def has_next_page(self) -> bool:
        if self.end_db_id is None:
            return False
        if self.min_max_ids is None:
            return False
        return self.min_max_ids.max > self.end_db_id


@strawberry.type
class Connection(Generic[_N]):
    loader_key: strawberry.Private[Any]
    pagination_params: strawberry.Private[PaginationParams]
    edges_loader: strawberry.Private[
        DataLoader[tuple[type["loader_key"], PaginationParams], list[Edge[_N]]]
    ]
    count_loader: strawberry.Private[DataLoader[type["loader_key"], int]]
    min_max_ids_loader: strawberry.Private[DataLoader[type["loader_key"], MinMaxIds]]

    async def _get_edges(self) -> list[Edge[_N]]:
        return await self.edges_loader.load((self.loader_key, self.pagination_params))

    @strawberry.field
    async def count(self) -> int:
        return await self.count_loader.load(self.loader_key)

    @strawberry.field
    async def edges(self) -> list[Edge[_N]]:
        return await self._get_edges()

    @strawberry.field
    async def nodes(self) -> list[_N]:
        return [e.node for e in await self._get_edges()]

    @strawberry.field
    async def page_info(self) -> PageInfo:
        edges = await self._get_edges()
        min_max_ids = await self.min_max_ids_loader.load(self.loader_key)
        return PageInfo(
            start_db_id=edges[0].node.db_id if len(edges) > 0 else None,
            start_cursor=edges[0].cursor if len(edges) > 0 else None,
            end_db_id=edges[0].node.db_id if len(edges) > 0 else None,
            end_cursor=edges[0].cursor if len(edges) > 0 else None,
            min_max_ids=min_max_ids,
        )
