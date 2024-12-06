import unittest
import os
from datetime import datetime
from logger import log

LOG_FILE = "logs/system.log"

def get_last_log_entry():
    """Helper function to read the last log entry from the log file."""
    with open(LOG_FILE, "r") as log_file:
        lines = log_file.readlines()
    return lines[-1].strip() if lines else None

class TestLogger(unittest.TestCase):
    def setUp(self):
        # clean the log file before each test
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)

    def test_log_info_message(self):
        log("INFO", "test_logger.py", "Test info message")
        last_log = get_last_log_entry()

        # check that the log entry exists and contains the expected content
        self.assertIsNotNone(last_log)
        self.assertIn("[INFO]", last_log)
        self.assertIn("[test_logger.py]", last_log)
        self.assertIn("Test info message", last_log)

    def test_log_warning_message(self):
        log("WARNING", "test_logger.py", "Test warning message")
        last_log = get_last_log_entry()

        # check that the log entry exists and contains the expected content
        self.assertIsNotNone(last_log)
        self.assertIn("[WARNING]", last_log)
        self.assertIn("[test_logger.py]", last_log)
        self.assertIn("Test warning message", last_log)

    def test_log_error_message(self):
        log("ERROR", "test_logger.py", "Test error message")
        last_log = get_last_log_entry()

        # check that the log entry exists and contains the expected content
        self.assertIsNotNone(last_log)
        self.assertIn("[ERROR]", last_log)
        self.assertIn("[test_logger.py]", last_log)
        self.assertIn("Test error message", last_log)

    def test_log_timestamp_format(self):
        log("INFO", "test_logger.py", "Check timestamp format")
        last_log = get_last_log_entry()

        # extract the timestamp from the log entry
        timestamp_str = last_log.split("]")[0][1:]  # get the first part inside brackets
        try:
            datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp_valid = True
        except ValueError:
            timestamp_valid = False

        self.assertTrue(timestamp_valid, "Timestamp format is invalid")

if __name__ == "__main__":
    unittest.main()