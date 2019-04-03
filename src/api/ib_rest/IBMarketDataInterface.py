import json
from time import sleep
from typing import List, Dict

import requests

from src.api.BaseMarketDataInterface import BaseMarketDataInterface
from src.api.types import Exchanges, MarketData
from src.api.ib_rest.IBRESTBrokerInterface import API_URL, REQUESTS_TIMEOUT_SEC
from src.logger import logger

# IEX_TOKEN = "sk_7c26fe796d21446badbda3e5684d3e01"
# ALPHA_TOKEN = "2G8RJF25L3Y8WY83"

SNAPSHOT_FIELDS = {
    "symbol": "55",
    "bid_price": "84",
    "bid_size": "88",
    "ask_price": "86",
    "ask_size": "85"
}

RETRIEVAL_RETRY_ATTEMPTS_THRESHOLD = 3


class IBMarketDataInterface(BaseMarketDataInterface):
    def __init__(self):
        self._retry_attempts = 0

    def get_market_data(self, contract_ids: List[int]) -> Dict[int, MarketData]:
        conids_str = ",".join(str(i) for i in contract_ids)
        res_content = self._perform_data_request(conids_str)

        md_dict = {}

        for pos_data in res_content:
            bid_price = float(pos_data[SNAPSHOT_FIELDS["bid_price"]]) \
                if SNAPSHOT_FIELDS["bid_price"] in pos_data else None

            bid_size = int(pos_data[SNAPSHOT_FIELDS["bid_size"]].replace(",", "")) \
                if SNAPSHOT_FIELDS["bid_size"] in pos_data else None

            ask_price = float(pos_data[SNAPSHOT_FIELDS["ask_price"]]) if \
                SNAPSHOT_FIELDS["ask_price"] in pos_data else None

            ask_size = int(pos_data[SNAPSHOT_FIELDS["ask_size"]].replace(",", "")) \
                if SNAPSHOT_FIELDS["ask_size"] in pos_data else None

            symbol = pos_data[SNAPSHOT_FIELDS["symbol"]]

            md_dict[pos_data["conid"]] = MarketData(symbol, ask_price, ask_size, bid_price, bid_size)

        return md_dict

    def _perform_data_request(self, conids_str, persist_if_not_valid=True):

        jres = requests.get(f"{API_URL}/iserver/marketdata/snapshot?conids={conids_str}", verify=False,
                            timeout=REQUESTS_TIMEOUT_SEC)

        res_content = json.loads(jres.content)

        if not self._validate_result(res_content):
            if self._retry_attempts > RETRIEVAL_RETRY_ATTEMPTS_THRESHOLD or not persist_if_not_valid:
                raise SystemError("Retrieval for market data failed, the data received is not valid. Stopping.")

            self._retry_attempts += 1
            sleep(1)
            logger.warn(f"Retrieval for market data failed. Retry #{self._retry_attempts}")
            return self._perform_data_request(conids_str)

        return res_content

    def _validate_result(self, md_result):
        items_to_validate = [SNAPSHOT_FIELDS["bid_price"], SNAPSHOT_FIELDS["bid_price"], SNAPSHOT_FIELDS["bid_price"],
                             SNAPSHOT_FIELDS["ask_size"]]

        if md_result:
            for data in md_result:
                if data == "error":
                    # 'Please query /accounts first' TODO: Handle this
                    return False
                if not any(elem in data.keys() for elem in items_to_validate):
                    return False
            return True
        return False
