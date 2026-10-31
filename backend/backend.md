# Backend Directory (`backend/`)

## 1. Directory Overview
The `backend/` directory houses the FastAPI orchestration gateway for Project SunFlow. It provides high-performance REST APIs for client applications, bridges with Odoo's XML-RPC interface, and provides an offline sandbox engine.

## 2. Subdirectory Documentation

| Subdirectory | Responsibility |
|---|---|
| `app/` | Core application source containing FastAPI entrypoint, configuration, API routes, Odoo client adapter, and Pydantic schemas. |

## 3. File Documentation

| File | Responsibility |
|---|---|
| `Dockerfile` | Multi-stage container build instructions for running the FastAPI service in production or Docker Compose. |
| `pyproject.toml` | Standard Python packaging configuration, tool specifications, and pytest options. |
| `requirements.txt` | Python dependency specifications including FastAPI, Uvicorn, Pydantic, and Requests. |

## 4. Architectural Relationships
The backend acts as an intermediary: it accepts RESTful requests from `frontend/`, executes validations, interacts with `odoo_addons/sunflow_core` via Odoo XML-RPC, and returns normalized JSON responses.

## 5. Documentation Rules
- Any root file added to `backend/` must be documented in the table above.
- Subdirectories must be documented in their respective `<subdirname>.md` files.
- Python dependencies modified in `requirements.txt` must be reflected in `learned.md`.
