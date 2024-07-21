import pytest

from componentsdb.graphql.schema import schema

from ..asserts import expected_sql_query_count


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
    with expected_sql_query_count(db_session, 2):
        result = await schema.execute(query, context_value=context)
    assert result.errors is None
    assert len(cabinets) == result.data["cabinets"]["count"]


@pytest.mark.asyncio
async def test_pagination(db_session, cabinets, context):
    after, limit = None, 5
    cabinets = sorted(cabinets, key=lambda c: c.id)
    query = """
        query ($after: String, $limit: Int) {
            cabinets(after: $after, limit: $limit) {
                nodes { id }
                pageInfo { endCursor, hasNextPage }
            }
        }
    """
    actual_ids = set()
    for _ in range(200):
        result = await schema.execute(
            query, context_value=context, variable_values={"after": after, "limit": limit}
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
        cabinets {
            nodes {
                id
                drawers {
                    nodes { id }
                }
            }
        }
    }
    """
    with expected_sql_query_count(db_session, 2):
        result = await schema.execute(query, context_value=context)
    assert result.errors is None
    for c in result.data["cabinets"]["nodes"]:
        ds = c["drawers"]["nodes"]
        expected_drawers = sorted(
            [d for d in drawers if d.cabinet_id == cabinets_by_uuid[c["id"]].id],
            key=lambda d: d.id,
        )
        if len(expected_drawers) > 0:
            assert (
                len(ds) > 0
            ), f"Cabinet {c['id']} has {len(expected_drawers)} drawers but {len(ds)} returned."
        for d, n in zip(expected_drawers, ds):
            assert str(d.uuid) == n["id"]
