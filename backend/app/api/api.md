# API Endpoints Directory (`backend/app/api/`)

## 1. Directory Overview
The `api/` directory contains FastAPI route controllers defining RESTful HTTP endpoints for project lifecycle queries, surveys, installation workflows, warranty registration, and analytics dashboards.

## 2. Subdirectory Documentation
Currently, `api/` contains no subdirectories. All route controllers reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Package initialization exporting the primary FastAPI router. |
| `routes.py` | Route definitions for `/api/v1/projects`, `/api/v1/surveys`, `/api/v1/warranties`, and `/api/v1/analytics`. |

## 4. Architectural Relationships
Routes in this directory receive validated requests parsed by `backend/app/schemas/` and call `backend/app/odoo/client.py` to retrieve or persist state in Odoo.

## 5. Documentation Rules
- Every new route handler file added to `api/` must be mounted in `routes.py` or `main.py` and documented in the table above.
- Endpoint changes must update API documentation in root `learned.md`.
