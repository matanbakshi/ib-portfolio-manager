"""
A Market order is an order to buy or sell at the market bid or offer price. A market order may increase the likelihood
and the speed of execution, but unlike the Limit order a Market order provides no price protection and may fill at
lower/higher than the current displayed bi
Products: BOND, CFD, EFP, CASH, FUND, FUT, FOP, OPT, STK, WAR
"""
from ibapi.order import Order


def create_MKT_order(action: str, quantity: int) -> Order:
    order = Order()
    order.action = action
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order
