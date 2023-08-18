import pendulum
from pydantic import BaseModel, Field, root_validator


class BaseItemInfoModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    item_id: int = Field(..., title="Item ID", alias="mainKey")
    name: str = Field(..., title="Item Name")
    grade: int = Field(..., title="Item Grade")
    is_godr_ayed: bool = Field(..., title="Is Godr Ayed", alias="isGodrAyed")
    main_category: str = Field(..., title="Main Category")
    sub_category: str = Field(..., title="Sub Category")
    main_category_id: str = Field(..., title="Main Category ID")
    sub_category_id: str = Field(..., title="Sub Category ID")
    retrieved_at: pendulum.DateTime = Field(None, title="Retrieved At")

    @root_validator(pre=True)
    @classmethod
    def add_retrieved_at(cls, values) -> dict:
        values["retrieved_at"] = pendulum.now(tz="UTC")
        return values
