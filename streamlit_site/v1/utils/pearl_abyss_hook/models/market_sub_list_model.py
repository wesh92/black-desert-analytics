import pendulum
from pydantic import BaseModel, Field, root_validator


class MarketSubListModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    item_id: int = Field(..., title="Item ID")
    enhancement_range_min: int = Field(..., title="Enhancement Range Min")
    enhancement_range_max: int = Field(..., title="Enhancement Range Max")
    base_price: int = Field(..., title="Base Price")
    current_stock: int = Field(..., title="Current Stock")
    total_trades: int = Field(..., title="Total Trades")
    price_hard_cap_min: int = Field(..., title="Price Hard Cap Min")
    price_hard_cap_max: int = Field(..., title="Price Hard Cap Max")
    last_sale_price: int = Field(..., title="Last Sale Price")
    last_sale_epoch_time: int = Field(..., title="Last Sale Epoch Time")
    created_at: pendulum.DateTime = Field(None, title="Created At")
    last_sale_datetime: pendulum.DateTime = Field(None, title="Last Sale DateTime")

    @root_validator(pre=True)
    @classmethod
    def convert_epoch_to_datetime(cls, values) -> dict:
        epoch_time = values.get('last_sale_epoch_time')
        if epoch_time:
            values['last_sale_datetime'] = pendulum.from_timestamp(epoch_time)
        values['created_at'] = pendulum.now(tz='UTC')
        return values
