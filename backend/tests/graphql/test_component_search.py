import pytest
import pytest_asyncio

from componentsdb.db import fakes
from componentsdb.graphql import schema

from ..asserts import expected_sql_query_maximum_count


@pytest_asyncio.fixture
async def searchable_components(faker, db_session, cabinets, db_session_lock):
    def make_components(description):
        cs = [fakes.fake_component(faker) for _ in range(20)]
        for c in cs:
            c.description = description
        return cs

    all_components = []
    all_components.extend(make_components("foofoo"))
    all_components.extend(make_components("foofoo x"))
    all_components.extend(make_components("barbar"))
    all_components.extend(make_components("barbar x"))
    all_components = faker.random_elements(all_components, unique=True, length=len(all_components))
    db_session.add_all(all_components)
    async with db_session_lock:
        await db_session.flush()

    return all_components


@pytest.mark.asyncio
async def test_basic_query(db_session, context, searchable_components):
    query = """
        query {
            components {
                count
                nodes { id }
            }
        }
    """
    with expected_sql_query_maximum_count(db_session, 5):
        result = await schema.execute(
            query, context_value=context, variable_values={"search": "foo"}
        )
    assert result.errors is None
    assert result.data is not None

    expected_ids = {str(c.uuid) for c in searchable_components}
    actual_ids = {n["id"] for n in result.data["components"]["nodes"]}
    assert len(searchable_components) == result.data["components"]["count"]
    assert len(searchable_components) == len(result.data["components"]["nodes"])
    assert expected_ids == actual_ids


@pytest.mark.asyncio
async def test_search_query(db_session, context, searchable_components):
    query = """
        query ($search: String) {
            components(search: $search) {
                count
                nodes { id }
            }
        }
    """
    with expected_sql_query_maximum_count(db_session, 5):
        result = await schema.execute(
            query, context_value=context, variable_values={"search": "foo"}
        )
    assert result.errors is None
    assert result.data is not None

    expected_foos = [c for c in searchable_components if "foo" in c.description]
    expected_ids = {str(c.uuid) for c in expected_foos}
    actual_ids = {n["id"] for n in result.data["components"]["nodes"]}
    assert len(expected_foos) == result.data["components"]["count"]
    assert len(expected_foos) == len(result.data["components"]["nodes"])
    assert expected_ids == actual_ids


@pytest.mark.asyncio
async def test_pagination(db_session, context, searchable_components):
    after, first = None, 3
    query = """
        query ($search: String, $after: String, $first: Int) {
            components(search: $search, after: $after, first: $first) {
                nodes { id }
                pageInfo { endCursor, hasNextPage }
            }
        }
    """
    actual_ids = set()
    for _ in range(200):
        with expected_sql_query_maximum_count(db_session, 5):
            result = await schema.execute(
                query,
                context_value=context,
                variable_values={"search": "foo", "after": after, "first": first},
            )
            assert result.errors is None
        actual_ids.update({n["id"] for n in result.data["components"]["nodes"]})
        if not result.data["components"]["pageInfo"]["hasNextPage"]:
            break
        after = result.data["components"]["pageInfo"]["endCursor"]
    else:
        assert False, "Infinite pagination loop?"

    expected_foos = [c for c in searchable_components if "foo" in c.description]
    expected_ids = {str(c.uuid) for c in expected_foos}
    assert expected_ids == actual_ids
