from abc import ABC, abstractmethod

from src.api.types import Exchanges, MarketData


class BaseMarketDataInterface(ABC):
    @abstractmethod
    def get_market_data(self, symbol: str, exchange: Exchanges) -> MarketData:
        pass
