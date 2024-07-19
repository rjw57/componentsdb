from typing import Optional

from faker import Faker

from . import models as m


def fake_cabinet(faker: Faker) -> m.Cabinet:
    return m.Cabinet(name=faker.bs())


def fake_component(faker: Faker) -> m.Component:
    return m.Component(
        code=faker.bothify("??####"),
        description=faker.optional.sentence(),
        datasheet_url=faker.optional.url(),
    )


def fake_drawer(faker: Faker, *, cabinet: Optional[m.Cabinet] = None) -> m.Drawer:
    cabinet = cabinet if cabinet is not None else fake_cabinet(faker)
    return m.Drawer(label=str(faker.random_int(1, 1000)), cabinet=cabinet)


def fake_collection(
    faker: Faker, *, drawer: Optional[m.Drawer] = None, component: Optional[m.Component] = None
) -> m.Collection:
    component = component if component is not None else fake_component(faker)
    drawer = drawer if drawer is not None else fake_drawer(faker)
    return m.Collection(
        count=faker.random_int(0, 1000),
        component=component,
        drawer=drawer,
    )
