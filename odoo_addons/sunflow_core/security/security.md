# Odoo Security Directory (`odoo_addons/sunflow_core/security/`)

## 1. Directory Overview
The `security/` directory contains access control lists (ACLs) and security rules that govern user and administrator permissions for all custom solar models.

## 2. Subdirectory Documentation
Currently, `security/` contains no subdirectories. All security definitions reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `ir.model.access.csv` | Standard Odoo Access Control List granting read/write/create/unlink permissions on solar models to base users and managers. |

## 4. Architectural Relationships
`ir.model.access.csv` is loaded automatically during addon installation by Odoo's ORM, enforcing security boundaries for internal users and external RPC calls.

## 5. Documentation Rules
- Every new model introduced into `models/` must have corresponding access control entries added to `ir.model.access.csv`.
- Changes to user or group permissions must be documented in this file.
