import asyncio
from typing import Annotated

import sqlalchemy as sa
import typer
from rich.console import Console
from rich.table import Table

from ..db import models as dbm
from ._db import db_session

app = typer.Typer()
console = Console()


async def _search(sqlalchemy_db_url: str, search: str):
    stmt = (
        sa.select(dbm.User)
        .where(
            sa.or_(
                dbm.User.display_name.icontains(search, autoescape=True),
                dbm.User.email.icontains(search, autoescape=True),
            )
        )
        .order_by(dbm.User.id)
    )

    table = Table("Id", "Display name", "Email")
    async with db_session(sqlalchemy_db_url) as session:
        for user in (await session.execute(stmt)).scalars():
            table.add_row(str(user.uuid), user.display_name, user.email)
    console.print(table)


@app.command()
def search(
    sqlalchemy_db_url: Annotated[str, typer.Option(envvar="SQLALCHEMY_DB_URL")],
    search: Annotated[str, typer.Argument()],
):
    asyncio.run(_search(sqlalchemy_db_url, search))
