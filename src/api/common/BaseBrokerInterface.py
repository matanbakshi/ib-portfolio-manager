from abc import ABC, abstractmethod

from src.api.common.types import *


class BaseBrokerInterface(ABC):
    @abstractmethod
    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        pass

    @abstractmethod
    def get_all_holdings(self):
        pass

    @abstractmethod
    def get_holding_by_symbol(self, symbol: str, exchange: Exchanges):
        pass

    @abstractmethod
    def get_all_pending_orders(self):
        pass
