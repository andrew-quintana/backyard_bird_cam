import unittest
import os
import json
from datetime import datetime
from logger import log

LOG_FILE = "logs/system.log"

def get_last_log_entry():
    """Helper function to read the last log entry."""
    with open(LOG_FILE, "r") as log_file:
        lines = log_file.readlines()
    return json.loads(lines[-1]) if lines else None

class TestLogger(unittest.TestCase):
    def setUp(self):
        # clean the log file before each test
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

    def test_log_info_message(self):
        log("INFO", "test_logger.py", "Test info message")
        log_entry = get_last_log_entry()

        self.assertEqual(log_entry["level"], "INFO")
        self.assertEqual(log_entry["source"], "test_logger.py")
        self.assertEqual(log_entry["message"], "Test info message")

    def test_log_error_message(self):
        log("WARNING", "test_logger.py", "Test warning message")
        log_entry = get_last_log_entry()

        self.assertEqual(log_entry["level"], "WARNING")
        self.assertEqual(log_entry["source"], "test_logger.py")
        self.assertEqual(log_entry["message"], "Test warning message")

    def test_log_error_message(self):
        log("ERROR", "test_logger.py", "Test error message")
        log_entry = get_last_log_entry()

        self.assertEqual(log_entry["level"], "ERROR")
        self.assertEqual(log_entry["source"], "test_logger.py")
        self.assertEqual(log_entry["message"], "Test error message")

if __name__ == "__main__":
    unittest.main()