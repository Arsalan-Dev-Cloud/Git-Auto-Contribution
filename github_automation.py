
import subprocess
import sys
from pathlib import Path

APPEND_SCRIPT = Path(
    r"E:\Python-Practice\Day-21_Advanced_File_Handling_in_Python\append.py"
)

GIT_SCRIPT = Path(
    r"E:\Git-Auto-Contribution\git_auto_contribute.py"
)

print("=" * 50)
print("       GITHUB AUTOMATION")
print("=" * 50)

while True:
    try:
        total = int(input("\nHow many commits do you want? "))

        if total > 0:
            break

        print("Enter a number greater than zero.")

    except ValueError:
        print("Please enter a valid number.")

successful = 0

for i in range(1, total + 1):

    print(f"\n========== ITERATION {i}/{total} ==========")

    # Run append.py
    print("\nRunning append.py...")

    result = subprocess.run(
        [sys.executable, str(APPEND_SCRIPT)],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("append.py failed. Stopping.")
        print(result.stderr)
        break

    # Run git_auto_contribute.py
    print("Running git_auto_contribute.py...")

    result = subprocess.run(
        [sys.executable, str(GIT_SCRIPT)],
        cwd=GIT_SCRIPT.parent,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("Git automation failed. Stopping.")
        print(result.stderr)
        break

    if "Files committed and pushed: 0" in result.stdout:
        print("No changes were committed. Stopping.")
        break

    successful += 1
    print(f"Iteration {i} completed.")

print("\n" + "=" * 50)
print("           FINAL REPORT")
print("=" * 50)
print(f"Requested commits: {total}")
print(f"Successful runs: {successful}")
print("=" * 50)
