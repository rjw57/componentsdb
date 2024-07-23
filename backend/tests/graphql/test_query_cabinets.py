import uuid

import pytest
from faker import Faker

from componentsdb.graphql import schema

from ..asserts import expected_sql_query_count, expected_sql_query_maximum_count


@pytest.mark.asyncio
async def test_basic_list(db_session, cabinets, context):
    cabinets = sorted(cabinets, key=lambda c: c.id)
    query = "query { cabinets { nodes { id } edges { cursor node { id } } } }"
    with expected_sql_query_count(db_session, 1):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None
    nodes = result.data["cabinets"]["nodes"]
    edges = result.data["cabinets"]["edges"]
    assert len(nodes) > 0
    for n, c in zip(nodes, cabinets):
        assert n["id"] == str(c.uuid)
    for e, c in zip(edges, cabinets):
        assert e["cursor"] is not None
        assert len(["cursor"]) > 0
        assert e["node"]["id"] == str(c.uuid)


@pytest.mark.asyncio
async def test_count(db_session, cabinets, context):
    query = "query { cabinets { count } }"
    with expected_sql_query_count(db_session, 1):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None
    assert len(cabinets) == result.data["cabinets"]["count"]


@pytest.mark.asyncio
async def test_pagination(db_session, cabinets, context):
    after, first = None, 5
    cabinets = sorted(cabinets, key=lambda c: c.id)
    query = """
        query ($after: String, $first: Int) {
            cabinets(after: $after, first: $first) {
                nodes { id }
                pageInfo { endCursor, hasNextPage }
            }
        }
    """
    actual_ids = set()
    for _ in range(200):
        with expected_sql_query_maximum_count(db_session, 2):
            result = await schema.execute(
                query, context_value=context, variable_values={"after": after, "first": first}
            )
            assert result.errors is None
        actual_ids.update({n["id"] for n in result.data["cabinets"]["nodes"]})
        if not result.data["cabinets"]["pageInfo"]["hasNextPage"]:
            break
        after = result.data["cabinets"]["pageInfo"]["endCursor"]
    else:
        assert False, "Infinite pagination loop?"

    expected_ids = {str(c.uuid) for c in cabinets}
    assert expected_ids == actual_ids


@pytest.mark.asyncio
async def test_basic_drawers_query(db_session, cabinets, drawers, context):
    cabinets_by_uuid = {str(c.uuid): c for c in cabinets}
    query = """query {
        cabinets(first: 5) {
            nodes {
                id
                drawers(first: 3) {
                    count
                    nodes { id }
                }
            }
        }
    }
    """
    with expected_sql_query_maximum_count(db_session, 3):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None
    for c in result.data["cabinets"]["nodes"]:
        ds = c["drawers"]["nodes"]
        expected_drawers = sorted(
            [d for d in drawers if d.cabinet_id == cabinets_by_uuid[c["id"]].id],
            key=lambda d: d.id,
        )
        assert c["drawers"]["count"] == len(expected_drawers)
        if len(expected_drawers) > 0:
            assert (
                len(ds) > 0
            ), f"Cabinet {c['id']} has {len(expected_drawers)} drawers but {len(ds)} returned."
        for d, n in zip(expected_drawers, ds):
            assert str(d.uuid) == n["id"]


@pytest.mark.asyncio
async def test_paginated_drawers_query(db_session, cabinets, drawers, context, faker: Faker):
    after, first = None, 5
    query = """
        query ($after: String, $first: Int) {
            cabinets(first: 1) {
                nodes {
                    id
                    drawers(after: $after, first: $first) {
                        nodes { id }
                        pageInfo { endCursor hasNextPage }
                    }
                }
            }
        }
    """
    cabinet_id = None
    actual_ids = set()
    for _ in range(200):
        with expected_sql_query_maximum_count(db_session, 3):
            result = await schema.execute(
                query, context_value=context, variable_values={"after": after, "first": first}
            )
            assert result.errors is None
        assert result.data is not None
        assert result.data["cabinets"]
        assert result.data["cabinets"]["nodes"] is not None
        cabinet_node = result.data["cabinets"]["nodes"][0]
        assert cabinet_id is None or cabinet_id == cabinet_node["id"]
        drawer_nodes = cabinet_node["drawers"]["nodes"]
        actual_ids.update({n["id"] for n in drawer_nodes})
        cabinet_id = cabinet_node["id"]
        if not cabinet_node["drawers"]["pageInfo"]["hasNextPage"]:
            break
        after = cabinet_node["drawers"]["pageInfo"]["endCursor"]
    else:
        assert False, "Infinite pagination loop?"

    cabinet = [c for c in cabinets if str(c.uuid) == cabinet_id][0]
    expected_ids = {str(d.uuid) for d in drawers if d.cabinet_id == cabinet.id}
    assert expected_ids == actual_ids


@pytest.mark.asyncio
async def test_basic_get(db_session, cabinets, context):
    cabinet = cabinets[len(cabinets) >> 1]
    query = "query ($id: ID!) { cabinet(id: $id) { id name } }"
    with expected_sql_query_count(db_session, 1):
        result = await schema.execute(
            query, context_value=context, variable_values={"id": str(cabinet.uuid)}
        )
        assert result.errors is None
    assert result.data is not None
    c = result.data["cabinet"]
    assert c is not None
    assert c["id"] == str(cabinet.uuid)
    assert c["name"] == cabinet.name


@pytest.mark.asyncio
async def test_basic_get_does_not_exist(db_session, cabinets, context):
    query = "query ($id: ID!) { cabinet(id: $id) { id name } }"
    with expected_sql_query_count(db_session, 1):
        result = await schema.execute(
            query, context_value=context, variable_values={"id": str(uuid.uuid4())}
        )
        assert result.errors is None
        assert result.data is not None
    assert result.data["cabinet"] is None


@pytest.mark.asyncio
async def test_single_cabinet_paginated_drawers_query(db_session, cabinets, drawers, context):
    cabinet = cabinets[len(cabinets) >> 1]
    after, first = None, 5
    query = """
        query ($id: ID!, $after: String, $first: Int) {
            cabinet(id: $id) {
                drawers(after: $after, first: $first) {
                    nodes { id }
                    pageInfo { endCursor hasNextPage }
                }
            }
        }
    """
    actual_ids = set()
    for _ in range(200):
        with expected_sql_query_maximum_count(db_session, 3):
            result = await schema.execute(
                query,
                context_value=context,
                variable_values={"id": str(cabinet.uuid), "after": after, "first": first},
            )
            assert result.errors is None
        assert result.data is not None
        assert result.data["cabinet"] is not None
        cabinet_node = result.data["cabinet"]
        drawer_nodes = cabinet_node["drawers"]["nodes"]
        actual_ids.update({n["id"] for n in drawer_nodes})
        if not cabinet_node["drawers"]["pageInfo"]["hasNextPage"]:
            break
        after = cabinet_node["drawers"]["pageInfo"]["endCursor"]
    else:
        assert False, "Infinite pagination loop?"

    expected_ids = {str(d.uuid) for d in drawers if d.cabinet_id == cabinet.id}
    assert expected_ids == actual_ids


@pytest.mark.asyncio
async def test_single_cabinet_drawer_count(db_session, cabinets, drawers, context):
    cabinet = cabinets[len(cabinets) >> 1]
    query = """
        query ($id: ID!) {
            cabinet(id: $id) {
                drawers {
                    count
                }
            }
        }
    """
    with expected_sql_query_maximum_count(db_session, 2):
        result = await schema.execute(
            query, context_value=context, variable_values={"id": str(cabinet.uuid)}
        )
        assert result.errors is None
    assert result.data is not None
    assert result.data["cabinet"] is not None
    assert result.data["cabinet"]["drawers"] is not None
    count = result.data["cabinet"]["drawers"]["count"]
    expected_drawers = [d for d in drawers if d.cabinet_id == cabinet.id]
    assert len(expected_drawers) == count


@pytest.mark.asyncio
async def test_single_cabinet_no_drawers(db_session, cabinets, context):
    cabinet = cabinets[len(cabinets) >> 1]
    query = """
        query ($id: ID!) {
            cabinet(id: $id) {
                drawers {
                    count
                    pageInfo { endCursor hasNextPage }
                }
            }
        }
    """
    with expected_sql_query_maximum_count(db_session, 4):
        result = await schema.execute(
            query, context_value=context, variable_values={"id": str(cabinet.uuid)}
        )
        assert result.errors is None
        assert result.data is not None
    assert result.data["cabinet"] is not None
    assert result.data["cabinet"]["drawers"] is not None
    assert result.data["cabinet"]["drawers"]["count"] == 0
    assert result.data["cabinet"]["drawers"]["pageInfo"]["endCursor"] is None
    assert not result.data["cabinet"]["drawers"]["pageInfo"]["hasNextPage"]


@pytest.mark.asyncio
async def test_cabinet_drawers_backref(db_session, cabinets, drawers, context):
    query = """query {
        cabinets {
            nodes {
                id
                drawers {
                    nodes {
                        cabinet {
                            id
                        }
                    }
                }
            }
        }
    }
    """
    with expected_sql_query_maximum_count(db_session, 3):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None
        assert result.data is not None

    cabinet_nodes = result.data["cabinets"]["nodes"]
    assert len(cabinet_nodes) > 0

    for cn in cabinet_nodes:
        for dn in cn["drawers"]["nodes"]:
            assert dn["cabinet"]["id"] == cn["id"]


@pytest.mark.asyncio
async def test_basic_collections_query(db_session, all_fakes, context):
    query = """query {
        cabinets {
            nodes {
                id
                drawers {
                    nodes {
                        id
                        collections {
                            nodes {
                                id
                                component {
                                    id
                                    code
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    with expected_sql_query_maximum_count(db_session, 4):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None
        assert result.data is not None

    cabinet_nodes = result.data["cabinets"]["nodes"]
    assert len(cabinet_nodes) > 0


@pytest.mark.asyncio
async def test_extreme_back_reference_query(db_session, all_fakes, context):
    query = """query {
        cabinets {
            nodes {
                id
                drawers {
                    nodes {
                        id
                        cabinet { id }
                        collections {
                            nodes {
                                id
                                drawer { id cabinet { id } }
                                component {
                                    collections { nodes { id drawer { id cabinet { id } } } }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    with expected_sql_query_maximum_count(db_session, 7):
        result = await schema.execute(query, context_value=context)
        assert result.errors is None
        assert result.data is not None

    cabinet_nodes = result.data["cabinets"]["nodes"]
    assert len(cabinet_nodes) > 0
