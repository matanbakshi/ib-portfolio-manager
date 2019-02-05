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
    def __init__(self, symbol, currency, pos, avg_cost):
        self.avg_cost = avg_cost
        self.pos = pos
        self.currency = currency
        self.symbol = symbol

    def __repr__(self):
        return f"{self.symbol} - {self.pos} {self.currency}"


class OrderStatus:
    def __init__(self, order_id: int, status: str, filled: float, remaining: float):
        self.order_id = order_id
        self.status = status
        self.filled = filled
        self.remaining = remaining

    def __repr__(self):
        return f"OID: {self.order_id} - Status: {self.status} Filled: {self.filled} Remaining: {self.remaining}"


