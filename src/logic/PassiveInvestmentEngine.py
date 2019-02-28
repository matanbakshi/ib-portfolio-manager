from typing import List

from src.api.BaseBrokerInterface import BaseBrokerInterface, PositionData
from src.api.BaseMarketDataInterface import BaseMarketDataInterface
from src.logic.config import *
from src.logic.rebalancing.LazyPortfolioRebalancer import LazyPortfolioRebalancer
from src.logic.rebalancing.entities.RebalanceAssetData import RebalanceAssetData
from src.utils.market_open import is_market_open


class PassiveInvestmentEngine:
    def __init__(self, broker_interface: BaseBrokerInterface, market_data_interface: BaseMarketDataInterface):
        self._market_data_interface = market_data_interface
        self._broker_interface = broker_interface
        self._rebalancer = LazyPortfolioRebalancer()
        self._current_positions = []
        self._check_open_markets = True

        # Group the configured data by asset type and market type for convenience
        self._ordered_mapping = {outer_v.market_type: {inner_v.asset_type: inner_v for inner_v in POSITIONS_MAPPINGS if
                                                       inner_v.market_type == outer_v.market_type}
                                 for outer_v in POSITIONS_MAPPINGS}

    def rebalance_with_available_cash(self):
        if not self._is_all_markets_open():
            raise SystemError(
                "Not all of the markets are open currently. "
                "Try again in better time when both London and NYE are trading")

        cash_balance = self._broker_interface.request_cash_balance()

        if cash_balance <= 0:
            raise SystemError("Insufficient funds to starts a rebalancing and ordering process.")

        self._current_positions = self._broker_interface.request_all_holdings()

        if not self._current_positions:
            raise SystemError("No tradeable holdings was received from the broker")

        assets_before_balance = self._create_rebalance_entites_from_holdings(self._current_positions)

        rebalanced_assets = self._rebalancer.rebalance_by_contribution(assets_before_balance,
                                                                       cash_balance - CASH_MARGIN)

        self._perform_assets_gap_ordering(rebalanced_assets)

    def _perform_assets_gap_ordering(self, reb_assets: List[RebalanceAssetData]):
        for reb_asset in reb_assets:
            if reb_asset.delta > 0:
                self._evaluate_and_order_asset(reb_asset.asset, reb_asset.delta)

    def _evaluate_and_order_asset(self, asset: Asset, value_to_order: float):
        actual_positions = self._ordered_mapping[asset.market_type][asset.asset_type]

        # There might be multiple positions for the same asset. Find the least valued asset
        min_pos_value = min(pos.market_value for pos in actual_positions)
        least_valued_pos = next(pos for pos in actual_positions if pos == min_pos_value)

        pos_md = self._market_data_interface.get_market_data(least_valued_pos.symbol, least_valued_pos.exchange)

        # self._broker_interface.place_single_order(least_valued_pos.)

    def _is_all_markets_open(self):
        for pos_map in POSITIONS_MAPPINGS:
            if not is_market_open(pos_map.exchange.value):
                return False
        return True

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
                    raise EnvironmentError(
                        f"Configuration error: {mapping.asset_type}.{mapping.market_type} is not tradable but wasn't "
                        f"found on non tradable assets configuration")

            else:
                position = positions_dict.get(mapping.name)

                if position is not None:
                    reb_asset.value += position.market_value
                else:
                    raise EnvironmentError(
                        f"{mapping.name} exists in the configuration but a position data was not received")

        return list(rebalance_assets.values())
