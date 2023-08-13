import json
from dataclasses import dataclass, field

import pendulum
import requests
from configs.config import LOCALES, known_items
from models.analytics import BDOlyticsAnalyticsModel
from models.market import BDOlyticsMarketModel, BDOlyticsKnownItemModel
from pendulum import DateTime


def _convert_to_epoch(date: DateTime = None) -> int:
    date = pendulum.now() if date is None else date
    string_date = str(date.float_timestamp).replace(".", "")
    return int(string_date[:13])


@dataclass
class BDOlyticsAnalyticsEndpoint:
    def get_analytics_data(
        self,
        item_id: int,
        epoch_start: int,
        epoch_end: int,
        region: str,
        enhancement_level: str = "0",
    ) -> list[list]:
        """_summary_

        Args:
            item_id (int): The item ID.
            epoch_start (int): The 13 digit timestamp to start the time window.
            epoch_end (int): The 13 digit timestamp that ends the time window.
            region (str): A string regional identifier.
            enhancement_level (str, optional): The enhancement specification if applicable. Defaults to "0".

        Returns:
            list[list]: A list of analytics data.

        Example Usage:
            >>> from utils.bdolytics_hook.bdolytics import BDOlyticsAnalyticsEndpoint
            >>> endpoint = BDOlyticsAnalyticsEndpoint()
            >>> endpoint.get_analytics_data(
                item_id=1, epoch_start=1627776000000, epoch_end=1627776000000, region="na", enhancement_level="0"
            )
        """
        base_url = f"https://apiv2.bdolytics.com/market/analytics/{item_id}"
        querystring = {
            "start_date": epoch_start,
            "end_date": epoch_end,
            "region": region,
            "enhancement_level": enhancement_level,
        }
        response = requests.request("GET", base_url, params=querystring)

        return json.loads(response.content.decode("utf-8"))["data"]

    def fill__analytics_request(
        self,
        item_id: int,
        epoch_start: int = None,
        epoch_end: int = None,
        regions: list[str] = None,
    ) -> list[BDOlyticsAnalyticsModel]:
        """Fills the analytics request with the given parameters.

        Args:
            item_id (int, required): The item ID.
            epoch_start (int, optional): The 13 digit timestamp to start the time window. Defaults to 7 days prior.
            epoch_end (int, optional): The 13 digit timestamp that ends the time window. Defaults to current timestamp.
            regions (list[str], optional): A list of string regional identifiers. Defaults to LOCALES from `configs`.

        Returns:
            list[BDOlyticsAnalyticsModel]: A list of analytics models.

        Example Usage:
            >>> from utils.bdolytics_hook.bdolytics import BDOlyticsAnalyticsEndpoint
            >>> endpoint = BDOlyticsAnalyticsEndpoint()
            >>> endpoint.fill__analytics_request(item_id=1)
            [BDOlyticsAnalyticsModel(epoch_timestamp=1627776000000, price=100000, stock=100, volume=100, item_id=1), ...]

            OR
            >>> endpoint.fill__analytics_request(
                item_id=1, epoch_start=1627776000000, epoch_end=1627776000000, regions=["na", "eu"]
                )
        """
        epoch_end = pendulum.now() if epoch_end is None else epoch_end
        epoch_start = (
            pendulum.now().subtract(days=7) if epoch_start is None else epoch_start
        )
        analytics_models = []
        for loc in regions if regions is not None else LOCALES:
            analytics_data = self.get_analytics_data(
                item_id=item_id,
                epoch_start=_convert_to_epoch(epoch_start),
                epoch_end=_convert_to_epoch(epoch_end),
                region=loc,
            )
            for data in analytics_data:
                analytics_models.append(
                    BDOlyticsAnalyticsModel(
                        epoch_timestamp=data[0],
                        price=data[1],
                        stock=data[2],
                        volume=data[3],
                        item_id=item_id,
                    )
                )
        return analytics_models


@dataclass
class BDOlyticsMarketEndpoint:
    """The BDOlyticsMarketEndpoint class is a dataclass that represents the BDOlytics market API.

    Raises:
        ValueError: If the region is not a valid region.

    Returns:
        list[BDOlyticsMarketModel] | BDOlyticsMarketModel: A pydantic model or list of pydantic models.
    """
    region: str = "NA"
    endpoint: str = "market/central-market-data"
    url: str = field(init=False)

    def __post_init__(self) -> None:
        self.url = (
            f"https://apiv2.bdolytics.com/en/{self.region.upper()}/{self.endpoint}"
        )

    def get_item_data(self) -> list[BDOlyticsMarketModel]:
        return json.loads(requests.request("GET", self.url).content.decode("utf-8"))[
            "data"
        ]

    def fill__item_data(self) -> list[BDOlyticsMarketModel]:
        """Returns a list of BDOlyticsMarketModel objects which correspond to the entire market data.

        Returns:
            list[BDOlyticsMarketModel]: _description_

        Example Usage:
            >>> from utils.bdolytics_hook.bdolytics import BDOlyticsMarketEndpoint
            >>> endpoint = BDOlyticsMarketEndpoint()
            >>> endpoint.fill__item_data()
        """
        item_data = self.get_item_data()
        return [
            BDOlyticsMarketModel(
                item_id=item["item_id"],
                enhancement_level=item["enhancement_level"],
                sub_id=item["sub_id"],
                grade_type=item["grade_type"],
                market_main_category=item["market_main_category"],
                market_sub_category=item["market_sub_category"],
                in_stock=item["in_stock"],
                total_trades=item["total_trades"],
                price=item["price"],
                price_change=item["price_change"],
                fourteen_day_volume=item["fourteen_day_volume"],
                volume_change=item["volume_change"],
                name=item["name"],
            )
            for item in item_data
        ]

    def fill__get_item_data_by_id(self, item_id: int) -> BDOlyticsMarketModel:
        """Returns a BDOlyticsMarketModel object which corresponds to the given item_id.

        Args:
            item_id (int): The item ID.

        Raises:
            ValueError: If the item_id is not found in the response.

        Returns:
            BDOlyticsMarketModel: The market model for the given item_id.

        Example Usage:
            >>> from utils.bdolytics_hook.bdolytics import BDOlyticsMarketEndpoint
            >>> endpoint = BDOlyticsMarketEndpoint()
            >>> endpoint.fill__get_item_data_by_id(item_id=1)

            OR to override the default region
            >>> endpoint = BDOlyticsMarketEndpoint(region="EU")
            >>> endpoint.fill__get_item_data_by_id(item_id=1)
        """
        if isinstance(item_id, str):
            item_id = int(item_id)
        if item_id in known_items:
            return BDOlyticsKnownItemModel(
                name=known_items[item_id],
            )
        item_data = self.get_item_data()
        # search for the item_id in the response
        for item in item_data:
            if item["item_id"] == item_id:
                return BDOlyticsMarketModel(
                    item_id=item["item_id"],
                    enhancement_level=item["enhancement_level"],
                    sub_id=item["sub_id"],
                    grade_type=item["grade_type"],
                    market_main_category=item["market_main_category"],
                    market_sub_category=item["market_sub_category"],
                    in_stock=item["in_stock"],
                    total_trades=item["total_trades"],
                    price=item["price"],
                    price_change=item["price_change"],
                    fourteen_day_volume=item["fourteen_day_volume"],
                    volume_change=item["volume_change"],
                    name=item["name"],
                )
        raise ValueError(f"Item ID {item_id} not found in response for URL {self.url}")
