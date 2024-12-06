from datetime import datetime
import os

LOG_FILE = "logs/system.log"

# ANSI color codes for terminal output
RESET = "\033[0m"
RED = "\033[31m"
YELLOW = "\033[33m"
NORMAL = "\033[0m"

# Ensure the logs directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(level: str, source: str, message: str):
    # Get the current timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Format the log entry
    log_entry = f"[{timestamp}] [{level}] [{source}] {message}"

    # Write the log entry to the log file
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(log_entry + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

    # Print the log entry to the console with color
    color = NORMAL
    if level == "ERROR":
        color = RED
    elif level == "WARNING":
        color = YELLOW
    print(f"{color}{log_entry}{RESET}")