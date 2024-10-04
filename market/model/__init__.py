from operator import truth
from typing import Optional, Any, List, Dict
from dataclasses import field, asdict
from marshmallow import Schema, pre_load, post_load, pre_dump, post_dump, fields
from marshmallow_dataclass import dataclass
from market.enum import MarketRegion

# API Models
@dataclass(repr=True, eq=True, order=True, frozen=True)
class IndexRequest(object):
    pass

@dataclass(repr=True, eq=True, order=True, frozen=True)
class IndexResponse(object):
    pass

class ResponseItemSchema(Schema):
    @pre_dump(pass_many=True)
    def pre_dump(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            item_id, enhancement_min, enhancement_max, base_price, current_stock, total_trades, price_min, price_max, price_last, last_sold, *_ = item.split('-')
            return {
                'id': item_id,
                'sid': enhancement_min,
                'enhancement_min': enhancement_min,
                'enhancement_max': enhancement_max,
                'base_price': base_price,
                'current_stock': current_stock,
                'total_trades': total_trades,
                'price_min': price_min,
                'price_max': price_max,
                'price_last': price_last,
                'last_sold': last_sold
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

    @pre_load(pass_many=True)
    def pre_load(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            item_id, enhancement_min, enhancement_max, base_price, current_stock, total_trades, price_min, price_max, price_last, last_sold, *_ = item.split('-')
            return {
                'id': item_id,
                'sid': enhancement_min,
                'enhancement_min': enhancement_min,
                'enhancement_max': enhancement_max,
                'base_price': base_price,
                'current_stock': current_stock,
                'total_trades': total_trades,
                'price_min': price_min,
                'price_max': price_max,
                'price_last': price_last,
                'last_sold': last_sold
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

@dataclass(repr=True, eq=True, order=True, frozen=True)
class RequestItem(object):
    id: int
    region: MarketRegion = MarketRegion.NA

@dataclass(repr=True, eq=True, order=True, frozen=True, base_schema=ResponseItemSchema)
class ResponseItem(object):
    id: int
    sid: int
    enhancement_min: int
    enhancement_max: int
    base_price: int
    current_stock: int
    total_trades: int
    price_min: int
    price_max: int
    price_last: int
    last_sold: int

class ResponseItemsSchema(Schema):
    @pre_dump(pass_many=True)
    def pre_dump(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            item_id, current_stock, total_trades, base_price, *_ = item.split('-')
            return {
                'id': item_id,
                'current_stock': current_stock,
                'total_trades': total_trades,
                'base_price': base_price
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))
    @pre_load(pass_many=True)
    def pre_load(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            item_id, current_stock, total_trades, base_price, *_ = item.split('-')
            return {
                'id': item_id,
                'current_stock': current_stock,
                'total_trades': total_trades,
                'base_price': base_price
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

@dataclass(repr=True, eq=True, order=True, frozen=True)
class RequestItems(object):
    category: int
    subcategory: int
    region: MarketRegion = MarketRegion.NA

@dataclass(repr=True, eq=True, order=True, frozen=True, base_schema=ResponseItemsSchema)
class ResponseItems(object):
    id: int
    current_stock: int
    total_trades: int
    base_price: int

class ResponseItemBiddingSchema(Schema):
    @pre_dump(pass_many=True)
    def pre_dump(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            price, sellers, buyers, *_ = item.split('-')
            return {
                'price': price,
                'sellers': sellers,
                'buyers': buyers
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))
    @pre_load(pass_many=True)
    def pre_load(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            price, sellers, buyers, *_ = item.split('-')
            return {
                'price': price,
                'sellers': sellers,
                'buyers': buyers
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

@dataclass(repr=True, eq=True, order=True, frozen=True)
class RequestItemBidding(object):
    id: int
    sid: int
    region: MarketRegion = MarketRegion.NA

@dataclass(repr=True, eq=True, order=True, frozen=True, base_schema=ResponseItemBiddingSchema)
class ResponseItemBidding(object):
    price: int
    sellers: int
    buyers: int

# Worker Models
class ItemSchema(Schema):
    @pre_load(pass_many=True)
    def pre_load(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            item_id, enhancement_min, enhancement_max, base_price, current_stock, total_trades, price_min, price_max, price_last, last_sold, *_ = item.split('-')
            return {
                'id': item_id,
                'sid': enhancement_min,
                'enhancement_min': enhancement_min,
                'enhancement_max': enhancement_max,
                'base_price': base_price,
                'current_stock': current_stock,
                'total_trades': total_trades,
                'price_min': price_min,
                'price_max': price_max,
                'price_last': price_last,
                'last_sold': last_sold
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

@dataclass(repr=True, eq=True, order=True, frozen=True, base_schema=ItemSchema)
class Item(object):
    id: int
    sid: int
    enhancement_min: int
    enhancement_max: int
    base_price: int
    current_stock: int
    total_trades: int
    price_min: int
    price_max: int
    price_last: int
    last_sold: int

class ItemsSchema(Schema):
    @pre_load(pass_many=True)
    def pre_load(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            item_id, current_stock, total_trades, base_price, *_ = item.split('-')
            return {
                'id': item_id,
                'current_stock': current_stock,
                'total_trades': total_trades,
                'base_price': base_price
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

@dataclass(repr=True, eq=True, order=True, frozen=True, base_schema=ItemsSchema)
class Items(object):
    id: int
    current_stock: int
    total_trades: int
    base_price: int

class ItemBiddingSchema(Schema):
    @pre_load(pass_many=True)
    def pre_load(self, item, many, *args, **kwargs):
        resultCode = item.get('resultCode')
        resultMsg = item.get('resultMsg')

        def parse_item(item):
            price, sellers, buyers, *_ = item.split('-')
            return {
                'price': price,
                'sellers': sellers,
                'buyers': buyers
            }

        return list(map(parse_item, filter(truth, resultMsg.split('|'))))

@dataclass(repr=True, eq=True, order=True, frozen=True, base_schema=ItemBiddingSchema)
class ItemBidding(object):
    price: int
    sellers: int
    buyers: int