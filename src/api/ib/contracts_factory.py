from ibapi.contract import Contract
from src.api.ib.string_consts import *


def create_US_contract(symbol, currency):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = SecTypes.STOCK
    contract.currency = currency
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract.exchange = ExchangeNames.NASDAQ_EXCHANGE
    return contract
