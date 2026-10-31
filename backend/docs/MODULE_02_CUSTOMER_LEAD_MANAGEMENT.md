# Module 02: Customer and Lead Management Specification

## 1. Module Purpose & Executive Summary

Module 02 implements the complete native Odoo 17 customer and lead management lifecycle for **SolarOps**. It models the intake, technical feasibility pre-qualification, assignment, stage progression, and customer conversion for prospective rooftop solar installation inquiries.

The core process flow implemented is:
```text
Inquiry Intake (WhatsApp / Phone / Web / Manual)
                     │
                     ▼
             Lead Registration
     (Auto-Sequence LEAD/YYYY/XXXXX)
                     │
                     ▼
        Solar Pre-Qualification
 (Bill, Energy Consumption, Roof Area, NOC)
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    [Qualified]          [Needs Info / Not Suitable]
         │                       │
         ▼                       ▼
   [Survey Ready]        Re-evaluate when info received
         │
         ▼
 Conversion into Customer & Opportunity
 (Duplicate prevention & history linking)
```

---

## 2. Architectural Decisions & Odoo 17 Native Reuse

1. **Native Model Extension (`crm.lead`)**:
   - Rather than creating an isolated custom lead table (`solar.lead`), SolarOps extends native `crm.lead`.
   - Reuses Odoo's native CRM pipeline stages, Kanban views, sales team assignments, salesperson routing, Chatter feeds, scheduled activities, and tracking history.
2. **Native Partner Extension (`res.partner`)**:
   - Extends standard `res.partner` with a non-intrusive relationship to multiple solar inquiries (`solar_lead_ids`), an inquiry count (`solar_lead_count`), and a solar customer flag (`is_solar_customer`).
   - Does not duplicate common contact fields (Name, Phone, Mobile, Email, Address, Tax ID, Company).
   - Keeps property-specific variables (roof dimensions, bills, electricity consumption) on the lead record to support customers with multiple sites/properties.
3. **Controlled Conversion & Duplicate Prevention**:
   - Lead-to-customer conversion reuses native Odoo partner creation and opportunity conversion routines while enforcing a pre-qualification check (`solar_qualification_status == 'qualified'`).
   - Prior to creating a new partner, the system checks for existing customer records by email and phone/mobile, linking the inquiry to existing records and setting `is_solar_customer = True` rather than creating duplicates.
4. **Sequence Generation**:
   - Reuses the `solar.lead` auto-numbering sequence (`LEAD/%(year)s/XXXXX`) defined in `data/sequences.xml` to assign a persistent human-readable reference `solar_lead_ref`.

---

## 3. Data Model Enhancements

### 3.1 Extended Model: `crm.lead`

| Technical Field | Type | Description / Constraints | Tracking |
| :--- | :--- | :--- | :---: |
| `solar_lead_ref` | `Char` | Auto-generated sequence identifier (e.g. `LEAD/2026/00001`). Indexed, Readonly. | No |
| `solar_lead_source` | `Selection` | Intake channel: `whatsapp`, `phone`, `website`, `manual`, `other`. Default: `manual`. | Yes |
| `monthly_bill_amount` | `Monetary` | Average monthly electricity bill amount paid by customer. Validated >= 0. | Yes |
| `avg_monthly_consumption_kwh` | `Float` | Monthly power consumption in kilowatt-hours (units). Validated >= 0. | Yes |
| `roof_area_sqft` | `Float` | Usable shadow-free rooftop area in square feet. Validated >= 0. | Yes |
| `roof_ownership` | `Selection` | `owned`, `rented_noc`, `rented_pending_noc`, `shared`. Default: `owned`. | Yes |
| `roof_suitability` | `Selection` | `suitable`, `partially_shaded`, `shaded`, `structural_risk`, `pending_inspection`. | Yes |
| `grid_connectivity` | `Selection` | `connected_stable`, `connected_unstable`, `off_grid`. Default: `connected_stable`. | Yes |
| `solar_system_type` | `Selection` | Preferred architecture: `on_grid`, `off_grid`, `hybrid`. Default: `on_grid`. | Yes |
| `expected_capacity_kw` | `Float` | Preliminary estimated system capacity in kW. Validated >= 0. | Yes |
| `solar_remarks` | `Text` | Customer requirements, backup expectations, equipment preferences. | No |
| `solar_qualification_status` | `Selection` | `not_evaluated`, `needs_info`, `qualified`, `not_suitable`. Default: `not_evaluated`. | Yes |
| `qualification_notes` | `Text` | Reason for rejection, missing data checklist, or qualification audit remarks. | Yes |
| `qualification_date` | `Datetime` | Timestamp when qualification was completed. Readonly. | No |
| `qualified_user_id` | `Many2one` | `res.users` record of the evaluator. Readonly. | No |
| `is_survey_ready` | `Boolean` | Flag indicating technical pre-qualification passed and ready for survey scheduling. | Yes |

### 3.2 Extended Model: `res.partner`

| Technical Field | Type | Description |
| :--- | :--- | :--- |
| `is_solar_customer` | `Boolean` | Flag identifying customers who have an active solar inquiry, proposal, or installation. |
| `solar_lead_ids` | `One2many` | Inverse relation to `crm.lead` via `partner_id`. Shows all historical inquiries. |
| `solar_lead_count` | `Integer` | Computed count of solar leads for smart-button display on partner form. |

### 3.3 Transient Model: `solar.lead.reason.wizard`

Used as a modal dialog to capture justification notes whenever a sales engineer marks a lead as "Needs More Information" or "Not Suitable":
- `lead_id`: Many2one `crm.lead` (ondelete='cascade')
- `action_type`: Selection (`needs_info`, `not_suitable`)
- `reason`: Text (required)

---

## 4. Business Workflow & Qualification Rules

### 4.1 Qualification Validation Rules (`action_qualify_lead`)
1. **Customer Identity**: Lead must have customer contact details (name and at least phone, mobile, or email).
2. **Energy Profile**: Either `monthly_bill_amount > 0` or `avg_monthly_consumption_kwh > 0` must be recorded.
3. **Roof Space**: `roof_area_sqft` must be specified and greater than zero.
4. **Feasibility Gate**:
   - If `roof_suitability == 'shaded'`, qualification is blocked (must be marked Not Suitable or re-evaluated).
   - If `roof_suitability == 'structural_risk'`, qualification is blocked (requires structural repair).
   - If `roof_ownership == 'rented_pending_noc'`, qualification is blocked until NOC is secured.
5. **Success Effect**:
   - `solar_qualification_status = 'qualified'`
   - `qualification_date = fields.Datetime.now()`
   - `qualified_user_id = env.user.id`
   - Stage moved to "Qualified"
   - Chatter note logged with summary audit.

### 4.2 Handing Rejection & Missing Data
- `action_needs_more_info`: Requires notes. Moves status to `needs_info` and stage to "Qualification Pending".
- `action_mark_not_suitable`: Requires reason. Moves status to `not_suitable`.
- `action_reset_qualification`: Resets status to `not_evaluated` and clears survey ready flag, enabling full re-evaluation.

### 4.3 Survey Ready Transition (`action_mark_survey_ready`)
- Lead must be `qualified`.
- Lead must have a physical site address (`street` or `city`).
- Sets `is_survey_ready = True` and moves stage to "Survey Ready".

### 4.4 Customer Conversion (`action_solar_convert_to_customer`)
- Only `qualified` leads can be converted.
- Searches for existing partner by email or phone/mobile to prevent duplicate contacts.
- If existing partner found: links to `partner_id` and sets `is_solar_customer = True`.
- If no existing partner found: creates `res.partner` using lead address and contact details.
- Converts lead to opportunity (`lead.convert_opportunity()`).
- Moves stage to "Converted".

---

## 5. Security & Access Rights

- **Role Inheritance**:
  - `group_solar_user` implies `sales_team.group_sale_salesman` (standard CRM salesman).
  - `group_solar_manager` implies `group_solar_user` and `sales_team.group_sale_manager` (CRM administrator).
- **Transient Model Access**:
  - `solar.lead.reason.wizard` is granted full CRUD for both `group_solar_user` and `group_solar_manager` via `security/ir.model.access.csv`.
- **Integrity Enforcement**:
  - Validations (`@api.constrains` and workflow methods) run at the model level; direct ORM updates cannot set negative financial/technical metrics.

---

## 6. Integration Points for Future Modules

- **Module 03 (Site Survey Management)**:
  - Technical surveys will reference `lead_id` (`crm.lead`) and `partner_id` (`res.partner`).
  - Action `action_solar_leads_survey_ready` provides the exact queue of leads ready for survey engineer dispatch.
  - Usable roof area and system type pre-set on the lead seed the survey form.
- **Module 04 (Solar Packages & BOM)**:
  - Consumes `expected_capacity_kw` and `solar_system_type` to recommend standard packages (3 kW, 5 kW, 10 kW).
- **Module 05 (Quotations & Sales Orders)**:
  - Quotations (`sale.order`) will link directly to `opportunity_id` / `lead_id` and `partner_id`.
- **Module 13 (Dashboards & Reporting)**:
  - Analyzes lead intake channel distribution (`solar_lead_source`), qualification conversion rates, and average system sizing demands.

---

## 7. Known Limitations & Deliberate Scope Boundaries

- Site survey measurements, azimuth, tilt angles, and shadow simulation are deferred to **Module 03**.
- Price estimations, equipment pricing, and formal quotations belong to **Module 05**.
- WhatsApp API gateway / automatic webhooks are not included in this module; inquiries from WhatsApp are logged via the `solar_lead_source = 'whatsapp'` intake channel.
