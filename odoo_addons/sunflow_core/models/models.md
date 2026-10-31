# Odoo Models Directory (`odoo_addons/sunflow_core/models/`)

## 1. Directory Overview
The `models/` directory contains Python model definitions for the `sunflow_core` Odoo module. These models extend Odoo's PostgreSQL schema to encapsulate the entire 19-stage solar lifecycle.

## 2. Subdirectory Documentation
Currently, `models/` contains no subdirectories. All model definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Python package initialization importing all model definitions. |
| `project_lifecycle.py` | Defines `solar.project`, the central lifecycle coordinator connecting CRM leads, surveys, sales orders, field installations, and gross margins. |
| `site_survey.py` | Defines `solar.survey`, capturing technical rooftop measurements, azimuth, tilt angles, shading factors, and grid feasibility. |
| `solar_package.py` | Defines `solar.package`, maintaining standardized 1kW – 5kW system configuration kits and component counts. |
| `installation_order.py` | Defines `solar.installation`, capturing technician work orders, electrical safety checklists, and customer handover signatures. |
| `warranty_registry.py` | Defines `solar.warranty`, recording equipment serial numbers (panels, inverters, batteries) and managing multi-year warranty terms. |

## 4. Architectural Relationships
These models represent the authoritative database schema in Odoo PostgreSQL. They link directly to Odoo's native entities (`res.partner`, `crm.lead`, `sale.order`, `stock.lot`) and are exposed via the FastAPI gateway in `backend/app/odoo/client.py`.

## 5. Documentation Rules
- Every newly created model file must be registered in `__init__.py` and documented in the table above.
- Significant changes to model fields or computed methods must be updated here and reflected in root `learned.md`.
