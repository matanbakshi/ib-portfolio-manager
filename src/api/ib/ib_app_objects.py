from ibapi import wrapper
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order_state import OrderState

from src.api.common.types import *
from src.api.ib.IBEventsHandler import IBEventsHandler
from src.api.ib.ib_custom_entities import AccountSummary


class IBWrapper(wrapper.EWrapper):
    def __init__(self, event_handler: IBEventsHandler):
        super().__init__()
        self._event_handler = event_handler

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self._event_handler.next_valid_oid_callback(orderId)

    def position(self, account: str, contract: Contract, position: float,
                 avgCost: float):
        super().position(account, contract, position, avgCost)

        self._event_handler.new_position_callback(PositionData(contract.symbol, contract.currency, position, avgCost))

    def positionEnd(self):
        self._event_handler.position_end_callback()

    def openOrder(self, orderId: int, contract: Contract, order: Order,
                  orderState: OrderState):
        # TODO: Implement of necessary in the future
        pass

    def orderStatus(self, orderId: int, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining,
                            avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)

        self._event_handler.new_open_order_callback(OrderStatus(orderId, status, filled, remaining))

    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        self._event_handler.account_summary_callback(AccountSummary(reqId, account, tag, value, currency))

    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        self._event_handler.account_summary_end()


class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class IBApp(IBWrapper, IBClient):
    def __init__(self, event_handler: IBEventsHandler):
        IBWrapper.__init__(self, event_handler)
        IBClient.__init__(self, wrapper=self)
