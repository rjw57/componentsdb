import pytest
import responses

from .authfixtures import *  # noqa: F401, F403
from .dbfixtures import *  # noqa: F401, F403
from .josefixtures import *  # noqa: F401, F403
from .oidcfixtures import *  # noqa: F401, F403


@pytest.fixture(autouse=True)
def mocked_responses() -> responses.RequestsMock:
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Since we use docker to manage containers, we want requests to the docker daemon to
        # succeed.
        rsps.add_passthru("http+docker://")
        yield rsps
