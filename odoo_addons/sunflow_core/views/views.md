# Odoo Views Directory (`odoo_addons/sunflow_core/views/`)

## 1. Directory Overview
The `views/` directory contains XML definitions for Odoo user interfaces, including form views, tree/list views, inherited view extensions, action windows, sequences, and top-level navigation menus for SunFlow.

## 2. Subdirectory Documentation
Currently, `views/` contains no subdirectories. All XML view definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `lifecycle_views.xml` | Form and tree view definitions for `solar.project` tracking lifecycle stages, embedded surveys (with inline `<tree>` and `<form>` supporting the One2many modal dialog), work orders, and registered warranties. Dedicated form (`view_solar_survey_form`), tree (`view_solar_survey_tree`), and action (`action_solar_survey`) for `solar.survey`. Defines the `action_solar_project` window action. |
| `inventory_views.xml` | **Phase 4.** Views for `solar.package` (with BOM tab), `solar.package.component`, `solar.stock.requirement`, and `solar.equipment.dispatch`. Also contains `view_solar_project_form_phase4`, an `_inherit` extension adding the Inventory & Dispatch notebook page and smart buttons to the solar project form. Sequences for project and dispatch numbering. |
| `menu_views.xml` | Odoo application root and submenu definitions creating the "SolarOps" top-level menu with "Operations" (Projects, Site Surveys) and "Inventory" sub-menus including Solar Packages, Stock Requirements, Stock Shortages, and Equipment Dispatches. |

## 4. Architectural Relationships
These views render data modeled in `odoo_addons/sunflow_core/models/` inside standard Odoo web clients and are registered in `odoo_addons/sunflow_core/__manifest__.py`. The Phase 4 views inherit from existing views using `<field name="inherit_id">` to avoid overwriting original form layouts.

## 5. Documentation Rules
- Any new XML view or menu file added to this directory must be declared in `__manifest__.py` and documented in the table above.
- Changes to view actions or statusbars must be documented here.
- Inherited views must reference the base view's XML ID using the `ref()` function.
