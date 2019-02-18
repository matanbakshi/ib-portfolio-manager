from typing import List

from src.api.BaseBrokerInterface import BaseBrokerInterface, PositionData
from src.config.classifications import *
from src.logic.rebalancing.entities.RebalanceAssetData import RebalanceAssetData


class PassiveInvestmentEngine:
    def __init__(self, broker_interface: BaseBrokerInterface):
        self._broker_interface = broker_interface

    def rebalance_with_available_cash(self):
        cash_balance = self._broker_interface.request_cash_balance()

        tradable_holdings = self._broker_interface.request_all_holdings()

        # Group to different assets

        pass

    def _create_rebalance_entites_from_holdings(self, holdings: List[PositionData]) -> List[RebalanceAssetData]:
        rebalance_assets = {}

        for asset in ASSET_ALLOCATIONS:
            rebalance_assets[f"{asset.asset_type}.{asset.market_type}"] = RebalanceAssetData(asset, 0.0,
                                                                                             asset.allocation_percentage)

        positions_dict = {x.symbol: x for x in holdings}

        for mapping in POSITIONS_MAPPINGS:
            reb_asset = rebalance_assets.get(f"{mapping.asset_type}.{mapping.market_type}")

            if reb_asset is None:
                raise EnvironmentError(
                    f"Configuration error: {mapping.asset_type}.{mapping.market_type} was not found in "
                    f"the assets allocations")

            if not mapping.is_tradable:
                value = NON_TRADABLE_ASSETS_VALUE.get(mapping.name)
                if value is not None:
                    reb_asset.value += value
            else:
                position = positions_dict.get(mapping.name)

                if position is not None:
                    reb_asset.value += position.avg_cost * position.pos
                else:
                    raise EnvironmentError(
                        f"{mapping.name} exists in the configuration but a position data was not received")

        return list(rebalance_assets.values())
