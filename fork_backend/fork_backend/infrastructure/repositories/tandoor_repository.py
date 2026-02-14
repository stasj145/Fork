"""Repository for interacting with Tandoor food and recipe data"""

from typing import List, Dict, Any

from fork_backend.core.constants import FOOD_ID_PLACEHOLDER
from fork_backend.core.logging import get_logger
from fork_backend.infrastructure.api_clients.tandoor_api_client import TandoorAPIClient
from fork_backend.models.food_item import FoodItem

log = get_logger()


class TandoorRepository:
    """Repository for Tandoor food and recipe data operations"""

    def __init__(self, api_client: TandoorAPIClient):
        """
        Initialize the Tandoor repository.

        :param api_client: Instance of TandoorAPIClient
        """
        self.api_client = api_client

    async def search_recipes(self, query: str, user_id: str, limit: int = 20) -> List[FoodItem]:
        """
        Search for recipes in Tandoor and convert them to FoodItem models.

        :param query: Search query string
        :param user_id: ID of the user performing the search
        :param limit: Maximum number of results to return
        :return: List of FoodItem objects representing recipes
        """
        try:
            results = await self.api_client.search_recipes(query, limit)
            recipe_items = []

            for item in results:
                recipe_item = await self._recipe_item_from_tandoor_response(item, user_id)
                recipe_items.append(recipe_item)

            log.debug("Found {len(recipe_items)} recipes for query: %s", query)
            return recipe_items
        except Exception as e:
            log.error("Error searching recipes in Tandoor repository: %s", str(e))
            raise

    async def _recipe_item_from_tandoor_response(self, response: Dict[str, Any], user_id: str
                                                 ) -> FoodItem:
        """
        Convert a Tandoor API response for a recipe to a FoodItem model.

        :param response: Tandoor API response for a recipe
        :param user_id: ID of the user performing the search
        :return: FoodItem object representing the recipe
        """
        # basic information
        tandoor_id = int(response.get("id"))
        name = str(response.get("name", ""))
        description = str(response.get("description", "")) or ""
        servings = str(response.get("servings", ""))
        servings_text = str(response.get("servings_text", ""))[:19]

        working_time = response.get("working_time", 0)
        waiting_time = response.get("waiting_time", 0)

        # Build description
        if working_time or waiting_time:
            time_info = []
            if working_time:
                time_info.append(f"Prep time: {working_time} min")
            if waiting_time:
                time_info.append(f"Wait time: {waiting_time} min")
            time_description = ", ".join(time_info)
            if description:
                description = f"{description} ({time_description})"
            else:
                description = time_description

            description += f", Source: {self.api_client.base_url}recipe/{str(tandoor_id)}"

        new_recipe_item = FoodItem(
            id=FOOD_ID_PLACEHOLDER,
            user_id=user_id,
            private=False,
            hidden=False,
            name=name,
            brand="Tandoor Recipes",
            description=description,
            barcode=None,
            serving_size=servings,
            serving_unit=servings_text,
            calories_per_100=0,
            protein_per_100=0,
            carbs_per_100=0,
            fat_per_100=0,
        )

        # Set external image URL if available
        image_url = None
        if 'image' in response and response['image']:
            image_url = response['image']

        if image_url:
            new_recipe_item.external_image_url = image_url

        await self._get_recipe_nutrition(recipie_id=tandoor_id, food_item=new_recipe_item)
        return new_recipe_item

    async def _get_recipe_nutrition(self, recipie_id: int, food_item: FoodItem) -> FoodItem:
        """
        Get detailed information about a specific recipie

        :param recipie_id: Tandoor id of the recipie
        :param food_item: The FoodItem model to update with the nutrition info
        :return: Updated FoodItem Model including nutrition information.
        """
        try:
            result = await self.api_client.get_recipe_details(recipie_id)

            nutrition_info: dict = result.get("food_properties", {})
            steps: list = result.get("steps", [])
            servings: int = int(result.get("servings", 1))

            total_carbs = 0
            total_calories = 0
            total_fat = 0
            total_protein = 0

            for item in nutrition_info.values():
                name = item.get("name", "")
                value = item.get("total_value", 0)
                if name == "Carbohydrates":
                    total_carbs = value
                elif name == "Proteins":
                    total_protein = value
                elif name == "Calories":
                    total_calories = value
                elif name == "Fat":
                    total_fat = value

            total_weight = 0

            for step in steps:
                ingredients = step.get("ingredients", [])
                for ingredient in ingredients:
                    unit_dict: dict | None = ingredient.get("unit", None)
                    unit_name: str = unit_dict.get(
                        "name", "") if unit_dict else ""
                    if unit_dict and (unit_name == "g" or unit_name == "ml"):
                        total_weight += ingredient.get("amount", 0)
                    elif ingredient.get("conversions", None):
                        for conversion in ingredient.get("conversions", []):
                            if conversion.get("unit", "") == "g":
                                total_weight += conversion.get("amount", 0)

            food_item.calories_per_100 = total_calories/total_weight * 100
            food_item.carbs_per_100 = total_carbs/total_weight * 100
            food_item.fat_per_100 = total_fat/total_weight * 100
            food_item.protein_per_100 = total_protein/total_weight * 100

            food_item.serving_size = round(total_weight/servings, 0)

            return food_item
        except Exception as e:
            log.error(
                "Error updating recipe nutrition info in Tandoor repository: %s", str(e))
            raise e

    async def close(self):
        """Close the underlying API client connection"""
        await self.api_client.close()
