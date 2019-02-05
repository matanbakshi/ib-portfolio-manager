from src.common.ClassificationTypes import *

POSITIONS_MAPPINGS = [
    # IB Assets
    PositionMapping("VEA", AssetTypes.Stocks, MarketTypes.Developed),
    PositionMapping("CSSPX", AssetTypes.Stocks, MarketTypes.Developed),
    PositionMapping("AGGU", AssetTypes.Bonds, MarketTypes.General),
    PositionMapping("VNQ", AssetTypes.REIT, MarketTypes.Developed),
    PositionMapping("VNQI", AssetTypes.REIT, MarketTypes.Developed),

    # Non-IB Assets
    PositionMapping("EIMI_IRA", AssetTypes.Stocks, MarketTypes.Emerging, is_tradable=False),
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

# Needs to be updated manually.
NON_TRADABLE_ASSETS_VALUE = {
    "InvProvident_Stocks": 40369.0,
    "InvProvident_Bonds": 40369.0,
    "Pension": 42372.0,

    # TODO: A more accurate value can be brought if I multiply the EIMI value with number of positions
    "EIMI_IRA": 17233.76
}
