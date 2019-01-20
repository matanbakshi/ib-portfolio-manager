from ibapi import wrapper
from ibapi.client import EClient
from ibapi.contract import Contract

from src.api.common.types import PositionData
from src.api.common.BrokerInterfaceEventsHandler import BrokerInterfaceEventsHandler


class IBWrapper(wrapper.EWrapper):
    def __init__(self, event_handler: BrokerInterfaceEventsHandler):
        super().__init__()
        self._event_handler = event_handler

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self._next_valid_order_id = orderId

    def position(self, account: str, contract: Contract, position: float,
                 avgCost: float):
        super().position(account, contract, position, avgCost)

        self._event_handler.get_holdings_callback(PositionData(contract.symbol, contract.currency, position))
        # print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:",
        #       contract.currency,
        #       "Position:", position, "Avg cost:", avgCost)

    def orderStatus(self, orderId: int, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining,
                            avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        print("OrderStatus. Id:", orderId, "Status:", status, "Filled:", filled,
              "Remaining:", remaining, "AvgFillPrice:", avgFillPrice,
              "PermId:", permId, "ParentId:", parentId, "LastFillPrice:",
              lastFillPrice, "ClientId:", clientId, "WhyHeld:",
              whyHeld, "MktCapPrice:", mktCapPrice)


class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class IBApp(IBWrapper, IBClient):
    def __init__(self, event_handler):
        IBWrapper.__init__(self, event_handler)
        IBClient.__init__(self, wrapper=self)