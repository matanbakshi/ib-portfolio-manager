from threading import Thread

from src.api.common.BaseBrokerInterface import BaseBrokerInterface
from src.api.common.BrokerInterfaceEventsHandler import BrokerInterfaceEventsHandler

from src.api.ib.ib_entities_factory import *
from src.api.common.types import *
from src.api.ib.ib_app_objects import IBApp


class IBBrokerInterface(BaseBrokerInterface):
    def __init__(self, event_handler, last_oid, hostname="127.0.0.1", port=7497):
        self.last_oid = last_oid
        self._ibApp = IBApp(event_handler)
        self._ibApp.connect(hostname, port, 0)

        thread = Thread(target=self._ibApp.run)
        self.start = thread.start()

        setattr(self._ibApp, "_thread", thread)

    def place_single_order(self, symbol: str, quantity: float, order_type: OrderTypes, action: OrderActions,
                           sec_type: SecTypes, currency: Currencies, exchange: Exchanges, limit_price: float = -1.0):
        # TODO: support multiple orders, grouping and enabling "One-Cancels All"
        order = create_order(action, quantity, order_type, limit_price)
        contract = create_contract(symbol, currency, exchange, sec_type)

        # TODO: understand how to use this order ID better.
        self._ibApp.placeOrder(self.last_oid, contract, order)
        self.last_oid += 1

    def get_all_holdings(self):
        self._ibApp.reqPositions()

    def get_holding_by_symbol(self, symbol: str, exchange: Exchanges):
        pass

    def get_all_pending_orders(self):
        self._ibApp.reqOpenOrders()
        pass


if __name__ == "__main__":
    with open("./oid", "r") as oid_file:
        _last_oid = int(oid_file.read())

    handler = BrokerInterfaceEventsHandler()
    handler.get_holdings_callback = lambda x: print(x)

    ib = IBBrokerInterface(handler, _last_oid)
    # ib.buy_holdings("IBKR", "1")
    #
    # with open("./oid", "w") as oid_file:
    #     oid_file.write(str(ib.last_oid))
    ib.getAllOrders()
    input()
    # ib.get_all_holdings()
