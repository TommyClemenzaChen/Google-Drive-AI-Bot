# Configuration file for the app

SCOPES = ['https://www.googleapis.com/auth/drive', 
          'https://www.googleapis.com/auth/drive.activity']
SERVICE_ACCOUNT_FILE = 'app/credentials.json'
FOLDER_ID = '1opVB2860nVGLHK6IHMt63CTF-4oFrzpF'
port = 8080
COOLDOWN_TIME = 300
# REMEMBER TO ALWAYS INCLUDE WEBHOOK IN THE URL
RECEIVER_URL = 'https://c290-2601-642-4f7f-c288-f11c-7375-ed9b-5fc0.ngrok-free.app/webhook'
