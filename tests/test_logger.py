import os
import shutil
import pytest
import logging
from utils.logger import setup_logger

LOG_DIR = "test_logs"

@pytest.fixture(autouse=True)
def cleanup():
    # Setup - clear any old test logs
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)
    yield
    # Teardown - clean up test logs
    logger = logging.getLogger("test_ai")
    if hasattr(logger, "handlers"):
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)

def test_logger_creation():
    """Test that the logger is created setup and logs messages."""
    logger = setup_logger("test_ai", log_dir=LOG_DIR, level=logging.DEBUG)
    
    assert logger.name == "test_ai"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2  # console + file

    logger.info("Test message for AI pipeline validation")
    
    # Verify file was created
    log_files = os.listdir(LOG_DIR)
    assert len(log_files) == 1
    
    log_path = os.path.join(LOG_DIR, log_files[0])
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Test message for AI pipeline validation" in content
