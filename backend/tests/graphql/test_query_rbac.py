import pytest
import sqlalchemy as sa
import sqlalchemy.orm as saorm

from componentsdb.db import models as dbm
from componentsdb.graphql import schema

from ..asserts import expected_sql_query_maximum_count


@pytest.mark.asyncio
async def test_basic_permissions_list(db_session, context):
    query = "query { rbac { permissions { nodes { id } } } }"
    with expected_sql_query_maximum_count(db_session, 2):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None

    expected_permission_ids = {
        p.id for p in (await db_session.execute(sa.select(dbm.Permission))).scalars()
    }
    assert expected_permission_ids == set(
        r["id"] for r in result.data["rbac"]["permissions"]["nodes"]
    )


@pytest.mark.asyncio
async def test_basic_roles_list(db_session, context):
    query = "query { rbac { roles { nodes { id } } } }"
    with expected_sql_query_maximum_count(db_session, 2):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None

    expected_role_ids = {p.id for p in (await db_session.execute(sa.select(dbm.Role))).scalars()}
    assert expected_role_ids == set(r["id"] for r in result.data["rbac"]["roles"]["nodes"])


@pytest.mark.skip(reason="not yet implemented")
@pytest.mark.asyncio
async def test_role_permissions_list(db_session, context):
    query = "query { rbac { roles { nodes { id permissions { nodes { id } } } } } }"
    with expected_sql_query_maximum_count(db_session, 2):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None

    all_roles_by_id = {
        r.id: r
        for r in (
            (
                await db_session.execute(
                    sa.select(dbm.Role).options(saorm.joinedload(dbm.Role.permissions))
                )
            )
            .unique()
            .scalars()
        )
    }

    expected_role_ids = set(all_roles_by_id.keys())
    assert expected_role_ids == set(r["id"] for r in result.data["rbac"]["roles"]["nodes"])

    for r in result.data["rbac"]["roles"]["nodes"]:
        expected_permission_ids = {p.id for p in all_roles_by_id[r["id"]].permissions}
        assert expected_permission_ids == {p["id"] for p in r["permissions"]["nodes"]}
