from src.common.ClassificationTypes import Asset


class RebalanceAssetData:
    def __init__(self, asset_object: Asset, value: float, actual_allocation=None, target_value=None, deviation=None,
                 delta=None):
        # self.is_tradable = is_tradable
        self.delta = delta
        self.deviation = deviation
        self.target_value = target_value
        self.actual_allocation = actual_allocation
        self.target_percent = asset_object.allocation_percentage
        self.value = value
        self.asset = asset_object

    def __repr__(self):
        return "{} {}: Dev: {} Delta: {}".format(str(self.asset.asset_type), str(self.asset.market_type),
                                                 str(self.deviation), str(self.delta))
