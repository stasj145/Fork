"""food management endpoints"""

from uuid import uuid4

from fastapi import APIRouter, status, Depends, HTTPException

from fork_backend.core.logging import get_logger
from fork_backend.api.dependencies import get_current_user
from fork_backend.services.food_service import FoodService
from fork_backend.api.schemas.food_schema import (FoodDetailed, FoodCreate, FoodUpdate, FoodSearch)
from fork_backend.models.food_item import FoodItem, FoodItemIngredient
from fork_backend.models.user import User

log = get_logger()
router = APIRouter(prefix="/food", tags=["Food"])

def verify_ownership(action: str, user: User, food_item: FoodItem, allow_edit_public: bool = True,
                     allow_delete_public: bool = False) -> bool:
    """
    Verify if the user has the right to access a FoodItem

    :param action: The action the user is trying to perform. "access", "edit" or "delete"
    :param user: The currently logged in user.
    :param food_item: The food_item they are trying to access.
    :param allow_edit_public: Wether or not users are allowed to edit non-private food-items they
        did not create themselves. Defaults to true.
    :param allow_delete_public: Wether or not users are allowed to delete non-private food-items
        they did not create themselves. Defaults to false.

    :param: True if user is allowed to access/edit/delete.
    """
    if action == "edit" and (
        user.id == food_item.user_id or (not food_item.private and allow_edit_public)):
        return True
    if action == "delete" and (
        user.id == food_item.user_id or (not food_item.private and allow_delete_public)):
        return True
    if action == "access" and (
        not food_item.private or (user.id == food_item.user_id)):
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to access. Worng user.",
    )

# --- Endpoints ---

@router.post("/", response_model=FoodDetailed, status_code=status.HTTP_201_CREATED)
async def create_food(food_info: FoodCreate, user: User = Depends(get_current_user)):
    """
    Create a new food item.
    """
    service = FoodService()

    try:
        food_item = FoodItem(id=str(uuid4()), user_id = user.id, **food_info.model_dump(exclude=["ingredients"]))
        food_item.ingredients = [FoodItemIngredient(parent_id=food_item.id, ingredient_id=ingredient.ingredient_id, quantity=ingredient.quantity) for ingredient in food_info.ingredients]
        new_food_item: FoodItem = await service.add_food_item(food_item)
        return FoodDetailed.model_validate(new_food_item)
    except Exception as e:
        log.error("Failed to create new FoodItem: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create FoodItem: {str(e)}",
        ) from e


@router.patch("/{food_id}", response_model=FoodDetailed, status_code=status.HTTP_200_OK)
async def update_food(food_id: str, food_info: FoodUpdate,
                      current_user: User = Depends(get_current_user)) -> FoodDetailed:
    """
    Update a specific user by ID.
    """

    print(food_info)

    try:
        service = FoodService()

        food_to_update = await service.get_food_item_by_id(food_id)

        if not verify_ownership(action="edit", user=current_user, food_item=food_to_update):
            return None

        # construct new FoodItem
        for k, v in vars(food_info).items():
            print(k, v)
            if v is None:
                setattr(food_info, k, getattr(food_to_update, k))
        
        print("reached")

        new_food_item: FoodItem = FoodItem(
            id=food_id,
            user_id=food_to_update.user_id,
            embedding=food_to_update.embedding,
            ingredients=[FoodItemIngredient(parent_id=food_id, ingredient_id=ingredient.ingredient_id, quantity=ingredient.quantity) for ingredient in food_info.ingredients],
            **food_info.model_dump(exclude=["ingredients"])
        )

        print(new_food_item.__dict__)

        updated_food_item = await service.update_food_item(new_food_item)

        log.debug("Updated info for food with id '%s'", food_id)
        return FoodDetailed.model_validate(updated_food_item)
    except Exception as e:
        log.error("Failed to update food with id '%s': %s", food_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to updated food: {str(e)}",
        ) from e


@router.get("/{food_id}", response_model=FoodDetailed, status_code=status.HTTP_200_OK)
async def get_food_item(food_id: str, current_user: User = Depends(get_current_user)) -> FoodDetailed:
    """
    Get a specific food item by ID.
    """
    try:
        service = FoodService()
        food_item = await service.get_food_item_by_id(food_id)

        if not verify_ownership(action="access", user=current_user, food_item=food_item):
            return None

        return FoodDetailed.model_validate(food_item)
    except Exception as e:
        log.error("Failed to get FoodItem with id '%s': %s", food_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to find requested FoodItem: {str(e)}",
        ) from e

@router.post("/search", response_model=list[FoodDetailed], status_code=status.HTTP_200_OK)
async def search_food(query: FoodSearch, user: User = Depends(get_current_user)):
    """
    Create a new food item.
    """
    service = FoodService()

    try:
        food_items: list[FoodItem] = await service.search_food_items(
            query=query.query,
            code=query.code,
            source=query.source,
            limit=query.limit,
            user_id=user.id
            )
        return [FoodDetailed.model_validate(food_item) for food_item in food_items]
    except Exception as e:
        log.error("Failed to search for FoodItems: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to search FoodItems: {str(e)}",
        ) from e


@router.delete("/{food_id}", status_code=status.HTTP_200_OK)
async def delete_food(food_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a specific food item by ID.
    """
    try:
        service = FoodService()
        food_item = await service.get_food_item_by_id(food_id)

        if not food_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found",
            )

        if not verify_ownership(action="delete", user=current_user, food_item=food_item):
            return None

        success = await service.delete_food_item(food_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food item not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        log.error("Failed to delete FoodItem with id '%s': %s", food_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to delete food item: {str(e)}",
        ) from e
