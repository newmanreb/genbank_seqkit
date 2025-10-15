# logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Create a logger instance
def create_logger():
    # Get the current directory and parent directory for the log path
    current_directory = str(Path(__file__).resolve().parent)
    parent_directory = Path(current_directory).parent.parent

    # Ensure the logs directory exists
    log_dir = parent_directory / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger('genbank_seqkit_logger')
    logger.setLevel(logging.DEBUG)  # Set the root logger level to DEBUG

    # Stream handler with INFO level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    stream_handler.setFormatter(stream_formatter)

    # File handler with ERROR level and rotating file configuration
    file_handler = RotatingFileHandler(str(parent_directory) + '/logs/genbank_seqkit.log',
                                       maxBytes=500000,  # 500 KB
                                       backupCount=2)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


# Instantiate the logger
logger = create_logger()