# Data Directory (`odoo_addons/sunflow_core/data/`)

## 1. Directory Overview
The `data/` directory contains declarative data records loaded during addon installation, such as Odoo sequences that power auto-generated document references.

## 2. Subdirectory Documentation
Currently, `data/` contains no subdirectories. All data records reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `sequences.xml` | Defines the `ir.sequence` (`sunflow_core.site_survey`) used to generate unique `solar.survey` reference numbers (`SURV/YYYY/#####`). Owned by sunflow_core to avoid cross-addon dependency on `solar_management`. |

## 4. Architectural Relationships
`sequences.xml` is loaded automatically during addon installation (registered in `__manifest__.py`). It is consumed by `solar.survey.create()` (`models/site_survey.py`) to assign the `name` field.

## 5. Documentation Rules
- Any new XML data file added to `data/` must be declared in `__manifest__.py` and documented in the table above.
- Sequence codes must remain owned by sunflow_core and must not collide with sequences from other addons.
