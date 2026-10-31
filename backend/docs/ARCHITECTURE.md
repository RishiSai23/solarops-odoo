# SolarOps Architecture Specification

## 1. Overview & System Philosophy

**SolarOps** is designed as a native **Odoo 17 Modular Monolith** for end-to-end solar installation lifecycle management. The system supports lead qualification, technical rooftop surveys, package engineering, bill of materials (BOM), quotation generation, inventory control with equipment serialization, installation logistics, warranty compliance, and after-sales service operations.

### Why a Native Odoo Modular Monolith?

Rather than distributing domain logic across disparate microservices (e.g., custom web frameworks, separate standalone relational databases, and third-party workflow engines) which introduce distributed transaction overhead, network latency, synchronization bugs, and integration brittleness, SolarOps leverages Odoo's native architecture:

1. **Tight Data Consistency & ACID Guarantees**: Solar operations involve financial commitments (down payments, milestone invoices, subsidies) directly tied to physical equipment inventory (panels, inverters, racking) and field operations. A unified PostgreSQL transactional layer ensures zero reconciliation drift between operational events and financial records.
2. **Built-in Enterprise Capabilities**: Out-of-the-box support for multi-currency, multi-company, document generation (PDF quotations, installation sign-offs), auditing/chatter feeds, automated email notifications, and role-based access control (RBAC).
3. **Extensibility via Python ORM and XML**: Odoo's inheritance model (`_inherit`) allows clean modular extension of core models (`res.partner`, `sale.order`, `stock.lot`, `account.move`) without monkey-patching or diverging from upstream Odoo improvements.
4. **Unified Operations UI**: Field technicians, project managers, sales teams, and accountants work within a coherent, reactive web client without maintaining bespoke frontend-to-backend glue APIs during initial operational rollout.

---

## 2. Platform Architecture & Layer Responsibilities

```
+--------------------------------------------------------------------------+
|                       Presentation Layer (Odoo Web Client)               |
|            Views: Form, Tree/List, Kanban, Calendar, Pivot, Graph        |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                  Application & Business Logic Layer                      |
|                  Odoo 17.0 Community Engine (Python 3.10+)               |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |                  SolarOps Custom Module Domain                   |   |
|   |                   (addons/solar_management)                      |   |
|   |  - Lead Pipeline & Feasibility   - Site Survey Geometry          |   |
|   |  - BOM & System Sizing           - Installation Milestones       |   |
|   |  - Serialized Lot Tracking       - Warranties & After-Sales      |   |
|   +------------------------------------------------------------------+   |
|                                    | (Odoo ORM / Model Inheritance)      |
|   +------------------------------------------------------------------+   |
|   |                  Odoo Native Framework Core                      |   |
|   |  - ORM Engine                    - Access Control & Record Rules |   |
|   |  - Automated Sequences           - Web Controllers & Routing     |   |
|   |  - Mail / Chatter Bus            - Report Engine (QWeb)          |   |
|   +------------------------------------------------------------------+   |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                         Database Persistence Layer                       |
|                          PostgreSQL 15 Database                          |
|         Relational schemas, foreign keys, constraints, write-ahead logs  |
+--------------------------------------------------------------------------+
```

### Odoo ORM Responsibilities
- **Data Modeling & Validation**: Schema definitions via Python classes (`models.Model`), constraints (`@api.constrains`), onchange handlers (`@api.onchange`), and computed dependencies (`@api.depends`).
- **Access Control Enforcement**: Model-level permissions (`ir.model.access`), record rules (`ir.rule`), and user group inheritance evaluated dynamically per session.
- **Transaction Management**: Atomic execution of business workflows, rolling back on unhandled exceptions to prevent partial writes.
- **Sequence Generation**: Thread-safe numbering via `ir.sequence` records.

### PostgreSQL Responsibilities
- **Physical Persistence**: High-throughput storage of transactional, relational, and configuration tables.
- **Relational Integrity**: Foreign key constraints, unique indexing, and multi-version concurrency control (MVCC).
- **Blob & Filestore Coordination**: Serving binary attachments metadata while large files are coordinated via Odoo filestore.

---

## 3. Addon Structure (`solar_management`)

The custom module is organized according to standard Odoo 17 structure:

```text
backend/addons/solar_management/
├── __init__.py               # Python root package entry point
├── __manifest__.py           # Module metadata, dependencies, and loading manifest
├── models/                   # Python ORM data models and business logic
│   └── __init__.py           # Model package index
├── security/                 # Access rights, security categories, and groups
│   ├── security.xml          # Module category and RBAC groups (User, Manager)
│   └── ir.model.access.csv   # Model-level CRUD matrix (added when models are introduced)
├── views/                    # XML UI views, menus, and actions
│   └── menu_views.xml        # SolarOps top-level root application menu
└── data/                     # Data records, sequences, and default configs
    └── sequences.xml         # Auto-numbering sequences for lifecycle objects
```

---

## 4. Docker Service Architecture

The development and production-oriented baseline is orchestrated via Docker Compose, isolating services within a private bridge network.

```
+----------------------------------------------------------------------------+
| Windows Host (Development Environment)                                    |
| Access URL: http://localhost:8069                                          |
+----------------------------------------------------------------------------+
        |
        | [Port ${ODOO_PORT:-8069} mapped to Container 8069]
        v
+----------------------------------------------------------------------------+
| Docker Network: solarops_network (isolated bridge)                         |
|                                                                            |
|  +-----------------------------------+    +-----------------------------+  |
|  | Service: odoo                     |    | Service: db                 |  |
|  | Image: odoo:17                    |    | Image: postgres:15          |  |
|  | User: odoo                        |    | Internal Port: 5432         |  |
|  | Addons Path:                      |    | (No host port exposure)     |  |
|  |  - /usr/lib/.../odoo/addons       |    |                             |  |
|  |  - /mnt/extra-addons              |    | Healthcheck:                |  |
|  | Depends on: db (service_healthy)  |--->|  pg_isready -U odoo ...     |  |
|  | Volumes:                          |    |                             |  |
|  |  - solarops_odoo_data:/var/lib/odoo    | Volumes:                    |  |
|  |  - ./addons:/mnt/extra-addons     |    |  - solarops_db_data:...     |  |
|  +-----------------------------------+    +-----------------------------+  |
+----------------------------------------------------------------------------+
```

### Key Infrastructure Guardrails:
1. **Database Isolation**: PostgreSQL port `5432` is not exposed to the Windows host, preventing accidental collisions with local development instances or other Docker networks.
2. **Healthcheck-Driven Startup**: Odoo waits for PostgreSQL to become fully healthy before booting, preventing crash-loops and race conditions during initial schema initialization.
3. **Volume Isolation**: Dedicated named persistent volumes (`solarops_db_data`, `solarops_odoo_data`) guarantee project isolation from any other systems on the developer machine.
4. **Environment-Driven Configuration**: Database credentials and port bindings are decoupled into environment variables via `compose.yaml` interpolation and `.env`.

---

## 5. Workflow Extension & Future Module Roadmap

The SolarOps architecture provides extension hooks for progressive development across the 14 project modules.

### Status of Integrations:

| Domain / Workflow Area | Architecture Strategy | Current Status | Target Module |
| :--- | :--- | :--- | :--- |
| **Foundation & Runtime** | Native Odoo Module + Docker Compose | **Implemented (Target)** | Module 1 |
| **Lead & CRM Management** | Extend `crm.lead` or custom `solar.lead` | *Planned* | Module 2 |
| **Site Survey Operations** | Custom `solar.site.survey` with Geo/Roof Models | *Planned* | Module 3 |
| **Solar Packages & BOM** | Integrate with `product.template` & `mrp.bom` | *Planned* | Module 4 |
| **Quotation & Sales Orders** | Inherit `sale.order` & `sale.order.line` | *Planned* | Module 5 |
| **Billing & Payments** | Inherit `account.move` & milestone payments | *Planned* | Module 6 |
| **Inventory & Serialization** | Inherit `stock.picking`, `stock.lot` | *Planned* | Module 7 |
| **Installation Project** | Integrate with `project.project` & `project.task` | *Planned* | Module 8 |
| **Warranty Tracking** | Custom `solar.warranty` with asset linking | *Planned* | Module 9 |
| **After-Sales & Repairs** | Inherit/integrate `helpdesk.ticket` or field service | *Planned* | Module 10 |
| **Costing & Profitability** | Analytic accounts and margin calculations | *Planned* | Module 11 |
| **Subsidy & Compliance** | Document verification pipeline & state machine | *Planned* | Module 12 |
| **Dashboards & KPIs** | Odoo spreadsheet & graphical reporting engine | *Planned* | Module 13 |
| **E2E Hardening & RBAC** | CSV Access Matrix, Automated flow validation | *Planned* | Module 14 |
