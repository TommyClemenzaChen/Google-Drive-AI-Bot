from app.helper.build import build_activity_service, build_drive_service
import logging
from app.helper.config import COOLDOWN_TIME
import time
from googleapiclient.http import MediaIoBaseDownload
import io
import fitz
from docx import Document


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriveMonitor:
    def __init__(self):
        """
        Initializes the DriveMonitor object

        Args:
            ActivityTracker: Service used to access the changes made to the drive
            self._last_processed_time: Time of the last processed change
        """

        self._last_processed_time = 0
        self.ActivityTracker = build_activity_service()
        self.DriveAPI = build_drive_service()
        self._resourceId = None
  
    #####################################################################
    # Getter and setter methods
    #####################################################################
    def get_prev_time(self):


        return self._last_processed_time
    
    def set_time(self, time):
        self._last_processed_time = time

    def _get_activities(self, request_body):
        """
        Gets the most recent activities from the drive
        """
        response = self.ActivityTracker.activity().query(body=request_body).execute()
        return response.get('activities', [])
    
    #####################################################################
    # Download methods
    #####################################################################
    
    def download(self, activities):
        """
        Download the files that were recently added or modified
        """
        files = set()
        for activity in activities:
            
            targets = activity.get('targets')
            # file_name = targets[0].get('driveItem').get('title')
            file_id = targets[0].get('driveItem').get('name')
            file_type = targets[0].get('driveItem').get('mimeType')
            files.add((file_id, file_type))
        
        self._download_files(files)

    def _download_files(self, files):

        logging.info(f"Downloading {len(files)} files")
        try:
        
            for file_id, file_type in files:
                # Ex: File ID: items/1wNI-N7sBqz8LSveE3GmfnOs9oxOvhefjW8vDdzThcWc
                file_id = file_id.split('/')[1]

                if file_type == 'application/vnd.google-apps.document':
                    self._docx_to_text(file_id)
                elif file_type == 'application/pdf':
                    self._pdf_to_text(file_id)
                else:
                    self._txt_to_text(file_id)
            logging.info(f"Finished Downloading files")
        except Exception as e:
            logging.error(f"Error downloading files: {e}")

            
    
    
            
    #####################################################################
    # Helper functions
    #####################################################################
    
    def _docx_to_text(self, file_id):
        """
        Converts a docx file to text
        """
        try:
        
            request = self.DriveAPI.files().export_media(
                        fileId=file_id, 
                        mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            download_file = self._download_helper(request) # bytes format
            download_path = 'data/' + file_id + '.txt'

            # Convert the docx file to text
            doc = Document(io.BytesIO(download_file.read()))
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            text_content = ''.join(full_text)
            with open(download_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            logging.info(f"Downloaded {file_id} to {download_path} DOCX")
        except Exception as e:
            logging.error(f"Error converting docx to text: {e}")


        
    def _pdf_to_text(self, file_id):
        """
        Converts a PDF file to text
        """
        try:
            request = self.DriveAPI.files().get_media(fileId=file_id)
            download_file = self._download_helper(request) # bytes format
            download_path = 'data/' + file_id + '.txt'

            # Convert the pdf file to text
            
            text_content = ""
            pdf_doc = fitz.open(stream=download_file.read(), filetype = "pdf")
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                text_content += page.get_text()

            # Save the text content to a .txt file
            with open(download_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            logging.info(f"Downloaded {file_id} to {download_path} PDF")

        except Exception as e:
            logging.error(f"Error converting pdf to text: {e}")


    def _txt_to_text(self, file_id):
        """
        Converts a txt file to text
        """
        try:
            request = self.DriveAPI.files().get_media(fileId=file_id)
            download_file = self._download_helper(request) # bytes format
            download_path = 'data/' + file_id + '.txt'

            with open(download_path, 'wb') as f:
                f.write(download_file.read())
            logging.info(f"Downloaded {file_id} to {download_path} TXT")
        except Exception as e:
            logging.error(f"Error converting txt to text: {e}")

    def _download_helper(self, request):
        """
        Downloads the file sent from google drive in bytes format
        """

        download_file = io.BytesIO()
        downloader = MediaIoBaseDownload(download_file, request)

        done = False 
        while done is False:
            status, done  = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

        download_file.seek(0)  # Go back to the beginning of the BytesIO object
        return download_file


    #####################################################################
    # Other functions(cool down and logging)
    #####################################################################

    
    def is_cooldown(self):
        """
        Checks if the program is still on cooldown
        """

        current_time = time.time()
        if current_time - self.get_prev_time() < COOLDOWN_TIME:
            logging.info("On cooldown")
            return True
        self.set_time(current_time)
        return False

    def log_activity(self, activities):
        """
        Logs the activity to the console
        """
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




    
