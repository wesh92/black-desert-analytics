from dataclasses import dataclass
from logging import log

import requests
from .configs.market_config import LOCALES, MarketEndpoint, market_url_structure
from .models.market_sub_list_model import MarketSubListModel
from .unpacker import unpack

@dataclass
class MarketData:
    region: str = None
    endpoint_name: str = None
    item_id: int = None

    def get_url(self) -> tuple[str, str]:
        region = LOCALES[0] if self.region is None else self.region
        endpoint = MarketEndpoint[self.endpoint_name.upper()] if self.endpoint_name else list(MarketEndpoint)[0]

        return (region.upper(), market_url_structure[region.lower()][endpoint.name])

    def get_market_data(self, url: str = None) -> list[dict]:
        url = url or self.get_url()[1]
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "BlackDesert",
        }
        data = {
            "keyType": 0,
            "mainKey": self.item_id
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get market data for item id {self.item_id}")

    def parse_response(self) -> list[MarketSubListModel]:
        # Extract the result string
        result_str = self.get_market_data()["resultMsg"]

        # Split the string on '|' to get individual listings
        listings = result_str.split('|')

        # Remove any empty strings from the listings list
        listings = [listing for listing in listings if listing]

        # Parse each listing and create a MarketSubListModel object
        parsed_listings = []
        for listing in listings:
            fields = listing.split('-')

            # Map fields to MarketSubListModel
            model_data = {
                "item_id": int(fields[0]),
                "enhancement_range_min": int(fields[1]),
                "enhancement_range_max": int(fields[2]),
                "base_price": int(fields[3]),
                "current_stock": int(fields[4]),
                "total_trades": int(fields[5]),
                "price_hard_cap_min": int(fields[6]),
                "price_hard_cap_max": int(fields[7]),
                "last_sale_price": int(fields[8]),
                "last_sale_epoch_time": int(fields[9]),
            }
            parsed_listings.append(MarketSubListModel(**model_data))

        return parsed_listings
