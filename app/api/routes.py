from fastapi import APIRouter, Request
import httpx

router = APIRouter()
@router.post("/proxy")
async def proxy_gateway(request: Request):
    target_url = "https://webhook.site/your-unique-id-here"
    payload = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(target_url, json=payload)
    return response.json()
