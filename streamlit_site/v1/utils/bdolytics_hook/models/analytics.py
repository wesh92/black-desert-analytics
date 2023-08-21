from pydantic import BaseModel, Field


class BDOlyticsAnalyticsModel(BaseModel):
    epoch_timestamp: int = Field(..., alias="epoch_timestamp", examples=[1627776000])
    price: int = Field(..., alias="price", examples=[1000000])
    stock: int = Field(..., alias="stock", examples=[100])
    volume: int = Field(..., alias="volume", examples=[100])
    item_id: int = Field(..., alias="item_id", examples=[1])
    