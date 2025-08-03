import traceback
import sys
from logger.custom_logger import CustomLogger
logger=CustomLogger().get_logger(__file__)

# traceback: For formatting stack traces.
# sys: To access sys.exc_info().
# CustomLogger: Your custom logging class from logger/custom_logger.py.
# Instantiates CustomLogger, which creates a timestamped log file in the logs directory.
# Retrieves a logger named after the current file.
# All log entries will be written to the file with full formatting.

class DocumentPortalException(Exception):
    """Custom exception for Document Portal"""
    def __init__(self,error_message,error_details):
        _,_,exc_tb= error_details.exc_info()
        self.file_name=exc_tb.tb_frame.f_code.co_filename
        self.lineno=exc_tb.tb_lineno
        self.error_message=str(error_message)
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info())) 

# Custom exception class that:
#  Captures the file name and line number of the exception
#  Stores the full traceback as a string
#  Formats it all for easy reading/logging

# Captures:
#  The file where the error occurred
#  The line number
#  A string representation of the original error
#  The full traceback as a formatted string

    def __str__(self):
       return f"""
        Error in [{self.file_name}] at line [{self.lineno}]
        Message: {self.error_message}
        Traceback:
        {self.traceback_str}
        """
# Returns a multi-line string when the exception is printed or logged.
    
if __name__ == "__main__":
    try:
        # Simulate an error
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc=DocumentPortalException(e,sys)
        logger.error(app_exc)
        raise app_exc