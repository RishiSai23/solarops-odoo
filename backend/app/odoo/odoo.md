# Odoo Integration Directory (`backend/app/odoo/`)

## 1. Directory Overview
The `odoo/` directory implements communication bridges and adapters between the FastAPI gateway and the Odoo ERP server, including XML-RPC protocol management and an automated offline sandbox adapter.

## 2. Subdirectory Documentation
Currently, `odoo/` contains no subdirectories. All connector and mock logic resides directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `__init__.py` | Package initialization exporting `odoo_client` singleton and adapter classes. |
| `client.py` | Primary XML-RPC client handling authentication, remote procedure calls, data transformation, and graceful fallback. |
| `mock_adapter.py` | In-memory sandbox adapter that simulates the Odoo solar lifecycle when the Odoo server is offline or during testing. |

## 4. Architectural Relationships
`client.py` is invoked by `backend/app/api/routes.py` to fetch, persist, and update solar lifecycle records in Odoo PostgreSQL.

## 5. Documentation Rules
- Any modification to RPC connection protocols, retry logic, or mock fixtures must be documented in this table.
- Changes in Odoo authentication parameters must be reflected in `app/config.py` and `learned.md`.
