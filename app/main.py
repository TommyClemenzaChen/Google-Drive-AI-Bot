from fastapi import FastAPI, Request
import time
import logging
from mangum import Mangum
import threading


from app.helper.config import FOLDER_ID
from app.drive_monitor import DriveMonitor
from app.file_to_pinecone import index_text_files, clear_folder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MANGUM FOR AWS LAMBDA

app = FastAPI()
mangum = Mangum(app)

request_lock = threading.Lock() # Lock to ensure only one request is processed at a time

logging.info("Starting DriveMonitor")
Drive = DriveMonitor() # initializing the DriveMonitor object
# time.sleep(10)  # Wait for 10 seconds before proceeding

@app.get("/")
def index():
    return "Hello, World!"

@app.post("/webhook")
def webhook(request: Request):
    logging.info("Received request")
     # Doesn't send the query when the server starts
    # state = request.headers.get('x-goog-resource-state', 'Not Found')
    # if state == 'sync':
    #     logger.info("Sync message received")
    #     return {"status": "Starting up"}

    # Checks if we are on cooldown
    if Drive.is_cooldown():
        return {"status": "On cooldown"}

    # Lock to ensure only one request is processed at a time
    with request_lock:
       
        request_body = {
            "pageSize": 1,
            "ancestorName": f"items/{FOLDER_ID}"
        }
        try:
            clear_folder("data/")
            activities = Drive._get_activities(request_body)
            Drive.download(activities)

            # chunk the data
            # index_text_files("data/")
            # clear_folder("data/")
            

        except Exception as e:
            logger.error(f"Error getting changes: {e}")
            return {"status": "Error"}

        return {"status": "Received"}
@app.post("/test")
def test():
    try:
        index_text_files("data/")

        return {"status": "Received"}
    except Exception as e:
        logger.error(f"Error getting changes: {e}")
        return {"status": "Error"}


# This entry point is used for local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)