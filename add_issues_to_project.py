#!/usr/bin/env python3
"""
Script to add all issues to GitHub project
"""

import subprocess
import sys

def add_issue_to_project(issue_number: int, project_number: str) -> bool:
    """Add an issue to a project"""
    try:
        url = f"https://github.com/cgoss/Moderation-ai/issues/{issue_number}"
        cmd = [
            'gh', 'project', 'item-add', project_number,
            '--url', url,
            '--owner', 'cgoss'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Added issue #{issue_number}")
            return True
        else:
            print(f"[FAIL] Issue #{issue_number}: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Issue #{issue_number}: {e}")
        return False

def main():
    # Project number for "Moderation AI - Phase 0: Foundation" (from gh project list)
    project_number = "7"

    # Issue numbers from our creation (10-69)
    issue_numbers = list(range(10, 70))

    print(f"Adding {len(issue_numbers)} issues to project...")

    successful = 0
    failed = 0

    for issue_num in issue_numbers:
        if add_issue_to_project(issue_num, project_number):
            successful += 1
        else:
            failed += 1

    print(f"\n[SUCCESS] Added: {successful} issues")
    if failed > 0:
        print(f"[FAILED] {failed} issues")

    print(f"\nProject: https://github.com/users/cgoss/projects/7")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
