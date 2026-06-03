from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.core.config import settings
import httpx

router = APIRouter()

@router.post("/proxy")
async def proxy_gateway(request: Request):
    target_url = settings.TARGET_VENDOR_URL
    payload = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(target_url, json=payload)
    if response.status_code == 400:
        # TODO: Tyson payload details ha pathuko 
    
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "detail": "Vendor schema mismatch detected.",
                "status": "healing_in_progress",
                "vendor_response": response.json()
            }
        )
    return response.json() # return if my status is clear(200)


