# Schemas Directory (`backend/app/schemas/`)

## 1. Directory Overview
The `schemas/` directory defines Pydantic models for request validation, response serialization, and contract enforcement between the frontend clients and the FastAPI orchestration gateway.

## 2. Subdirectory Documentation
Currently, `schemas/` contains no subdirectories. All schema models reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Package initialization exporting core Pydantic models for project lifecycle and validation. |
| `project.py` | Defines data validation schemas for solar projects, site surveys, installation checklists, warranties, and responses. |

## 4. Architectural Relationships
Schemas in this directory validate HTTP request bodies received by `backend/app/api/routes.py` and serialize internal domain data into JSON sent to the frontend.

## 5. Documentation Rules
- Every newly created schema file must be imported in `__init__.py` and documented in the table above.
- Changes to API validation constraints must be reflected here and in root `learned.md`.
