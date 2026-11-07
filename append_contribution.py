from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "contribution_log.txt"

update = input("Describe your actual project update: ").strip()

if not update:
    print("No update entered. Stopping.")
    raise SystemExit(1)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open(LOG_FILE, "a", encoding="utf-8") as file:
    file.write(f"[{timestamp}] {update}\n")

print("Project update recorded successfully!")