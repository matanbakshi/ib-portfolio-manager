from typing import List, Dict

from src.api.BaseBrokerInterface import BaseBrokerInterface, PositionData, OrderTypes, OrderActions
from src.api.BaseMarketDataInterface import BaseMarketDataInterface
from src.logic.config import *
from src.logic.rebalancing.LazyPortfolioRebalancer import LazyPortfolioRebalancer
from src.logic.rebalancing.entities.RebalanceAssetData import RebalanceAssetData
from src.utils.market_open import is_market_open
from src.logic.TransactionManager import TransactionManager

from src.logger import logger


class PassiveInvestmentEngine:
    def __init__(self, broker_interface: BaseBrokerInterface, market_data_interface: BaseMarketDataInterface):
        self._market_data_interface = market_data_interface
        self._broker_interface = broker_interface
        self._rebalancer = LazyPortfolioRebalancer()
        self._current_positions = []
        self._check_open_markets = True
        self._latest_market_data = []
        self._transaction_mgr = TransactionManager()
        # Group the configured data by asset type and market type and symbol for convenience
        self._ordered_mapping = self._group_configured_assets()

    @staticmethod
    def _group_configured_assets() -> Dict[MarketTypes, Dict[AssetTypes, Dict[str, PositionMapping]]]:
        return {
            outer_v.market_type: {inner_v.asset_type: {pos.name: pos for pos in POSITIONS_MAPPINGS if
                                                       pos.market_type == outer_v.market_type and
                                                       pos.asset_type == inner_v.asset_type}
                                  for inner_v in POSITIONS_MAPPINGS}
            for outer_v in POSITIONS_MAPPINGS
        }

    def rebalance_with_available_cash(self):
        # if not self._is_all_markets_open():
        #     raise SystemError(
        #         "Not all of the markets are open currently. "
        #         "Try again in better time when both London and NYE are trading")

        cash_balance = self._broker_interface.request_cash_balance()

        if cash_balance <= 0:
            raise SystemError("Insufficient funds to starts a rebalancing and ordering process.")

        logger.info(f"Cash balance: {cash_balance}")

        cash_balance = 5000.0  # TESTING
        logger.warn(f"Using constant: {cash_balance} for testing")

        self._current_positions = self._broker_interface.request_all_holdings()

        logger.info(f"Current positions: {self._current_positions}")

        if not self._current_positions:
            raise SystemError("No tradeable holdings was received from the broker")

        assets_before_balance = self._create_rebalance_entites_and_enrich_data(self._current_positions)

        logger.info(f"Assets before rebalance: {assets_before_balance}")

        self._fetch_latest_market_data()

        rebalanced_assets = self._rebalancer.rebalance_by_contribution(assets_before_balance,
                                                                       cash_balance - CASH_MARGIN)

        logger.info(f"Assets after rebalance: {rebalanced_assets}")

        self._perform_assets_gap_ordering(rebalanced_assets)

    def _perform_assets_gap_ordering(self, reb_assets: List[RebalanceAssetData]):
        for reb_asset in reb_assets:
            if reb_asset.delta and reb_asset.delta > 0:
                self._evaluate_and_order_asset(reb_asset.asset, reb_asset.delta)

        self._transaction_mgr.execute_all()

    def _evaluate_and_order_asset(self, asset: Asset, value_to_order: float):
        actual_positions = self._ordered_mapping[asset.market_type][asset.asset_type]

        # There might be multiple positions for the same asset. Find the least valued asset.
        least_valued_pos = min(actual_positions.values(), key=lambda x: x.updated_data.market_value)

        pos_md = self._latest_market_data[least_valued_pos.updated_data.contract_id]

        # Quantity of stocks must be an integer. This might change for other markets.
        ask_price = pos_md.ask_price

        if ask_price is None:
            raise SystemError(f"Ask price is not available for: {least_valued_pos.name}")

        quantity = int(value_to_order / ask_price)

        logger.info(f"Placing order: BUY >> {least_valued_pos.name}, "
                    f"Quantity: {quantity}, "
                    f"Ask Price: {pos_md.ask_price}")

        self._transaction_mgr.queue_for_execution(
            self._broker_interface.place_single_order,

            least_valued_pos.updated_data.contract_id,
            least_valued_pos.name,
            quantity, OrderTypes.LIMIT, OrderActions.BUY_ORDER,
            least_valued_pos.updated_data.sec_type,
            least_valued_pos.updated_data.currency,
            limit_price=ask_price)

    @staticmethod
    def _is_all_markets_open() -> bool:
        for pos_map in POSITIONS_MAPPINGS:
            if not is_market_open(pos_map.exchange.value):
                return False
        return True

    def _create_rebalance_entites_and_enrich_data(self, updated_positions: List[PositionData]) \
            -> List[RebalanceAssetData]:

        rebalance_assets = {}

        for asset in ASSET_ALLOCATIONS:
            rebalance_assets[f"{asset.asset_type}.{asset.market_type}"] = RebalanceAssetData(asset, 0.0,
                                                                                             asset.allocation_percentage)

        positions_dict = {x.symbol: x for x in updated_positions}

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
                    self._ordered_mapping[mapping.market_type][mapping.asset_type][mapping.name].updated_data = position
                else:
                    raise EnvironmentError(
                        f"{mapping.name} exists in the configuration but a position data was not received")

        return list(rebalance_assets.values())

    def _fetch_latest_market_data(self):
        con_ids = [pos.contract_id for pos in self._current_positions]
        if con_ids:
            self._latest_market_data = self._market_data_interface.get_market_data(con_ids)
