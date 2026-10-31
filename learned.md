# Project SunFlow — Architectural & Domain Knowledge Repository (`learned.md`)

This living document captures the architectural decisions, business domain context, system topology, integration patterns, and operational lessons of **Project SunFlow**. Every developer and AI agent must consult and maintain this file.

---

## 1. Project Overview

Project SunFlow is an integrated solar operations and lifecycle management ERP platform developed for the **Odoo × GCET Hackathon Finale**. 

Solar EPC (Engineering, Procurement, and Construction) operations face acute fragmentation:
- Sales reps collect leads in generic CRMs without understanding electrical feasibility.
- Survey teams capture roof dimensions and shading on paper or chat apps.
- Engineering produces Bills of Materials (BOM) manually in spreadsheets.
- Warehouses dispatch components without scanning serial numbers, breaking warranty chains.
- Field technicians lack standardized checklists, leading to failed inspections and payment delays.
- After-sales service teams cannot verify whether an inverter or battery was part of the original project.

SunFlow eliminates this fragmentation under the guiding thesis:
> **ONE CUSTOMER. ONE PROJECT RECORD. ONE CONNECTED OPERATIONAL LIFECYCLE.**

SunFlow manages the target business scenario of **SunPower Solutions**: 40+ installations/month, 15 field technicians, 1 kW to 5 kW systems (residential & small commercial), On-Grid & Off-Grid equipment with multi-year warranties.

---

## 2. System Architecture

SunFlow follows a **Dual-Engine / Orchestration Architecture**:

```
+-----------------------------------------------------------------------------------+
|                              PRESENTATION LAYER                                   |
|   React 18 + Vite + TypeScript + Tailwind CSS + Lucide Icons + Recharts           |
|   - Operations Executive Dashboard (Metrics, Lifecycle Pipeline, Financials)      |
|   - Field Engineer App (Surveys, Serial Scanner, Photo Evidence, Customer Sign)   |
+-----------------------------------------------------------------------------------+
                                         │  JSON / REST API
                                         ▼
+-----------------------------------------------------------------------------------+
|                            ORCHESTRATION GATEWAY                                  |
|   FastAPI (Python 3.10+)                                                          |
|   - API Gateway & Route Handlers (/api/projects, /api/surveys, /api/warranties)   |
|   - Odoo RPC Adapter (XML-RPC / JSON-RPC with connection pooling)                 |
|   - Standalone Sandbox Adapter (Instant mock execution for offline demo & tests)  |
|   - Hardware & File Stream Processor (Barcode decoding, photo compression)        |
+-----------------------------------------------------------------------------------+
                                         │  Authenticated RPC
                                         ▼
+-----------------------------------------------------------------------------------+
|                            AUTHORITATIVE ERP CORE                                 |
|   Odoo 17/18 Community / Enterprise + PostgreSQL                                  |
|   - Custom Addon: sunflow_core                                                    |
|     * solar.project (Central lifecycle orchestrator)                              |
|     * solar.survey (Technical rooftop assessment)                                 |
|     * solar.package (1kW - 5kW modular configurations)                            |
|     * solar.installation (Checklists, geo-stamps, signatures)                     |
|     * solar.warranty (Equipment serial number registry)                           |
|   - Standard Odoo Modules: crm, sale, stock, account, project, repair             |
+-----------------------------------------------------------------------------------+
```

---

## 3. Technology Stack

| Layer | Technology | Selection Rationale |
|---|---|---|
| **Authoritative ERP** | Odoo 17 / 18 (Python, PostgreSQL) | Industry-standard open-source ERP with native CRM, Sales, Inventory, Accounting, and Repair modules. |
| **Custom ERP Module** | `sunflow_core` (Odoo Addon) | Extends Odoo data models directly in PostgreSQL, ensuring referential integrity and seamless Odoo UI views. |
| **API Gateway** | Python FastAPI (3.10+) | High throughput, asynchronous capabilities, native Pydantic schema validation, and seamless Odoo XML-RPC bridging. |
| **Frontend Framework** | React 18 with Vite & TypeScript | Lightning-fast HMR, type safety across API boundaries, robust ecosystem. |
| **Design System & UI** | Tailwind CSS + Lucide React | Highly responsive, premium aesthetic, custom solar-themed palette, zero runtime overhead. |
| **State & Remote Data** | TanStack React Query | Server state synchronization, optimistic caching, automatic refetching. |
| **Data Visualization** | Recharts | Declarative, SVG-based charting for operational metrics and project profitability. |
| **Deployment & Containers** | Docker & Docker Compose | Multi-container stack orchestrating Odoo, PostgreSQL, FastAPI Gateway, and Web UI. |

---

## 4. Architectural Decisions & Trade-Offs

### ADR-001: Odoo PostgreSQL as the Authoritative Single Source of Truth
- **Context**: Solar operations require strict accounting, inventory reservations, and customer records.
- **Decision**: Avoid maintaining an independent secondary database for business data. All solar lifecycle records are anchored to Odoo models.
- **Rationale**: Eliminates split-brain database sync issues and honors native Odoo tax rules, journal entries, and serial number tracking (`stock.lot`).

### ADR-002: Dedicated FastAPI Orchestration Gateway
- **Context**: Directly calling Odoo XML-RPC from client browsers exposes credentials, lacks modern REST semantics, and complicates client-side photo uploads or offline caching.
- **Decision**: Introduce a lightweight FastAPI gateway between React and Odoo.
- **Rationale**:
  - Provides clean RESTful JSON endpoints for client consumption.
  - Implements connection pooling and credential management.
  - Incorporates a **Mock/Sandbox Adapter** allowing development, automated tests, and offline demonstrations even when a local Odoo server is not yet booted.

### ADR-003: Modular Odoo Addon (`sunflow_core`)
- **Context**: Extending Odoo via monkey-patching or database modifications breaks version upgrades.
- **Decision**: Encapsulate all custom models, views, and security rules inside a clean Odoo addon directory (`odoo_addons/sunflow_core`).
- **Rationale**: Fully compliant with Odoo standards, easily installable in any standard Odoo 17/18 instance.

---

## 5. Business Domain Knowledge

```
                       +----------------+
                       |   res.partner  | (Customer)
                       +--------+-------+
                                | 1
                                |
                                | *
                       +--------▼-------+
                       |  solar.project | (Central Project Record)
                       +--------+-------+
                                |
       +------------------------+-----------------------+
       | 1                      | 1                     | 1
       |                        |                       |
+------▼-------+       +--------▼-------+       +-------▼--------+
| solar.survey |       |   sale.order   |       | solar.install  |
+--------------+       +--------+-------+       +-------+--------+
                                | 1                     | 1
                                |                       |
                       +--------▼-------+       +-------▼--------+
                       | stock.picking  |       | solar.warranty |
                       +--------+-------+       +----------------+
                                | *
                       +--------▼-------+
                       |   stock.lot    | (Scanned Serial Numbers)
                       +----------------+
```

### Core Business Entities
1. **Customer (`res.partner`)**: Residential homeowner or commercial facility owner.
2. **Solar Project (`solar.project`)**: The central lifecycle coordinator tracking state, milestone dates, technician assignments, and total cost/margin.
3. **Site Survey (`solar.survey`)**: Technical rooftop assessment (roof azimuth, tilt angle, shadow percentage, sanctioned grid load, meter phase).
4. **Solar Package (`solar.package`)**: Standardized 1kW – 5kW bill-of-materials templates (number of panels, inverter rating, battery capacity, structure type).
5. **Sales Order (`sale.order`)**: Customer commercial contract with milestone payment terms (Booking Advance, Pre-dispatch, Commissioning).
6. **Stock Picking & Lots (`stock.picking`, `stock.lot`)**: Equipment dispatch and serialized item tracking.
7. **Installation Order (`solar.installation`)**: Field work order with technician checklists, earthing test values, inverter test results, and photo evidence.
8. **Warranty Registry (`solar.warranty`)**: Equipment-level warranty records linked to serialized panels, inverters, and batteries.
9. **Service Ticket (`solar.service.ticket`)**: After-sales maintenance, warranty claims, and repair tickets.

---

## 6. Workflow Knowledge (The 19-Stage Lifecycle)

1. **Enquiry & CRM**: Lead generated via website, referral, or field agent.
2. **Lead Qualification**: Verifies electricity bill, roof ownership, and customer budget.
3. **Site Survey**: Field engineer records GPS coordinates, roof layout, shading, and meter capacity.
4. **Package Configuration**: System recommends optimal package (e.g., 3 kW Hybrid On-Grid).
5. **Automated BOM**: Computes panels, inverter, mounting rails, DC cables, ACDB, and lightning arresters.
6. **Quotation & Order**: Generates formal solar proposal; customer approves contract.
7. **Advance Payment**: Triggers 20% booking milestone via Odoo invoice.
8. **Inventory Reservation**: Reserves specific brand inverters and panels in warehouse.
9. **Serial Number Scan**: Warehouse operator scans 2D/1D barcodes of panels and inverters into `stock.lot`.
10. **Dispatch Management**: Materials dispatched to site; delivery receipt confirmed.
11. **Technician Scheduling**: SunPower dispatch coordinator assigns a certified crew of 2-3 technicians.
12. **Installation Execution**: Field crew follows step-by-step digital checklist (Structure -> Panels -> Inverter -> Earthing).
13. **Customer Acceptance**: Customer reviews live generation, signs digital handover document on mobile.
14. **Warranty Registration**: Serial numbers are automatically registered in the warranty database with supplier terms.
15. **After-Sales Service**: Customer can report issues via portal; SLAs trigger automatic technician dispatch.
16. **Warranty Validation & RMA**: Service engineer checks serial number validity before replacing faulty inverters.
17. **Project Profitability**: System computes final margin (Contract Revenue - Equipment Cost - Labor - Travel).
18. **Subsidy Tracking**: Tracks submission of net metering application and subsidy disbursement from government agencies.
19. **Management Analytics**: Dashboard reveals cycle times, technician efficiency, and margin per watt.

---

## 7. API Architecture & Contracts

The FastAPI gateway exposes RESTful JSON endpoints under `/api/v1`:

- `GET  /api/v1/health` — System status and Odoo connectivity check.
- `GET  /api/v1/projects` — Fetch active solar projects with lifecycle status filters.
- `POST /api/v1/projects` — Create a new customer solar project.
- `GET  /api/v1/projects/{id}` — Full 360-degree lifecycle details for a project.
- `POST /api/v1/projects/{id}/survey` — Submit or update rooftop survey data.
- `POST /api/v1/projects/{id}/bom/generate` — Generate dynamic Bill of Materials.
- `POST /api/v1/projects/{id}/install/checklist` — Submit installation checklist & photos.
- `POST /api/v1/projects/{id}/warranties/register` — Register equipment serial numbers.
- `GET  /api/v1/analytics/dashboard` — Aggregated operational KPIs and financials.

---

## 8. Database Architecture

Odoo's PostgreSQL database houses all models:
- **`solar_project`**: Key fields: `name`, `partner_id`, `stage`, `kw_capacity`, `system_type`, `contract_amount`, `cost_amount`, `installation_date`.
- **`solar_survey`**: Key fields: `project_id`, `azimuth`, `tilt`, `shading_factor`, `roof_type`, `sanctioned_load_kw`, `meter_phase`, `geo_latitude`, `geo_longitude`.
- **`solar_package`**: Key fields: `name`, `capacity_kw`, `package_type`, `panel_qty`, `inverter_wattage`, `battery_included`.
- **`solar_installation`**: Key fields: `project_id`, `technician_id`, `status`, `earthing_resistance_ohms`, `voc_measured_volts`, `handover_signature`, `completion_date`.
- **`solar_warranty`**: Key fields: `project_id`, `serial_number_id`, `equipment_type`, `start_date`, `end_date`, `warranty_status`.

---

## 9. Odoo Integration Knowledge

- **Communication Protocol**: XML-RPC or JSON-RPC over HTTP/HTTPS.
- **Authentication**: Odoo database name (`db`), user login (`username`), and API password / user token (`password`).
- **Native Models Utilized**:
  - `res.partner`: Customer details and address.
  - `crm.lead`: Pre-qualification leads.
  - `sale.order` & `sale.order.line`: Quotations and commercial orders.
  - `stock.picking` & `stock.move`: Material movements and transfers.
  - `stock.lot`: Traceable equipment serial numbers.
  - `account.move`: Invoices and customer milestone payments.
  - `repair.order`: Equipment warranty replacements and repairs.

---

## 10. Important Implementation Discoveries

- **Discovery 001 (Environment Status)**: Python 3.10 and Node v22.14 are installed on the local system. Docker is installed but Docker Desktop daemon is not currently active.
- **Architectural Solution**: The backend includes an auto-fallback **Sandbox / Mock Adapter**. When Odoo is reachable, calls route to real Odoo XML-RPC; when offline, the gateway serves consistent sandbox data matching Odoo data structures, enabling frictionless UI testing and development!

---

## 11. Change History

| Date | Author | Description |
|---|---|---|
| 2026-10-31 | Antigravity AI | Initialized repository foundation, defined 19-stage lifecycle architecture, created documentation system. |
