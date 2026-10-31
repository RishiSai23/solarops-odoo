# Backend Addons Directory (`backend/addons/`)

## 1. Directory Overview
The `addons/` directory contains supplemental Odoo addon modules bundled with the backend repository for development, demonstration, or staging use. These addons are separate from the primary `odoo_addons/sunflow_core` addon in the repository root.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `solar_management/` | Supplemental solar management Odoo addon providing additional sequences, views, and security configurations for backend-bundled development instances. |

## 3. File Documentation
No standalone files exist at this directory level — all content is within subdirectories.

## 4. Architectural Relationships
Addons in this directory are intended for development and demo deployments. The authoritative addon for production use is `odoo_addons/sunflow_core/` in the repository root. These backend-bundled addons may provide supplemental configuration or experimental features.

## 5. Documentation Rules
- Every addon subdirectory must have its own `<addon_name>.md` documentation file.
- Changes to addon dependencies must be reflected in `__manifest__.py` and documented here.

