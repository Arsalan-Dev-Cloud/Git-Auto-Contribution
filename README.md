
# Git Auto Contribution

A Python-based automation project for managing Git commits and pushes.

## Features

- Automatically detects changed files.
- Creates individual commits for individual files.
- Pushes each commit to its configured remote.
- Verifies that commits exist in remote history.
- Supports multiple Git repositories.
- Protects against selected sensitive filenames.
- Maintains a timestamped contribution log.
- Provides a dedicated contribution automation controller.

## Requirements

- Python 3.9+
- Git installed and configured
- GitHub repository with an upstream branch
- GitHub authentication configured

## Project Structure

Git-Auto-Contribution/
|
|-- append_contribution.py
|-- contribution_log.txt
|-- git_auto_contribute.py
|-- github_automation.py
|-- README.md

## Installation

Clone the repository:

    git clone https://github.com/Arsalan-Dev-Cloud/Git-Auto-Contribution.git

Enter the folder:

    cd Git-Auto-Contribution

Check requirements:

    python --version
    git --version

## Workflow 1: General Git Automation

The reusable Git automation script can be used from any Git repository.

Example:

    python E:\Git-Auto-Contribution\git_auto_contribute.py E:\Python-Practice

The program:

1. Detects the target repository.
2. Identifies modified, added and deleted files.
3. Stages one file at a time.
4. Creates an individual commit.
5. Pushes the commit.
6. Verifies the remote commit.
7. Continues with the next file.

## Workflow 2: Contribution Log Automation

Run the dedicated controller:

    python github_automation.py

Enter the desired number of iterations.

Each iteration:

1. Adds a timestamp to contribution_log.txt.
2. Runs Git automation.
3. Creates one commit.
4. Pushes the commit.
5. Verifies that exactly one new commit was created.

This workflow is restricted to the dedicated
Git-Auto-Contribution repository.

## Verify Git History

Check repository status:

    git status

View recent commits:

    git log -10 --oneline

Check commit author and email:

    git log -5 --format="%h %an <%ae> %aI"

Check remote:

    git remote -v

## Safety

- Review changes before pushing.
- Never commit passwords, private keys or API tokens.
- Filename-based security checks cannot inspect every secret.
- Do not run automation with unresolved conflicts.
- Push failures require manual inspection.
- Successful pushes do not guarantee GitHub profile contribution eligibility.

## Author

Arsalan-Dev-Cloud

GitHub:
https://github.com/Arsalan-Dev-Cloud

