import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from app.api.routes import router as api_router
from app.services.worker import start_queue_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI application."""
    worker_task = asyncio.create_task(start_queue_consumer())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass    

app = FastAPI(
    title="MorphicAPI Self-Healing Gateway Engine",
    lifespan=lifespan
)    

app.include_router(api_router, prefix="/api")

@app.get('/')
def testing():
    return {"status": "working"}