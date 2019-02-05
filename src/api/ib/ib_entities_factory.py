from ibapi.contract import Contract
from ibapi.order import Order


def create_contract(symbol: str, currency: Currencies, exchange: Exchanges, sec_type: SecTypes) -> Contract:
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type.value
    contract.currency = currency.value
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract.exchange = exchange.value
    return contract


def create_order(action: OrderActions, quantity: float, order_type: OrderTypes, limit_price: float = -1.0) -> Order:
    order = Order()
    order.action = action.value
    order.orderType = order_type.value
    order.totalQuantity = quantity

    if limit_price != -1.0:
        order.lmtPrice = limit_price

    return order
