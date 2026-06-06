import asyncio
import logging
logging.basicConfig(level=logging.INFO)

#global state
failed_request_queue=None

#producer function
async def add_to_queue(original_payload: dict,error_details:dict)-> None:

    global failed_request_queue
    if failed_request_queue is None:
        logging.info("Intializing asyncio.Queue within the running event loop...")
        failed_request_queue=asyncio.Queue()

    #construct transaction log envelope
    failed_item={
        "original_payload":original_payload,
        "error_details":error_details,
    }

    await failed_request_queue.put(failed_item)

    logging.info(f"Successfully queued failed request packet. Current size: {get_queue_size()}")

#Debugger
def get_queue_size()->int:

    if failed_request_queue is None:
        return 0
    return failed_request_queue.qsize()   

#exit door for item retrieval     
async def get_from_queue()-> dict:

    global failed_request_queue

    if failed_request_queue is None:
        failed_request_queue=asyncio.Queue()

    item=await failed_request_queue.get()
    failed_request_queue.task_done()
    return item    

   



