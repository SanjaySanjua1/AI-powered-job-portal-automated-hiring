import logging
import os
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a standard scalable logger for AI modules.
    Logs are written to stdout (sys.stdout) and to a file in the logging directory.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Return logger if already configured to avoid duplicating handlers
    if logger.handlers:
        return logger

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Formatter for structured logging
    formatter = logging.Formatter(
        '%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s'
    )

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 2. File Handler (daily rotation approach via names, or just append)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(log_dir, f"{date_str}_ai_engine.log")
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger
