import json
from typing import List, Dict

import requests

from src.api.BaseMarketDataInterface import BaseMarketDataInterface
from src.api.types import Exchanges, MarketData
from src.api.ib_rest.IBRESTBrokerInterface import API_URL, IB_ACC_ID

# IEX_TOKEN = "sk_7c26fe796d21446badbda3e5684d3e01"
# ALPHA_TOKEN = "2G8RJF25L3Y8WY83"

SNAPSHOT_FIELDS = {
    "bid_price": "84",
    "bid_size": "88",
    "ask_price": "86",
    "ask_size": "85"
}


class IBMarketDataInterface(BaseMarketDataInterface):
    def get_market_data(self, contract_ids: List[int]) -> Dict[int, MarketData]:
        conids_str = ",".join(str(i) for i in contract_ids)
        jres = requests.get(f"{API_URL}/iserver/account/{IB_ACC_ID}/order?conids={conids_str}")
        res_content = json.loads(jres.content)

        md_dict = {}

        for pos_data in res_content:
            bid_price = pos_data[SNAPSHOT_FIELDS["bid_price"]]
            bid_size = pos_data[SNAPSHOT_FIELDS["bid_size"]]
            ask_price = pos_data[SNAPSHOT_FIELDS["ask_price"]]
            ask_size = pos_data[SNAPSHOT_FIELDS["ask_size"]]

            md_dict[pos_data["conid"]] = MarketData(ask_price, ask_size, bid_price, bid_size)

        return md_dict
