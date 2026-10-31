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
- **`solar_project`**: Key fields: `name`, `partner_id`, `stage`, `kw_capacity`, `system_type`, `contract_amount`, `cost_amount`, `installation_date`, `package_id`, `stock_requirement_ids`, `dispatch_ids`, `stock_ready`, `has_shortage`.
- **`solar_survey`**: Key fields: `project_id`, `azimuth`, `tilt`, `shading_factor`, `roof_type`, `sanctioned_load_kw`, `meter_phase`, `geo_latitude`, `geo_longitude`.
- **`solar_package`**: Key fields: `name`, `capacity_kw`, `package_type`, `panel_qty`, `inverter_wattage`, `battery_included`, `component_ids`, `component_count`.
- **`solar_package_component`** (BOM): Key fields: `package_id`, `product_id`, `product_tmpl_id`, `component_type`, `quantity`, `product_uom_id`, `is_serialized`.
- **`solar_stock_requirement`**: Key fields: `project_id`, `sale_order_id`, `product_id`, `component_type`, `required_qty`, `qty_on_hand`, `qty_reserved`, `qty_incoming`, `qty_available`, `qty_shortage`, `has_shortage`, `status`, `picking_id`, `purchase_order_line_ids`.
- **`solar_equipment_dispatch`**: Key fields: `name`, `project_id`, `partner_id`, `sale_order_id`, `picking_id`, `dispatch_date`, `actual_dispatch_date`, `dispatched_by`, `state`, `line_ids`, `serial_validation_complete`.
- **`solar_equipment_dispatch_line`**: Key fields: `dispatch_id`, `product_id`, `component_type`, `quantity`, `is_serialized`, `lot_id`, `stock_requirement_id`.
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
  - `product.template` & `product.product`: Master components (panels, inverters, batteries, BOS).
  - `stock.quant`: Live warehouse stock on-hand and reserved quantity queries.
  - `stock.warehouse` & `stock.location`: Storage facilities and source/destination locations.
  - `stock.picking` & `stock.move` & `stock.move.line`: Material transfers, picking validations, and dispatched moves.
  - `stock.lot`: Traceable equipment serial numbers for inverters, batteries, and panels.
  - `purchase.order` & `purchase.order.line`: Replenishment and vendor procurement for shortages.
  - `account.move`: Invoices and customer milestone payments.
  - `repair.order`: Equipment warranty replacements and repairs.

---

## 10. Important Implementation Discoveries

- **Discovery 001 (Environment Status)**: Python 3.10 and Node v22.14 are installed on the local system. Docker is installed but Docker Desktop daemon is not currently active.
- **Architectural Solution**: The backend includes an auto-fallback **Sandbox / Mock Adapter**. When Odoo is reachable, calls route to real Odoo XML-RPC; when offline, the gateway serves consistent sandbox data matching Odoo data structures, enabling frictionless UI testing and development!
- **Discovery 002 (Odoo Stubs & Frontend Dependencies)**: Since Odoo runtime runs containerized in Docker, the host Python 3.10 environment lacked `odoo` packages, generating IDE import errors. We added comprehensive Odoo interface stubs in `typings/odoo/__init__.pyi` mapped via `pyrightconfig.json` and `.vscode/settings.json`. Frontend packages were installed cleanly, achieving zero compilation errors with `npx tsc --noEmit`.
- **Discovery 003 (Lightweight BOM Pattern vs. MRP Dependency)**: In Odoo, the native `mrp` module is heavy and often omitted in simple distribution/service installations. For solar EPC packaging, we implemented `solar.package.component` as a clean One2many BOM on `solar.package` linked directly to `product.product`. This retains 100% compatibility with standard Community Odoo without forcing the manufacturing stack.
- **Discovery 004 (Stock Snapshotting & Zero Fake Movements)**: Rather than writing simulated inventory adjustments or fake stock quants, `solar.stock.requirement` queries native `stock.quant` and `purchase.order.line` directly to determine `qty_on_hand`, `qty_reserved`, `qty_available`, and `qty_incoming`. All inventory movements are strictly delegated to Odoo's native `stock.picking` execution pipeline.
- **Discovery 005 (Dispatch Validation & Serial Traceability Chain)**: `solar.equipment.dispatch` validates that all serialized components (`is_serialized=True`) have an assigned `stock.lot`, verifies that the lot matches the correct product, confirms warehouse availability, and strictly prohibits assigning the same lot across multiple active customer projects. Upon validation, lots are synchronized directly to `stock.move.line.lot_id` and committed via native `stock.picking.button_validate()`.
- **Discovery 006 (Phase 4 Runtime Verification & ORM Defensiveness)**: Executing the 25 `TransactionCase` tests and end-to-end integration workflows (`scripts/verify_phase4_runtime.py`) revealed two critical real-world runtime edge cases that passed static AST checks:
  1. *Module attribute bug*: In `stock_requirement.py`, dead code in `_get_incoming_qty` referenced `models.fields.Float.compare` instead of `fields.Float.compare`, fixed by using standard python aggregation over `purchase.order.line`.
  2. *Defensive UoM and Template Resolution*: In `action_create_purchase_order`, `self.product_id.product_tmpl_id.seller_ids` and `self.product_id.uom_po_id.id` raised `AttributeError` when products lacked template or PO UoM relations. Fixed by adding fallback to `product_id.uom_id` and defensive seller checks.
  3. *Cross-Model Search Domain Optimization*: Querying `solar.equipment.dispatch.line` with nested domain `('dispatch_id.state', '=', 'dispatched')` was refactored to an explicit two-step query via `dispatched_headers.mapped('id')`, ensuring 100% database engine portability across Odoo 17 and 18.
- **Discovery 007 (Odoo 17 Native Server Environment & View Engine Validation)**:
  1. *Complete Deprecation of `attrs`*: In Odoo 17.0, `attrs="{'invisible': ...}"` and `attrs="{'required': ...}"` are completely removed from the view parser and will fail addon loading with `ParseError`. They must be written directly as `invisible="..."`, `required="..."`, and `readonly="..."`.
  2. *Field Registration Rule for Dynamic Modifiers*: In Odoo 17, any field used in an `invisible` or `required` Python condition on a view (e.g., `invisible="not has_shortage"`, `invisible="not stock_ready or requirement_count == 0"`) MUST be explicitly present in that view definition (such as `<field name="has_shortage" invisible="1"/>`).
  3. *Forbidden Translatable Selectors in View Inheritance*: In Odoo 17, `xpath expr="//notebook/page[@string='...']"` raises a hard `ParseError` (`View inheritance may not use attribute 'string' as a selector`). Views must select elements by `name` attribute or hierarchical position (e.g. `//notebook` with `position="inside"`).
  4. *Odoo Model Instance Descriptors*: Methods on recordsets cannot be monkey-patched on instance objects (`AttributeError: read-only`). In tests, standard native execution or `unittest.mock.patch.object` on the model class should be utilized.
  5. *Incoming Receipt Serial Tracking*: When receiving products tracked by serial number (`tracking='serial'`), native Odoo `stock.picking` requires specifying `stock.lot` on `stock.move.line` prior to executing `button_validate()`.
  6. *Real-Time Creation Constraints*: Added `@api.constrains('lot_id', 'dispatch_id')` to `solar.equipment.dispatch.line` to prevent cross-project duplicate serial number assignment immediately at record creation/save time, complementing workflow action validation.

- **Discovery 008 (One2many Fallback Views, Web Client Resolution, & Container In-Memory ORMCACHE)**:
  1. *Web Client Form Resolution in Owl (`relational_utils.js`)*: When a user clicks "Add a line" on a One2many tree view, `useOpenX2ManyRecord` invokes `getFormViewInfo({ activeField, ... })`. If the parent view has an inline embedded `<form>` inside the `<field>` tag, `activeField.views.form` is immediately used. If absent, the web client executes an asynchronous `viewService.loadViews` RPC call to retrieve `[[false, 'form']]` for the comodel.
  2. *In-Memory ORMCACHE Desynchronization*: In a persistent container running Odoo (`sunflow_odoo` PID 1), `ir.ui.view` methods (`_get_view`, `default_view`) utilize `@tools.ormcache` keyed by user context (including `lang='en_US'`). If a user opens a model before its view is declared, the fallback form is cached in RAM. Upgrading the database via a secondary CLI command (`odoo -u module --stop-after-init`) modifies PostgreSQL records but leaves PID 1's in-memory cache intact. A container restart (`docker restart sunflow_odoo`) or service reload is mandatory to evict stale view caches.
  3. *Canonical Fix for One2many Modals*: Embed an explicit `<form>` directly inside the parent `<field name="survey_ids">` tag containing the required fields (Survey reference, Project, Surveyor, Survey date, Sanctioned load, Meter phase, Service voltage, Roof type, Usable area, Azimuth, Tilt, Shading percentage, Shading notes, Remarks, Feasibility status), pass `context="{'default_project_id': id, 'form_view_ref': 'sunflow_core.view_solar_survey_form'}"`, and restart the server container.

- **Discovery 009 (Site Survey Approval & Project Lifecycle Stage Progression Engine)**:
  1. *Decoupled Survey State vs Project Stage*: `solar.survey` tracks technical feasibility (`draft`, `feasible`, `conditional`, `rejected`), while `solar.project` tracks macro project stages (`lead`, `survey`, `feasibility`, `quotation`, `procurement`, `installation`, etc.). Updating a survey's status on `SPF-0117` did not advance the project from "Enquiry / Lead" because no synchronizer or transition hooks existed to bridge survey feasibility and project stages.
  2. *Automatic Synchronization & Governance Gate*:
     - Linking a survey moves the project from `lead` -> `survey`.
     - Marking a survey `feasible` or `conditional` automatically triggers `_sync_survey_feasibility()` to transition the project from `lead`/`survey` -> `feasibility` ("Feasibility Review"), computes `feasibility_status`, and registers `approved_survey_id`.
     - Advancing from `feasibility` -> `quotation` ("Quotation & BOM") requires formal engineering sign-off via `action_approve_feasibility()`.
  3. *Six Rigorous Business Rules & Sanctioned Load Guard*:
     - *Rule 1 (Draft Guard)*: Draft surveys cannot authorize quotation generation.
     - *Rule 2 (Rejected Guard)*: Rejected surveys cannot authorize quotation generation.
     - *Rule 3 (Conditional Guard)*: Conditional surveys require engineering review before quotation.
     - *Rule 4 (Grid Incompatibility Guard)*: System capacity must not exceed utility sanctioned grid load (`kw_capacity <= sanctioned_load_kw`). Enforced by `@api.constrains('feasibility_status', 'sanctioned_load_kw', 'project_id')` on `solar.survey`, blocking `feasible` status if capacity > grid connection.
     - *Rules 5 & 6 (Multiple Surveys & Non-Destructive Invalidation)*: Multiple surveys prioritize approved feasible surveys; subsequent rejected surveys never silently overwrite or invalidate an approved feasible survey.
     - *Quotation Generation*: `action_create_quotation()` automatically creates a native Odoo `sale.order` with project and package lines.
  4. *Dual Verification*:
     - 10 `TransactionCase` tests in `test_survey_lifecycle.py` (35/35 test suite PASS).
     - 7/7 live HTTP JSON-RPC verification steps in `scripts/verify_survey_lifecycle_e2e.py` executed on `sunflow_test` against project `SPF-0117` and test projects.

---

## 11. Change History

| Date | Author | Description |
|---|---|---|
| 2026-10-31 | Antigravity AI | Initialized repository foundation, defined 19-stage lifecycle architecture, created documentation system. |
| 2026-10-31 | Antigravity AI | Resolved IDE diagnostics: installed frontend node_modules, created Odoo type stubs in typings/, configured pyright and vscode settings. |
| 2026-10-31 | Antigravity AI | **Phase 4 Implementation**: Stock & Procurement Management in `odoo_addons/sunflow_core`. Added BOM (`solar.package.component`), inventory demand (`solar.stock.requirement`), serialized dispatch (`solar.equipment.dispatch`), Odoo stock/purchase integration, data sequences/categories (`solar_data.xml`), UI views (`inventory_views.xml`), security ACLs, and test suite (`test_phase4_inventory.py`). |
| 2026-10-31 | Antigravity AI | **Phase 4 Runtime Verification**: Created `scripts/verify_phase4_runtime.py` executing all 25 `TransactionCase` tests (100% PASS) and verifying Scenarios 4–11 (BOM demand generation, PO creation, incoming receipts, serialized dispatch, duplicate lot rejection, failed dispatch rollback, ACLs, and customer equipment history). Fixed 3 runtime bugs. |
| 2026-10-31 | Antigravity AI | **Phase 4 Final Integration Gate (Genuine Odoo 17 Server + PostgreSQL)**: Launched genuine Odoo 17 and PostgreSQL 16 containers via Docker. Resolved Odoo 17 XML modifier syntax (`attrs` removal), view field registration, and xpath inheritance constraints. Successfully installed and upgraded `sunflow_core` on test database `sunflow_test`. Executed the entire 25-test `TransactionCase` test suite (25/25 PASS, 0 failures, 0 errors). Created and verified 15-step end-to-end integration workflow script (`verify_runtime_e2e.py`) in Odoo shell. Enforced cross-project duplicate serial constraint. System 100% certified ready for Phase 5. |
| 2026-10-31 | Antigravity AI | **Site Survey UI Defect Investigation & Embedded Modal Fix**: Resolved issue where clicking "Site Surveys → Add a line" showed generic `mail.thread` fields. Added missing fields to `solar.survey` (`service_voltage`, `shading_notes`, `remarks`), embedded explicit `<form>` directly inside `<field name="survey_ids">` in `view_solar_project_form`, configured `context="{'default_project_id': id, 'form_view_ref': 'sunflow_core.view_solar_survey_form'}"`, restarted Odoo container to clear stale in-memory ORMCACHE, and verified all 8 runtime browser acceptance criteria over HTTP JSON-RPC (`scripts/verify_survey_popup_e2e.py`). 25/25 regression tests pass. |
| 2026-10-31 | Antigravity AI | **Site Survey Approval & Project Lifecycle Integration**: Solved decouple between survey approval and project stage. Added `feasibility_status`, `approved_survey_id`, `_sync_survey_feasibility()`, `action_approve_feasibility()`, `action_create_quotation()`, and grid load constraints (`kw_capacity <= sanctioned_load_kw`). Built 10 new `TransactionCase` tests (35/35 PASS) and verified live on `SPF-0117` via HTTP JSON-RPC (`scripts/verify_survey_lifecycle_e2e.py`, 7/7 PASS). |
