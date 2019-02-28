from src.api.BaseMarketDataInterface import BaseMarketDataInterface
from src.api.types import Exchanges, MarketData


class IEXMarketDataInterface(BaseMarketDataInterface):
    def get_market_data(self, symbol: str, exchange: Exchanges) -> MarketData:
        pass
