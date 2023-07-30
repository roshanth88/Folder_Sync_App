import logging
from datetime import datetime
import os
import sys


class SingletonLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Create a single instance of the logger class."""
        if cls._instance is None:
            cls._instance = super(SingletonLogger, cls).__new__(cls)
            cls._instance._init_new_logger(*args, **kwargs)
        return cls._instance

    def _init_new_logger(self, log_file_path=None):
        """
        Configure the logger and attach standard ouput to the logger instance.
        """
        print(log_file_path)
        log_file_name = datetime.now().strftime("logfile_on_%H:%M %d_%m_%Y.log")
        if not os.path.exists(log_file_path):
            os.makedirs(log_file_path)
        logging.basicConfig(
            filename=log_file_path + log_file_name,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filemode="w",
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger("Folder sync logger")
        self.logger.setLevel(logging.DEBUG)

        # Create a stream handler to log to the console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
