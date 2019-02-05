from typing import Dict

from src.api.BaseBrokerInterface import BaseBrokerInterface


class PassiveInvestmentLogic:
    def __init__(self, broker_interface: BaseBrokerInterface, positions_classification_config: Dict[str, str]):
        self.positions_classification_config = positions_classification_config
        self.broker_interface = broker_interface

    def perform_rebalance_logic(self):
        # Check available cash

        # Get current positions

        # Group to different assets

        pass
