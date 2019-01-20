from pprint import pprint
from threading import Thread, Event

from src.api.common.BaseBrokerInterface import BaseBrokerInterface

from src.api.ib.ib_entities_factory import *
from src.api.common.types import *
from src.api.ib.ib_app_objects import IBApp
from src.api.ib.IBEventsHandler import IBEventsHandler

API_TIMEOUT = 5.0


class IBBrokerInterface(BaseBrokerInterface):
    def __init__(self, hostname="127.0.0.1", port=7497):
        self._last_oid = None
        self._event_handler = IBEventsHandler()
        self._event_handler.next_valid_oid_callback = self._next_valid_id_response
        self._event_handler.position_end_callback = self._positions_end_callback

        self._ibApp = IBApp(self._event_handler)
        self._ibApp.connect(hostname, port, 0)

        thread = Thread(target=self._ibApp.run)
        self.start = thread.start()
        setattr(self._ibApp, "_thread", thread)

        self._req_oid_wait_handle = Event()
        self._request_next_oid_and_wait()

        self._req_positions_wait_handle = Event()

    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        # TODO: support multiple orders, grouping and enabling "One-Cancels All"
        order = create_order(action, quantity, order_type, limit_price)
        contract = create_contract(symbol, currency, exchange, sec_type)

        self._ibApp.placeOrder(self._last_oid, contract, order)
        self._last_oid += 1

    def request_all_holdings(self):
        all_positions = []
        self._event_handler.new_position_callback = lambda pos: all_positions.append(pos)
        self._ibApp.reqPositions()

        event_set = self._req_positions_wait_handle.wait(API_TIMEOUT)
        if not event_set:
            raise ConnectionError(f"The API call to request holding timed out after {API_TIMEOUT} "
                                  f"seconds")

        return all_positions

    def _positions_end_callback(self):
        self._req_positions_wait_handle.set()
        self._req_positions_wait_handle.clear()

    # def request_all_pending_orders(self): TODO: Implement if necessary in the future
    #     self._ibApp.reqOpenOrders()

    def _request_next_oid_and_wait(self):
        self._ibApp.reqIds(-1)  # The parameter is ignored (according to IB API)
        event_set = self._req_oid_wait_handle.wait(API_TIMEOUT)
        if not event_set or self._last_oid is None:
            raise ConnectionError("The next valid order ID wasn't received from the "
                                  f"IB API and timed out ({API_TIMEOUT} second(s)) "
                                  f"or there was no callback assigned to it.")

        self._req_oid_wait_handle.clear()

    def _next_valid_id_response(self, oid):
        self._last_oid = oid
        self._req_oid_wait_handle.set()


if __name__ == "__main__":
    ib = IBBrokerInterface()
    result = ib.request_all_holdings()
    pprint(result)

    # ib.place_single_order("IBKR", 1, OrderTypes.LIMIT, OrderActions.BUY_ORDER, SecTypes.STOCK, Currencies.USD,
    #                       Exchanges.NASDAQ_EXCHANGE, limit_price=200)
    #
    input()
