import pytest
import responses

from .jose import *  # noqa: F401, F403
from .oidc import *  # noqa: F401, F403


@pytest.fixture(autouse=True)
def mocked_responses() -> responses.RequestsMock:
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
