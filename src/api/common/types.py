from enum import Enum


class OrderActions(Enum):
    SELL_ORDER = "SELL"
    BUY_ORDER = "BUY"


class OrderTypes(Enum):
    MARKET = "MKT",
    LIMIT = "LMT"


class Exchanges(Enum):
    # In the IB API side, NASDAQ is always defined as ISLAND in the exchange field (TODO: take this to somewhere else)
    NASDAQ_EXCHANGE = "ISLAND"


class SecTypes(Enum):
    STOCK = "STK"


class Currencies(Enum):
    USD = "USD"


class PositionData:
    def __init__(self, symbol, currency, pos):
        self.pos = pos
        self.currency = currency
        self.symbol = symbol

    def __repr__(self):
        return f"{self.symbol} - {self.pos} {self.currency}"
