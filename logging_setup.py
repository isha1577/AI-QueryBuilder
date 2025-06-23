import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file='app.log'):
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)
    log_path = os.path.join('logs', log_file)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Avoid adding multiple handlers if logger already has some
    if not logger.handlers:
        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch_formatter = logging.Formatter('%(levelname)s: %(message)s')
        ch.setFormatter(ch_formatter)
        logger.addHandler(ch)

        # File Handler with rotation
        fh = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=5)
        fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(fh_formatter)
        logger.addHandler(fh)

    return logger
