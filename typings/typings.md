# Typings Directory (`typings/`)

## 1. Directory Overview
The `typings/` directory contains Python type stub files (`.pyi`) for external runtime environments (such as Odoo) that run inside Docker containers or external servers, providing type resolution and code intelligence to IDE language servers (Pyright / Pylance).

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `odoo/` | Type definitions and interface stubs for Odoo core classes (`models`, `fields`, `api`, `exceptions`). |

## 3. File Documentation
This directory contains only subdirectories and this documentation file. No standalone root files exist in `typings/`.

## 4. Architectural Relationships
Configured via `pyrightconfig.json` (`stubPath: "typings"`), enabling seamless static analysis across `odoo_addons/` without requiring Odoo to be installed directly in the host OS Python interpreter.

## 5. Documentation Rules
- Any additional library stubs added to `typings/` must be listed in the Subdirectory Documentation table.
