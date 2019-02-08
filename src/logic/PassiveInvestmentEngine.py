from src.api.BaseBrokerInterface import BaseBrokerInterface
from src.config.classifications import *


class PassiveInvestmentEngine:
    def __init__(self, broker_interface: BaseBrokerInterface):
        self._broker_interface = broker_interface

    def rebalance_with_available_cash(self):
        cash_balance = self._broker_interface.request_cash_balance()

        tradable_holdings = self._broker_interface.request_all_holdings()

        # Group to different assets

        pass
