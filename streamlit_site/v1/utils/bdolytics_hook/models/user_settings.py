from pydantic import BaseModel, Field, computed_field


class UserSettings(BaseModel):
    # make sure to snake_case the field names
    value_pack_active: bool = Field(..., alias="valuePackActive", examples=[True])
    merchant_ring_active: bool = Field(
        ..., alias="merchantRingActive", examples=[False]
    )
    family_fame_bonus: float = Field(..., alias="familyFameBonus", examples=[0.005])
    weight: int = Field(..., alias="weight", examples=[2400])
    used_weight: int = Field(..., alias="usedWeight", examples=[300])
    feathery_steps_tier: int = Field(..., alias="featheryStepsTier", examples=[5])
    lumbering_mastery: int = Field(..., alias="lumberingMastery", examples=[1500])
    fluid_collecting_mastery: int = Field(
        ..., alias="fluidCollectingMastery", examples=[1500]
    )
    hoe_gathering_mastery: int = Field(
        ..., alias="hoeGatheringMastery", examples=[1500]
    )
    butchering_mastery: int = Field(..., alias="butcheringMastery", examples=[1500])
    tanning_mastery: int = Field(..., alias="tanningMastery", examples=[1500])
    mining_mastery: int = Field(..., alias="miningMastery", examples=[1500])
    water_scooping_mastery: int = Field(
        ..., alias="waterScoopingMastery", examples=[1500]
    )
    hedgehog_tier: int = Field(..., alias="hedgehogTier", examples=[4])
    energy: int = Field(..., alias="energy", examples=[400])
    kama_blessing_active: bool = Field(..., alias="kamaBlessingActive", examples=[True])
    villa_buff_active: bool = Field(..., alias="villaBuffActive", examples=[True])
    gather_taxed_milk: bool = Field(..., alias="gatherTaxedMilk", examples=[False])
    gather_craft_potion_usage: str = Field(
        ..., alias="gatherCraftPotionUsage", examples=["silverWithoutPots"]
    )
    mastery_tool_droprate: float = Field(
        ..., alias="masteryToolDroprate", examples=[0.3]
    )
    artifact_droprate: float = Field(..., alias="artifactDroprate", examples=[0])
    lifestone_droprate: float = Field(..., alias="lifestoneDroprate", examples=[0.1])
    fig_pie_active: bool = Field(..., alias="figPieActive", examples=[False])
    additional_droprate: float = Field(..., alias="additionalDroprate", examples=[0])
    speed_cooking_mastery: int = Field(
        ..., alias="speedCookingMastery", examples=[1000]
    )
    speed_cooking_time: float = Field(..., alias="speedCookingTime", examples=[1.2])
    slow_cooking_mastery: int = Field(..., alias="slowCookingMastery", examples=[1500])
    slow_cooking_time: float = Field(..., alias="slowCookingTime", examples=[4.1])
    cooking_byproduct_usage: int = Field(
        ..., alias="cookingByproductUsage", examples=[9065]
    )
    cooking_min_profit: int = Field(
        ..., alias="cookingMinProfit", examples=[-300000000]
    )
    cooking_max_profit: int = Field(..., alias="cookingMaxProfit", examples=[300000000])
    alchemy_mastery: int = Field(..., alias="alchemyMastery", examples=[1500])
    alchemy_time: float = Field(..., alias="alchemyTime", examples=[1.2])
    alchemy_byproduct_usage: int = Field(
        ..., alias="alchemyByproductUsage", examples=[5301], description="An item ID"
    )
    alchemy_min_profit: int = Field(
        ..., alias="alchemyMinProfit", examples=[-100000000]
    )
    alchemy_max_profit: int = Field(..., alias="alchemyMaxProfit", examples=[150000000])
    processing_mastery: int = Field(..., alias="processingMastery", examples=[1200])
    processing_success_rate: float = Field(
        ..., alias="processingSuccessRate", examples=[0.9]
    )
    processing_costume_active: bool = Field(
        ..., alias="processingCostumeActive", examples=[False]
    )
    processing_min_profit: int = Field(
        ..., alias="processingMinProfit", examples=[-50000000]
    )
    processing_max_profit: int = Field(
        ..., alias="processingMaxProfit", examples=[70000000]
    )

    @computed_field
    @property
    def tax_rate(self) -> float:
        return 0.65 + 0.65 * (
            (0.3 if self.value_pack_active else 0)
            + (0.05 if self.merchant_ring_active else 0)
            + self.family_fame_bonus
        )

    @computed_field
    @property
    def total_weight(self) -> int:
        return self.weight * (1 + self.feathery_steps_tier * 0.05) - self.used_weight

    @computed_field
    @property
    def additional_energy_regen(self) -> int:
        return (1 if self.villa_buff_active else 0) + (
            2 if self.kama_blessing_active else 0
        )

    @computed_field
    @property
    def total_drop_rate(self) -> float:
        return (
            self.mastery_tool_droprate
            + self.artifact_droprate
            + self.lifestone_droprate
            + self.additional_droprate
            + (0.03 if self.fig_pie_active else 0)
        )
