"""
SQLAlchemy models defining the database schema.

"""

import datetime
import uuid as uuid_
from dataclasses import dataclass
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, backref, mapped_column, relationship


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


class _ResourceMixin(_IdMixin, _UUIDMixin, _TimestampsMixin):
    pass


@dataclass
class Cabinet(Base, _ResourceMixin):
    __tablename__ = "cabinets"

    name: Mapped[str]


sa.Index("idx_cabinets_uuid", Cabinet.uuid)


@dataclass
class Drawer(Base, _ResourceMixin):
    __tablename__ = "drawers"

    label: Mapped[str]
    cabinet_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("cabinets.id"))

    cabinet: Mapped[Cabinet] = relationship(
        backref=backref("drawers", cascade="all, delete-orphan"), lazy="raise"
    )


sa.Index("idx_drawers_uuid", Drawer.uuid)
sa.Index("idx_drawers_cabinet", Drawer.cabinet_id)


@dataclass
class Component(Base, _ResourceMixin):
    __tablename__ = "components"

    code: Mapped[str]
    description: Mapped[Optional[str]]
    datasheet_url: Mapped[Optional[str]]


sa.Index("idx_components_uuid", Component.uuid)


@dataclass
class Collection(Base, _ResourceMixin):
    __tablename__ = "collections"
    __table_args__ = (sa.CheckConstraint("count >= 0"),)

    count: Mapped[int]
    drawer_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("drawers.id"))
    component_id: Mapped[int] = mapped_column(sa.BigInteger, sa.ForeignKey("components.id"))

    drawer: Mapped[Drawer] = relationship(
        backref=backref("collections", cascade="all, delete-orphan"), lazy="raise"
    )
    component: Mapped[Component] = relationship(
        backref=backref("collections", cascade="all, delete-orphan"), lazy="raise"
    )


sa.Index("idx_collections_uuid", Collection.uuid)
sa.Index("idx_collections_drawer", Collection.drawer_id)
sa.Index("idx_collections_component", Collection.component_id)
