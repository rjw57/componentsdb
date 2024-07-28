import datetime
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


def fake_user(faker: Faker) -> m.User:
    return m.User(
        email=faker.optional.email(),
        email_verified=faker.pybool(),
        display_name=faker.name(),
        avatar_url=faker.optional.url(schemes=["https"]),
    )


def fake_access_token(faker: Faker, user: Optional[m.User] = None) -> m.AccessToken:
    user = user if user is not None else fake_user(faker)
    return m.AccessToken(token=faker.slug(), user=user, expires_at=faker.date_time(datetime.UTC))


def fake_federated_user_credential(faker: Faker, user: Optional[m.User] = None) -> m.AccessToken:
    user = user if user is not None else fake_user(faker)
    return m.FederatedUserCredential(
        subject=faker.user_name(),
        audience=faker.url(schemes=["https"]),
        issuer=faker.url(schemes=["https"]),
        user=user,
    )
