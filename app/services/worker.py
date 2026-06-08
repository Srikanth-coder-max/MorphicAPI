import asyncio
import os,json
import logging
import httpx
from pydantic import ValidationError
from app.schemas.vendor import VendorPayloadValidation
from app.services.queue_manager import get_from_queue, acknowldge_task
from app.services.ai_mapper import heal_payload_with_ai
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

#DLQ (In memory Dead Letter Queue)
DLQ_FILE_PATH="dead_letter_queue.json"

def save_to_persistent_dlq(packet:dict):
    """
    Safely reads and appends the error payload to guarantee the data persistence. 
    """
    dlq_data=[]

    if os.path.exists(DLQ_FILE_PATH):
        try:
            with open(DLQ_FILE_PATH,"r") as file:
                dlq_data=json.load(file)
                if not isinstance(dlq_data,list):
                    dlq_data=[]
        except (json.JSONDecodeError,IOError):
            logging.error(f"Failed to read existing file data at {DLQ_FILE_PATH}")
            dlq_data=[]
    dlq_data.append(packet)        

    try:
        with open(DLQ_FILE_PATH,"w") as file:
            json.dump(dlq_data,file,indent=2)
    except IOError as e:
        logging.critical(f"Critical: Failed to write to disk storage at {DLQ_FILE_PATH}:{e}")


async def start_queue_consumer():
    """
    inifinte background loop to process failed request items from the queue 
    """
    logging.info("AI Consumer Worker started and watching failed requests...")

    while True:
        try:
            #non-blocking fetch
            item=await get_from_queue()
            original_payload = item["original_payload"]
            error_details = item["error_details"]
            #acknowledgment and logging
            logging.info("WORKER ACTIVATED")
            logging.info(f"Processing payload: {original_payload}")
            logging.info(f"Analyzing error: {error_details['message']}")

            healed_payload = await heal_payload_with_ai(original_payload, error_details)
            logging.info(f"Healed payload: {healed_payload}")

            #pydantic validation gate
            try:
                VendorPayloadValidation(**healed_payload)
            except ValidationError as val_error:

                dlq_packet={
                    "attempted_payload":healed_payload,
                    "vendor_final_rejection":f"Schema Validation Failure: {val_error.errors()}",
                    "status_code":422
                }    
                save_to_persistent_dlq(dlq_packet)

                continue
            
            #retry engine
            target_url=settings.TARGET_VENDOR_URL
            logging.info(f"Executing Retry Engine delivery to: {target_url}")

            async with httpx.AsyncClient() as client:
                vendor_response=await client.post(target_url, json=healed_payload)

                #The safety valve(DLQ)
                if vendor_response.status_code==200:
                    logging.info("SUccess: Vendor accepted the AI-Healed Payload!")
                    logging.info(f"Vendor Response: {vendor_response.json()}")
                else:
                    logging.info(f"Retry Failed with status {vendor_response.status_code}")
                    logging.info(f"Vendor final Rejection details: {vendor_response.text}")   

                    dlq_packet={
                        "attempted_payload":healed_payload,
                        "vendor_final_rejection":vendor_response.text,
                        "status_code":vendor_response.status_code
                    }
                    save_to_persistent_dlq(dlq_packet)
                  
            await asyncio.sleep(0.1)         
            
        except Exception as e:
            logging.error(f"Worker encountered an unexpected error: {e}")
            await asyncio.sleep(5)
    
        finally:
            try:
                acknowldge_task()
            except Exception:
                pass        