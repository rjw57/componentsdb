import sqlalchemy as sa
import sqlalchemy.orm as saorm
import strawberry

from ..db import models as dbm
from . import context


@strawberry.type
class Permission:
    id: strawberry.ID


@strawberry.type
class Role:
    id: strawberry.ID
    permissions: list[Permission]


@strawberry.type
class RBACQueries:
    @strawberry.field
    async def permissions(self, info: strawberry.Info) -> list[Permission]:
        db = context.get_db(info.context)
        async with db.db_lock:
            return [
                Permission(id=p.name)
                for p in (
                    await db.db_session.execute(
                        sa.select(dbm.Permission).order_by(dbm.Permission.name)
                    )
                ).scalars()
            ]

    @strawberry.field
    async def roles(self, info: strawberry.Info) -> list[Role]:
        db = context.get_db(info.context)
        async with db.db_lock:
            return [
                Role(id=role.name, permissions=[Permission(id=p.name) for p in role.permissions])
                for role in (
                    await db.db_session.execute(
                        sa.select(dbm.Role).options(
                            saorm.joinedload(dbm.Role.permissions), saorm.raiseload("*")
                        )
                    )
                )
                .unique()
                .scalars()
            ]
