# Odoo Addons Directory (`odoo_addons/`)

## 1. Directory Overview
The `odoo_addons/` directory contains custom native Odoo modules developed for Project SunFlow. These modules extend Odoo's native data models, views, and security configurations to support end-to-end solar lifecycle operations.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `sunflow_core/` | Core custom Odoo addon defining the authoritative solar lifecycle models (`solar.project`, `solar.survey`, `solar.package`, `solar.installation`, `solar.warranty`), security access rules, and backend views. |

## 3. File Documentation
This directory contains only addon subdirectories and this documentation file. No standalone root files exist in `odoo_addons/`.

## 4. Architectural Relationships
Modules in `odoo_addons/` are loaded by Odoo during server startup via the `--addons-path` parameter (or `/mnt/extra-addons` mount in Docker). They interact directly with native Odoo apps (`crm`, `sale`, `stock`, `account`, `repair`) and provide the data schema queried by `backend/app/odoo/client.py`.

## 5. Documentation Rules
- Every custom Odoo addon created in `odoo_addons/` must have a corresponding entry in the Subdirectory Documentation section.
- Each addon must maintain its own internal directory markdown file (`<addon_name>/<addon_name>.md`).
