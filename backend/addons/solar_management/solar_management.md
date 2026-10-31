# Solar Management Addon (`backend/addons/solar_management/`)

## 1. Directory Overview
`solar_management` is a supplemental Odoo addon bundled with the backend for development and demo instances. It provides additional sequence definitions, security groups, and menu views for backend-bundled Odoo deployments.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `data/` | XML data files defining IR sequences for this addon. |
| `models/` | Python model definitions (currently empty/placeholder). |
| `security/` | Security group and record rule definitions. |
| `views/` | Menu and action XML views for the backend-bundled Odoo instance. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Python package initialization for the Odoo addon. |
| `__manifest__.py` | Odoo module manifest defining addon metadata, dependencies, and data file list. |

## 4. Architectural Relationships
This addon supplements the authoritative `sunflow_core` addon. For production deployments, use `odoo_addons/sunflow_core/` instead. This addon is loaded when running a backend-local Odoo instance for development.

## 5. Documentation Rules
- Changes to this addon's manifest dependencies must be documented here.
- Any new model, view, or security file added must be listed in the file table.

