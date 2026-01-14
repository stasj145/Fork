"""Script to import exercise activities from CSV file"""

import csv
import asyncio

from fork_backend.models.system import System
from fork_backend.models.activities import Activities
from fork_backend.core.db import get_sync_db
from fork_backend.services.activity_service import ActivityService

async def import_activities_from_csv(csv_file: str, batch_size: int = 100):
    """Import activities from CSV file into the database"""
    
    service = ActivityService()
    imported_count = 0
    skipped_count = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for i, row in enumerate(reader):
            try:
                activity_name_imperial = row[0]
                activity_name_metric = row[6]
                # The "Calories per kg" has seemingly gone through multiple round of unintelligible
                # conversions. To get the actual value we need to convert from kg to pound twice.
                calories_per_kg = float(row[5]) * 2.20462 * 2.20462
                
                # Create activity object with admin user
                activity_data = {
                    'user_id': "admin",
                    'name': activity_name_metric,
                    'calories_burned_kg_h': calories_per_kg
                }
                
                activity = Activities(**activity_data)
                await service.add_activity(activity)
                imported_count += 1
                
                # Yield control back to the event loop periodically
                if imported_count % 100 == 0:
                    await asyncio.sleep(0)
                
                if imported_count % batch_size == 0:
                    print(f"Imported {imported_count} activities... (skipped {skipped_count})")
                    
            except Exception as e:
                print(f"Error importing row {i}: {row[0] if row else 'unknown'} - {str(e)}")
                skipped_count += 1
                continue
    
    print(f"\n{'='*60}")
    print("Import complete!")
    print(f"Successfully imported: {imported_count}")
    print(f"Skipped (errors): {skipped_count}")
    print(f"{'='*60}")


async def import_exercise_activities():
    """Import exercise activities in an async context"""
    with get_sync_db() as session:
        system = session.query(System).first()
        if system.exercise_import_finished:
            print("Import of exercise activities already done. Skipping")
            return
        
        print("Starting import of exercise activities")
        system.exercise_import_started = True
        session.commit()
    
    await import_activities_from_csv('data/exercise_dataset_metric.csv', batch_size=1000)
    
    with get_sync_db() as session:
        system = session.query(System).first()
        system.exercise_import_finished = True
        session.commit()
        print("Import finished")
