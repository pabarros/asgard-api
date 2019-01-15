from typing import Union
from aiohttp import ClientSession
from yarl import URL


class _HttpClient:
    _session: ClientSession

    def __init__(
        self, session_class, url: Union[str, URL], method: str, *args, **kwargs
    ):
        self._session = None
        self._session_class = session_class
        self._url = url
        self._args = args
        self._kwargs = kwargs

    async def __aenter__(self):
        if not self._session:
            self._session = self._session_class(*self._args, **self._kwargs)
        return await self._session.get(self._url)

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self._session.close()


class _HttpClientMaker:
    def get(self, url: Union[str, URL], *args, **kwargs):
        return _HttpClient(url=url, method="GET", *args, **kwargs)


http_client = _HttpClientMaker()
