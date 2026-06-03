import httpx
from fastapi import FastAPI, APIRouter, Request
from app.api import routes

app1 = FastAPI()
router = APIRouter()
# app.include_router(#)
@app1.get('/')
def testing():
    return {"status" : "working"}