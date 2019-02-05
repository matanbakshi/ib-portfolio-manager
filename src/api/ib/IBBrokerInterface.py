from threading import Thread, Event
from src.tools.sync_helpers import wait_for_all_events
from typing import List
from ibapi.account_summary_tags import AccountSummaryTags

from src.api.BaseBrokerInterface import BaseBrokerInterface

from src.api.ib.ib_entities_factory import *
from src.api.ib.ib_app_objects import IBApp
from src.api.ib.IBEventsHandler import IBEventsHandler

CONSTANT_ID = 9008

API_TIMEOUT = 15.0


class IBBrokerInterface(BaseBrokerInterface):
    def __init__(self, hostname="127.0.0.1", port=7497):
        self._last_oid = None
        self._event_handler = IBEventsHandler()
        self._event_handler.next_valid_oid_callback = self._next_valid_id_response
        self._event_handler.position_end_callback = self._set_sync_event
        self._event_handler.account_summary_end = self._set_sync_event

        self._ibApp = IBApp(self._event_handler)
        self._ibApp.connect(hostname, port, 0)

        thread = Thread(target=self._ibApp.run)
        self.start = thread.start()
        setattr(self._ibApp, "_thread", thread)

        self._sync_event = Event()
        self._request_next_oid_and_wait()

    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        order = create_order(action, quantity, order_type, limit_price)
        contract = create_contract(symbol, currency, exchange, sec_type)

        self._ibApp.placeOrder(self._last_oid, contract, order)
        self._last_oid += 1

    def request_all_holdings(self) -> List[PositionData]:
        all_positions = []
        self._event_handler.new_position_callback = lambda pos: all_positions.append(pos)
        self._ibApp.reqPositions()

        event_set = self._sync_event.wait(API_TIMEOUT)
        if not event_set:
            raise ConnectionError(f"The API call to request holding timed out after {API_TIMEOUT} seconds")

        return all_positions

    def request_cash_balance(self) -> float:
        acc_summary_list = []

        # The IB API has a race condition and sends the END message before the account summary message. Therefore,
        # I added another wait mechanism here that will fire on the first account summary callback,
        # and wait for both events.
        # TODO: This race condition occurred when only one tag was requested,
        #  it might also happen in other places (like requesting positions). Check this in the future.
        data_received_wait_event = Event()

        def _account_summary_callback(acc_sum):
            acc_summary_list.append(acc_sum)
            data_received_wait_event.set()

        self._event_handler.account_summary_callback = _account_summary_callback

        # Currently I send only const ID because it doesn't have any meaning except for tagging, might be
        # interesting in the future.
        ib._ibApp.reqAccountSummary(CONSTANT_ID, "All", AccountSummaryTags.TotalCashValue)

        event_set = wait_for_all_events([self._sync_event, data_received_wait_event], API_TIMEOUT)
        if not event_set:
            raise ConnectionError(f"The API call to request cash balance timed out after {API_TIMEOUT} seconds")

        cash_balance = next(
            acc_sum.value for acc_sum in acc_summary_list if acc_sum.tag == AccountSummaryTags.TotalCashValue)

        return cash_balance

    def _set_sync_event(self):
        self._sync_event.set()
        self._sync_event.clear()

    def _request_next_oid_and_wait(self):
        self._ibApp.reqIds(-1)  # The parameter is ignored (according to IB API)
        event_set = self._sync_event.wait(API_TIMEOUT)
        if not event_set or self._last_oid is None:
            raise ConnectionError("The next valid order ID wasn't received from the "
                                  f"IB API and timed out ({API_TIMEOUT} second(s)) "
                                  f"or there was no callback assigned to it.")

        self._sync_event.clear()

    def _next_valid_id_response(self, oid):
        self._last_oid = oid

        self._set_sync_event()


if __name__ == "__main__":
    ib = IBBrokerInterface()

    # ib._ibApp.reqAccountSummary(9008, "All", AccountSummaryTags.TotalCashValue)
    balance = ib.request_cash_balance()
    print(balance)
    # result = ib.request_all_holdings()
    # pprint(result)

    # ib.place_single_order("IBKR", 1, OrderTypes.LIMIT, OrderActions.BUY_ORDER, SecTypes.STOCK, Currencies.USD,
    #                       Exchanges.NASDAQ_EXCHANGE, limit_price=200)
    #
    input()
