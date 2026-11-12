import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = None


# ==================================================
# GIT COMMAND EXECUTION
# ==================================================

def run_git(*args):

    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


def stop(message):

    print(f"\nSTOP: {message}")
    raise SystemExit(1)


# ==================================================
# REPOSITORY DETECTION
# ==================================================

def find_repository(target):

    target = Path(target).expanduser().resolve()

    if not target.is_dir():
        stop(f"Directory does not exist: {target}")

    result = subprocess.run(
        [
            "git",
            "-C",
            str(target),
            "rev-parse",
            "--show-toplevel"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        stop("No Git repository found.")

    return Path(result.stdout.strip()).resolve()


# ==================================================
# REPOSITORY VALIDATION
# ==================================================

def validate_repository():

    branch = run_git("branch", "--show-current")

    if branch.returncode != 0 or not branch.stdout.strip():
        stop("Checkout a normal Git branch first.")

    branch_name = branch.stdout.strip()

    remote = run_git(
        "config",
        "--get",
        f"branch.{branch_name}.remote"
    )

    merge = run_git(
        "config",
        "--get",
        f"branch.{branch_name}.merge"
    )

    if remote.returncode != 0 or merge.returncode != 0:
        stop("Configure an upstream remote branch first.")

    remote_name = remote.stdout.strip()
    merge_ref = merge.stdout.strip()

    if remote_name == "." or not merge_ref.startswith("refs/heads/"):
        stop("A remote tracking branch is required.")

    upstream = run_git(
        "rev-parse",
        "--symbolic-full-name",
        "@{upstream}"
    )

    if upstream.returncode != 0:
        stop("Could not identify the upstream branch.")

    upstream_ref = upstream.stdout.strip()

    if not upstream_ref.startswith("refs/remotes/"):
        stop("Invalid remote tracking reference.")

    identity = run_git("var", "GIT_AUTHOR_IDENT")

    if identity.returncode != 0:
        stop("Git author identity is not configured.")

    print(f"Repository : {REPO_ROOT}")
    print(f"Branch     : {branch_name}")
    print(f"Remote     : {remote_name}")
    print(f"Author     : {identity.stdout.strip()}")

    return branch_name, remote_name, merge_ref, upstream_ref


# ==================================================
# GIT OPERATION CHECKS
# ==================================================

def check_git_operations():

    operations = [
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD"
    ]

    for operation in operations:

        result = run_git(
            "rev-parse",
            "-q",
            "--verify",
            operation
        )

        if result.returncode == 0:
            stop(f"Git operation in progress: {operation}")


def ensure_clean_index():

    result = run_git("diff", "--cached", "--quiet")

    if result.returncode == 1:
        stop(
            "Staged changes already exist. "
            "Commit or unstage them manually first."
        )

    if result.returncode != 0:
        stop("Could not verify staging area.")


# ==================================================
# DETECT CHANGED FILES
# ==================================================

def get_changes():

    result = run_git(
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all"
    )

    if result.returncode != 0:
        stop("Could not read repository status.")

    changes = []

    for entry in result.stdout.split("\0"):

        if not entry:
            continue

        if len(entry) < 4 or entry[2] != " ":
            stop("Unexpected Git status format.")

        status = entry[:2]
        path = entry[3:]

        if "R" in status or "C" in status:
            stop(
                f"Rename or copy detected: {path}. "
                "Handle it manually first."
            )

        if "U" in status or status in {"AA", "DD"}:
            stop(f"Merge conflict detected: {path}")

        changes.append((path, status))

    return changes


# ==================================================
# SENSITIVE FILE PROTECTION
# ==================================================

def is_sensitive(path):

    parts = path.replace("\\", "/").lower().split("/")
    filename = parts[-1]

    allowed_env = {
        ".env.example",
        ".env.sample",
        ".env.template"
    }

    if filename.startswith(".env") and filename not in allowed_env:
        return True

    sensitive_names = {
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "secrets.json"
    }

    if filename in sensitive_names:
        return True

    sensitive_extensions = {
        ".pem",
        ".key",
        ".p12",
        ".pfx"
    }

    if Path(filename).suffix in sensitive_extensions:
        return True

    sensitive_words = (
        "secret",
        "password",
        "credential",
        "token"
    )

    return any(
        word in part
        for part in parts
        for word in sensitive_words
    )


# ==================================================
# COMMIT MESSAGE GENERATION
# ==================================================

def make_message(path, status):

    filename = Path(path.replace("\\", "/")).name

    if "D" in status:
        return f"Delete {filename}"

    if status == "??" or "A" in status:
        return f"Add {filename}"

    return f"Update {filename}"


# ==================================================
# VERIFY REMOTE COMMIT
# ==================================================

def verify_remote(remote, branch, upstream_ref, commit_hash):

    print("\nVerifying remote commit...")

    fetch = run_git(
        "fetch",
        "--quiet",
        remote,
        branch
    )

    if fetch.returncode != 0:
        print(fetch.stderr)
        stop("Could not fetch the remote branch for verification.")

    result = run_git(
        "merge-base",
        "--is-ancestor",
        commit_hash,
        upstream_ref
    )

    if result.returncode == 0:
        print("Remote verification successful.")
        return True

    stop("The new commit was not found in remote branch history.")


# ==================================================
# PROCESS INDIVIDUAL FILE
# ==================================================

def process_file(path, status, remote, branch, upstream_ref):

    print("\n" + "-" * 60)
    print(f"File   : {path}")
    print(f"Status : {status}")

    if is_sensitive(path):
        stop(f"Potentially sensitive file detected: {path}")

    ensure_clean_index()

    message = make_message(path, status)

    print(f"Message: {message}")

    # Stage only this file.
    result = run_git(
        "add",
        "-A",
        "--",
        path
    )

    if result.returncode != 0:
        print(result.stderr)
        stop(f"Could not stage {path}")

    # Verify staged files.
    staged = run_git(
        "diff",
        "--cached",
        "--name-only",
        "-z"
    )

    if staged.returncode != 0:
        stop("Could not verify staged files.")

    staged_paths = [
        item for item in staged.stdout.split("\0") if item
    ]

    if staged_paths != [path]:
        stop("Unexpected staged files detected.")

    # Create one commit.
    result = run_git(
        "commit",
        "-m",
        message
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        stop(f"Commit failed: {path}")

    commit = run_git("rev-parse", "HEAD")

    if commit.returncode != 0:
        stop("Could not retrieve commit hash.")

    commit_hash = commit.stdout.strip()

    print(f"\nCommit created: {commit_hash}")

    # Push this commit.
    result = run_git(
        "push",
        remote,
        f"HEAD:{branch}"
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)

        stop(
            f"Push failed for {path}. "
            "The local commit already exists. "
            "Resolve the problem and push it manually."
        )

    print("Push command completed.")

    # Verify the remote history.
    verify_remote(
        remote,
        branch,
        upstream_ref,
        commit_hash
    )

    print(f"PUSH VERIFIED: {path}")
    print(f"COMMIT HASH : {commit_hash}")

    return commit_hash


# ==================================================
# MAIN AUTOMATION
# ==================================================

def main():

    global REPO_ROOT

    parser = argparse.ArgumentParser(
        description="Reusable file-by-file Git automation."
    )

    parser.add_argument(
        "repository",
        nargs="?",
        default=".",
        help="Path to the target Git repository."
    )

    args = parser.parse_args()

    REPO_ROOT = find_repository(args.repository)

    print("\n" + "=" * 60)
    print("          REUSABLE GIT AUTOMATION")
    print("=" * 60)

    branch, remote, merge_ref, upstream_ref = validate_repository()

    check_git_operations()
    ensure_clean_index()

    print("\nStarting individual file commits and pushes...")

    processed = set()
    successful = 0

    while True:

        changes = get_changes()

        pending = [
            (path, status)
            for path, status in changes
            if path not in processed
        ]

        if not pending:
            break

        path, status = pending[0]

        commit_hash = process_file(
            path,
            status,
            remote,
            merge_ref.removeprefix("refs/heads/"),
            upstream_ref
        )

        processed.add(path)
        successful += 1

        print(f"\nCompleted commit: {commit_hash}")

    remaining = get_changes()

    if remaining:
        stop(
            "Some files changed again during execution. "
            "Review repository status manually."
        )

    print("\n" + "=" * 60)
    print("              FINAL REPORT")
    print("=" * 60)
    print(f"Repository          : {REPO_ROOT}")
    print(f"Branch              : {branch}")
    print(f"Verified commits    : {successful}")
    print("All detected changes processed.")
    print("=" * 60)


if __name__ == "__main__":

    main()