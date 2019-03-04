from src.api.BaseBrokerInterface import BaseBrokerInterface
from src.api.types import OrderTypes, OrderActions, SecTypes, Currencies, Exchanges, OrderState, PositionData
import requests
import json
from datetime import datetime

IB_ACC_ID = "DU1162858"
API_URL = "https://localhost:5000/v1/portal"
CURRENCY_FOR_CASH = "USD"  # Can also be 'BASE' or other currency.
IB_SMART_ROUTING = "SMART"


class IBRESTBrokerInterface(BaseBrokerInterface):
    def __init__(self):
        super().__init__()

    def place_single_order(self, contract_id: int, symbol: str, quantity: float, order_type: OrderTypes,
                           action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges = None,
                           limit_price: float = -1.0):
        # TODO: finish after receiving answer for the "conid" parameter

        payload = {
            "acctId": IB_ACC_ID,
            "conid": contract_id,
            "secType": f"{contract_id}:{sec_type.value}",  # should include conid (xxx:STK)
            "cOID": f"{symbol}-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}",  # Custom string
            "orderType": order_type.value,
            "listingExchange": exchange.value if exchange else IB_SMART_ROUTING,
            "outsideRTH": False,
            "side": action.value,
            "ticker": symbol,
            "tif": "GTC",  # order will be "Good Till Cancel", maybe it is required...
            "referrer": "",
            "quantity": quantity
        }

        if order_type is OrderTypes.LIMIT:  # No support for 'STOP' type
            payload["price"] = limit_price

        jres = requests.post(f"{API_URL}/iserver/account/{IB_ACC_ID}/order", json=payload, verify=False)
        res_content = json.loads(jres.content)

        if 'error' in res_content:
            raise SystemError(
                f"API error occurred while trying to order {symbol} ({contract_id}): {res_content['error']}")

        response = res_content[0]

        if "id" in response and "order_id" not in response:  # Requires sending reply (not always)
            reply_id = response["id"]
            jres = requests.post(f"{API_URL}/iserver/reply/{reply_id}", json={"confirmed": True}, verify=False)
            res_content = json.loads(jres.content)

            response = res_content[0]

        if "order_id" in response and "order_status" in response:
            return OrderState(response["order_status"])
        else:
            raise SystemError(f"Ordering {contract_id} failed. {response['error'] if 'error' in response else ''}")

    def request_all_holdings(self):
        pageId = 0  # Paginated result. Shows the first 30 positions.

        jres = requests.get(f"{API_URL}/portfolio/{IB_ACC_ID}/positions/{pageId}", verify=False)
        payload = json.loads(jres.content)

        for item in payload:
            yield PositionData(symbol=item["ticker"], currency=Currencies(item["currency"]), quantity=item["position"],
                               market_price=item["mktPrice"], sec_type=SecTypes(item["assetClass"]),
                               contract_id=item["conid"])

    def request_cash_balance(self) -> float:
        res = requests.get(f"{API_URL}/portfolio/{IB_ACC_ID}/ledger", verify=False)
        jres = json.loads(res.content)

        cash_balance = jres[CURRENCY_FOR_CASH]["cashbalance"]

        return cash_balance


if __name__ == "__main__":
    ib = IBRESTBrokerInterface()

    holdings = list(ib.request_all_holdings())

    first = holdings[0]

    res = ib.place_single_order(first.contract_id, first.symbol, 30, OrderTypes.LIMIT,
                                OrderActions.BUY_ORDER, SecTypes.STOCK,
                                Currencies.USD, limit_price=176)
