import firebase_admin
from firebase_admin import credentials, firestore
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class google_drive_manager:

    def __init__(self, user_id):
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.user_id = user_id


        self.DriveAPI = self._build_drive_service()


    def _exists(self):
        """
        Checks if the user_id exists in our database

        Args:
            self
        Returns:
            Boolean
        """
        doc = doc_ref.document(self.user_id).get()
        return doc.exists
    
    def _get_data(self):
        """
        Gets the credentials from the database
        """
        
        token = doc_ref.document(self.user_id).get()
        return token
    
    def _set_data(self, creds):
        """
        Saves the credentials to the database
        """
        creds_dict = json.loads(creds.to_json())
        doc_ref.document(self.user_id).set({"user_data": creds_dict})

    def _check_expired(self, creds):
        """
        Refreshes and updates the credentials in database if expired
        """
        if creds.expired:
            creds.refresh(Request())
            self._set_data(creds)



    def _build_drive_service(self):
        creds = None
        if self._exists():
            data = self._get_data()
            creds = Credentials.from_authorized_user_info(data.to_dict()['user_data'])

            self._check_expired(creds)
        else:
            creds = self._generate_token_data()
            self._set_data(creds)

        return build("drive", "v3", credentials=creds)

        

    # Get the json file token
    def _generate_token_data(self):
        
        flow = InstalledAppFlow.from_client_secrets_file(
            "misc/credentials.json", self.SCOPES
        )
        creds = flow.run_local_server(port=0)
        return creds
    
    def print_files(self):
        results = self.DriveAPI.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get("files", [])

        if not items:
            print("No files found.")
        else:
            print("Files:")
            for item in items:
                print(u"{0} ({1})".format(item["name"], item["id"]))
    

    


if __name__ == '__main__':
    gcp_cred = credentials.Certificate('app/service_key.json')
    firebase_admin.initialize_app(gcp_cred)

    db = firestore.client()

    # table
    doc_ref = db.collection('auth_tokens')
    

    # get_data("user1")
    drive1 = google_drive_manager(user_id="user2")

    drive1.print_files()


