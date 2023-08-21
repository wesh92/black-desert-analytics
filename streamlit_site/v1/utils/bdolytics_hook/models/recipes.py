from pydantic import BaseModel, Field
from typing import Optional


class NormalProc(BaseModel):
    id: int = Field(..., alias="id", examples=[568])
    name: str = Field(..., alias="name", examples=["Highly Concentrated Grain Juice"])
    processing_type: Optional[str] = Field(
        None, alias="processingType", examples=["Simple Cooking"]
    )
    xp: int = Field(..., alias="xp", examples=[0])
    grade: int = Field(..., alias="grade", examples=[0])
    processing_time: Optional[int] = Field(None, alias="processingTime", examples=[9])
    min_proc: int = Field(..., alias="minProc", examples=[1])
    max_proc: int = Field(..., alias="maxProc", examples=[1])
    level: int = Field(..., alias="level", examples=[30])
    crafting_type: str = Field(..., alias="craftingType", examples=["Processing"])


class RareProc(BaseModel):
    "Note: The Rare Proc model may not always be present."

    id: int = Field(..., alias="id", examples=[578])
    name: str = Field(
        ...,
        alias="name",
        examples=["Refined Grain Juice"],
        description="The name of the rare proc. Needs to be enriched with the item name.",
    )
    xp: int = Field(..., alias="xp", examples=[0])
    grade: int = Field(..., alias="grade", examples=[0])
    min_proc: int = Field(..., alias="minProc", examples=[1])
    max_proc: int = Field(..., alias="maxProc", examples=[1])
    proc_chance: Optional[float] = Field(None, alias="procChance", examples=[0.05])


class Ingredient(BaseModel):
    group_id: Optional[int] = Field(None, alias="groupId", examples=[15])
    type: Optional[str] = Field(None, alias="type", examples=["materialGroup"])
    id: int = Field(..., alias="id", examples=[7011])
    name: Optional[str] = Field(
        None,
        alias="name",
        examples=["Special Wheat"],
        description="The name of the ingredient. Needs to be enriched with the item name.",
    )
    quantity_needed_per_craft: int = Field(..., alias="quantityPerCraft", examples=[1])
