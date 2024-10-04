import sys
import os
import logging
import yaml

from typing import Optional, Any, List, Dict

from dotenv import load_dotenv, find_dotenv

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client.core import REGISTRY

from flask import Flask, current_app
from flask_smorest import Api, Blueprint

from webargs.flaskparser import FlaskParser

from marshmallow import EXCLUDE

from market.api import (
    MarketAPI,
    MarketAPIManager
)
from market.enum import (
    MarketRegion
)
from market.model import (
    IndexRequest,
    IndexResponse,
    RequestItem,
    ResponseItem,
    RequestItems,
    ResponseItems,
    RequestItemBidding,
    ResponseItemBidding,
    Item,
    ItemBidding
)

FlaskParser.DEFAULT_UNKNOWN_BY_LOCATION.update({
    'json_or_form': EXCLUDE,
    'json': EXCLUDE,
    'form': EXCLUDE
})

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

bdo_market_api_manager = MarketAPIManager()

web_app = Flask(__name__)
web_app.config.update({
    'API_TITLE': 'Black Desert Online',
    'API_VERSION': '0.0.1',
    'OPENAPI_VERSION': '3.0.2',
    'OPENAPI_URL_PREFIX': '/',
    'OPENAPI_JSON_PATH': 'api-spec.json',
    'OPENAPI_SWAGGER_UI_PATH': '/swagger',
    'OPENAPI_SWAGGER_UI_URL': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/',
})

web_app_metrics = PrometheusMetrics(web_app, registry=REGISTRY)
web_app_metrics.info(name='BDOMarket', description='Black Desert Online Market API', version='0.0.1', major=0, minor=0, patch=1)

web_app.bdo_market_api_manager: MarketAPIManager = bdo_market_api_manager
web_api = Api(web_app)
web_blp = Blueprint('market', __name__, url_prefix='/')

@web_blp.route('/')
@web_blp.route('/health')
@web_blp.route('/healthz')
@web_blp.arguments(IndexRequest.Schema(), location='query')
@web_blp.response(200, IndexResponse.Schema())
def index(*args, **kwargs) -> IndexResponse:
    return {}

@web_blp.route('/items')
@web_blp.arguments(RequestItems.Schema(), location='query')
@web_blp.response(200, ResponseItems.Schema(many=True))
def items(request: RequestItems, *args, **kwargs) -> List[ResponseItems]:
    return current_app.bdo_market_api_manager.api(request.region).GetWorldMarketList(mainCategory=request.category, subCategory=request.subcategory)

@web_blp.route('/item')
@web_blp.arguments(RequestItem.Schema(), location='query')
@web_blp.response(200, ResponseItem.Schema(many=True))
def item(request: RequestItem, *args, **kwargs) -> List[ResponseItem]:
    return current_app.bdo_market_api_manager.api(request.region).GetWorldMarketSubList(mainKey=request.id)

@web_blp.route('/orders')
@web_blp.arguments(RequestItemBidding.Schema(), location='query')
@web_blp.response(200, ResponseItemBidding.Schema(many=True))
def orders(request: RequestItemBidding, *args, **kwargs) -> List[ResponseItemBidding]:
    return current_app.bdo_market_api_manager.api(request.region).GetBiddingInfoList(mainKey=request.id, subKey=request.sid)

web_api.register_blueprint(web_blp)