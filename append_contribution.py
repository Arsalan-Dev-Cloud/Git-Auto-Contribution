from datetime import datetime
from pathlib import Path
import sys


REPO_DIR = Path(__file__).resolve().parent
LOG_FILE = REPO_DIR / "contribution_log.txt"


def append_log():

    timestamp = datetime.now().astimezone().isoformat(
        timespec="microseconds"
    )

    entry = f"Automation run: {timestamp}\n"

    try:
        with LOG_FILE.open(
            "a",
            encoding="utf-8",
            newline="\n"
        ) as file:

            file.write(entry)

    except OSError as error:
        print(f"ERROR: Could not update log: {error}")
        return False

    print(f"Log updated successfully: {timestamp}")

    return True


def main():

    if append_log():
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())