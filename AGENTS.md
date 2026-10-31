# Project SunFlow — Agent Engineering Handbook (`AGENTS.md`)

Welcome to **Project SunFlow**, the Unified Solar Operations & Lifecycle Management Platform built for the **Odoo × GCET Hackathon Finale**.

This document is the **primary instruction manual** for all AI coding agents (and human engineers) contributing to this codebase. All autonomous agents must adhere strictly to the protocols, navigation sequences, coding standards, and documentation requirements established herein.

---

## 1. Project Mission & Business Context

Project SunFlow is an integrated ERP-driven operational management platform designed specifically for residential and commercial solar EPC (Engineering, Procurement, and Construction) companies. 

### Core Product Principle
> **ONE CUSTOMER. ONE PROJECT RECORD. ONE CONNECTED OPERATIONAL LIFECYCLE.**

Rather than operating as a set of disconnected CRUD applications, SunFlow tracks a single customer journey across all 19 lifecycle stages:
1. Customer enquiry & CRM lead capture.
2. Lead qualification & energy assessment.
3. Rooftop site survey & technical feasibility (tilt, azimuth, shade, electrical load).
4. Solar package configuration (1 kW – 5 kW On-Grid / Off-Grid / Hybrid).
5. Automated Bill of Materials (BOM) generation.
6. Quotation & sales order workflow.
7. Milestone payment tracking (Advance, Delivery, Commissioning).
8. Inventory reservation & warehouse picking.
9. Mandatory serial number scanning & traceability (panels, inverters, batteries).
10. Material dispatch & site delivery verification.
11. Technician scheduling & field dispatch (managing 15 technicians).
12. Installation execution with geo-tagged photographic evidence & electrical checklist.
13. Digital customer acceptance & electronic handover sign-off.
14. Automatic warranty registration linked to scanned serial numbers.
15. After-sales service ticketing & SLA tracking.
16. Warranty validation, RMA, and repair management.
17. Real-time project profitability & cost accounting.
18. Subsidy compliance & documentation tracking (PM Surya Ghar / State net metering).
19. Executive management analytics & KPI dashboards.

### Reference Organization: SunPower Solutions
- 40+ solar installations per month.
- 15 field technicians deployed across active project sites.
- Packages: 1 kW to 5 kW (expandable to small C&I).
- High-value serialized assets: Solar PV panels, solar string/hybrid inverters, lithium battery banks, charge controllers.
- Multi-decade warranty liabilities (25-year panel performance, 5–10 year inverter warranty).

---

## 2. Overall System Architecture

The SunFlow platform leverages a **Dual-Engine Architecture**:

```
+---------------------------------------------------------------------------+
|                      CLIENT TIERS (React / TypeScript)                   |
|  - Operations & Executive Hub (Web)    - Field Operations & Survey (PWA) |
+---------------------------------------------------------------------------+
                                     |  REST API / JSON
                                     v
+---------------------------------------------------------------------------+
|              BACKEND ORCHESTRATION GATEWAY (Python / FastAPI)             |
|  - Workflow Orchestrator   - Serial Validator   - Media/Evidence Handler  |
|  - Mock / Sandbox Engine   - Odoo XML-RPC / JSON-RPC Client               |
+---------------------------------------------------------------------------+
                                     |  RPC (Odoo External API)
                                     v
+---------------------------------------------------------------------------+
|                  NATIVE ODOO ERP (Odoo 17/18 Community/Enterprise)        |
|  - Authoritative PostgreSQL Database                                      |
|  - Core Modules: crm, sale_management, stock, account, project, repair    |
|  - Custom Addon: sunflow_core (Models: solar.project, solar.survey, etc.) |
+---------------------------------------------------------------------------+
```

1. **Authoritative ERP Core (`odoo_addons/sunflow_core`)**:
   - Odoo serves as the **single source of truth** for all business data.
   - Solar-specific lifecycle models (`solar.project`, `solar.survey`, `solar.package`, `solar.installation`, `solar.warranty`, `solar.service.ticket`) reside directly in the native Odoo module.
2. **API & Orchestration Gateway (`backend/`)**:
   - High-performance Python FastAPI service.
   - Handles fast client requests, barcode/serial scanning validations, image streaming, and offline sync payloads.
   - Communicates with Odoo via authenticated XML-RPC / JSON-RPC. Includes an integrated sandbox adapter when running without an active Odoo instance.
3. **Responsive Client Applications (`frontend/`)**:
   - Single-Page Application (SPA) powered by React 18, Vite, TypeScript, and Tailwind CSS.
   - Rich UX tailored for executive oversight (Recharts, metric cards) and streamlined field engineer workflows (touch-friendly checklists, photo capture, digital signature).

---

## 3. Repository Directory Structure

```
solarops-odoo/
├── AGENTS.md                    # Primary instructions for AI agents (this file)
├── learned.md                   # Central technical & business knowledge repository
├── progress.md                  # Development progress checklist & task tracker
├── README.md                    # Public repository presentation & overview
├── ENGINEERING_PROTOCOL.md      # High-discipline engineering & architectural protocols
├── .gitignore                   # Version control ignore definitions
├── docs/                        # Architectural diagrams & specifications
│   ├── docs.md                  # Directory documentation
│   ├── architecture.md          # Architectural deep-dive
│   └── lifecycle_workflow.md    # 19-stage lifecycle technical specification
├── odoo_addons/                 # Native Odoo modules
│   ├── odoo_addons.md           # Directory documentation
│   └── sunflow_core/            # Custom Odoo addon for solar operations
│       ├── sunflow_core.md      # Addon documentation
│       ├── __init__.py          # Module Python package init
│       ├── __manifest__.py      # Odoo module manifest
│       ├── models/              # Business data models
│       ├── security/            # Access control lists (ir.model.access.csv)
│       └── views/               # Odoo XML UI views and menus
├── backend/                     # FastAPI Orchestration Gateway
│   ├── backend.md               # Directory documentation
│   ├── requirements.txt         # Python runtime dependencies
│   ├── pyproject.toml           # Backend packaging & linting config
│   └── app/                     # FastAPI application source
│       ├── app.md               # App directory documentation
│       ├── main.py              # Application entrypoint & CORS config
│       ├── config.py            # Environment settings & configuration
│       ├── api/                 # REST API route handlers
│       ├── odoo/                # Odoo RPC client & sandbox adapter
│       └── schemas/             # Pydantic request/response schemas
├── frontend/                    # React / Vite Client Application
│   ├── frontend.md              # Directory documentation
│   ├── package.json             # NPM package definitions
│   ├── tsconfig.json            # TypeScript compiler configuration
│   ├── vite.config.ts           # Vite build & proxy settings
│   ├── index.html               # Web HTML entrypoint
│   ├── tailwind.config.js       # Tailwind CSS design system tokens
│   ├── postcss.config.js        # PostCSS configuration
│   └── src/                     # React source code
│       ├── src.md               # Source directory documentation
│       ├── main.tsx             # Application bootstrap
│       ├── App.tsx              # Root React component & Router
│       ├── index.css            # Base stylesheet & Tailwind utilities
│       ├── components/          # Reusable UI components
│       ├── pages/               # Application view screens
│       ├── services/            # API client services
│       └── types/               # TypeScript domain interfaces
├── docker/                      # Containerization & local deployment
│   ├── docker.md                # Directory documentation
│   ├── docker-compose.yml       # Multi-service stack (Odoo, DB, Gateway, Web)
│   └── odoo.conf                # Odoo server runtime configuration
└── scripts/                     # Developer tooling & QA automation
    ├── scripts.md               # Directory documentation
    └── validate_docs.py         # Automated documentation validation script
```

---

## 4. Mandatory Agent Navigation Procedure

Before implementing or modifying ANY code in this repository, every AI agent MUST execute the following sequence:

1. **Read root `AGENTS.md`**: Understand system rules, standards, and workflow principles.
2. **Read root `learned.md`**: Check recent architectural decisions, domain discoveries, and past learnings.
3. **Read root `progress.md`**: Confirm the current phase, active task status, and dependencies.
4. **Read the relevant directory's markdown documentation** (`<directory_name>/<directory_name>.md`): Review existing files and architectural relationships.
5. **Inspect the existing code**: Never overwrite or duplicate functionality without inspecting existing files first.
6. **Identify dependencies & impact**: Review which upstream and downstream layers are affected.
7. **Implement the requested change**: Write clean, modular, self-documenting code.
8. **Update the parent directory's markdown documentation**: Ensure any newly created, renamed, or modified file is documented with its exact responsibility.
9. **Update `learned.md`**: If any architectural decision, technical pattern, or discovery was made.
10. **Update `progress.md`**: Update task completion status or add new subtasks.
11. **Run validation checks**: Execute `python scripts/validate_docs.py` to guarantee compliance.

---

## 5. Coding & Architectural Conventions

### A. General Principles
- **No Duplicate Logic**: If Odoo provides an authoritative calculation (e.g. tax, discount, inventory reservation), do not reinvent a divergent version in the frontend.
- **Defensive Input Validation**: Validate inputs at every layer using Pydantic (Backend) and TypeScript interfaces (Frontend).
- **Environment Parity**: Never hardcode credentials, IP addresses, or secrets. Use environment variables with sensible defaults.

### B. Python / Backend Conventions
- Standard: Python 3.10+, PEP 8 compliance.
- Framework: FastAPI with asynchronous route handlers where IO-bound.
- Schema Validation: Pydantic v2 schemas for all request payloads and response models.
- Logging: Use Python's built-in `logging` module with structured messages.

### C. Frontend / TypeScript Conventions
- Standard: TypeScript strict mode enabled.
- Styling: Tailwind CSS using curated design tokens. Avoid hardcoded hex colors when semantic classes are available.
- Icons: `lucide-react`.
- State & Data Fetching: TanStack React Query for remote data, React hooks for local component state.
- Component Design: Single responsibility, small composable components.

### D. Odoo Addon Conventions
- Target Version: Odoo 17.0 / 18.0 Community / Enterprise.
- Model Naming: `solar.<entity_name>` (e.g., `solar.project`, `solar.survey`).
- Field Naming: Snake_case with descriptive prefixes (`installation_date`, `assigned_technician_id`).
- Security: Every model must have explicit entry in `security/ir.model.access.csv`.

---

## 6. Mandatory Documentation Protocol

Every directory must maintain a Markdown file named after that directory: `<directory_name>/<directory_name>.md`.

Each directory documentation file must include:
1. **Directory Overview**: 2–3 line summary of responsibilities.
2. **Subdirectory Documentation**: List of subdirectories with 1-line purpose.
3. **File Documentation Table**: Exhaustive table containing EVERY immediate file:
   | File | Responsibility |
   |---|---|
   | `<filename>` | Precise responsibility, connections, and why it exists. |
4. **Architectural Relationships**: Explanation of inbound and outbound communication.
5. **Documentation Rules**: Maintenance rules and verification reminder.

**Enforcement**: Run `python scripts/validate_docs.py`. A failure in this script means the pull request / commit is defective.

---

## 7. How to Update Project Knowledge

- **Updating `progress.md`**: Check items `[x]` ONLY when the implementation is completed, tested, and validated. If blocked, mark as `BLOCKED` with an explanation.
- **Updating `learned.md`**: Whenever a technical discovery, API integration quirk, or architectural trade-off occurs, record it under the appropriate section in `learned.md`.
- **Nested `AGENTS.md`**: When working in a deep, specialized subsystem (such as an embedded offline sync engine), a local `AGENTS.md` may be created to supplement root instructions.
