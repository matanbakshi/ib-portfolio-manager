from abc import ABC, abstractmethod
from typing import List

from src.api.types import Exchanges, MarketData


class BaseMarketDataInterface(ABC):
    @abstractmethod
    def get_market_data(self, contract_ids: List[int]) -> List[MarketData]:
        pass
