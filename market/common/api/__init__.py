from typing import Any, Tuple, Dict, Union
from urllib.parse import urljoin
from enum import Enum, unique
from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@unique
class Scheme(str, Enum):
    HTTP = 'http'
    HTTPS = 'https'

@unique
class Port(int, Enum):
    HTTP = 80
    HTTPS = 443

class API:
    def __init__(self, server: str,
                       scheme: Union[str, Scheme] = Scheme.HTTPS,
                       port: Union[int, Port] = Port.HTTPS,
                       *args: Tuple[Any],
                       **kwargs: Dict[Any, Any]) -> None:
        self._server = server
        self._scheme = str(scheme.value)
        self._port = int(port.value)
        self._url = f'{self._scheme}://{self._server}:{self._port}'
        self._adapter = HTTPAdapter(max_retries=Retry(
            total=3
        ))
        self._session = Session()
        self._session.mount("https://", self._adapter)
        self._session.mount("http://", self._adapter)

    @property
    def url(self):
        return self._url

    @property
    def scheme(self):
        return self._scheme

    @property
    def server(self):
        return self._server

    @property
    def port(self):
        return self._port

    @property
    def session(self):
        return self._session

    def request(self, **kwargs) -> Response:
        if 'url' in kwargs:
            kwargs['url']  = urljoin(self._url, kwargs['url'])
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 5
        response = self._session.request(**kwargs)
        response.raise_for_status()
        return response
