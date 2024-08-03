import asyncio
import sqlite3
from typing import Annotated

import typer
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import models as dbm
from ._db import db_session

app = typer.Typer()


async def _bitsbox(session: AsyncSession, sqlite_con):
    cur = sqlite_con.cursor()

    cabinets: dict[int, dbm.Cabinet] = {}
    for cab_id, name in cur.execute("SELECT id, name FROM cabinets"):
        cabinets[cab_id] = dbm.Cabinet(name=name)
    session.add_all(cabinets.values())

    drawers: dict[int, dbm.Drawer] = {}
    for drawer_id, label, cab_id in cur.execute(
        """
        SELECT drawers.id, drawers.label, locations.cabinet_id
        FROM drawers
        JOIN locations ON drawers.location_id = locations.id
        """
    ):
        if cab_id not in cabinets:
            print(f"Warning: drawer {label} not in any cabinet")
            continue
        drawers[drawer_id] = dbm.Drawer(label=label, cabinet=cabinets[cab_id])
    session.add_all(drawers.values())

    for name, description, count, drawer_id in cur.execute(
        """
        SELECT name, description, content_count, drawer_id
        FROM collections
        """
    ):
        if drawer_id not in drawers:
            print(f"Warning: component {name} not in any drawers.")
            continue
        component = dbm.Component(code=name, description=description)
        collection = dbm.Collection(count=count, component=component, drawer=drawers[drawer_id])
        session.add_all([component, collection])


@app.command()
def bitsbox(
    sqlalchemy_db_url: Annotated[str, typer.Option(envvar="SQLALCHEMY_DB_URL")],
    sqlite_db: Annotated[str, typer.Argument()],
):
    sqlite_con = sqlite3.connect(sqlite_db)

    async def _do_import():
        async with db_session(sqlalchemy_db_url) as session:
            await _bitsbox(session, sqlite_con)

    asyncio.run(_do_import())
