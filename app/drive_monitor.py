from app.helper.build import build_activity_service
from app.helper.config import FOLDER_ID, RECEIVER_URL

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
        self._resourceId = None
  
    
    def get_prev_time(self):
        return self._last_processed_time
    
    def set_time(self, time):
        self._last_processed_time = time

    
