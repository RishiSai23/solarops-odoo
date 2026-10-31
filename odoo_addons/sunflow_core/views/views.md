# Odoo Views Directory (`odoo_addons/sunflow_core/views/`)

## 1. Directory Overview
The `views/` directory contains XML definitions for Odoo user interfaces, including form views, tree/list views, kanban stages, action windows, and top-level navigation menus for SunFlow.

## 2. Subdirectory Documentation
Currently, `views/` contains no subdirectories. All XML view definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `lifecycle_views.xml` | Form and tree view definitions for `solar.project` tracking lifecycle stages, embedded surveys, work orders, and registered warranties. |
| `menu_views.xml` | Odoo application root and submenu definitions creating the "SunFlow Solar" menu in the standard Odoo top bar. |

## 4. Architectural Relationships
These views render data modeled in `odoo_addons/sunflow_core/models/` inside standard Odoo web clients and are registered in `odoo_addons/sunflow_core/__manifest__.py`.

## 5. Documentation Rules
- Any new XML view or menu file added to this directory must be declared in `__manifest__.py` and documented in the table above.
- Changes to view actions or statusbars must be documented here.
