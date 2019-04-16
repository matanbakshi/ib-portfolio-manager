from src.logic.PassiveInvestmentEngine import PassiveInvestmentEngine
from src.api.ib_rest.IBRESTBrokerInterface import IBRESTBrokerInterface
from src.api.ib_rest.IBMarketDataInterface import IBMarketDataInterface


def run():
    engine = PassiveInvestmentEngine(IBRESTBrokerInterface(), IBMarketDataInterface())

    engine.rebalance_with_available_cash()

    return True


if __name__ == "__main__":
    run()
