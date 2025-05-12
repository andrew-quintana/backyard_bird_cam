import os
import sys
import logging
import logging.handlers
from datetime import datetime

# Configure logging
def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # File handler for persistent logs
    log_file = os.path.join(log_dir, f'bird_camera_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(file_handler)
    
    # Console handler for immediate output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # Log system information
    logging.info("=== Bird Camera Service Starting ===")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Working directory: {os.getcwd()}")
    logging.info(f"User: {os.getuid()}")
    logging.info(f"Group: {os.getgid()}")
    logging.info(f"Environment: {dict(os.environ)}")
    logging.info("=== System Information Logged ===")

# Call setup_logging at the start of the script
setup_logging() 