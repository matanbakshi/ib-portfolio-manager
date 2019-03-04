from enum import Enum

from src.api.types import Exchanges


class AssetTypes(Enum):
    Stocks = 1
    Bonds = 2
    REIT = 3


class MarketTypes(Enum):
    General = 1
    Developed = 2
    Emerging = 3


class PositionMapping:
    def __init__(self, name: str, asset_type: AssetTypes, market_type: MarketTypes, exchange: Exchanges = None,
                 is_tradable=True):
        self.exchange = exchange
        self.name = name
        self.asset_type = asset_type
        self.market_type = market_type
        self.is_tradable = is_tradable
        self.updated_data = None


class Asset:
    def __init__(self, asset_type: AssetTypes, market_type: MarketTypes, allocation_percentage: float):
        self.asset_type = asset_type
        self.market_type = market_type
        self.allocation_percentage = allocation_percentage
