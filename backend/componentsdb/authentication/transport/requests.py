import asyncio
from typing import Optional

import requests
from requests.exceptions import RequestException

from ..exceptions import FetchError


class RequestSessionFetch:
    """
    Fetch callable which fetches using a requests.Session.

    Args:
        session: requests.Session to use for fetching. If omitted a new session is created.
    """

    session: requests.Session

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session if session is not None else requests.Session()

    def __call__(self, url: str) -> bytes:
        try:
            r = requests.get(url, headers={"Accept": "application/json"})
            r.raise_for_status()
            return r.content
        except RequestException as e:
            raise FetchError(f"Error fetching URL {url!r}: {e}")


class AsyncRequestSessionFetch:
    """
    Fetch callable which is an asyncio wrapper around RequestSessionFetch.
    """

    _sync_fetch: RequestSessionFetch

    def __init__(self, *args, **kwargs):
        self._sync_fetch = RequestSessionFetch(*args, **kwargs)

    async def __call__(self, url: str) -> bytes:
        return await asyncio.to_thread(self._sync_fetch, url)


def fetch(url: str) -> bytes:
    "Fetch callable which uses a default requests session."
    return RequestSessionFetch()(url)


async def async_fetch(url: str) -> bytes:
    """
    Asynchronous fetch callable which uses a default requests session running in a separate thread.
    """
    return await AsyncRequestSessionFetch()(url)
