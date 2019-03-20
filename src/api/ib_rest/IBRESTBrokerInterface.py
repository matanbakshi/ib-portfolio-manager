from src.api.BaseBrokerInterface import BaseBrokerInterface
from src.api.types import OrderTypes, OrderActions, SecTypes, Currencies, Exchanges, OrderState, PositionData
import requests
import json
from datetime import datetime
from src.logger import logger as L
import sys

import src.utils.ib_gateway_launcher as _launcher

IB_ACC_ID = "DU1162858"
API_URL = "https://localhost:5000/v1/portal"
CURRENCY_FOR_CASH = "USD"  # Can also be 'BASE' or other currency.
IB_SMART_ROUTING = "SMART"

REQUESTS_TIMEOUT_SEC = 3
AUTH_RETRY_THRESHOLD = 3


class IBRESTBrokerInterface(BaseBrokerInterface):
    def __init__(self):
        super().__init__()

        self._connection_attempts = 0

        self._launch_and_validate_ib_gateway()

    def _launch_and_validate_ib_gateway(self):
        self._connection_attempts += 1
        _launcher.launch_ib_gateway_and_auth(retry_auth=self._connection_attempts > 1)
        self._validate_gateway_auth()

    def _validate_gateway_auth(self):
        # Validate if authentication was successful
        try:
            balance = self.request_cash_balance()
            assert balance is float
        except:
            L.error(f"Authentication to IB failed for attempt #{self._connection_attempts}, error: {sys.exc_value}.")

            if self._connection_attempts < AUTH_RETRY_THRESHOLD:
                self._launch_and_validate_ib_gateway()
            else:
                L.fatal(f"Stopped retrying connection reaching a threshold.")
                raise

    def place_single_order(self, contract_id: int, symbol: str, quantity: float, order_type: OrderTypes,
                           action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges = None,
                           limit_price: float = -1.0) -> OrderState:
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

        jres = requests.post(f"{API_URL}/iserver/account/{IB_ACC_ID}/order", json=payload, verify=False,
                             timeout=REQUESTS_TIMEOUT_SEC)
        res_content = json.loads(jres.content)

        if 'error' in res_content:
            L.error(f"API error occurred while trying to order {symbol} ({contract_id}): {res_content['error']}")
            return OrderState.FAILED

        response = res_content[0]

        if "id" in response and "order_id" not in response:  # Requires sending reply (not always)
            reply_id = response["id"]
            jres = requests.post(f"{API_URL}/iserver/reply/{reply_id}", json={"confirmed": True}, verify=False,
                                 timeout=REQUESTS_TIMEOUT_SEC)
            res_content = json.loads(jres.content)

            response = res_content[0]

        if "order_id" in response and "order_status" in response:
            return OrderState(response["order_status"])
        else:
            L.error(f"Ordering {contract_id} failed. {response['error'] if 'error' in response else ''}")
            return OrderState.FAILED

    def request_all_holdings(self):
        pageId = 0  # Paginated result. Shows the first 30 positions.

        jres = requests.get(f"{API_URL}/portfolio/{IB_ACC_ID}/positions/{pageId}", verify=False,
                            timeout=REQUESTS_TIMEOUT_SEC)
        payload = json.loads(jres.content)

        for item in payload:
            yield PositionData(symbol=item["ticker"], currency=Currencies(item["currency"]), quantity=item["position"],
                               market_price=item["mktPrice"], sec_type=SecTypes(item["assetClass"]),
                               contract_id=item["conid"])

    def request_cash_balance(self) -> float:
        res = requests.get(f"{API_URL}/portfolio/{IB_ACC_ID}/ledger", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
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
