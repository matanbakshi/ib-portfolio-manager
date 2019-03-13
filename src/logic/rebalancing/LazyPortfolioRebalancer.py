from typing import List

from src.logic.rebalancing.entities.RebalanceAssetData import RebalanceAssetData


class LazyPortfolioRebalancer:
    def rebalance_by_contribution(self, assets: List[RebalanceAssetData], contribution: float) \
            -> List[RebalanceAssetData]:
        current_value = sum(asset.value for asset in assets)
        total_value = current_value + contribution

        assets = self._calculate_deviation_for_each_asset(assets, current_value, total_value)

        sorted_assets = sorted(assets, key=lambda a: a.deviation)
        if contribution < 0.0:
            sorted_assets = list(reversed(sorted_assets))

        deviation, index_to_stop = self._calculate_overall_deviation(sorted_assets, contribution)
        finalized_assets = self._calculate_delta_to_each_asset(sorted_assets, deviation, index_to_stop)

        return finalized_assets

    def _calculate_delta_to_each_asset(self, sorted_assets, overall_deviation, index_to_stop):
        for i, asset in enumerate(sorted_assets):
            if i >= index_to_stop:
                break

            asset.delta = asset.target_value * (overall_deviation - asset.deviation)
        return sorted_assets

    def _calculate_overall_deviation(self, sorted_assets, contribution):
        contribution_left = contribution
        sum_allocation = 0.0
        last_known_index = None
        current_deviation = 0
        for i, asset in enumerate(sorted_assets):
            if abs(contribution_left) <= 0.0:
                return sorted_assets
            last_known_index = i
            current_deviation = asset.deviation
            sum_allocation += asset.target_value

            next_least_deviation = 0 if i >= len(sorted_assets) - 1 else sorted_assets[i + 1].deviation
            delta = sum_allocation * (next_least_deviation - current_deviation)

            if abs(delta) <= abs(contribution_left):
                contribution_left -= delta
                current_deviation = next_least_deviation
            else:
                current_deviation = current_deviation + (contribution_left / sum_allocation)
                break

        if last_known_index is not None:
            return current_deviation, last_known_index + 1

        return current_deviation, 0

    def _calculate_deviation_for_each_asset(self, assets, current_value, total_value):
        for asset in assets:
            target_value = total_value * asset.target_percent
            deviation = (asset.value / target_value) - 1.0

            asset.actual_allocation = asset.value / current_value
            asset.target_value = target_value
            asset.deviation = deviation

        return assets
