from src.api.BaseBrokerInterface import BaseBrokerInterface
from src.config.classifications import *


class PassiveInvestmentEngine:
    def __init__(self, broker_interface: BaseBrokerInterface):
        self._broker_interface = broker_interface

    def run_logic(self):
        # Check available cash

        # Get current positions

        # Group to different assets

        pass

    def _get_available_cash(self):
        self._broker_interface.request_cash_balance()
