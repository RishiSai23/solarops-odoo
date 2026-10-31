# Project SunFlow — System Architecture & Topology

## 1. Architectural Philosophy
Project SunFlow adopts an **authoritative-core, high-responsiveness edge** architecture.

Solar installation companies deal with complex physical assets (PV panels, inverters, storage batteries, charge controllers) and stringent financial compliance (milestone invoicing, advance deposits, warranty claims, government subsidy audits). Therefore, data integrity is paramount.

Rather than maintaining a parallel database that inevitably falls out of sync with accounting and warehouse stock, SunFlow designates **Odoo PostgreSQL as the single source of truth**.

## 2. Component Topology

```
+------------------------------------------------------------------------------------+
|                         CLIENT LAYER (React 18 / TypeScript)                      |
|                                                                                    |
|  [Operations & Management Portal]              [Field Technician Mobile App (PWA)] |
|  - Real-time Lifecycle Pipeline Tracker        - Touch-friendly Site Survey Wizard |
|  - Dynamic BOM & Quotation Reviewer            - Hardware Barcode & QR Scanner     |
|  - Warehouse Traceability & Dispatch Board     - Digital Handover Signature Pad    |
|  - Financial Margins & Subsidy Dashboard       - After-Sales Service Ticketer      |
+------------------------------------------------------------------------------------+
                                         ▲
                                         │ JSON / HTTPS (REST API)
                                         ▼
+------------------------------------------------------------------------------------+
|                     ORCHESTRATION GATEWAY (Python / FastAPI)                       |
|                                                                                    |
|  - Unified RESTful API Endpoints (/api/v1/...)                                     |
|  - Barcode Validation & Normalization Engine                                       |
|  - Image & Attachment Upload Streaming & Compression                               |
|  - Automatic Fallback Sandbox Adapter (Mocking for offline demos & test suites)    |
|  - Authenticated Odoo RPC Connector (XML-RPC & JSON-RPC with session caching)     |
+------------------------------------------------------------------------------------+
                                         ▲
                                         │ Odoo External RPC (Port 8069)
                                         ▼
+------------------------------------------------------------------------------------+
|                       AUTHORITATIVE ERP (Odoo 17/18 Engine)                        |
|                                                                                    |
|  [Native Odoo Core Modules]                [Custom SunFlow Addon: sunflow_core]    |
|  - res.partner (Customers & Contractors)   - solar.project (Central lifecycle hub) |
|  - crm.lead (Pre-qualification)            - solar.survey (Technical feasibility)  |
|  - sale.order (Commercial quotations)      - solar.package (Configured packages)   |
|  - stock.picking & stock.lot (Serials)     - solar.installation (Field execution)  |
|  - account.move (Milestone invoicing)      - solar.warranty (Equipment registry)   |
|  - repair.order (Warranty claims & RMA)    - solar.subsidy (Subsidy tracker)       |
+------------------------------------------------------------------------------------+
                                         ▲
                                         │ SQL
                                         ▼
+------------------------------------------------------------------------------------+
|                         DATABASE LAYER (PostgreSQL 16)                             |
|  Authoritative storage for ERP business transactions and solar lifecycle records.  |
+------------------------------------------------------------------------------------+
```

## 3. Communication Patterns

1. **Client to Gateway**:
   - The React client communicates exclusively through the FastAPI backend via standard REST JSON APIs.
   - Authentication tokens are handled via HTTP Bearer tokens.
2. **Gateway to Odoo**:
   - Communicates via Odoo XML-RPC (`/xmlrpc/2/common` and `/xmlrpc/2/object`).
   - Translates high-level business actions into Odoo transactional calls (`search_read`, `create`, `write`, `execute_kw`).
3. **Resilience & Sandbox Mode**:
   - When the Odoo server is unreachable (e.g. during local offline development or CI test pipelines), the gateway automatically activates the **Sandbox Adapter**, simulating complete business lifecycle transitions with zero configuration.
