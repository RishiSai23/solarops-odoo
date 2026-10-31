# SunFlow Core Addon Directory (`odoo_addons/sunflow_core/`)

## 1. Directory Overview
`sunflow_core` is the native Odoo module for Project SunFlow. It implements authoritative data models, business workflows, views, and security rules that govern the 19-stage solar operations lifecycle directly in Odoo. Phase 4 adds full inventory and procurement integration: BOM management, stock requirement generation, shortage detection, procurement linkage, and serialized equipment dispatch.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `models/` | Python data models defining the complete solar lifecycle. Phase 1–3: `solar.project`, `solar.survey`, `solar.package`, `solar.installation`, `solar.warranty`. Phase 4: `solar.package.component` (BOM), `solar.stock.requirement` (demand), `solar.equipment.dispatch` + `solar.equipment.dispatch.line` (serialized dispatch), plus `_inherit` extensions for `solar.package` and `solar.project`. |
| `views/` | Odoo XML views (form, tree, inherited extensions) and top-level navigation menus. Phase 4 adds `inventory_views.xml` with full BOM, requirements, shortages, and dispatch UI. |
| `security/` | Access control lists defining user and manager permissions for all custom models (`ir.model.access.csv`). Phase 4 adds ACL rows for the 3 new models (5 new model classes → 6 new ACL rows). |
| `data/` | XML master data files loaded at installation: IR sequences for project and dispatch references, and solar product category hierarchy. |
| `tests/` | Odoo `TransactionCase` unit and integration tests. Phase 4 includes 25 test cases covering BOM, stock requirements, serial validation, dispatch workflow, and project integration. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Python package initialization file importing the `models` sub-package. |
| `__manifest__.py` | Odoo module manifest (v17.0.2.0.0) defining metadata, dependencies (`crm`, `sale_management`, `stock`, `purchase`, `account`, `repair`), and ordered data file list. |

## 4. Architectural Relationships
`sunflow_core` is installed in Odoo, extending standard Odoo models (`product.product`, `stock.quant`, `stock.picking`, `stock.lot`, `purchase.order`) and exposing records to the FastAPI backend via Odoo's external RPC interface. The `purchase` module is a new Phase 4 dependency.

## 5. Documentation Rules
- Any new model, security rule, view, or data file added to `sunflow_core` must be documented in its respective subdirectory markdown file.
- Changes to dependencies in `__manifest__.py` must be reflected here and in root `learned.md`.
- Every new subdirectory created inside `sunflow_core` must have its own `<dir_name>.md` file.
