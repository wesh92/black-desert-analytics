from dataclasses import dataclass
from logging import error, info, warning

import polars as pl
import requests
from .configs.market_config import MARKET_CATEGORIES
from .configs.secrets_cookies import cookies, request_token
from .models.base_item_info_model import BaseItemInfoModel
from polars.exceptions import SchemaFieldNotFoundError


@dataclass
class ItemData:
    """Contains Methods for getting item data from the market.

    Attributes:
        main_categories (str | list[str] | int): The main category(ies) to get item data for.
            If None, all main categories will be used.
    
    Example Usages:
        >>> from utils.pearl_abyss_hook.pa_base_item_info import ItemData
        >>> ItemData(["1"]).get_base_item_data()
        >>> ItemData(["1"]).get_base_item_data().filter(pl.col("mainKey") == 10003) # Filter for Elsh Longsword
        >>> ItemData(["1"]).create_info_models()

        >>> # Create a model for a specific Item ID
        >>> a = ItemData(["1"]).get_base_item_data().filter(pl.col("mainKey") == 10003)
        >>> ItemData(["1"]).create_info_models(a)
    """
    main_categories: str | list[str] | int = None

    def get_base_item_data(self) -> pl.DataFrame:
        """Get base item data from the market.

        Returns:
            pl.DataFrame: A DataFrame containing the base item data.

        Notes:
            Reads from `configs.secrets_cookies` for cookies and request_token.
        """
        categories = MARKET_CATEGORIES

        if isinstance(self.main_categories, str):
            self.main_categories = [self.main_categories]
        # or if main_categories is an int, convert to list of strings
        elif isinstance(self.main_categories, int):
            self.main_categories = [str(self.main_categories)]

        if self.main_categories:
            # Filtering main categories
            categories = {
                key: categories[key] for key in self.main_categories if key in categories
            }

            # Check for non-existing main categories and log a warning
            non_existing_categories = [
                key for key in self.main_categories if key not in categories
            ]
            for key in non_existing_categories:
                warning(f"Main category {key} does not exist.")

        session = requests.Session()
        session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

        all_items_df = pl.DataFrame()

        for main_category, details in categories.items():
            sub_categories = details[1]
            main_category_name = details[0]

            for sub_category, sub_details in sub_categories.items():
                sub_category_name = sub_details

                data = {
                    "__RequestVerificationToken": request_token,
                    "mainCategory": f"{main_category}",
                    "subCategory": f"{sub_category}",
                }
                info(data)

                response = session.post(
                    "https://na-trade.naeu.playblackdesert.com/Home/GetWorldMarketList",
                    cookies=cookies,
                    data=data,
                )
                try:
                    item_info_df = (
                        pl.from_records(response.json()["marketList"])
                        .with_columns(
                            pl.lit(f"{main_category_name}").alias("main_category"),
                            pl.lit(f"{sub_category_name}").alias("sub_category"),
                            pl.lit(main_category).alias("main_category_id"),
                            pl.lit(sub_category).alias("sub_category_id"),
                        )
                        .drop(["sumCount", "minPrice"])
                    )
                except SchemaFieldNotFoundError:
                    error(response.json())
                    item_info_df = pl.from_records(
                        response.json()["marketList"]
                    ).with_columns(
                        pl.lit(f"{main_category_name}").alias("main_category"),
                        pl.lit(f"{sub_category_name}").alias("sub_category"),
                        pl.lit(main_category).alias("main_category_id"),
                        pl.lit(sub_category).alias("sub_category_id"),
                    )

                all_items_df = all_items_df.vstack(item_info_df)

        return all_items_df

    def create_info_models(self, data: list[dict] | pl.DataFrame = None) -> list[BaseItemInfoModel]:
        """Create BaseItemInfoModel objects from the data returned by `get_base_item_data()` 
            or a user-defined/requested data from `get_base_item_data()`.

        Args:
            data (list[dict], optional): The data to create BaseItemInfoModel objects from.
                Defaults to None, in which case `get_base_item_data()` will be called.

        Returns:
            list[BaseItemInfoModel]: A list of BaseItemInfoModel objects.
        """
        if data is None:
            data = self.get_base_item_data().to_dicts()
        elif isinstance(data, pl.DataFrame):
            data = data.to_dicts()

        return [BaseItemInfoModel(**item) for item in data]