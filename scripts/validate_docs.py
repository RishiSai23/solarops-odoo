#!/usr/bin/env python3
"""
SunFlow Documentation Validation Script
---------------------------------------
Verifies that:
1. Mandatory root knowledge files exist (AGENTS.md, learned.md, progress.md, README.md).
2. Every non-ignored directory contains a markdown file named <dirname>/<dirname>.md.
3. Every immediate non-ignored file inside each directory is documented in that directory's markdown file.
4. No phantom (nonexistent) files are documented in the directory markdown file.
"""

import os
import sys
import re
from pathlib import Path

# Directories and files to ignore during validation
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

IGNORED_FILES = {
    ".DS_Store",
    "thumbs.db",
}

ROOT_MANDATORY_FILES = [
    "AGENTS.md",
    "learned.md",
    "progress.md",
    "README.md",
]


def check_root_files(root_path: Path) -> list[str]:
    errors = []
    for file_name in ROOT_MANDATORY_FILES:
        target = root_path / file_name
        if not target.is_file():
            errors.append(f"[ROOT ERROR] Missing mandatory root file: {file_name}")
        elif target.stat().st_size == 0:
            errors.append(f"[ROOT ERROR] Mandatory root file is empty: {file_name}")
    return errors


def validate_directory_docs(root_path: Path) -> list[str]:
    errors = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Exclude ignored directories in-place so os.walk does not descend
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and not d.startswith(".")]

        current_dir = Path(dirpath)
        if current_dir == root_path:
            continue

        dir_name = current_dir.name
        doc_filename = f"{dir_name}.md"
        doc_path = current_dir / doc_filename

        # 1. Check directory doc exists
        if not doc_path.is_file():
            errors.append(f"[DOC ERROR] Missing directory documentation: {current_dir.relative_to(root_path)}/{doc_filename}")
            continue

        doc_content = doc_path.read_text(encoding="utf-8", errors="replace")

        # 2. Check all immediate files in current_dir are documented
        immediate_files = [
            f for f in filenames
            if f not in IGNORED_FILES
            and not f.endswith(".pyc")
            and f != doc_filename
        ]

        for file_name in immediate_files:
            # Check if file_name is mentioned in the markdown file
            if file_name not in doc_content:
                errors.append(
                    f"[FILE ERROR] Undocumented file '{file_name}' in {doc_path.relative_to(root_path)}"
                )

        # 3. Check for obvious table row entries that reference files that don't exist
        # Look for table rows like `| filename | description |` or `| `filename` | description |`
        table_rows = re.findall(r"^\|\s*`?([a-zA-Z0-9_\-\.]+[\.a-zA-Z0-9]*)`?\s*\|", doc_content, re.MULTILINE)
        for referenced_file in table_rows:
            if referenced_file in ("File", "---", "Subdirectory", "Directory"):
                continue
            ref_path = current_dir / referenced_file
            if not ref_path.exists():
                errors.append(
                    f"[STALE DOC] Documented file '{referenced_file}' does not exist in {current_dir.relative_to(root_path)}"
                )

    return errors


def main():
    root_path = Path(__file__).resolve().parent.parent
    print(f"=== Project SunFlow Documentation Validator ===")
    print(f"Checking repository at: {root_path}")

    all_errors = []
    root_errors = check_root_files(root_path)
    all_errors.extend(root_errors)

    doc_errors = validate_directory_docs(root_path)
    all_errors.extend(doc_errors)

    if all_errors:
        print(f"\nFAILED: Found {len(all_errors)} documentation issues:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\nSUCCESS: All mandatory root files and directory documentation pass validation!")
        sys.exit(0)


if __name__ == "__main__":
    main()
