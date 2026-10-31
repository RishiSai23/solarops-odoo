# SunFlow Core Addon Directory (`odoo_addons/sunflow_core/`)

## 1. Directory Overview
`sunflow_core` is the native Odoo module for Project SunFlow. It implements authoritative data models, business workflows, views, and security rules that govern the 19-stage solar operations lifecycle directly in Odoo.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `models/` | Python data models defining `solar.project`, `solar.survey`, `solar.package`, `solar.installation`, and `solar.warranty`. |
| `security/` | Access control lists defining user and manager permissions (`ir.model.access.csv`). |
| `views/` | Odoo XML views (form, tree, kanban) and top-level navigation menus. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Python package initialization file importing models. |
| `__manifest__.py` | Odoo module manifest defining metadata, dependencies (`crm`, `sale`, `stock`, `account`), and view assets. |

## 4. Architectural Relationships
`sunflow_core` is installed in Odoo, extending standard Odoo models and exposing records to the FastAPI backend via Odoo's external RPC interface.

## 5. Documentation Rules
- Any new model, security rule, or view added to `sunflow_core` must be documented in its respective subdirectory markdown file.
- Changes to dependencies in `__manifest__.py` must be reflected here and in root `learned.md`.
