from pydantic import BaseModel, Field, field_validator


class BDOlyticsMarketModel(BaseModel):
    item_id: int = Field(..., alias="item_id")
    enhancement_level: int = Field(..., alias="enhancement_level")
    sub_id: int = Field(..., alias="sub_id")
    grade_type: int = Field(..., alias="grade_type")
    market_main_category: int = Field(..., alias="market_main_category")
    market_sub_category: int = Field(..., alias="market_sub_category")
    in_stock: int = Field(..., alias="in_stock")
    total_trades: int = Field(..., alias="total_trades")
    price: int = Field(..., alias="price")
    price_change: int = Field(..., alias="price_change")
    fourteen_day_volume: int = Field(..., alias="fourteen_day_volume")
    volume_change: int = Field(..., alias="volume_change")
    name: str = Field(..., alias="name")

    @field_validator("enhancement_level")
    @classmethod
    def _validate_enhancement_level(cls, value) -> int:
        if value < 0 or value > 20:
            raise ValueError("enhancement_level must be between 0 and 20")
        return value

class BDOlyticsKnownItemModel(BaseModel):
    name: str = Field(..., alias="name")
