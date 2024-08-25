from fastapi import FastAPI, Request, Depends
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import atexit
import time


app = FastAPI()
port = 8080
reciever_url = 'https://b9a6-2601-642-4f7f-c288-bcd3-968e-87ee-4bef.ngrok-free.app/webhook'

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.activity'
]
# the folder we are watching
FOLDER_ID = '1opVB2860nVGLHK6IHMt63CTF-4oFrzpF'

COOLDOWN_TIME = 300 # time in seconds to wait before processing next update

# Used to keep track of the page token
class DriveMonitor:
    def __init__(self, DriveWatcher, ActivityTracker):
        """
        Initializes the DriveMonitor object

        Args:
            DriveWatcher: Service for watching for google drive changes
            ActivityTracker: Service used to access the changes made to the drive
            _page_token: Token used to track which change we are at
        """
        self.DriveWatcher = DriveWatcher
        self.ActivityTracker = ActivityTracker
        self._page_token = None
        self._last_processed_time = 0

    def set_token(self, token):
        self._page_token = token

    def get_token(self):
        return self._page_token
    
    def get_prev_time(self):
        return self._last_processed_time
    
    def set_time(self, time):
        self._last_processed_time = time



def build_drive_service(creds):
    '''
    Builds the drive service
    Args:
        creds: the credentials object
    Returns:
        the drive service
    '''
    try:
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        print(f"Error building service: {e}")
        return None
    
def build_activity_service(creds):
    '''
    Builds the activity service
    Args:
        creds: the credentials object
    Returns:
        the activity service
    '''

    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        return build("driveactivity", "v2", credentials=creds)
    except Exception as e:
        print(f"Error building service: {e}")
        return None
    
# starts the watcher
def start_watcher():
    request_body = {
        "id": FOLDER_ID,
        "type": "web_hook",
        "address": reciever_url,
    }
    # getting the last change
    change_response = Drive.DriveWatcher.changes().getStartPageToken().execute()
    start_page_token = change_response.get("startPageToken")
    # Drive.set_token(start_page_token)

    # starting the watcher
    try:
        response = Drive.DriveWatcher.changes().watch(pageToken=start_page_token, body=request_body).execute()
        return response['resourceId']
    
    except Exception as e:
        print(f"Error starting watcher: {e}")
        return None

# ends the watcher
def end_watcher(resourceId):
    request_body = {
        'id': FOLDER_ID,
        'resourceId': resourceId
    }

    try: 
        Drive.DriveWatcher.channels().stop(body=request_body).execute()
    except Exception as e:
        print(f"Error ending watcher: {e}")
        return None
    

    
@app.get("/")
def index():
    return "Hello, World!"

@app.post("/webhook")
async def webhook(request: Request):
    
    # Doesn't send the query when the server starts
    state = request.headers.get('x-goog-resource-state', 'Not Found')
    if state == 'sync':
        # print("Sync message received")
        return {"status": "Starting up"}

    # Checks if we are on cool down
    current_time = time.time()
    if current_time - Drive.get_prev_time() < COOLDOWN_TIME:
        return {"status": "On Cooldown"}
    Drive.set_time(current_time)
    
    time.sleep(30) # Wait for 30 seconds before proceeding

    request_body = {
        "pageSize": 1,
        "ancestorName": f"items/{FOLDER_ID}"
    }
    try:
        response = Drive.ActivityTracker.activity().query(body=request_body).execute()
        activities = response.get('activities', [])
        Drive.set_token(response.get('nextPageToken'))

        if not activities:
            print("No activity.")
        else:
            print('Recent activity:')
            print(len(activities))
            for activity in activities:
                event = activity.get('primaryActionDetail')
                targets = activity.get('targets')
                file_name = targets[0].get('driveItem').get('title')
                file_id = targets[0].get('driveItem').get('name')
                file_type = targets[0].get('driveItem').get('mimeType')

                # print the variables
                print("=====================================")
                print(f"Event: {event}")
                print(f"File Name: {file_name}")
                print(f"File ID: {file_id}")
                print(f"File Type: {file_type}")
                print("=====================================\n\n\n")

    
    except Exception as e:
        print(f"Error getting changes: {e}")
        return None


    return {"status": "Received"}

if __name__ == "__main__":
    import uvicorn
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    Drive = DriveMonitor(build_drive_service(creds), build_activity_service(creds))
    resourceId = start_watcher()

    # ends the watcher when server stops
    atexit.register(end_watcher, resourceId)
    uvicorn.run(app, port=port)