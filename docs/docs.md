# Documentation Directory (`docs/`)

## 1. Directory Overview
The `docs/` directory houses detailed architectural specifications, lifecycle flow definitions, integration blueprints, and domain reference material for Project SunFlow. It serves as an in-depth companion to the root-level knowledge base.

## 2. Subdirectory Documentation
Currently, `docs/` contains no subdirectories. All architectural and process specifications reside directly in this directory.

## 3. File Documentation

| File | Responsibility |
|---|---|
| `architecture.md` | In-depth system architecture guide describing the dual-engine topology (Odoo ERP, FastAPI Gateway, React Client), communication mechanisms, and sandbox fallback. |
| `lifecycle_workflow.md` | Comprehensive 19-stage solar operations lifecycle specification covering stages from lead intake through field installation, warranty registration, and subsidy tracking. |

## 4. Architectural Relationships
The documents in `docs/` provide the technical theory and operational requirements implemented by `odoo_addons/` (authoritative models), `backend/` (API routes and business logic), and `frontend/` (user experience).

## 5. Documentation Rules
- Any new architectural blueprint, sequence diagram, or workflow guide placed in `docs/` must be documented in the table above.
- If a workflow stage or architectural component is altered, both `docs/` and root `learned.md` must be updated.
