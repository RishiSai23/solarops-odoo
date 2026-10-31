# SolarOps Development Tracker & Module Roadmap

This document outlines the full 14-module delivery lifecycle for SolarOps.

---

## Roadmap Summary

| Module | Title | Scope Summary | Dependencies | Status |
| :---: | :--- | :--- | :--- | :---: |
| **01** | **Project Foundation & Environment Setup** | Repository organization (`frontend/`, `backend/`), Docker Compose (`odoo:17`, `postgres:15`), base addon `solar_management`, security hierarchy, sequences, base menu, architecture docs. | None | **Implemented (Target)** |
| **02** | **Customer & Lead Management** | Native `crm.lead` and `res.partner` extension, solar intake channels (WhatsApp/Phone/Web), technical pre-qualification, duplicate-safe customer conversion, survey readiness dispatch, full test suite. | Module 01 | **Implemented (Target)** |
| **03** | **Site Survey Management** | On-site technical roof evaluation, shading analysis, orientation/tilt data, electrical infrastructure audit, survey reports. | Module 02 | *Planned* |
| **04** | **Solar Packages & Bill of Materials** | Pre-configured solar system packages (kW sizes), component BOMs (panels, inverters, structures, balance of system), dynamic sizing. | Module 01, 03 | **Implemented (solar.package.component)** |
| **05** | **Quotations & Sales Orders** | Solar customer proposals, technical/commercial quotation generation, system yield projections, ROI/payback periods, contract confirmation. | Module 03, 04 | *Planned* |
| **06** | **Payment Management** | Milestone-based billing schedules (booking deposit, delivery, commissioning), customer invoicing, payment reconciliation. | Module 05 | *Planned* |
| **07** | **Inventory & Serial Tracking** | Warehouse stock allocation, procurement of BOM components, mandatory serial number scanning and traceability for panels/inverters. | Module 04, 05 | **Verified Runtime (25/25 Tests Pass)** |
| **08** | **Installation Management** | Project execution workflows, field crew scheduling, installation stage checklists (mounting, wiring, inverter connection, safety testing). | Module 06, 07 | *Planned* |
| **09** | **Warranty Management** | Digital warranty certificate generation, manufacturer warranty mapping, asset-to-serial number binding, expiration alerts. | Module 07, 08 | *Planned* |
| **10** | **After-Sales Service & Repairs** | Service helpdesk tickets, scheduled preventative maintenance (cleaning, electrical audits), breakdown dispatch, replacement RMA. | Module 08, 09 | *Planned* |
| **11** | **Project Costing & Profitability** | Real-time project cost tracking (hardware BOM, labor, permits, logistics) vs. contractual revenue, gross and net margin analytics. | Module 06, 08 | *Planned* |
| **12** | **Subsidy & Documentation** | Regulatory documentation tracking (grid interconnection, net metering applications, DISCOM approvals, government subsidy claims). | Module 05, 08 | *Planned* |
| **13** | **Dashboards & Reporting** | Operational and executive dashboards: sales pipeline, survey throughput, installation backlog, inventory aging, system generation KPIs. | Modules 02-12 | *Planned* |
| **14** | **Integration, Security & E2E Validation** | Access control matrices (ir.model.access.csv), record rules, multi-user role validation, full lifecycle end-to-end integration test. | Modules 01-13 | *Planned* |

---

## Detailed Module Breakdown

### Module 01: Project Foundation and Environment Setup
- **Status**: **Implemented (Target)** *(Note: Implemented as a development baseline; manual execution, startup, and verification pending by developer)*
- **Scope**:
  - Top-level repository reorganization: `backend/` and `frontend/`.
  - Docker Compose environment with isolated network and persistent named volumes for Odoo 17 and PostgreSQL 15.
  - Safe environment variable interpolation via `backend/.env.example`.
  - Comprehensive `.gitignore` protecting secrets, Python caches, and Odoo logs.
  - Native Odoo addon foundation `backend/addons/solar_management/` (`__manifest__.py`, `__init__.py`).
  - Security category and RBAC groups: `SolarOps User` and `SolarOps Manager`.
  - Root application menu structure and reusable `ir.sequence` auto-numbering records.
  - Technical architecture, project context, and development tracker documentation.

### Module 02: Customer and Lead Management
- **Status**: **Implemented (Target)** *(Note: Complete implementation in place; manual verification and testing in Odoo 17 pending by developer)*
- **Scope**:
  - Native `crm.lead` extension with reference sequence (`LEAD/YYYY/XXXXX`), multi-channel lead intake (`solar_lead_source`: WhatsApp, Phone, Website, Manual, Other).
  - Energy & consumption profiling (`monthly_bill_amount`, `avg_monthly_consumption_kwh`).
  - Rooftop feasibility & space pre-checks (`roof_area_sqft`, `roof_ownership`, `roof_suitability`, `grid_connectivity`, `solar_system_type`, `expected_capacity_kw`).
  - Business qualification workflow (`action_qualify_lead`, `action_needs_more_info`, `action_mark_not_suitable`, `action_reset_qualification`).
  - Rejection / missing data reason capture via modal wizard (`solar.lead.reason.wizard`).
  - Site survey readiness gating (`action_mark_survey_ready`, `is_survey_ready`).
  - Duplicate-preventative customer conversion (`action_solar_convert_to_customer`).
  - Native `res.partner` extension with `is_solar_customer`, historical `solar_lead_ids`, count, and smart-button navigation.
  - Custom list, search, inherited form views, and dedicated SolarOps Sales submenus.
  - 11 comprehensive automated test cases (`tests/test_solar_lead.py`).
- **Dependencies**: Module 01, Odoo native `crm`.

### Module 03: Site Survey Management
- **Status**: *Planned*
- **Scope**: Technical survey data models, rooftop dimensions, surface materials, azimuth, shade obstacles, structural stability assessment, photo attachments.
- **Dependencies**: Module 02.

### Module 04: Solar Packages and Bill of Materials
- **Status**: *Planned*
- **Scope**: Standard solar package bundles (3kW, 5kW, 10kW, etc.), component master catalog, dynamic BOM assembly, electrical hardware requirements.
- **Dependencies**: Module 01, 03.

### Module 05: Quotations and Sales Orders
- **Status**: *Planned*
- **Scope**: Proposal generation, solar energy yield estimation, tariff savings calculations, customer quotation PDF reports, sales confirmation workflows.
- **Dependencies**: Module 03, 04.

### Module 06: Payment Management
- **Status**: *Planned*
- **Scope**: Staged payment milestones (down payment, pre-dispatch, post-commissioning), automated invoice creation, payment matching.
- **Dependencies**: Module 05.

### Module 07: Inventory and Serial Number Tracking
- **Status**: *Planned*
- **Scope**: Warehouse stock reservations, goods delivery notes, mandatory scanning/recording of panel and inverter serial numbers, dispatch verification.
- **Dependencies**: Module 04, 05.

### Module 08: Installation Management
- **Status**: *Planned*
- **Scope**: Project tasks for physical deployment, team scheduling, mechanical mounting, electrical wiring, testing, and commissioning sign-off.
- **Dependencies**: Module 06, 07.

### Module 09: Warranty Management
- **Status**: *Planned*
- **Scope**: Customer warranty registry, manufacturer warranty linkage per serial number, warranty certificates, and renewal/expiry tracking.
- **Dependencies**: Module 07, 08.

### Module 10: After-Sales Service and Repairs
- **Status**: *Planned*
- **Scope**: Customer ticketing system, field technician service dispatch, preventive maintenance schedules, spare parts consumption, RMA workflow.
- **Dependencies**: Module 08, 09.

### Module 11: Project Costing and Profitability
- **Status**: *Planned*
- **Scope**: Analytic accounts, material costs, labor expense logging, overhead allocation, quotation vs. actual cost margin analysis.
- **Dependencies**: Module 06, 08.

### Module 12: Subsidy and Documentation Management
- **Status**: *Planned*
- **Scope**: Net-metering approval tracking, utility interconnection documentation, national/regional solar subsidy claim workflows and disbursement logs.
- **Dependencies**: Module 05, 08.

### Module 13: Dashboards and Reporting
- **Status**: *Planned*
- **Scope**: Executive KPIs, conversion funnels, installation cycle time metrics, inventory availability, financial profitability reports.
- **Dependencies**: Modules 02-12.

### Module 14: Integration, Security and End-to-End Validation
- **Status**: *Planned*
- **Scope**: Final access control matrix (`ir.model.access.csv`), record-level security rules (`ir.rule`), performance tuning, full-lifecycle verification walkthrough.
- **Dependencies**: Modules 01-13.
