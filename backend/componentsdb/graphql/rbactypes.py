from typing import Optional

import strawberry

from . import context
from .paginationtypes import Connection, Node, PaginationParams


@strawberry.type
class Permission(Node):
    pass


@strawberry.type
class Role(Node):
    @strawberry.field
    def permissions(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> "Connection[Permission]":
        raise NotImplementedError()


@strawberry.type
class RBACQueries:
    @strawberry.field
    async def permissions(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection[Permission]:
        return (
            context.get_db(info.context)
            .permission_connection(PaginationParams(after=after, first=first))
            .make_connection(None)
        )

    @strawberry.field
    async def roles(
        self, info: strawberry.Info, after: Optional[str] = None, first: Optional[int] = None
    ) -> Connection[Role]:
        return (
            context.get_db(info.context)
            .role_connection(PaginationParams(after=after, first=first))
            .make_connection(None)
        )
