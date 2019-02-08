from src.api.BaseBrokerInterface import BaseBrokerInterface
from src.api.types import OrderTypes, OrderActions, SecTypes, Currencies, Exchanges
import requests
import json

IB_ACC_ID = "DU1162858"
API_URL = "https://localhost:5000/v1/portal"
CURRENCY_FOR_CASH = "USD"  # Can also be 'BASE' or other currency.


class IBRESTBrokerInterface(BaseBrokerInterface):

    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        # TODO: finish after receiving answer for the "conid" parameter
        payload = {
            "acctId": IB_ACC_ID,
            "conid": 0,  # get conid beforehand
            "secType": "string",  # should include conid (xxx:STK)
            "cOID": "single-order",  # Arbitrary string
            "orderType": order_type.value,
            "listingExchange": exchange.value,
            "outsideRTH": False,
            "side": action.value,
            "ticker": symbol,
            "tif": "GTC",  # order will be "Good Till Cancel", maybe it is required...
            "referrer": "string",
            "quantity": quantity
        }

        if order_type is OrderTypes.LIMIT:  # TODO: add "STOP" type
            payload["price"] = limit_price

        res = requests.post(f"{API_URL}/iserver/account/{IB_ACC_ID}/order", data=payload, verify=False)

    def request_all_holdings(self):
        pass

    def request_cash_balance(self) -> float:
        res = requests.get(f"{API_URL}/portfolio/{IB_ACC_ID}/ledger", verify=False)
        jres = json.loads(res.content)

        cash_balance = jres[CURRENCY_FOR_CASH]["cashbalance"]

        return cash_balance


if __name__ == "__main__":
    ib = IBRESTBrokerInterface()

    b = ib.request_cash_balance()
    print(b)
