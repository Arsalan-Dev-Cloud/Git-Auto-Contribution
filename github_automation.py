
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent

APPEND_SCRIPT = REPO_DIR / "append_contribution.py"
GIT_SCRIPT = REPO_DIR / "git_auto_contribute.py"


def run_script(script):
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_DIR
    )


def main():

    print("=" * 50)
    print("       GITHUB AUTOMATION")
    print("=" * 50)

    while True:
        try:
            total = int(input("\nHow many updates do you want to push? "))

            if total > 0:
                break

            print("Enter a number greater than zero.")

        except ValueError:
            print("Enter a valid whole number.")

    successful = 0

    for i in range(1, total + 1):

        print(f"\n========== ITERATION {i}/{total} ==========")

        print("\nRunning append_contribution.py...")

        result = run_script(APPEND_SCRIPT)

        if result.returncode != 0:
            print("Append script failed. Stopping.")
            break

        print("\nRunning git_auto_contribute.py...")

        result = run_script(GIT_SCRIPT)

        if result.returncode != 0:
            print("Git automation failed. Stopping.")
            break

        successful += 1

        print(f"\nIteration {i} completed.")

    print("\n" + "=" * 50)
    print("             FINAL REPORT")
    print("=" * 50)
    print(f"Requested updates: {total}")
    print(f"Successful pushes: {successful}")
    print("=" * 50)


if __name__ == "__main__":
    main()
