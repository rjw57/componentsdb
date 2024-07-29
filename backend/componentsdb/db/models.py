"""
SQLAlchemy models defining the database schema.

"""

import datetime
import uuid as uuid_
from dataclasses import dataclass
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class _IdMixin(object):
    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True)


class _UUIDMixin(object):
    uuid: Mapped[uuid_.UUID] = mapped_column(
        sa.UUID, nullable=False, server_default=sa.Function("gen_random_uuid")
    )


class _TimestampsMixin(object):
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.Function("now")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.Function("now")
    )


class ResourceMixin(_IdMixin, _UUIDMixin, _TimestampsMixin):
    pass


@dataclass
class Cabinet(Base, ResourceMixin):
    __tablename__ = "cabinets"

    name: Mapped[str]
    drawers: Mapped[list["Drawer"]] = relationship(
        lazy="raise", cascade="all, delete-orphan", back_populates="cabinet"
    )


sa.Index("idx_cabinets_uuid", Cabinet.uuid)


@dataclass
class Drawer(Base, ResourceMixin):
    __tablename__ = "drawers"

    label: Mapped[str]
    cabinet_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("cabinets.id"))

    cabinet: Mapped[Cabinet] = relationship(lazy="raise", back_populates="drawers")
    collections: Mapped[list["Collection"]] = relationship(
        lazy="raise", cascade="all, delete-orphan", back_populates="drawer"
    )


sa.Index("idx_drawers_uuid", Drawer.uuid)
sa.Index("idx_drawers_cabinet", Drawer.cabinet_id)


@dataclass
class Component(Base, ResourceMixin):
    __tablename__ = "components"

    code: Mapped[str]
    description: Mapped[Optional[str]]
    datasheet_url: Mapped[Optional[str]]

    collections: Mapped[list["Collection"]] = relationship(
        cascade="all, delete-orphan", back_populates="component"
    )


sa.Index("idx_components_uuid", Component.uuid)


@dataclass
class Collection(Base, ResourceMixin):
    __tablename__ = "collections"
    __table_args__ = (sa.CheckConstraint("count >= 0"),)

    count: Mapped[int]
    drawer_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("drawers.id"))
    component_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("components.id"))

    drawer: Mapped[Drawer] = relationship(lazy="raise", back_populates="collections")
    component: Mapped[Component] = relationship(lazy="raise", back_populates="collections")


sa.Index("idx_collections_uuid", Collection.uuid)
sa.Index("idx_collections_drawer", Collection.drawer_id)
sa.Index("idx_collections_component", Collection.component_id)


@dataclass
class User(Base, ResourceMixin):
    __tablename__ = "users"

    email: Mapped[Optional[str]]
    display_name: Mapped[str]
    avatar_url: Mapped[Optional[str]]
    email_verified: Mapped[bool] = mapped_column(server_default="f")

    federated_credentials: Mapped[list["FederatedUserCredential"]] = relationship(
        cascade="all, delete-orphan", back_populates="user"
    )


sa.Index("idx_users_uuid", User.uuid)


@dataclass
class AccessToken(Base, _TimestampsMixin):
    __tablename__ = "access_tokens"

    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("users.id"))
    expires_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))

    user: Mapped[User] = relationship(lazy="raise")


sa.Index("idx_access_tokens_expires_at", AccessToken.expires_at)


@dataclass
class RefreshToken(Base, _TimestampsMixin):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("users.id"))
    expires_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    used_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship(lazy="raise")


sa.Index("idx_refresh_tokens_expires_at", RefreshToken.expires_at)


@dataclass
class FederatedUserCredential(Base, ResourceMixin):
    __tablename__ = "federated_user_credentials"

    subject: Mapped[str]
    audience: Mapped[str]
    issuer: Mapped[str]
    user_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("users.id"))

    user: Mapped[User] = relationship(lazy="raise", back_populates="federated_credentials")


sa.Index("idx_federated_user_credentials_user", FederatedUserCredential.user_id)
sa.Index(
    "idx_federated_user_credentials_subject_audience_issuer",
    FederatedUserCredential.subject,
    FederatedUserCredential.audience,
    FederatedUserCredential.issuer,
    unique=True,
)


@dataclass
class FederatedUserCredentialUse(Base, _IdMixin, _TimestampsMixin):
    __tablename__ = "federated_user_credential_uses"

    claims: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(postgresql.JSONB), server_default=sa.func.json_build_object()
    )


sa.Index(
    "idx_federated_user_credential_uses_claims",
    FederatedUserCredentialUse.claims,
    postgresql_using="gin",
)
