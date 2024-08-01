import asyncio
from typing import Annotated

import typer
from faker import Faker

from ..db import fakes
from ._db import db_session

app = typer.Typer()


async def _create(faker: Faker, sqlalchemy_db_url: str):
    async with db_session(sqlalchemy_db_url) as session:
        cabinets = [fakes.fake_cabinet(faker) for _ in range(4)]
        session.add_all(cabinets)
        drawers = [
            fakes.fake_drawer(faker, cabinet=faker.random_element(cabinets)) for _ in range(60)
        ]
        session.add_all(drawers)
        components = [fakes.fake_component(faker) for _ in range(300)]
        session.add_all(components)
        collections = [
            fakes.fake_collection(faker, drawer=faker.random_element(drawers), component=c)
            for c in components
        ]
        session.add_all(collections)
        await session.flush()


@app.command()
def create(
    sqlalchemy_db_url: Annotated[str, typer.Option(envvar="SQLALCHEMY_DB_URL")],
):
    asyncio.run(_create(Faker(), sqlalchemy_db_url))
