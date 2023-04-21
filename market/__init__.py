import sys
import os
import logging
import yaml

from typing import Optional, Any, List, Dict

from dotenv import load_dotenv, find_dotenv

from prometheus_flask_exporter import PrometheusMetrics

from prometheus_client.core import REGISTRY, GaugeMetricFamily, Gauge

from flask import Flask, current_app, Request, Response
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
    Config,
    ConfigMarketItem,
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

config: Config = Config()
config_schema = Config.Schema(partial=True, unknown=EXCLUDE)
cfg_dir = os.getenv('CONFIG_DIR', os.path.abspath(__name__))
cfg_name = os.getenv('CONFIG_NAME', 'default_config.yml')
with open(os.path.join(cfg_dir, cfg_name)) as _cfg:
    _cfg_yaml = yaml.safe_load(_cfg)
    config: Config = config_schema.load(_cfg_yaml)

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

market_item_schema = Item.Schema(many=True)
market_item_bidding_schema = ItemBidding.Schema(many=True)

def worker_app():
    for market_region in MarketRegion:
        market_region_api: MarketAPI = bdo_market_api_manager.api(market_region)

        for market_item in config.items:
            market_items_raw = market_region_api.GetWorldMarketSubList(market_item.id)
            market_items_data: List[Item] = market_item_schema.load(market_items_raw)

            market_items_bidding_raw = market_region_api.GetBiddingInfoList(market_item.id, market_item.sid)
            market_items_bidding_data: List[ItemBidding] = market_item_bidding_schema.load(market_items_bidding_raw)

class MarketItemCollector(object):
    def collect(self):
        metric_market_item_total_trades = GaugeMetricFamily(
            'market_item_total_trades',
            'Market Item Total Trades',
            labels=[
                'region',
                'name',
                'id',
                'sid'
            ]
        )
        metric_market_item_current_stock = GaugeMetricFamily(
            'market_item_current_stock',
            'Market Item Current Stock',
            labels=[
                'region',
                'name',
                'id',
                'sid'
            ]
        )
        metric_market_item_base_price = GaugeMetricFamily(
            'market_item_base_price',
            'Market Item Base Price',
            labels=[
                'region',
                'name',
                'id',
                'sid'
            ]
        )

        for market_region in MarketRegion:
            market_region_api: MarketAPI = bdo_market_api_manager.api(market_region)

            for market_item in config.items:
                market_items_raw = market_region_api.GetWorldMarketSubList(market_item.id)
                market_items_data: List[Item] = market_item_schema.load(market_items_raw)

                for market_item_data in market_items_data:
                    metric_market_item_total_trades.add_metric(
                        [
                            market_region.name,
                            market_item.name,
                            str(market_item.id),
                            str(market_item.sid),
                        ],
                        market_item_data.total_trades
                    )
                    metric_market_item_current_stock.add_metric(
                        [
                            market_region.name,
                            market_item.name,
                            str(market_item.id),
                            str(market_item.sid),
                        ],
                        market_item_data.current_stock
                    )
                    metric_market_item_base_price.add_metric(
                        [
                            market_region.name,
                            market_item.name,
                            str(market_item.id),
                            str(market_item.sid),
                        ],
                        market_item_data.base_price
                    )

        yield metric_market_item_total_trades
        yield metric_market_item_current_stock
        yield metric_market_item_base_price

class MarketItemBiddingCollector(object):
    def collect(self):
        metric_market_item_buyers = GaugeMetricFamily(
            'market_item_bidding_buyers',
            'Market Item Bidding Buyers',
            labels=[
                'region',
                'name',
                'id',
                'sid',
                'price'
            ]
        )
        metric_market_item_sellers = GaugeMetricFamily(
            'market_item_bidding_sellers',
            'Market Item Bidding Sellers',
            labels=[
                'region',
                'name',
                'id',
                'sid',
                'price'
            ]
        )

        for market_region in MarketRegion:
            market_region_api: MarketAPI = bdo_market_api_manager.api(market_region)

            for market_item in config.items:
                market_items_raw = market_region_api.GetBiddingInfoList(market_item.id, market_item.sid)
                market_items_data: List[ItemBidding] = market_item_bidding_schema.load(market_items_raw)

                for market_item_data in market_items_data:
                    metric_market_item_buyers.add_metric(
                        [
                            market_region.name,
                            market_item.name,
                            str(market_item.id),
                            str(market_item.sid),
                            str(market_item_data.price)
                        ],
                        market_item_data.buyers
                    )
                    metric_market_item_sellers.add_metric(
                        [
                            market_region.name,
                            market_item.name,
                            str(market_item.id),
                            str(market_item.sid),
                            str(market_item_data.price)
                        ],
                        market_item_data.sellers
                    )

        yield metric_market_item_buyers
        yield metric_market_item_sellers

REGISTRY.register(MarketItemCollector())
REGISTRY.register(MarketItemBiddingCollector())