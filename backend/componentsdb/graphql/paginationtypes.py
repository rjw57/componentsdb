from typing import Any, Generic, NamedTuple, Optional, Sequence, TypeVar

import strawberry
from strawberry.dataloader import DataLoader

from ..db.models import ResourceMixin

DEFAULT_LIMIT = 100


@strawberry.type
class Node:
    db_resource: strawberry.Private[ResourceMixin]
    id: strawberry.ID


_N = TypeVar("_N", bound=Node)


class PaginationParams(NamedTuple):
    after: Optional[str] = None
    first: Optional[int] = None


@strawberry.type
class Edge(Generic[_N]):
    cursor: str
    node: _N


class LoadEdgesResult(Generic[_N], NamedTuple):
    edges: Sequence[Edge[_N]]
    has_next_page: bool
    has_previous_page: bool


@strawberry.type
class PageInfo:
    start_cursor: Optional[str]
    end_cursor: Optional[str]
    has_previous_page: bool
    has_next_page: bool


@strawberry.type
class Connection(Generic[_N]):
    loader_key: strawberry.Private[Any]
    edges_loader: strawberry.Private[DataLoader[Any, LoadEdgesResult[_N]]]
    count_loader: strawberry.Private[DataLoader[Any, int]]

    async def _get_edges(self) -> LoadEdgesResult[_N]:
        return await self.edges_loader.load(self.loader_key)

    @strawberry.field
    async def count(self) -> int:
        return await self.count_loader.load(self.loader_key)

    @strawberry.field
    async def edges(self) -> Sequence[Edge[_N]]:
        return (await self._get_edges()).edges

    @strawberry.field
    async def nodes(self) -> Sequence[_N]:
        return [e.node for e in (await self._get_edges()).edges]

    @strawberry.field
    async def page_info(self) -> PageInfo:
        edges_result = await self._get_edges()
        edges = edges_result.edges
        return PageInfo(
            start_cursor=edges[0].cursor if len(edges) > 0 else None,
            end_cursor=edges[-1].cursor if len(edges) > 0 else None,
            has_previous_page=edges_result.has_previous_page,
            has_next_page=edges_result.has_next_page,
        )
