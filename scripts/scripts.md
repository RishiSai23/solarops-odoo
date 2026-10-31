# Scripts Directory (`scripts/`)

## 1. Directory Overview
The `scripts/` directory contains developer automation, quality assurance, verification, and database seeding utilities for Project SunFlow. It provides continuous compliance checks and operational helpers that can be executed locally or inside CI/CD pipelines.

## 2. Subdirectory Documentation
Currently, `scripts/` has no subdirectories. All foundation-level utility scripts are located directly in this root utility folder.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `validate_docs.py` | Automated documentation validation script that enforces Project SunFlow's mandatory documentation rules across all directories. |

## 4. Architectural Relationships
`scripts/validate_docs.py` traverses the entire repository tree, reading every directory and its corresponding `<directory_name>.md` file to guarantee that newly added or modified source files are properly documented and that no stale file references exist.

## 5. Documentation Rules
- Every script added to `scripts/` must be documented in the table above with its direct operational responsibility.
- Deleted scripts must be immediately removed from this file.
- Any modification to script behavior or parameters must be updated in this file.
