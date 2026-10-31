# Scripts Directory (`scripts/`)

## 1. Directory Overview
The `scripts/` directory contains developer automation, quality assurance, verification, and database seeding utilities for Project SunFlow. It provides continuous compliance checks and operational helpers that can be executed locally or inside CI/CD pipelines.

## 2. Subdirectory Documentation
Currently, `scripts/` has no subdirectories. All foundation-level utility scripts are located directly in this root utility folder.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `seed_solarops_e2e.py` | Master synthetic data generation and seeding engine for all 9 custom SolarOps models. Supports Pilot (10 records/model) and Full (250/300 records/model) execution, enforces electrical compatibility and serial uniqueness, uses Odoo supported inventory adjustments, and executes an automated integrity audit. |
| `validate_docs.py` | Automated documentation validation script that enforces Project SunFlow's mandatory documentation rules across all directories. |
| `verify_phase4_runtime.py` | Runtime verification and testing engine for Phase 4 Stock & Procurement. Executes the 25 `TransactionCase` tests directly against the actual `sunflow_core` models and verifies all end-to-end inventory workflows (BOM, shortages, procurement POs, incoming receipts, serialized dispatch, duplicate lot prevention, and customer equipment retrieval). |
| `verify_survey_lifecycle_e2e.py` | End-to-end HTTP JSON-RPC runtime verification script testing the complete survey-to-project lifecycle integration: survey approval to `feasible`, automatic project stage transition to `feasibility`, manual sign-off to `quotation`, and testing all 6 business rules (draft guard, rejected guard, conditional guard, grid compatibility constraint, multiple survey precedence, and non-destructive survey updates). |
| `verify_survey_popup_e2e.py` | End-to-end HTTP JSON-RPC runtime verification script testing Site Surveys One2many modal dialog behavior on `solar.project` (SPF-0117), validating embedded form view architecture, default context propagation, survey persistence, and all 15 solar engineering fields. |

## 4. Architectural Relationships
`scripts/validate_docs.py` traverses the entire repository tree, reading every directory and its corresponding `<directory_name>.md` file to guarantee that newly added or modified source files are properly documented and that no stale file references exist.

## 5. Documentation Rules
- Every script added to `scripts/` must be documented in the table above with its direct operational responsibility.
- Deleted scripts must be immediately removed from this file.
- Any modification to script behavior or parameters must be updated in this file.
