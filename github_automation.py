import subprocess
import sys
from pathlib import Path


REPO_DIR = Path(__file__).resolve().parent

APPEND_SCRIPT = REPO_DIR / "append_contribution.py"
GIT_SCRIPT = REPO_DIR / "git_auto_contribute.py"

EXPECTED_REPOSITORY = (
    "github.com/arsalan-dev-cloud/git-auto-contribution"
)


# ==================================================
# GIT COMMAND EXECUTION
# ==================================================

def run_git(*args):

    return subprocess.run(
        ["git", *args],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


def stop(message):

    print(f"\nSTOP: {message}")
    raise SystemExit(1)


# ==================================================
# REPOSITORY VALIDATION
# ==================================================

def validate_repository():

    result = run_git("rev-parse", "--show-toplevel")

    if result.returncode != 0:
        stop("This folder is not a Git repository.")

    actual_root = Path(result.stdout.strip()).resolve()

    if actual_root != REPO_DIR:
        stop("Unexpected repository directory.")

    # Verify GitHub remote.
    remote = run_git("remote", "get-url", "origin")

    if remote.returncode != 0:
        stop("Origin remote is not configured.")

    remote_url = remote.stdout.strip().lower()
    remote_url = remote_url.removesuffix(".git")

    if not (
        remote_url.endswith(EXPECTED_REPOSITORY)
        or remote_url.endswith(
            "github.com:arsalan-dev-cloud/git-auto-contribution"
        )
    ):
        stop("This is not your dedicated contribution repository.")

    # Verify default branch.
    branch = run_git("branch", "--show-current")

    if branch.returncode != 0 or branch.stdout.strip() != "main":
        stop("Checkout the main branch first.")

    # Verify upstream.
    upstream = run_git(
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}"
    )

    if upstream.returncode != 0:
        stop("Main branch has no upstream configured.")

    # Check author identity.
    identity = run_git("var", "GIT_AUTHOR_IDENT")

    if identity.returncode != 0:
        stop("Git author identity is not configured.")

    print(f"Repository : {REPO_DIR}")
    print(f"Branch     : main")
    print(f"Remote     : {remote_url}")
    print(f"Author     : {identity.stdout.strip()}")


# ==================================================
# CHECK WORKING TREE
# ==================================================

def ensure_clean_repository():

    result = run_git(
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all"
    )

    if result.returncode != 0:
        stop("Could not inspect repository status.")

    if result.stdout:
        stop(
            "Uncommitted changes already exist. "
            "Review and commit them before starting this automation."
        )


# ==================================================
# RUN PYTHON SCRIPT
# ==================================================

def run_script(script):

    if not script.is_file():
        stop(f"Script not found: {script}")

    return subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_DIR
    )


# ==================================================
# GET CURRENT COMMIT
# ==================================================

def get_head():

    result = run_git("rev-parse", "HEAD")

    if result.returncode != 0:
        stop("Could not retrieve current commit.")

    return result.stdout.strip()


# ==================================================
# VERIFY COMMIT COUNT
# ==================================================

def get_new_commit_count(previous, current):

    result = run_git(
        "rev-list",
        "--count",
        f"{previous}..{current}"
    )

    if result.returncode != 0:
        stop("Could not calculate new commit count.")

    return int(result.stdout.strip())


# ==================================================
# MAIN AUTOMATION
# ==================================================

def main():

    print("=" * 60)
    print("          GITHUB CONTRIBUTION AUTOMATION")
    print("=" * 60)

    validate_repository()

    ensure_clean_repository()

    print("\nRepository validation successful.")

    while True:

        try:
            total = int(
                input("\nHow many updates do you want to push? ")
            )

            if total > 0:
                break

            print("Enter a number greater than zero.")

        except ValueError:
            print("Enter a valid whole number.")

    successful = 0

    for i in range(1, total + 1):

        print("\n" + "=" * 60)
        print(f"             ITERATION {i}/{total}")
        print("=" * 60)

        ensure_clean_repository()

        previous_commit = get_head()

        # Step 1: Append timestamp.
        print("\nStep 1: Updating contribution log...")

        result = run_script(APPEND_SCRIPT)

        if result.returncode != 0:
            print("Append operation failed.")
            break

        # Step 2: Commit and push.
        print("\nStep 2: Running Git automation...")

        result = run_script(GIT_SCRIPT)

        if result.returncode != 0:
            print("Git automation failed.")
            break

        current_commit = get_head()

        # Step 3: Verify exactly one commit.
        new_commits = get_new_commit_count(
            previous_commit,
            current_commit
        )

        if new_commits != 1:
            print(
                f"Expected one new commit, found {new_commits}."
            )
            break

        # Step 4: Verify clean working tree.
        ensure_clean_repository()

        successful += 1

        print("\nITERATION SUCCESSFUL")
        print(f"Commit: {current_commit}")

    print("\n" + "=" * 60)
    print("                FINAL REPORT")
    print("=" * 60)
    print(f"Requested updates       : {total}")
    print(f"Verified pushed commits : {successful}")
    print(f"Failed iterations       : {total - successful}")
    print("=" * 60)


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
        sys.exit(1)