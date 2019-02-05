from src.common.ClassificationTypes import *

POSITIONS_MAPPINGS = [
    # IB Assets
    PositionMapping("VEA", AssetTypes.Stocks, MarketTypes.Developed),
    PositionMapping("CSSPX", AssetTypes.Stocks, MarketTypes.Developed),
    PositionMapping("AGGU", AssetTypes.Bonds, MarketTypes.General),
    PositionMapping("VNQ", AssetTypes.REIT, MarketTypes.Developed),
    PositionMapping("VNQI", AssetTypes.REIT, MarketTypes.Developed),

    # Non-IB Assets
    PositionMapping("InvProvident_Stocks", AssetTypes.Stocks, MarketTypes.General, is_tradable=False),
    PositionMapping("InvProvident_Bonds", AssetTypes.Bonds, MarketTypes.General, is_tradable=False),
    PositionMapping("Pension_Stocks", AssetTypes.Stocks, MarketTypes.General, is_tradable=False),
]

ASSET_ALLOCATIONS = [
    Asset(AssetTypes.Stocks, MarketTypes.Developed, 30.0),
    Asset(AssetTypes.Stocks, MarketTypes.Emerging, 30.0),
    Asset(AssetTypes.Bonds, MarketTypes.General, 30.0),
    Asset(AssetTypes.REIT, MarketTypes.General, 10.0),
]
