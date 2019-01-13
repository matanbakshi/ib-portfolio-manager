from threading import Thread

from ibapi.contract import Contract

from src.api.BaseBrokerInterface import BaseBrokerInterface
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper


class IBWrapper(wrapper.EWrapper):
    def position(self, account: str, contract: Contract, position: float,
                 avgCost: float):
        super().position(account, contract, position, avgCost)

        print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:",
              contract.currency,
              "Position:", position, "Avg cost:", avgCost)

    def positionEnd(self):
        super().positionEnd()
        print("PositionEnd")


class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class IBApp(IBWrapper, IBClient):
    def __init__(self):
        IBWrapper.__init__(self)
        IBClient.__init__(self, wrapper=self)


class IBBrokerInterface(BaseBrokerInterface):
    def __init__(self, hostname="127.0.0.1", port=7497):
        self._ibApp = IBApp()
        self._ibApp.connect(hostname, port, 0)

        thread = Thread(target=self._ibApp.run)
        self.start = thread.start()

        setattr(self._ibApp, "_thread", thread)

    def buy_holdings(self, symbol, positions):
        pass

    def sell_holdings(self, symbol, positions):
        pass

    def get_all_holdings(self):
        self._ibApp.reqPositions()

    def get_holding_by_symbol(self, symbol):
        pass


if __name__ == "__main__":
    ib = IBBrokerInterface()

    ib.get_all_holdings()
