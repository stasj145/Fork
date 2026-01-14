"""Main api router"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fork_backend.api.routes.login_endpoint import router as login_router
from fork_backend.api.routes.user_endpoint import router as user_router
from fork_backend.api.routes.food_endpoint import router as food_router
from fork_backend.api.routes.food_log_endpoint import router as food_log_router
from fork_backend.api.routes.activity_endpoint import router as activity_router
from fork_backend.api.routes.activity_log_endpoint import router as activity_log_router
from fork_backend.core.init.compute_embeddings import import_food
from fork_backend.core.init.import_activities import import_exercise_activities


async def run_import_in_background():
    """Run the import process in the background after a short delay"""
    # Give the server a moment to start
    await asyncio.sleep(1)
    await import_food()
    await import_exercise_activities()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the import process in the background """
    asyncio.create_task(run_import_in_background())
    yield

app = FastAPI(title="Fork_backend API", lifespan=lifespan)

V1_PREFIX = "/api/v1"
app.include_router(login_router, prefix=V1_PREFIX)
app.include_router(user_router, prefix=V1_PREFIX)
app.include_router(food_router, prefix=V1_PREFIX)
app.include_router(food_log_router, prefix=V1_PREFIX)
app.include_router(activity_router, prefix=V1_PREFIX)
app.include_router(activity_log_router, prefix=V1_PREFIX)

@app.get("/")
def read_root():
    """Base root response."""
    return {"message": "Up."}
