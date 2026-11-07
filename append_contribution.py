
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "contribution_log.txt"

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(LOG_FILE, "a", encoding="utf-8") as file:
    file.write(f"Automation run: {timestamp}\n")

print(f"Log updated: {timestamp}")
