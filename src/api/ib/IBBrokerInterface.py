import asyncio
from os import getcwd
from threading import Thread
from ibapi.contract import Contract

from src.api.BaseBrokerInterface import BaseBrokerInterface
from ibapi import wrapper
from ibapi.client import EClient

from src.api.ib.orders_factory import *
from src.api.ib.contracts_factory import *
from src.api.ib.string_consts import *


class PositionData:
    def __init__(self, symbol, currency, pos):
        self.pos = pos
        self.currency = currency
        self.symbol = symbol

    def __repr__(self):
        return f"{self.symbol} - {self.pos} {self.currency}"


class BrokerInterfaceEventsHandler:
    def __init__(self):
        self.get_holdings_callback = lambda pos: None
        self.next_valid_oid = lambda oid: None


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


class IBBrokerInterface(BaseBrokerInterface):
    def __init__(self, event_handler, last_oid, hostname="127.0.0.1", port=7497, ):
        self.last_oid = last_oid
        self._ibApp = IBApp(event_handler)
        self._ibApp.connect(hostname, port, 0)

        self._event_loop = asyncio.get_event_loop()

        thread = Thread(target=self._ibApp.run)
        self.start = thread.start()

        setattr(self._ibApp, "_thread", thread)

    def buy_holdings(self, symbol, positions):
        # TODO: Currently only trading in US NASDAQ, add support for different exchanges.
        # TODO: Currentry support MKT orders, add support for different orders.
        # TODO: support multiple orders, grouping and enbaling "One-Cancels All"

        mkt_order = create_MKT_order(OrderTypes.BUY_ORDER, positions)
        us_contract = create_US_contract(symbol, Currencies.USD, )

        # TODO: understand how to use this order ID better.
        self._ibApp.placeOrder(self.last_oid, us_contract, mkt_order)
        self.last_oid += 1

    def sell_holdings(self, symbol, positions):
        pass

    def get_all_holdings(self):
        self._ibApp.reqPositions()

    def get_holding_by_symbol(self, symbol):
        pass

    def getAllOrders(self):
        self._ibApp.reqOpenOrders()
        pass


if __name__ == "__main__":
    with open("./oid", "r") as oid_file:
        _last_oid = int(oid_file.read())

    handler = BrokerInterfaceEventsHandler()
    handler.get_holdings_callback = lambda x: print(x)

    ib = IBBrokerInterface(handler, _last_oid)
    # ib.buy_holdings("IBKR", "1")
    #
    # with open("./oid", "w") as oid_file:
    #     oid_file.write(str(ib.last_oid))
    ib.getAllOrders()
    input()
    # ib.get_all_holdings()
