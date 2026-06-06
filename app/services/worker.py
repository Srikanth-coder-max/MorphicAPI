import asyncio
import logging
from app.services.queue_manager import get_from_queue
from app.services.ai_mapper import heal_payload_with_ai

logging.basicConfig(level=logging.INFO)

async def start_queue_consumer():
    """
    inifinte background loop to process failed request items from the queue 
    """
    logging.info("AI Consumer Worker started and warching failed reuests...")

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

            # TODO pass item to gemini ai
            healed_payload = await heal_payload_with_ai(original_payload, error_details)
            logging.info(f"Healed payload: {healed_payload}")
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logging.error(f"Worker encountered an unexpected error: {e}")
            await asyncio.sleep(5)
    
            