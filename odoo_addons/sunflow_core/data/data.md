# Data Directory (`odoo_addons/sunflow_core/data/`)

## 1. Directory Overview
The `data/` directory contains Odoo XML data files that are loaded during module installation. These define master data such as IR sequences, product categories, and other configuration records required for the SunFlow Core addon to function correctly.

## 2. Subdirectory Documentation
Currently, `data/` contains no subdirectories. All data files reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `solar_data.xml` | Defines IR sequences (`solar.project`, `solar.equipment.dispatch`), and product categories (`Solar Equipment`, `Solar Panels`, `Inverters`, `Battery Storage`, `BOS & Accessories`) used to categorize inventory products for solar components. |

## 4. Architectural Relationships
Data files in this directory are loaded by Odoo during `sunflow_core` installation, in the order specified under the `'data'` key in `__manifest__.py`. Sequences defined here are consumed by `solar.project.create()` and `solar.equipment.dispatch.create()` to generate human-readable reference codes. Product categories are used when registering solar products in the native Odoo inventory.

## 5. Documentation Rules
- Every new data file added to this directory must be declared in `__manifest__.py` (under `'data'`) and documented in the table above.
- Data files must be declared AFTER `security/ir.model.access.csv` and BEFORE view files in `__manifest__.py`.
- Changes to sequence codes or prefixes must be reflected in `learned.md` if they affect external integrations.

