class IBEventsHandler:
    def __init__(self):
        self.new_open_order_callback = lambda open_order: None
        self.open_order_end_callback = lambda: None
        self.order_status_callback = lambda order_status: None

        self.new_position_callback = lambda position: None
        self.position_end_callback = lambda: None

        self.next_valid_oid_callback = lambda oid: None

        self.account_summary_callback = lambda acc_summary: None
        self.account_summary_end = lambda reqId: None
