class BrokerInterfaceEventsHandler:
    def __init__(self):
        self.get_holdings_callback = lambda pos: None
        self.next_valid_oid = lambda oid: None