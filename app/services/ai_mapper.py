import logging
import json
from google import genai
from google.genai import types
from app.schemas.vendor import VendorPayloadValidation
logging.basicConfig(level=logging.INFO)

client = genai.Client()

async def heal_payload_with_ai(original_payload: dict,error_details:dict):
    logging.info("Initiating live Gemini payload auto-healing...")
    
    prompt = f"""
You are an automated API middleware data transformer. Your sole job is to repair broken API payloads based on vendor error messages.
Analyze the original data and the vendor error message to produce a fixed JSON payload matching what the vendor expects.
Original Broken Payload sent by user:
{json.dumps(original_payload, indent=2)}
Target Schema Blueprint:
{json.dumps(VendorPayloadValidation.model_json_schema(), indent=2)}
Vendor Error Message received:
{json.dumps(error_details, indent=2)}
"""
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            ),
        )
        healed_data = json.loads(response.text)
        return healed_data
    
    except Exception as e:
        logging.error(f"Failed to auto_heal payload with Gemini: {str(e)}")
        raise e


