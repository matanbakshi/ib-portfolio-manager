class AccountSummary:
    def __init__(self, req_id, acc_id, tag, value, currency):
        self.currency = currency
        self.value = value
        self.tag = tag
        self.req_id = req_id
