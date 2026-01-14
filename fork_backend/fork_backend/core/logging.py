"""Custom logger"""

import logging
from logging import Logger as Log
import sys

class Logger:
    """Custom Logger class"""
    def __init__(self, name="Fork_Backend_Logger", log_file="fork_backend.log", level=logging.INFO):
        """
        Initialize the logger with file and console handlers.
        
        :param: name: Name of the logger.
        :param: log_file: Path to the log file.
        :param: level: Logging level (e.g., logging.INFO, logging.DEBUG).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Prevent adding multiple handlers if the logger is already initialized
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # File Handler
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to set up file handler: {e}")

            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self) -> Log:
        """Return the underlying logger object."""
        return self.logger

def get_logger() -> Log:
    """Simple func to get a logger instance
    
    :return: a logger instance
    """
    return Logger().get_logger()
