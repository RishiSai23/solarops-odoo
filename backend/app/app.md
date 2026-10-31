# Application Core Directory (`backend/app/`)

## 1. Directory Overview
The `app/` directory contains the FastAPI server entrypoint, global environment configuration, route controllers, Odoo integration adapters, and data validation schemas.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `api/` | RESTful route handlers exposing lifecycle operations, analytics, surveys, and warranties. |
| `odoo/` | XML-RPC connection client, authentication handlers, and offline sandbox adapter. |
| `schemas/` | Pydantic validation models defining API contracts and serialization schemas. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `config.py` | Centralized environment configuration and Odoo connection credentials loaded using Pydantic Settings. |
| `main.py` | FastAPI application bootstrap, lifespan lifecycle management, CORS middleware configuration, and router mounting. |

## 4. Architectural Relationships
`app/main.py` is the primary entrypoint for Uvicorn. It mounts route handlers from `api/`, which validate inputs via `schemas/` and query Odoo via `odoo/`.

## 5. Documentation Rules
- Any top-level file added to `backend/app/` must be registered in the table above.
- Subdirectories must maintain their own respective `<dirname>.md` documentation.
