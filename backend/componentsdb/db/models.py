"""
SQLAlchemy models defining the database schema.

"""

import datetime
import uuid as uuid_
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


# The 'type:ignore' is required because mypy doesn't understand that "kw_only" can be passed to
# MappedAsDataclass.
class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase, kw_only=True):
    # type:ignore[call-arg]
    pass


class _IdMixin(MappedAsDataclass):
    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, default=None)


class _UUIDMixin(MappedAsDataclass):
    uuid: Mapped[uuid_.UUID] = mapped_column(
        sa.UUID, nullable=False, server_default=sa.Function("gen_random_uuid"), default=None
    )


class _TimestampsMixin(MappedAsDataclass):
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.Function("now"), default=None
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.Function("now"), default=None
    )


class ResourceMixin(_IdMixin, _UUIDMixin, _TimestampsMixin):
    pass


class Cabinet(Base, ResourceMixin):
    __tablename__ = "cabinets"

    name: Mapped[str]
    drawers: Mapped[list["Drawer"]] = relationship(
        cascade="all, delete-orphan",
        back_populates="cabinet",
        default_factory=list,
        repr=False,
    )


sa.Index("idx_cabinets_uuid", Cabinet.uuid)


class Drawer(Base, ResourceMixin):
    __tablename__ = "drawers"

    label: Mapped[str]
    cabinet_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("cabinets.id"), default=None
    )

    cabinet: Mapped[Cabinet] = relationship(back_populates="drawers", default=None, repr=False)
    collections: Mapped[list["Collection"]] = relationship(
        cascade="all, delete-orphan",
        back_populates="drawer",
        default_factory=list,
        repr=False,
    )


sa.Index("idx_drawers_uuid", Drawer.uuid)
sa.Index("idx_drawers_cabinet", Drawer.cabinet_id)


class Component(Base, ResourceMixin):
    __tablename__ = "components"

    code: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(default=None)
    datasheet_url: Mapped[Optional[str]] = mapped_column(default=None)
    search_text: Mapped[str] = mapped_column(
        sa.Computed("lower(coalesce(code, '') || coalesce(description, ''))"),
        init=False,
        repr=False,
    )

    collections: Mapped[list["Collection"]] = relationship(
        cascade="all, delete-orphan", back_populates="component", default_factory=list, repr=False
    )


sa.Index("idx_components_uuid", Component.uuid)
sa.Index(
    "idx_components_trigrams",
    Component.search_text,
    postgresql_using="gin",
    postgresql_ops={
        "search_text": "gin_trgm_ops",
    },
)


class Collection(Base, ResourceMixin):
    __tablename__ = "collections"
    __table_args__ = (sa.CheckConstraint("count >= 0"),)

    count: Mapped[int]
    drawer_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("drawers.id"), default=None
    )
    component_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("components.id"), default=None
    )

    drawer: Mapped[Drawer] = relationship(back_populates="collections", default=None, repr=False)
    component: Mapped[Component] = relationship(
        back_populates="collections", default=None, repr=False
    )


sa.Index("idx_collections_uuid", Collection.uuid)
sa.Index("idx_collections_drawer", Collection.drawer_id)
sa.Index("idx_collections_component", Collection.component_id)


class User(Base, ResourceMixin):
    __tablename__ = "users"

    email: Mapped[Optional[str]] = mapped_column(default=None)
    display_name: Mapped[str] = mapped_column()
    avatar_url: Mapped[Optional[str]] = mapped_column(default=None)
    email_verified: Mapped[bool] = mapped_column(server_default="f")

    federated_credentials: Mapped[list["FederatedUserCredential"]] = relationship(
        cascade="all, delete-orphan", back_populates="user", default_factory=list, repr=False
    )


sa.Index("idx_users_uuid", User.uuid)


class AccessToken(Base, _TimestampsMixin):
    __tablename__ = "access_tokens"

    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("users.id"), default=None)
    expires_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))

    user: Mapped[User] = relationship(default=None)


sa.Index("idx_access_tokens_expires_at", AccessToken.expires_at)


class RefreshToken(Base, _TimestampsMixin):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("users.id"), default=None)
    expires_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime(timezone=True))
    used_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True, default=None
    )

    user: Mapped[User] = relationship(default=None, repr=False)


sa.Index("idx_refresh_tokens_expires_at", RefreshToken.expires_at)


class FederatedUserCredential(Base, ResourceMixin):
    __tablename__ = "federated_user_credentials"

    subject: Mapped[str]
    audience: Mapped[str]
    issuer: Mapped[str]
    user_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("users.id"), default=None)

    user: Mapped[User] = relationship(
        back_populates="federated_credentials", default=None, repr=False
    )


sa.Index("idx_federated_user_credentials_user", FederatedUserCredential.user_id)
sa.Index(
    "idx_federated_user_credentials_subject_audience_issuer",
    FederatedUserCredential.subject,
    FederatedUserCredential.audience,
    FederatedUserCredential.issuer,
    unique=True,
)


class FederatedUserCredentialUse(Base, _IdMixin, _TimestampsMixin):
    __tablename__ = "federated_user_credential_uses"

    claims: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(postgresql.JSONB),
        server_default=sa.func.json_build_object(),
        default=None,
    )


sa.Index(
    "idx_federated_user_credential_uses_claims",
    FederatedUserCredentialUse.claims,
    postgresql_using="gin",
)


class Role(Base, _UUIDMixin):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(primary_key=True)

    permissions: Mapped[list["Permission"]] = relationship(
        secondary=lambda: RolePermissionBinding.__table__,
        repr=False,
        default_factory=list,
        cascade="all, delete",
    )


class Permission(Base, _UUIDMixin):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(primary_key=True)


class RolePermissionBinding(Base):
    __tablename__ = "role_permission_bindings"

    role_id: Mapped[str] = mapped_column(sa.ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[str] = mapped_column(sa.ForeignKey("permissions.id"), primary_key=True)


class UserGlobalRoleBinding(Base, _TimestampsMixin):
    __tablename__ = "user_global_role_bindings"

    user_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("users.id"), default=None, primary_key=True
    )
    role_id: Mapped[str] = mapped_column(sa.ForeignKey("roles.id"), default=None, primary_key=True)

    user: Mapped[User] = relationship(default=None, repr=False, cascade="all, delete")
    role: Mapped[Role] = relationship(default=None, repr=False, cascade="all, delete")


class UserCabinetRoleBinding(Base, _TimestampsMixin):
    __tablename__ = "user_cabinet_role_bindings"

    user_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("users.id"), default=None, primary_key=True
    )
    cabinet_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("cabinets.id"), default=None, primary_key=True
    )
    role_id: Mapped[str] = mapped_column(sa.ForeignKey("roles.id"), default=None, primary_key=True)

    user: Mapped[User] = relationship(default=None, repr=False, cascade="all, delete")
    role: Mapped[Role] = relationship(default=None, repr=False, cascade="all, delete")
    cabinet: Mapped[Cabinet] = relationship(default=None, repr=False, cascade="all, delete")
