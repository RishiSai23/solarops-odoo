# Project SunFlow — 19-Stage Solar Operations Lifecycle Specification

## The Guiding Principle
> **ONE CUSTOMER. ONE PROJECT RECORD. ONE CONNECTED OPERATIONAL LIFECYCLE.**

The solar operations lifecycle is represented in the system as a state machine governed by the `solar.project` entity.

---

## Detailed Lifecycle Stages

| Stage # | Stage Name | Triggering Event | Primary Responsible Role | Key Artifact / Entity | Completion Gate |
|---|---|---|---|---|---|
| **01** | **Customer Enquiry** | Website lead, walk-in, phone call | Sales Representative | `crm.lead` | Customer contact & utility provider recorded. |
| **02** | **Lead Qualification** | Monthly bill review | Sales Representative | `crm.lead` | Monthly electricity consumption & budget verified. |
| **03** | **Rooftop Site Survey** | Site visit by field engineer | Survey Engineer | `solar.survey` | Tilt, azimuth, shadow factor, sanctioned kW load, and roof photos uploaded. |
| **04** | **Package Configuration** | System recommendation | Solutions Architect | `solar.package` | System type (On-Grid / Off-Grid / Hybrid) and kW capacity selected (1-5 kW). |
| **05** | **Automated BOM Generation** | Package confirmation | Automated Engine | `mrp.bom` / Custom BOM | Exact counts of PV panels, inverter, mounting rails, and DC/AC cables calculated. |
| **06** | **Quotation & Sales Order** | Customer proposal generation | Sales Manager | `sale.order` | Commercial contract generated with milestone payment terms. |
| **07** | **Advance Payment** | Customer signs contract | Finance Officer | `account.move` (Invoice) | Booking deposit (e.g. 20%) cleared in bank. |
| **08** | **Inventory Reservation** | Advance payment confirmation | Warehouse Manager | `stock.picking` | Panels, inverter, and battery reserved in warehouse inventory. |
| **09** | **Serial Number Scanning** | Warehouse pick & pack | Warehouse Operator | `stock.lot` | Barcodes of PV panels and inverters scanned for mandatory traceability. |
| **10** | **Dispatch Management** | Materials loaded for transport | Logistics Coordinator | `stock.picking` (Outbound) | Materials dispatched and delivery receipt signed at site. |
| **11** | **Technician Scheduling** | Delivery confirmation | Operations Lead | `resource.calendar` / Schedule | 2-3 certified field technicians assigned based on location and skill. |
| **12** | **Installation Execution** | Field team arrival at site | Field Technician Lead | `solar.installation` | Checklists completed: Structure mount, electrical wiring, earthing resistance, VOC test. |
| **13** | **Customer Acceptance** | System commissioning & test run | Customer & Field Lead | Digital Handover Form | Customer digital signature & OTP captured on mobile device. |
| **14** | **Automatic Warranty Registration**| Acceptance sign-off | Automated Engine | `solar.warranty` | Warranty certificates registered using scanned serial numbers (e.g., 25-yr panels, 5-yr inverter). |
| **15** | **After-Sales Service** | Customer complaint or maintenance schedule | Support Engineer | `solar.service.ticket` | Ticket categorized with SLA priority and technician dispatch. |
| **16** | **Warranty Validation & RMA** | Defective component reported | Service Technician | `repair.order` | Serial number verified against warranty database before RMA replacement. |
| **17** | **Project Profitability** | Project completion | Financial Controller | Cost Accounting Ledger | Actual revenue vs material, labor, and logistics costs reconciled. |
| **18** | **Subsidy Documentation** | Net meter installation | Compliance Officer | `solar.subsidy` | PM Surya Ghar / State subsidy documentation submitted and tracked to disbursement. |
| **19** | **Management Analytics** | Continuous monitoring | Executive Management | BI Dashboard | Real-time conversion rates, cycle times, warranty incident rates, and gross margin per watt. |
