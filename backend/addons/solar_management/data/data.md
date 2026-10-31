# Data Directory (`backend/addons/solar_management/data/`)

## 1. Directory Overview
Contains XML data files loaded by the `solar_management` addon during Odoo installation.

## 2. Subdirectory Documentation
No subdirectories.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `sequences.xml` | Defines IR sequences (e.g., project reference numbers) for the backend-bundled solar_management addon. |

## 4. Architectural Relationships
Sequences defined here are used by model `create()` methods in the `solar_management` addon to generate human-readable reference codes.

## 5. Documentation Rules
- Every new data file added must be listed in the file table and declared in `__manifest__.py`.

