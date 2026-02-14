"""Service class to manipulate food items"""

from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor  # pylint: disable=no-name-in-module

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from sentence_transformers import SentenceTransformer
import openfoodfacts

from fork_backend.core.constants import OPENFOODFACTS_USER_AGENT
from fork_backend.core.db import get_async_db
from fork_backend.core.logging import get_logger
from fork_backend.models.food_item import FoodItem, FoodItemIngredient
from fork_backend.models.food_sources import Sources
from fork_backend.models.food_log import FoodLog
from fork_backend.models.food_entry import FoodEntry
from fork_backend.services.image_service import ImageService

log = get_logger()

print("Loading embedding model...")
EMBEDDING_MODEL = SentenceTransformer('intfloat/multilingual-e5-small')
print("Model loaded")

# Thread pool for CPU-bound encoding operations
ENCODER_POOL = ThreadPoolExecutor(max_workers=4)


class FoodService:
    """Service class for management of Food"""

    def __init__(self) -> None:
        """"""

    @staticmethod
    def _encode_sync(text: str) -> list:
        """Synchronous encoding function to run in thread pool"""
        return EMBEDDING_MODEL.encode(text).tolist()

    @staticmethod
    async def _encode_async(text: str) -> list:
        """
        Async wrapper for encoding using thread pool.
        Prevents blocking the event loop.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            ENCODER_POOL,
            FoodService._encode_sync,
            text
        )

    @staticmethod
    async def _generate_embeddings(food_item: FoodItem) -> list:
        """
        Generate embeddings for a food item asynchronously.

        :return: name_embedding
        """

        name_emb = await FoodService._encode_async(food_item.name)

        return name_emb

    async def add_food_item(self, food_item: FoodItem) -> FoodItem:
        """
        Adds a new food item to the database with embeddings.

        :param food_item: The new item to add.
        :return: The created FoodItem with embeddings.
        """
        try:
            # Generate embeddings asynchronously
            name_emb = await self._generate_embeddings(food_item)
            food_item.embedding = name_emb

            async with get_async_db() as db:

                db.add(food_item)

                # add ingredients
                if len(food_item.ingredients) > 0:
                    for item in food_item.ingredients:
                        db.add(item)
                    log.debug("added ingredients for food item: %s",
                              food_item.name)

                await db.commit()
                log.debug("New food item added with embeddings: %s",
                          food_item.name)
                return await self.get_food_item_by_id(food_item.id)

        except Exception as e:
            log.error("Failed to add food_item from user '%s': %s",
                      food_item.user_id, e)
            raise e

    async def update_food_item(self, food_item: FoodItem) -> FoodItem | None:
        """
        Update an existing food item's information.
        Regenerates embeddings if searchable fields changed.

        :param food_item: The food item to update.
        :return: The updated FoodItem.
        """
        try:
            async with get_async_db() as db:
                # Get original to check if searchable fields changed
                result = await db.execute(
                    select(FoodItem).filter(FoodItem.id == food_item.id).options(
                        selectinload(FoodItem.ingredients).selectinload(
                            FoodItemIngredient.ingredient))
                )

                original = result.scalar_one_or_none()

                if not original:
                    log.error("Unable to find requested foodItem")
                    return None

                # Check if searchable fields changed
                needs_reembedding = (
                    original.name != food_item.name
                )

                if needs_reembedding:
                    name_emb = await self._generate_embeddings(food_item)
                    food_item.embedding = name_emb
                    log.debug(
                        "Regenerated embeddings for food item: %s", food_item.name)

                # Check if ingredients have actually changed before updating them
                if self._have_ingredients_changed(original.ingredients, food_item.ingredients):
                    # Clear existing ingredients and add new ones
                    original.ingredients.clear()

                    for item in food_item.ingredients:
                        new_ingredient = FoodItemIngredient(
                            parent_id=food_item.id,
                            ingredient_id=item.ingredient_id,
                            quantity=item.quantity
                        )
                        original.ingredients.append(new_ingredient)
                    log.debug("Updated ingredients for food item: %s",
                              food_item.name)
                elif len(food_item.ingredients) > 0:
                    log.debug(
                        "Ingredients unchanged for food item: %s", food_item.name)

                updated_food_item = await db.merge(food_item)
                await db.commit()

                log.debug("Updated FoodItem with id '%s'", food_item.id)
                return await self.get_food_item_by_id(updated_food_item.id)

        except Exception as e:
            log.error("Failed to update food_item with id '%s': %s",
                      food_item.id, e)
            raise e

    @staticmethod
    def _have_ingredients_changed(original_ingredients: list[FoodItemIngredient],
                                  new_ingredients: list[FoodItemIngredient]) -> bool:
        """
        Check if the ingredients have actually changed between the original and new lists.

        :param original_ingredients: The original list of ingredients
        :param new_ingredients: The new list of ingredients
        :return: True if ingredients have changed, False otherwise
        """
        # If lengths are different, ingredients have definitely changed
        if len(original_ingredients) != len(new_ingredients):
            return True

        # Create dictionaries for easier comparison
        # Key: (ingredient_id, quantity)
        original_dict = {(ing.ingredient_id, ing.quantity)
                         for ing in original_ingredients}
        new_dict = {(ing.ingredient_id, ing.quantity)
                    for ing in new_ingredients}

        # Compare the sets
        return original_dict != new_dict

    async def get_food_item_by_id(self, food_item_id: str) -> FoodItem | None:
        """
        Get a FoodItem given its db id.

        :param food_item_id: The id of the food item to get.
        :return: An instance of the FoodItem.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(FoodItem).filter(FoodItem.id == food_item_id).options(
                        selectinload(FoodItem.ingredients),
                        selectinload(FoodItem.ingredients).selectinload(
                            FoodItemIngredient.ingredient))
                )
                food_item = result.scalar_one_or_none()
                return food_item

        except Exception as e:
            log.error("Failed to get food_item with id '%s': %s",
                      food_item_id, e)
            raise e

    async def search_food_items(
        self,
        user_id: str,
        query: Optional[str] = None,
        code: Optional[str] = None,
        source: Sources = Sources.LOCAL,
        limit: int = 20,
        min_similarity: float = 0.3,
    ) -> list[FoodItem]:
        """
        Search for food items based on query text, barcode, or both, with various filtering options.

        :param user_id: The ID of the user performing the search. Used for privacy filtering.
        :type user_id: str
        :param query: Text query for semantic search. Cannot be used with 'code' parameter.
        :type query: Optional[str]
        :param code: Barcode to search for exact matches. Cannot be used with 'query' parameter.
        :type code: Optional[str]
        :param source: Source to search in (LOCAL or OPENFOODFACTS). Defaults to LOCAL.
        :type source: Sources, optional
        :param limit: Maximum number of results to return. Defaults to 20.
        :type limit: int, optional
        :param min_similarity: Minimum similarity threshold for semantic search (0.0 to 1.0).
                              Only applies to local semantic searches. Defaults to 0.3.
        :type min_similarity: float, optional
        :return: List of FoodItem objects matching the search criteria.
        :rtype: list[FoodItem]
        :raises ValueError: If both 'query' and 'code' parameters are provided.
        :raises Exception: If there's an error during the search process.

        **Search Behavior:**
        - If 'query' is provided, performs semantic search in the specified source
        - If 'code' is provided, performs exact barcode match (first in local DB, then OpenFoodFacts)
        - If neither 'query' nor 'code' is provided, returns empty list
        - Cannot use both 'query' and 'code' simultaneously

        **Privacy Filtering:**
        - For LOCAL searches: 
          * When private_only=True: Only returns private items owned by the user
          * When private_only=False: Returns public items and user's private items
        - For OPENFOODFACTS searches: No privacy filtering (external source)
        """
        if not query and not code:
            return []

        if query and code:
            err_msg = ("Cannot search with both query and code parameters provided at the same " +
                       "time. Please only provide one.")
            log.error(err_msg)
            raise ValueError(err_msg)

        if source == Sources.LOCAL or source == Sources.PERSONAL and query:
            return await self.semantic_search_food_items_local(
                query=query,
                user_id=user_id,
                limit=limit,
                private_only = True if source == Sources.PERSONAL else False,
                min_similarity=min_similarity)
        if source == Sources.OPENFOODFACTS and query:
            return await self.semantic_search_food_items_open_food_facts(
                query=query,
                user_id=user_id,
                limit=limit,
            )
        if code:
            ret_val = await self.code_search_food_items_local(
                code=code,
                user_id=user_id,
            )
            if len(ret_val) == 0:
                ret_val = await self.code_search_food_items_open_food_facts(
                    code=code,
                    user_id=user_id,
                )
            return ret_val

    async def code_search_food_items_local(
        self,
        code: str,
        user_id: str,
        include_private: bool = True,
    ) -> list[FoodItem]:
        """
        Search for food items in the local db using barcode.
        """
        try:
            async with get_async_db() as db:

                # pylint: disable=singleton-comparison
                if include_private:
                    stmt = select(FoodItem).where(
                        and_(
                            or_(
                                FoodItem.private == False,
                                FoodItem.user_id == user_id
                            ),
                            FoodItem.barcode == code
                        )
                    )
                else:
                    stmt = select(FoodItem).where(
                        and_(
                            FoodItem.private == False,
                            FoodItem.barcode == code
                        )
                    )

                stmt = stmt.options(
                    selectinload(FoodItem.ingredients).selectinload(
                        FoodItemIngredient.ingredient))

                # Since barcodes are unique, there should only be one result
                stmt = stmt.limit(1)

                result = await db.execute(stmt)
                row = result.first()

                if row:
                    return [row.FoodItem]
                return []

        except Exception as e:
            log.error(
                "Failed to search food items with code '%s' in local db: %s", code, e)
            raise e

    async def code_search_food_items_open_food_facts(
        self,
        code: str,
        user_id: str,
    ) -> list[FoodItem]:
        """
        Search for food items in OpenFoodFacts using barcode.
        """
        try:
            api = openfoodfacts.API(user_agent=OPENFOODFACTS_USER_AGENT, timeout=30)
            response = api.product.get(code=code)
            if not response:
                return []

            new_food_item = await self._food_item_from_open_food_facts_response(
                response=response,
                user_id=user_id
            )
            return [new_food_item]

        except Exception as e:
            log.error(
                "Failed to search food items with code '%s' in open food facts: %s", code, e)
            raise e
        return []

    async def semantic_search_food_items_open_food_facts(
        self,
        query: str,
        user_id: str,
        limit: int = 20,
    ) -> list[FoodItem]:
        """
        Search for food items in OpenFoodFacts using barcode.
        """
        try:
            api = openfoodfacts.API(
                user_agent=OPENFOODFACTS_USER_AGENT, timeout=30)
            response = api.product.text_search(
                query=query,
                page=1,
                page_size=limit)
            if not response:
                return []

            new_food_items = [await self._food_item_from_open_food_facts_response(
                response=response_item,
                user_id=user_id
            ) for response_item in response.get('products', [])
            ]
            return new_food_items

        except Exception as e:
            log.error(
                "Failed to search food items with query '%s' in open food facts: %s", query, e)
            raise e
        return []

    async def _food_item_from_open_food_facts_response(self, response: Dict[str, Any], user_id: str
                                                       ) -> FoodItem:
        new_food_item = FoodItem(
            id="PLACEHOLDER_ID_ITEM_NOT_IN_LOCAL_DB",
            user_id=user_id,
            private=False,
            hidden=False,
            name=str(response.get("product_name", "")),
            brand=str(response.get("brands", "")),
            description=", ".join([ing.get("text", "")
                                  for ing in response.get("ingredients", [])]),
            barcode=response.get("code", "0"),
            serving_size=response.get("serving_quantity", 0),
            serving_unit="serving",
            calories_per_100=response.get(
                "nutriments", {}).get("energy-kcal_100g", 0),
            protein_per_100=response.get(
                "nutriments", {}).get("proteins_100g", 0),
            carbs_per_100=response.get("nutriments", {}).get(
                "carbohydrates_100g", 0),
            fat_per_100=response.get("nutriments", {}).get("fat_100g", 0),
        )
        new_food_item.external_image_url = response.get("image_small_url", None)
        return new_food_item

    async def semantic_search_food_items_local(
        self,
        query: str,
        user_id: str,
        limit: int = 20,
        private_only: bool = False,
        min_similarity: float = 0.3,
    ) -> list[FoodItem]:
        """
        Semantic search for food items in the local db.
        """
        try:
            # Generate query embedding asynchronously
            query_embedding = await self._encode_async(query)

            async with get_async_db() as db:
                similarity = 1 - \
                    FoodItem.embedding.cosine_distance(query_embedding)

                # pylint: disable=singleton-comparison
                stmt = select(FoodItem, similarity.label('similarity')).where(
                    FoodItem.hidden == False).options(
                        selectinload(FoodItem.ingredients).selectinload(
                            FoodItemIngredient.ingredient))

                # pylint: disable=singleton-comparison
                if private_only:
                    stmt = stmt.where(
                        and_(
                            FoodItem.private == True,
                            FoodItem.user_id == user_id,
                            similarity >= min_similarity
                        )
                    )
                else:
                    stmt = stmt.where(
                        and_(
                            or_(
                                FoodItem.private == False,
                                FoodItem.user_id == user_id
                            ),
                            similarity >= min_similarity
                        )
                    )

                stmt = stmt.order_by(similarity.desc()).limit(limit)

                result = await db.execute(stmt)
                rows = result.all()

                log.debug("Search for '%s' returned %d results",
                          query, len(rows))
                return [row.FoodItem for row in rows]

        except Exception as e:
            log.error(
                "Failed to search food items for query '%s' in local db: %s", query, e)
            raise e

    async def search_by_barcode(
        self,
        barcode: str,
        user_id: str
    ) -> Optional[FoodItem]:
        """
        Search for a food item by barcode.

        :param barcode: The barcode to search for.
        :param user_id: Current user ID for privacy filtering.
        :return: FoodItem if found, None otherwise.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(FoodItem).where(
                        and_(
                            FoodItem.barcode == barcode,
                            or_(
                                FoodItem.private == False,
                                FoodItem.user_id == user_id
                            )
                        )
                    ).options(
                        selectinload(FoodItem.ingredients).selectinload(
                            FoodItemIngredient.ingredient))
                )
                food_item = result.scalar_one_or_none()

                if food_item:
                    log.debug("Found food item by barcode: %s", food_item.name)
                else:
                    log.debug("No food item found for barcode: %s", barcode)

                return food_item

        except Exception as e:
            log.error("Failed to search by barcode '%s': %s", barcode, e)
            raise e

    async def delete_food_item(self, food_item_id: str) -> bool:
        """
        Delete a food item from the database.

        :param food_item_id: The ID of the food item to delete.
        :return: True if deletion was successful, False if item was not found.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(FoodItem).filter(FoodItem.id == food_item_id)
                )
                food_item = result.scalar_one_or_none()

                if not food_item:
                    log.warning(
                        "Unable to find food item with id '%s' for deletion", food_item_id)
                    return False
                
                if food_item.img_name:
                    image_service = ImageService()
                    await image_service.delete(food_item.img_name)

                await db.delete(food_item)
                await db.commit()
                log.debug("Deleted FoodItem with id '%s'", food_item_id)
                return True

        except Exception as e:
            log.error("Failed to delete food_item with id '%s': %s",
                      food_item_id, e)
            raise e

    async def get_last_logged(self, n_items: int, user_id: str) -> list[FoodItem]:
        """
        Docstring for get_last_logged
        
        :param n_items: Max number of food items to return
        :type n_items: int
        :param user_id: Id of user for which to get the items
        :type user_id: str
        :return: Deduplicated list of last logged food items with max lenght n_items
        :rtype: list[FoodItem]
        """

        try:
            async with get_async_db() as db:

                last_eaten_subquery = (
                    select(
                        FoodEntry.food_id.label("f_id"),
                        func.max(FoodLog.date).label("max_date")
                    )
                    .join(FoodLog)
                    .filter(FoodLog.user_id == user_id)
                    .group_by(FoodEntry.food_id)
                    .subquery()
                )

                stmt = (select(FoodItem)
                        .join(last_eaten_subquery, FoodItem.id == last_eaten_subquery.c.f_id)
                        .order_by(desc(last_eaten_subquery.c.max_date))
                        .limit(n_items)
                        .options(
                            selectinload(FoodItem.ingredients)
                            .selectinload(FoodItemIngredient.ingredient)))


                results = await db.execute(stmt)

                food_items = results.scalars().all()

                return food_items

        except Exception as e:
            log.error("Failed to load last %s food_items from user with id '%s': %s",
                    n_items, user_id, e)
            raise e

        return []
