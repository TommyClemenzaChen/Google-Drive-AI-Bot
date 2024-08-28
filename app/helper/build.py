from googleapiclient.discovery import build
from app.helper.initialize_credentials import initialize_credentials

creds = initialize_credentials()

def build_drive_service():
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
    

def build_activity_service():
    '''
    Builds the activity service
    Args:
        creds: the credentials object
    Returns:
        the activity service
    '''

    try:
        return build("driveactivity", "v2", credentials=creds)
    except Exception as e:
        print(f"Error building service: {e}")
        return None
    
if __name__ == "__main__":

    build_drive_service()
    build_activity_service()