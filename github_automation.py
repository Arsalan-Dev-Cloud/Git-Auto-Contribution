
import subprocess
import sys
from pathlib import Path


# ==========================================
# FILE LOCATIONS
# ==========================================

REPO_DIR = Path(r"E:\Git-Auto-Contribution")

APPEND_SCRIPT = Path(
    r"E:\Python-Practice\Day-21_Advanced_File_Handling_in_Python\append.py"
)

GIT_SCRIPT = REPO_DIR / "git_auto_contribute.py"


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def run_command(command, cwd):
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


def get_latest_commit():
    result = run_command(
        ["git", "rev-parse", "HEAD"],
        REPO_DIR
    )

    if result.returncode != 0:
        raise RuntimeError("Unable to read latest Git commit.")

    return result.stdout.strip()


def check_git_status():
    result = run_command(
        ["git", "status", "--porcelain"],
        REPO_DIR
    )

    if result.returncode != 0:
        raise RuntimeError("Unable to check Git status.")

    return result.stdout.strip()


# ==========================================
# MAIN AUTOMATION
# ==========================================

def main():

    print("=" * 55)
    print("          GITHUB AUTO CONTRIBUTION")
    print("=" * 55)

    # Ask for number of iterations
    while True:
        try:
            iterations = int(
                input("\nHow many iterations do you want? ")
            )

            if iterations <= 0:
                print("Please enter a positive number.")
                continue

            break

        except ValueError:
            print("Invalid input! Enter a whole number.")

    # Verify required files
    if not APPEND_SCRIPT.is_file():
        print("\nERROR: append.py not found.")
        return

    if not GIT_SCRIPT.is_file():
        print("\nERROR: git_auto_contribute.py not found.")
        return

    if not (REPO_DIR / ".git").exists():
        print("\nERROR: Git repository not found.")
        return

    # Ensure there are no previous uncommitted changes
    try:
        if check_git_status():
            print("\nSTOP: Your Git repository is not clean.")
            print("Commit or resolve existing changes first.")
            return

        previous_commit = get_latest_commit()

    except RuntimeError as error:
        print(f"\nERROR: {error}")
        return

    successful_iterations = 0

    print("\n" + "=" * 55)
    print(f"Starting {iterations} iterations...")
    print("=" * 55)

    # Repeat automation
    for i in range(1, iterations + 1):

        print(f"\n\n========== ITERATION {i}/{iterations} ==========")

        # Step 1: Run append.py
        print("\n[1] Running append.py...")

        append_result = run_command(
            [sys.executable, str(APPEND_SCRIPT)],
            APPEND_SCRIPT.parent
        )

        print(append_result.stdout, end="")

        if append_result.returncode != 0:
            print("\nSTOP: append.py failed.")
            print(append_result.stderr)
            break

        # Step 2: Run Git automation
        print("\n[2] Running git_auto_contribute.py...")

        git_result = run_command(
            [sys.executable, str(GIT_SCRIPT)],
            REPO_DIR
        )

        print(git_result.stdout, end="")

        if git_result.returncode != 0:
            print("\nSTOP: Git automation failed.")
            print(git_result.stderr)
            break

        # Step 3: Verify a new commit was created
        try:
            current_commit = get_latest_commit()

            if current_commit == previous_commit:
                print("\nSTOP: No new commit was created.")
                break

            if check_git_status():
                print("\nSTOP: Repository still has uncommitted changes.")
                break

        except RuntimeError as error:
            print(f"\nSTOP: {error}")
            break

        previous_commit = current_commit
        successful_iterations += 1

        print(f"\nSUCCESS: Iteration {i} completed!")
        print(f"Commit: {current_commit[:10]}")

    # Final report
    print("\n")
    print("=" * 55)
    print("             AUTOMATION REPORT")
    print("=" * 55)

    print(f"Requested iterations : {iterations}")
    print(f"Successful iterations: {successful_iterations}")
    print(f"Unsuccessful iterations: {iterations - successful_iterations}")

    print("=" * 55)

    if successful_iterations == iterations:
        print("ALL ITERATIONS COMPLETED SUCCESSFULLY!")
    else:
        print("AUTOMATION STOPPED BEFORE COMPLETION.")

    print("=" * 55)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\nAutomation interrupted by user.")
