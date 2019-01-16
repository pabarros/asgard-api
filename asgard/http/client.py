from typing import Union, Optional
from aiohttp import ClientSession


class _HttpClient:
    _session: Optional[ClientSession]

    def __init__(self, session_class, url: str, method: str, *args, **kwargs) -> None:
        self._session = None
        self._session_class = session_class
        self._url = url
        self._args = args
        self._kwargs = kwargs
        self._method = method

    async def __aenter__(self):
        if not self._session:
            self._session = self._session_class(*self._args, **self._kwargs)
        return await self._return_session_method(self._session, self._method)(self._url)

    def _return_session_method(self, session, method_name):
        return getattr(session, method_name.lower())

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self._session.close()


class _HttpClientMaker:
    def get(self, url: str, *args, **kwargs):
        return _HttpClient(ClientSession, url, "GET", *args, **kwargs)

    def post(self, url: str, *args, **kwargs):
        return _HttpClient(ClientSession, url, "POST", *args, **kwargs)

    def put(self, url: str, *args, **kwargs):
        return _HttpClient(ClientSession, url, "PUT", *args, **kwargs)

    def delete(self, url: str, *args, **kwargs):
        return _HttpClient(ClientSession, url, "DELETE", *args, **kwargs)


http_client = _HttpClientMaker()
