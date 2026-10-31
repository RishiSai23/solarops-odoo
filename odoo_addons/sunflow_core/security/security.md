# Odoo Security Directory (`odoo_addons/sunflow_core/security/`)

## 1. Directory Overview
The `security/` directory contains access control lists (ACLs) and security rules that govern user and administrator permissions for all custom solar models.

## 2. Subdirectory Documentation
Currently, `security/` contains no subdirectories. All security definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `ir.model.access.csv` | Standard Odoo Access Control List granting read/write/create/unlink permissions on solar models to base users and managers. Includes entries for `solar.survey.reject.wizard` granted to `base.group_user` and `base.group_system`. |

## 4. Architectural Relationships
`ir.model.access.csv` is loaded automatically during addon installation by Odoo's ORM, enforcing security boundaries for internal users and external RPC calls.

Role separation relies on the existing groups `base.group_user` (surveyor) and `base.group_system` (manager/administrator). No custom solar groups are introduced to avoid cross-addon dependencies (the separate `solar_management` addon is not a dependency of `sunflow_core`).

Critical permissions are enforced server-side in Python methods, not only through XML button visibility:
- `solar.survey.action_approve()` blocks a surveyor from approving their own survey (`site_survey.py`).
- `solar.survey.reject.wizard.action_reject_confirm()` blocks a surveyor from rejecting their own survey (`survey_reject_wizard.py`).
- `solar.survey.action_reset_draft()` requires `base.group_system` via `_check_manager_rights()` (`site_survey.py`).
- `solar.project.action_create_quotation()` and `_check_quotation_eligibility()` enforce survey approval + feasibility before a Sales Order is linked (`project_lifecycle.py`).

## 5. Documentation Rules
- Every new model introduced into `models/` must have corresponding access control entries added to `ir.model.access.csv`.
- Changes to user or group permissions must be documented in this file.
- No record rules (`ir.rule`) are defined; access is group-based plus Python method enforcement, consistent with the existing addon design.
