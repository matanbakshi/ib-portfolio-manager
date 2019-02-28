from abc import ABC, abstractmethod
from typing import List

from src.api.types import *


class BaseBrokerInterface(ABC):
    @abstractmethod
    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        pass

    @abstractmethod
    def request_all_holdings(self) -> List[PositionData]:
        pass

    @abstractmethod
    def request_cash_balance(self) -> float:
        pass

    # @abstractmethod
    # def get_exchange_for_symbol(self) -> Exchanges:
    #     pass

    # @abstractmethod TODO: Implement if necessary in the future
    # def request_all_pending_orders(self):
    #     pass
