from flask import Flask, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import atexit


import os

app = Flask(__name__)
# Maybe use websockets?
port = 8080

# permissions for the service account
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1opVB2860nVGLHK6IHMt63CTF-4oFrzpF'


def initialize_credentials():
    # Initializing the credentials
    credts = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def start_watcher(service):
    

    request_body = {
        "id": FOLDER_ID,
        "type": "web_hook",
        "address": "https://b20f-2601-642-4f7f-c288-4dc1-fbc4-c623-ca20.ngrok-free.app/webhook"
    }
    # getting the last change
    change_response = service.changes().getStartPageToken().execute()
    saved_start_page_token = change_response.get("startPageToken")
    try:
        response = service.changes().watch(pageToken=saved_start_page_token, body=request_body).execute()
        return response['resourceId']
    
    except Exception as e:
        print(f"Error starting watcher: {e}")
        return None

def end_watcher(channel_id, resourceId, service):
    try:
        # Prepare the request body
        request_body = {
            'id': channel_id,         # Channel ID
            'resourceId': resourceId # Resource ID
        }
        
        # Print debug information
        print(f"Stopping channel with ID: {channel_id}, Resource ID: {resourceId}")
        
        # Call the stop method
        response = service.channels().stop(body=request_body).execute()
        
        # Print success message
        print("Channel stopped successfully.")
    except Exception as e:
        # Print the error message
        print(f"Error stopping watcher: {e}")


@app.route("/", methods=['GET'])
def index():
    return "Hi buddu"


@app.route("/webhook", methods = ['POST'])
def webhook():
    data = request.headers.items()
    print("Headers Received:")
    for header, value in data:
        print(f"{header}: {value}")

    return "recieved"

if __name__ == '__main__':
    creds = initialize_credentials()

    # building the service
    service = build("drive", "v3", credentials=creds)

    # starts the watcher
    resourceId = start_watcher(service)

    # Register the function to stop the watcher when the server stops
    atexit.register(lambda: end_watcher(FOLDER_ID, resourceId, service))

    app.run(port = port, debug = True)