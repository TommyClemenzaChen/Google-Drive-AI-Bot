import os
from google.oauth2.service_account import Credentials
# from google.auth.transport.requests import Request
# from google_auth_oauthlib.flow import InstalledAppFlow
from app.helper.config import SCOPES


# Initializing the credentials
def initialize_credentials():

  creds = Credentials.from_service_account_file("app/service_key.json", scopes=SCOPES)
  return creds



# if __name__ == "__main__":
#   initialize_credentials()