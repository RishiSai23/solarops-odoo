# Odoo Models Directory (`odoo_addons/sunflow_core/models/`)

## 1. Directory Overview
The `models/` directory contains Python model definitions for the `sunflow_core` Odoo module. These models extend Odoo's PostgreSQL schema to encapsulate the entire 19-stage solar lifecycle, including Phase 4 stock and procurement management.

## 2. Subdirectory Documentation
Currently, `models/` contains no subdirectories. All model definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Python package initialization importing all model definitions in correct dependency order. |
| `project_lifecycle.py` | Defines `solar.project`, the central lifecycle coordinator connecting CRM leads, surveys, sales orders, field installations, and gross margins. Includes auto-sequence generation and chatter/activity mixin. |
| `site_survey.py` | Defines `solar.survey`, capturing technical rooftop measurements, roof type, azimuth, tilt angles, shading factors, electrical grid specs (sanctioned load, meter phase, service voltage), feasibility status, and survey/shading notes. |
| `solar_package.py` | Defines `solar.package`, maintaining standardized 1kW – 5kW system configuration kits and component counts. Base model without Phase 4 fields. |
| `installation_order.py` | Defines `solar.installation`, capturing technician work orders, electrical safety checklists (torque, DC polarity, earthing), and customer handover signatures. |
| `warranty_registry.py` | Defines `solar.warranty`, recording equipment serial numbers (panels, inverters, batteries) and managing multi-year warranty terms, linked to native `stock.lot`. |
| `package_bom.py` | **Phase 4.** Defines `solar.package.component`, the lightweight BOM line model. Each line specifies a product, quantity, component category, and serial-tracking flag per solar package. Avoids the `mrp` module dependency. |
| `stock_requirement.py` | **Phase 4.** Defines `solar.stock.requirement`, per-project inventory demand lines generated from the package BOM. Caches stock snapshots from `stock.quant`, computes shortages, and provides actions to refresh stock and create purchase orders. |
| `equipment_dispatch.py` | **Phase 4.** Defines `solar.equipment.dispatch` (header) and `solar.equipment.dispatch.line` (component lines). Manages the project-linked dispatch workflow: serial number scanning, duplicate allocation prevention, and native `stock.picking.button_validate()` integration. |
| `solar_package_ext.py` | **Phase 4.** `_inherit` extensions for `solar.package` (adds `component_ids` one2many) and `solar.project` (adds `package_id`, `stock_requirement_ids`, `dispatch_ids`, stock readiness flags, and action methods for generating requirements, checking stock, and creating dispatches). |

## 4. Architectural Relationships
These models represent the authoritative database schema in Odoo PostgreSQL. They link directly to Odoo's native entities (`res.partner`, `crm.lead`, `sale.order`, `stock.lot`, `stock.quant`, `stock.picking`, `purchase.order`) and are exposed via the FastAPI gateway in `backend/app/odoo/client.py`.

## 5. Documentation Rules
- Every newly created model file must be registered in `__init__.py` and documented in the table above.
- Significant changes to model fields or computed methods must be updated here and reflected in root `learned.md`.
