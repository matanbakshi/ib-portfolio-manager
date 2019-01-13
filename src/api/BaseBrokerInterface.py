from abc import ABC, abstractmethod


class BaseBrokerInterface(ABC):
    @abstractmethod
    def buy_holdings(self, symbol, positions):
        pass

    @abstractmethod
    def sell_holdings(self, symbol, positions):
        pass

    @abstractmethod
    def get_all_holdings(self):
        pass

    @abstractmethod
    def get_holding_by_symbol(self, symbol):
        pass
