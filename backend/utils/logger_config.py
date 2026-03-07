import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "logs"))
LOG_FILE = "app.log"

os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove all default handlers (like console)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.propagate = False 
    # File handler only
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE))
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s - %(name)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger