import os
import json
from functools import wraps
from typing import Any, Dict, List, Tuple, Union, Optional
from datetime import timedelta
from market.common.api import API
from market.enum import MarketRegion
from market.util.huffman import HuffmanData
from redis import Redis, RedisCluster
from requests import Response

def cache_decorator(func):
    @wraps(func)
    def inner_func(self: "MarketAPI", *args, **kwargs):
        cache_name = f"{self.region.name}_{func.__name__}_{'_'.join(map(str, args))}_{'_'.join(map(str, kwargs.values()))}"
        cached_fetch = self._cache_get(cache_name)
        if cached_fetch:
            return cached_fetch
        fresh_fetch = func(self, *args, **kwargs)
        self._cache_set(cache_name, fresh_fetch)
        return fresh_fetch
    return inner_func

class MarketAPI(API):
    def __init__(self, region: MarketRegion, cache: Union[Redis, RedisCluster] = None, *args: Tuple[Any], **kwargs: Dict[Any, Any]) -> None:
        super().__init__(server=region.value, *args, **kwargs)
        self._region = region
        self.session.headers.update({
            'User-Agent': 'BlackDesert'
        })
        self.session.hooks.update({
            'response': [
                self._response_hook
            ]
        })
        self._cache = cache
        if cache is None:
            redis_url = os.getenv('REDIS_URL')
            if redis_url is not None:
                self._cache = Redis.from_url(redis_url)
            redis_cluster_url = os.getenv('REDIS_CLUSTER_URL')
            if redis_cluster_url is not None:
                self._cache = RedisCluster.from_url(redis_cluster_url)

    @property
    def region(self) -> MarketRegion:
        return self._region

    def _cache_get(self, name: str) -> Optional[Dict[Any, Any]]:
        if self._cache is not None:
            cached_response = self._cache.get(name=name)
            if cached_response:
                return json.loads(cached_response)
        return None

    def _cache_set(self, name: str, value: str) -> None:
        if self._cache is not None:
            self._cache.set(
                name=name,
                value=json.dumps(value),
                ex=timedelta(minutes=5)
            )

    @cache_decorator
    def GetBiddingInfoList(self, mainKey: int, subKey: int, keyType: int = 0) -> Dict[Any, Any]:
        response = self.request(
            url='Trademarket/GetBiddingInfoList',
            method='POST',
            json={
                'keyType': keyType,
                'mainKey': mainKey,
                'subKey': subKey
            }
        )
        return response.json()

    @cache_decorator
    def GetWorldMarketList(self, mainCategory: int, subCategory: int, keyType: int = 0) -> Dict[Any, Any]:
        response = self.request(
            url='Trademarket/GetWorldMarketList',
            method='POST',
            json={
                'keyType': keyType,
                'mainCategory': mainCategory,
                'subCategory': subCategory
            }
        )
        return response.json()

    @cache_decorator
    def GetWorldMarketSubList(self, mainKey: int, keyType: int = 0) -> Dict[Any, Any]:
        response = self.request(
            url='Trademarket/GetWorldMarketSubList',
            method='POST',
            json={
                'keyType': keyType,
                'mainKey': mainKey
            }
        )
        return response.json()

    @cache_decorator
    def GetWorldMarketSearchList(self, searchResult: str) -> Dict[Any, Any]:
        response = self.request(
            url='/Trademarket/GetWorldMarketSearchList',
            method='POST',
            json={
                'searchResult': searchResult
            }
        )
        return response.json()

    def _response_hook(self, response: Response, *args, **kwargs) -> Response:
        content_type = response.headers['Content-Type']

        if 'application/octet-stream' in content_type.lower():
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response._content = json.dumps({'resultCode': 0, 'resultMsg': HuffmanData(raw_data=response.content).data}).encode()

        return response

class MarketAPIManager(object):
    def __init__(self, cache: Redis = None) -> None:
        self._apis = {
            region: MarketAPI(region, cache)
            for region
            in MarketRegion
        }

    @property
    def apis(self) -> List[MarketAPI]:
        return self._apis

    def api(self, region: MarketRegion) -> MarketAPI:
        return self._apis[region]
