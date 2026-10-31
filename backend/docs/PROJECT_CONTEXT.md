# SolarOps Project Context

## 1. Problem Statement

Solar energy installation businesses face operational complexity across disconnected, non-standardized workflows. Typical operations juggle:
- Fragmented lead capture without technical pre-qualification.
- Inaccurate, unstructured rooftop site survey data (shadow analysis, roof tilt, electrical load, panel layout).
- Error-prone manual generation of Bills of Materials (BOM) and customer quotations.
- Disconnected supply chain tracking, leading to missing serialized equipment (panels, inverters, batteries) at the installation site.
- Poor coordination between installation teams, grid approval authorities, and subsidy documentation pipelines.
- Fragmented warranty records and unstructured after-sales support resulting in compliance lapses and customer dissatisfaction.
- Lack of consolidated visibility into actual project profitability versus estimated costs.

**SolarOps** solves this by unifying the solar engineering, procurement, installation, and service lifecycle into a cohesive, native Odoo management platform.

---

## 2. Business Objectives

1. **Standardize the End-to-End Pipeline**: Provide a single operational system from initial prospect inquiry through commissioning and post-installation warranty service.
2. **Eliminate Engineering & Sizing Discrepancies**: Connect site survey measurements directly to package configuration and automated Bill of Materials generation.
3. **Rigorous Equipment Serialization**: Guarantee end-to-end traceability of high-value components (PV panels, string/micro inverters, battery banks) from warehouse intake to roof installation.
4. **Accelerate Financial Turnaround**: Streamline milestone-based customer invoicing, down-payment collection, and government subsidy disbursement tracking.
5. **Ensure Post-Installation Reliability**: Digitize warranty tracking, scheduled maintenance visits, and emergency repair workflows.
6. **Protect Profitability**: Enable accurate tracking of labor, materials, permits, and overhead against quoted prices.

---

## 3. Main User Roles

- **SolarOps User**:
  - Operational staff executing day-to-day lifecycle tasks.
  - Sub-roles include:
    - *Sales Representative*: Captures leads, analyzes energy bills, issues proposals.
    - *Survey Engineer*: Conducts on-site technical and rooftop feasibility assessments.
    - *Installation Technician*: Executes physical mounting, wiring, testing, and commissioning.
    - *Service & Support Agent*: Logs customer tickets, manages maintenance dispatches.
- **SolarOps Manager**:
  - Operational leadership and administrative oversight.
  - Sub-roles include:
    - *Operations / Project Manager*: Approves site surveys, schedules installation crews, oversees inventory dispatches.
    - *Finance & Commercial Head*: Validates milestone billings, margins, and subsidy compliance.
    - *System Administrator*: Configures master data, packages, sequences, and security permissions.

---

## 4. Complete Solar Installation Lifecycle

The complete lifecycle modeled by SolarOps spans 8 sequential stages:

```
[1. Lead & Enquiry]
       │
       ▼
[2. Rooftop Site Survey]
       │
       ▼
[3. Package Sizing & BOM Engineering]
       │
       ▼
[4. Quotation & Sales Order Confirmation]
       │
       ▼
[5. Down Payment & Inventory Reservation / Dispatch]
       │
       ▼
[6. Installation, Testing & Grid Commissioning]
       │
       ▼
[7. Subsidy Documentation & Final Billing]
       │
       ▼
[8. Warranty Issuance & After-Sales Service]
```

1. **Lead and Enquiry Management**: Capture customer contact details, monthly electricity consumption, address, connection type (residential/commercial/industrial), and sanction load.
2. **Site Survey Management**: Technical assessment of roof area, roof type (flat RCC, metal sheet, tiled), azimuth angle, tilt, shading obstacles, existing wiring route, and distribution box (DB) location.
3. **Solar Packages and Bill of Materials**: Sizing the system (kW capacity), selecting tier-1 panels, inverters, mounting structures, AC/DC distribution boxes, and lightning arresters.
4. **Quotations and Sales Orders**: Generating comprehensive financial proposals including equipment costs, installation services, estimated solar generation, payback period, and payment milestones.
5. **Payment Management**: Managing down payment, pre-dispatch installment, commissioning installment, and retention/subsidy balances.
6. **Inventory and Serial Number Tracking**: Reserving and dispatching items, capturing unique serial numbers for panels and inverters tied to the specific customer project.
7. **Installation Management**: Crew assignment, structural installation, electrical wiring, safety checks, net-metering inspection, and customer handover sign-off.
8. **Warranty & After-Sales Operations**: Issuing warranty certificates, managing periodic preventative maintenance (panel cleaning, inverter diagnostics), and servicing breakdown tickets.

---

## 5. Key Functional Requirements

- **Unified Lead Pipeline**: Automated lead sequence (`LEAD/YYYY/XXXXX`), pre-qualification criteria, and conversion to survey requests.
- **Structured Survey Capture**: Standardized checklist for rooftop dimensions, photos, azimuth, shading factors, and structural integrity.
- **Dynamic Package Configurator**: Standardized packages (e.g., 3 kW, 5 kW, 10 kW On-Grid/Off-Grid/Hybrid) with configurable BOM components.
- **Milestone-Based Financial Operations**: Automated invoicing triggers aligned with operational stage gates (e.g., 20% on booking, 60% on dispatch, 20% on commissioning).
- **Serial Tracking at Fulfillment**: Inability to complete dispatch or installation sign-off without scanning/entering verified serial numbers for major electrical assets.
- **Installation Milestones**: Project tracking with checklists for structure mounting, panel fixing, inverter wiring, earthing/grounding, and grid synchronization.
- **Automated Warranty Records**: Creation of customer warranty records linked directly to the installed serialized equipment.
- **Service Desk**: Ticket management for generation issues, inverter fault codes, and physical damage with SLA monitoring.

---

## 6. Important Business Rules

1. **Survey Pre-requisite**: Quotations exceeding standard residential capacities cannot be confirmed without an approved technical site survey.
2. **Serial Number Requirement**: High-value inventory items (PV modules, inverters, battery modules) must require serial number registration before dispatching to an installation site.
3. **Stage-Gated Dispatch**: Equipment delivery cannot be released without confirmation of the required initial payment milestone.
4. **Commissioning Sign-off**: An installation project cannot be marked as "Commissioned" without verified electrical test values (insulation resistance, open-circuit voltage, short-circuit current) and customer sign-off.
5. **Warranty Validity**: Equipment warranty is strictly activated on the official commissioning date and tied to specific serial numbers.
6. **Role Separation**: Only SolarOps Managers can approve custom BOM discounts, sign off on survey feasibility exceptions, and close completed projects.

---

## 7. Expected Final Demonstration Workflow

At the conclusion of the 14-module roadmap, the system will support an end-to-end demonstration scenario:
1. Create a prospective lead for a residential rooftop solar project.
2. Schedule and log a detailed rooftop site survey with technical measurements.
3. Generate a customized 5 kW On-Grid package and automated Bill of Materials.
4. Create and send a quotation, convert it into a confirmed Sales Order.
5. Process the initial down payment and trigger inventory reservation.
6. Pick and dispatch serialized solar panels and inverter from warehouse stock.
7. Schedule and execute installation phases, completing testing and commissioning checklists.
8. Submit net-metering and subsidy documentation.
9. Issue the final invoice, record full payment, and generate warranty certificates.
10. Open an after-sales service ticket against the installed system and resolve it through technician dispatch.
11. Review the executive project profitability report showing real revenue, hardware costs, labor costs, and net margin.
