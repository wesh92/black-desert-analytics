from configs.recipes import recipes
from models.recipes import NormalProc, RareProc, Ingredient
from bdolytics import BDOlyticsMarketEndpoint


def recipe_reader(recipe_item_id: str = None, region: str = "na"):
    if isinstance(recipe_item_id, int):
        recipe_item_id = str(recipe_item_id)
    main_data = recipes[recipe_item_id]
    # if the normal proc dict is missing the "name" key, then enrich it with the item name
    if not main_data["normalProc"].get("name"):
        main_data["normalProc"]["name"] = (
            BDOlyticsMarketEndpoint(region=region)
            .fill__get_item_data_by_id(recipe_item_id)
            .name
        )
    normal_proc = NormalProc(**main_data["normalProc"])
    ingredients = []
    for ingredient in main_data["ingredients"]:
        # as long as the "type" key does not exist, enrich it with the item name
        if not ingredient.get("type"):
            ingredient["name"] = (
                BDOlyticsMarketEndpoint(region=region)
                .fill__get_item_data_by_id(ingredient["id"])
                .name
            )
        ingredients.append(Ingredient(**ingredient))
    if main_data.get("rareProc"):
        main_data["rareProc"]["name"] = (
            BDOlyticsMarketEndpoint(region=region)
            .fill__get_item_data_by_id(main_data["rareProc"]["id"])
            .name
        )
        rare_proc = RareProc(**main_data["rareProc"])
        return {"normal_proc": normal_proc, "rare_proc": rare_proc, "ingredients": ingredients}
    return {"normal_proc": normal_proc, "ingredients": ingredients}


print(recipe_reader(9201))
