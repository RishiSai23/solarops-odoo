# Odoo Typings Directory (`typings/odoo/`)

## 1. Directory Overview
The `typings/odoo/` directory provides type stubs for the native Odoo framework classes used across custom addons in `odoo_addons/`.

## 2. Subdirectory Documentation
This directory contains no subdirectories.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.pyi` | Type stub declarations for `models.Model`, `fields.*`, `api.*`, and `exceptions` to satisfy IDE and static analyzer import resolution. |
| `exceptions.pyi` | Type stub declarations for native Odoo exceptions (`UserError`, `ValidationError`, `AccessError`, etc.). |

## 4. Architectural Relationships
Referenced by Pyright and VS Code Pylance to validate Odoo model definitions in `odoo_addons/sunflow_core/models/`.

## 5. Documentation Rules
- Any additional `.pyi` stub files added to this directory must be documented in the File Documentation table.
