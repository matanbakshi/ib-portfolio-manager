from abc import ABC, abstractmethod

from src.api.common.types import *


class BaseBrokerInterface(ABC):
    @abstractmethod
    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        pass

    @abstractmethod
    def request_all_holdings(self):
        pass

    # @abstractmethod TODO: Implement if necessary in the future
    # def request_all_pending_orders(self):
    #     pass
