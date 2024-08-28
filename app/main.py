from fastapi import FastAPI, Request
import time
import logging
from mangum import Mangum
import threading


from app.helper.config import FOLDER_ID
from app.drive_monitor import DriveMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MANGUM FOR AWS LAMBDA

app = FastAPI()
mangum = Mangum(app)

COOLDOWN_TIME = 60  # time in seconds to wait before processing next update
request_lock = threading.Lock() # Lock to ensure only one request is processed at a time
port = 8080


Drive = DriveMonitor() # initializing the DriveMonitor object
# time.sleep(10)  # Wait for 10 seconds before proceeding

@app.get("/")
def index():
    return "Hello, World!"

@app.post("/webhook")
def webhook(request: Request):

     # Doesn't send the query when the server starts
    state = request.headers.get('x-goog-resource-state', 'Not Found')
    if state == 'sync':
        logger.info("Sync message received")
        return {"status": "Starting up"}

    # Checks if we are on cooldown
    current_time = time.time()
    if current_time - Drive.get_prev_time() < COOLDOWN_TIME:
        logging.info("On cooldown")
        return {"status": "On Cooldown"}
    Drive.set_time(current_time)

        
    with request_lock:
       
        request_body = {
            "pageSize": 1,
            "ancestorName": f"items/{FOLDER_ID}"
        }
        try:
            response = Drive.ActivityTracker.activity().query(body=request_body).execute()
            activities = response.get('activities', [])

            # Print out the activities
            if not activities:
                logger.info("No activity.")
            else:
                logger.info('Recent activity:')
                logger.info(f"Number of activities: {len(activities)}")

                for i, activity in enumerate(activities):
                    event = activity.get('primaryActionDetail')
                    targets = activity.get('targets')
                    file_name = targets[0].get('driveItem').get('title')
                    file_id = targets[0].get('driveItem').get('name')
                    file_type = targets[0].get('driveItem').get('mimeType')

                    # Log the variables
                    logger.info("=====================================")
                    logger.info(f"Event: {event}_{i}")
                    logger.info(f"File Name: {file_name}")
                    logger.info(f"File ID: {file_id}")
                    logger.info(f"File Type: {file_type}")
                    logger.info("=====================================\n\n\n")

        except Exception as e:
            logger.error(f"Error getting changes: {e}")
            return {"status": "Error"}

        return {"status": "Received"}

# This entry point is used for local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=port)