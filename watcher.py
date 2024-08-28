from app.helper.config import FOLDER_ID, RECEIVER_URL
from app.helper.build import build_drive_service
import sys
import os

Drive = build_drive_service()

# starts the watcher
def start_watcher():

    """
    Starts the watcher and stores the resource ID in a file
    """
    request_body = {
        "id": FOLDER_ID,
        "type": "web_hook",
        "address": RECEIVER_URL,
    }
    # getting the last change
    change_response = Drive.changes().getStartPageToken().execute()
    start_page_token = change_response.get("startPageToken")

    # starting the watcher
    try:
        response = Drive.changes().watch(pageToken=start_page_token, body=request_body).execute()

        # Stores the resource ID
        with open("resource_id.txt", "w") as f:
            f.write(response['resourceId'])
        print(f"Watcher started on {RECEIVER_URL}.\n")
    
    except Exception as e:
        print(f"Error starting watcher: {e}")
        return None
    
# ends the watcher
def end_watcher():
    """
    Ends the watcher and deletes the resource ID file
    """

    try: 
        with open("resource_id.txt", "r") as f:
            resourceId = f.read()
        # delete the resource ID file
        os.remove("resource_id.txt")

        request_body = {
            'id': FOLDER_ID,
            'resourceId': resourceId
        }

        Drive.channels().stop(body=request_body).execute()
        print("Watcher ended.\n")
    except Exception as e:
        print(f"Error ending watcher: {e}")
        return None
    
def main():
    if len(sys.argv) != 2:
        print("Usage: python watcher.py [start|stop|stats]")
        sys.exit(1)
    
    command = sys.argv[1]

    if command == "start":
        start_watcher()
    elif command == "stop":
        end_watcher()
    elif command == "status":
        if os.path.exists("resource_id.txt"):
            print(f"Watcher is running")
        else:
            print("Watcher is not running.")
    else:
        print("Invalid command. Use 'start', 'stop', or status.")
        sys.exit(1)

if __name__ == "__main__":
    main()