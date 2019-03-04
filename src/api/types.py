from enum import Enum

from src.common.ClassificationTypes import AssetTypes


class OrderActions(Enum):
    SELL_ORDER = "SELL"
    BUY_ORDER = "BUY"


class OrderTypes(Enum):
    MARKET = "MKT",
    LIMIT = "LMT"


class Exchanges(Enum):
    # In the IB API side, NASDAQ is always defined as ISLAND in the exchange field (TODO: take this to somewhere else)
    NASDAQ = "NASDAQ",
    ARCA = "ARCA",
    LSE = "LSE",
    NYSE = "NYSE"


class SecTypes(Enum):
    STOCK = "STK"


class Currencies(Enum):
    USD = "USD"


class MarketData:
    def __init__(self, ask_price: float, ask_size: int, bid_price: float, bid_size: int):
        self.ask_price = ask_price
        self.ask_size = ask_size
        self.bid_price = bid_price
        self.bid_size = bid_size


class PositionData:
    def __init__(self, symbol: str, currency: Currencies, quantity: float, market_price: float, exchange: Exchanges,
                 sec_type: SecTypes):
        self.sec_type = sec_type
        self.exchange = exchange
        self.market_price = market_price
        self.quantity = quantity
        self.currency = currency
        self.symbol = symbol

    def __repr__(self):
        return f"{self.symbol} - {self.quantity} {self.currency}"

    @property
    def market_value(self):
        return self.market_price * self.quantity


class OrderStatus:
    def __init__(self, order_id: int, status: str, filled: float, remaining: float):
        self.order_id = order_id
        self.status = status
        self.filled = filled
        self.remaining = remaining

    def __repr__(self):
        return f"OID: {self.order_id} - Status: {self.status} Filled: {self.filled} Remaining: {self.remaining}"
