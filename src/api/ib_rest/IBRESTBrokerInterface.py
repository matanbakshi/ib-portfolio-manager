from time import sleep
from src.api.BaseBrokerInterface import BaseBrokerInterface
from src.api.types import OrderTypes, OrderActions, SecTypes, Currencies, Exchanges, OrderState, PositionData
import requests
import json
from datetime import datetime
from src.logger import logger as L
import sys
from src.utils.config_loader import creds_conf

import src.utils.ib_gateway_launcher as _launcher

API_URL = "https://localhost:5000/v1/portal"
CURRENCY_FOR_CASH = "USD"  # Can also be 'BASE' or other currency.
IB_SMART_ROUTING = "SMART"

REQUESTS_TIMEOUT_SEC = 3
AUTH_RETRY_THRESHOLD = 20


class IBRESTBrokerInterface(BaseBrokerInterface):
    def __init__(self):
        super().__init__()

        self._ib_acc_id = creds_conf["account_id"]
        self._connection_attempts = 0
        self._launch_and_validate_ib_gateway()

    def _launch_and_validate_ib_gateway(self, retry=False, relaunch=False):
        # _launcher.launch_ib_gateway_and_auth(retry_auth=self._connection_attempts > 1)
        self._connection_attempts += 1

        if not retry:
            _launcher.launch_ib_gateway_and_auth()
        elif relaunch:
            _launcher.relaunch()
        else:
            res = requests.post(f"{API_URL}/iserver/reauthenticate", verify=False)
            L.debug(res.content)

        sleep(3)
        self._call_post_auth_methods()

        sleep(2)
        self._validate_gateway_auth()

    def _validate_gateway_auth(self):
        # Validate if authentication was successful
        if not self._check_auth_status():
            if self._connection_attempts < AUTH_RETRY_THRESHOLD:
                L.error(
                    f"AUTH status validation failed, trying to relaunch gateway (attempt #{self._connection_attempts})")
                sleep(2)
                self._launch_and_validate_ib_gateway(relaunch=True)
            else:
                raise SystemError("AUTH status validation failed after reaching a threshold.")

        try:
            balance = self.request_cash_balance()
            assert balance is not float
        except:
            L.error(
                f"Authentication to IB failed for attempt #{self._connection_attempts}, error: {sys.exc_info()[0]}.")

            if self._connection_attempts < AUTH_RETRY_THRESHOLD:
                sleep(2)
                self._launch_and_validate_ib_gateway(retry=True)
            else:
                L.fatal(f"Stopped retrying connection reaching a threshold.")
                raise

    def _call_post_auth_methods(self):
        res = requests.get(f"{API_URL}/sso/validate", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
        L.debug(res.content)
        sleep(.5)
        res = requests.get(f"{API_URL}/one/user", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
        L.debug(res.content)
        sleep(.5)
        res = requests.get(f"{API_URL}/portfolio/accounts", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
        L.debug(res.content)
        sleep(.5)
        res = requests.get(f"{API_URL}/iserver/accounts", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
        L.debug(res.content)

    def _check_auth_status(self):
        res = requests.get(f"{API_URL}/iserver/auth/status", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
        status_content = json.loads(res.content)

        L.debug(f"AUTH status: {status_content}")

        return status_content["authenticated"] and status_content["connected"] and not status_content["competing"]

    def place_single_order(self, contract_id: int, symbol: str, quantity: float, order_type: OrderTypes,
                           action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges = None,
                           limit_price: float = -1.0) -> OrderState:
        # TODO: finish after receiving answer for the "conid" parameter
        L.info(f"Trying to order: {symbol}")

        payload = {
            "acctId": self._ib_acc_id,
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

        jres = requests.post(f"{API_URL}/iserver/account/{self._ib_acc_id}/order", json=payload, verify=False,
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

        jres = requests.get(f"{API_URL}/portfolio/{self._ib_acc_id}/positions/{pageId}", verify=False,
                            timeout=REQUESTS_TIMEOUT_SEC)
        payload = json.loads(jres.content)

        positions = []
        for item in payload:
            positions.append(
                PositionData(symbol=item["ticker"], currency=Currencies(item["currency"]), quantity=item["position"],
                             market_price=item["mktPrice"], sec_type=SecTypes(item["assetClass"]),
                             contract_id=item["conid"]))
        return positions

    def request_cash_balance(self) -> float:
        res = requests.get(f"{API_URL}/portfolio/{self._ib_acc_id}/ledger", verify=False, timeout=REQUESTS_TIMEOUT_SEC)
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
