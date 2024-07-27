import asyncio
import contextlib
from typing import Mapping, Optional

import requests
from requests.exceptions import RequestException
from requests_cache import CachedSession

from ..exceptions import TransportError
from . import AsyncRequestBase, RequestBase, Response


class RequestsSession(RequestBase):
    """
    HTTP transport based on a requests.Session object.

    Args:
        session: requests.Session to use for HTTP requests. If omitted a new session is created.
    """

    session: requests.Session

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session if session is not None else requests.Session()

    def __call__(
        self,
        url: str,
        body: Optional[bytes] = None,
        method: Optional[str] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Response:
        try:
            r = self.session.get(url, headers={"Accept": "application/json"})
        except RequestException as e:
            raise TransportError(f"Error requesting URL {url!r}: {e}")
        return Response(content=r.content, status_code=r.status_code, headers=r.headers)


class AsyncRequestsSession(AsyncRequestBase):
    """
    An asyncio wrapper around RequestsSession.
    """

    _sync_request: RequestsSession

    def __init__(self, *args, **kwargs):
        self._sync_request = RequestsSession(*args, **kwargs)

    async def __call__(self, *args, **kwargs) -> Response:
        return await asyncio.to_thread(self._sync_request, *args, **kwargs)


_cached_session = CachedSession(backend="memory")

#: RequestsSession object which uses an in-memory cache.
request = RequestsSession(_cached_session)

#: AsyncRequestsSession object which uses an in-memory cache.
async_request = AsyncRequestsSession(_cached_session)


@contextlib.contextmanager
def caching_disabled():
    "Context manager which disables caching for the default request and async_request transports."
    with _cached_session.cache_disabled():
        yield
