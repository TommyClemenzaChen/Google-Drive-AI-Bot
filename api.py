from fastapi import FastAPI, Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import atexit
import uvicorn


app = FastAPI()
port = 8080
reciever_url = 'https://e405-2601-642-4f7f-c288-c56c-cf00-cf3f-b769.ngrok-free.app/webhook'

SCOPES = ['https://www.googleapis.com/auth/drive']
# the folder we are watching
FOLDER_ID = '1opVB2860nVGLHK6IHMt63CTF-4oFrzpF'


# class PageTokenManager:
#     def __init__(self):
#         self._curr_page_token = None

#     def get_token(self):
#         return self._curr_page_token

#     def set_token(self, token):
#         self._curr_page_token = token


# Builds the service
def build_service():
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        print(f"Error building service: {e}")
        return None
    
# starts the watcher
def start_watcher(service):
    request_body = {
        "id": FOLDER_ID,
        "type": "web_hook",
        "address": reciever_url,
    }
    # getting the last change
    change_response = service.changes().getStartPageToken().execute()
    CURR_PAGE_TOKEN = change_response.get("startPageToken")

    # starting the watcher
    try:
        response = service.changes().watch(pageToken=CURR_PAGE_TOKEN, body=request_body).execute()
        return response['resourceId'], CURR_PAGE_TOKEN
    
    except Exception as e:
        print(f"Error starting watcher: {e}")
        return None

# ends the watcher
def end_watcher(resourceId, service):
    request_body = {
        'id': FOLDER_ID,
        'resourceId': resourceId
    }

    try: 
        service.channels().stop(body=request_body).execute()
    except Exception as e:
        print(f"Error ending watcher: {e}")
        return None
    
# def get_file_changes():
#     results = service.changes().list(
#         pageToken=CURR_PAGE_TOKEN,
#         spaces='drive',
#         fields='newStartPageToken, changes',
#         pageSize=10
#     ).execute()

#     # get the most recent token
#     CURR_PAGE_TOKEN = results.get('newStartPageToken')
#     print(results)
#     return results
    
@app.get("/")
def index():
    return "Hello, World!"

@app.post("/webhook")
async def webhook(request: Request):
    print("Headers:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

    state = request.headers.get('x-goog-resource-state', 'Not Found')
    # print(f"State: {x_goog_resource_state}")
    # get_file_changes()
    

    return {"status": "Received"}

if __name__ == "__main__":
    
    service = build_service()
    resourceId = start_watcher(service)

    atexit.register(end_watcher, resourceId, service)
    uvicorn.run(app, port=port)