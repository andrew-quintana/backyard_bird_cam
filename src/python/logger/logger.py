import json
from datetime import datetime

LOG_FILE = "logs/system.log"

def log(level: str, source: str, message: str):
    log_entry = {
        "timestamp": datetime.timezone.utc().isoformat() + "Z",
        "level": level,
        "source": source,
        "message": message,
    }

    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")