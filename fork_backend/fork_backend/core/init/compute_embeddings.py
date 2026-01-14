"""Script to import the opennutrition database"""

import csv
import json
import asyncio

from fork_backend.models.system import System
from fork_backend.models.food_item import FoodItem
from fork_backend.core.db import get_sync_db
from fork_backend.services.food_service import FoodService

TYPES_TO_KEEP = ["everyday"]


def parse_nutrition_100g(nutrition_str: str) -> dict[str, float]:
    """Parse the nutrition_100g JSON string and extract key nutrients"""
    if not nutrition_str:
        return {
            'calories_per_100': 0,
            'protein_per_100': 0,
            'carbs_per_100': 0,
            'fat_per_100': 0,
        }

    try:
        nutrition = json.loads(nutrition_str)

        return {
            'calories_per_100': float(nutrition.get('calories', 0)),
            'protein_per_100': float(nutrition.get('protein', 0)),
            'carbs_per_100': float(nutrition.get('carbohydrates', 0)),
            'fat_per_100': float(nutrition.get('total_fat', 0)),
        }
    except (json.JSONDecodeError, ValueError, TypeError):
        return {
            'calories_per_100': 0,
            'protein_per_100': 0,
            'carbs_per_100': 0,
            'fat_per_100': 0,
        }


def parse_serving_size(serving_str: str) -> tuple[float | None, str]:
    """
    Parse the serving JSON string and extract metric serving size
    Returns: (serving_size, unit)
    """
    if not serving_str:
        return None, 'g'

    try:
        serving = json.loads(serving_str)

        # Try to get metric serving first
        if 'metric' in serving and serving['metric']:
            metric = serving['metric']
            quantity = float(metric.get('quantity', 0))
            unit = metric.get('unit', 'g')

            return quantity, unit

        # Fallback to common serving
        if 'common' in serving and serving['common']:
            common = serving['common']
            unit = common.get('unit', 'serving')
            quantity = float(common.get('unit', 'N/A'))
            return quantity, unit

        return None, 'g'

    except (json.JSONDecodeError, ValueError, TypeError, KeyError):
        return None, 'g'


def parse_alternate_names(alternate_names_str: str) -> str | None:
    """Parse alternate names array and join them"""
    if not alternate_names_str:
        return None

    try:
        names = json.loads(alternate_names_str)
        if isinstance(names, list) and names:
            return ', '.join(names)
        return None
    except (json.JSONDecodeError, TypeError):
        return None


async def import_tsv(tsv_file: str, batch_size: int = 100):
    """Import TSV into existing FoodItem model"""

    service = FoodService()
    imported_count = 0
    skipped_count = 0

    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for i, row in enumerate(reader):
            try:
                food_type = row.get('type', 'na')
                if food_type not in TYPES_TO_KEEP:
                    continue
                nutrition = parse_nutrition_100g(row.get('nutrition_100g', ''))

                serving_size, serving_unit = parse_serving_size(row.get('serving', ''))

                #alternate_names = parse_alternate_names(row.get('alternate_names', ''))

                description = ""
                if row.get('description'):
                    description = row['description']

                food_data = {
                    'user_id': "admin",
                    'private': False,
                    'name': row['name'],
                    'brand': 'OpenNutrition Foods',
                    'description': description,

                    # Serving information
                    'serving_size': serving_size,
                    'serving_unit': "Serving",

                    # Nutrition per 100g
                    **nutrition
                }

                food_item = FoodItem(**food_data)
                await service.add_food_item(food_item)
                imported_count += 1

                # Yield control back to the event loop periodically
                if imported_count % 100 == 0:
                    await asyncio.sleep(0)

                if imported_count % batch_size == 0:
                    print(f"Imported {imported_count} items... (skipped {skipped_count})")

            except Exception as e:
                print(f"Error importing row {i}: {row.get('name', 'unknown')} - {str(e)}")
                skipped_count += 1
                continue

    print(f"\n{'='*60}")
    print("Import complete!")
    print(f"Successfully imported: {imported_count}")
    print(f"Skipped (errors): {skipped_count}")
    print(f"{'='*60}")


async def import_food():
    """Import food data in an async context"""
    with get_sync_db() as session:
        system = session.query(System).first()
        if system.open_nutrition_data_import_finished:
            print("Import of openNutrition data already done. Skipping")
            return

        print("Starting import of openNutrition data")
        system.open_nutrition_data_import_started = True
        session.commit()
    
    await import_tsv('data/opennutrition_foods.tsv', batch_size=1000)
    
    with get_sync_db() as session:
        system = session.query(System).first()
        system.open_nutrition_data_import_finished = True
        session.commit()
        print("Import finished")
