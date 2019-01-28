class RebalanceAsset:
    def __init__(self, name, value, target_percent, actual_allocation=None, target_value=None, deviation=None,
                 delta=None):
        self.delta = delta
        self.deviation = deviation
        self.target_value = target_value
        self.actual_allocation = actual_allocation
        self.target_percent = target_percent
        self.value = value
        self.name = name

    def __repr__(self):
        return "{}: Dev: {} Delta: {}".format(self.name, str(self.deviation), str(self.delta))
