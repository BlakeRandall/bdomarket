from werkzeug.routing import BaseConverter
from market.enum import MarketRegion

class RegionConverter(BaseConverter):

    def to_python(self, value):
        return MarketRegion[value]

    def to_url(self, obj):
        return obj.name