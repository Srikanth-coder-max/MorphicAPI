import asyncio
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, APIRouter, Request
from app.api.routes import router as api_router
from app.services.worker import start_queue_consumer

<<<<<<< Updated upstream
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI application."""

    worker_task=asyncio.create_task(start_queue_consumer())
    yield

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass    

app=FastAPI(
    title="MorphicAPI Self-Healing Gateway Engine",
    lifespan=lifespan
)    

app.include_router(api_router,prefix="/api")


@app.get('/')
=======

app1 = FastAPI()
router = APIRouter()
# app.include_router(#)
@app1.get('/')
>>>>>>> Stashed changes
def testing():
    return {"status" : "working"}