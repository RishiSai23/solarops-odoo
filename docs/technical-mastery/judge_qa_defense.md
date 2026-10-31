# Phase 4 Judge Preparation & Architectural Defense (`judge_qa_defense.md`)

This guide prepares the engineering team to defend every architectural decision, data model choice, failure recovery mechanism, and code implementation of **Phase 4: Stock & Procurement Management** during the Odoo × GCET Hackathon Finale.

---

## Section A: Beginner Questions (10 Questions)

### Q1: What is the primary purpose of Phase 4 in the SunFlow platform?
**Answer**:
Phase 4 connects commercial solar project sales with warehouse operations and procurement. Rather than treating inventory as an isolated CRUD tool, Phase 4 automatically translates a confirmed customer order into itemized component demand lines (`solar.stock.requirement`), queries real warehouse availability, raises vendor purchase orders for deficits, tracks high-value serial numbers (inverters, batteries), and validates native Odoo delivery pickings to deduct stock.

---

### Q2: Which Odoo models are created or extended in Phase 4?
**Answer**:
- **New Models Created**:
  1. `solar.package.component`: BOM lines linked to a package template ([`package_bom.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/package_bom.py#L18)).
  2. `solar.stock.requirement`: Project component demand and availability status ([`stock_requirement.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py#L19)).
  3. `solar.equipment.dispatch`: Material delivery header manifest ([`equipment_dispatch.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/equipment_dispatch.py#L20)).
  4. `solar.equipment.dispatch.line`: Itemized delivery lines with serial tracking ([`equipment_dispatch.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/equipment_dispatch.py#L227)).
- **Existing Models Extended via `_inherit`**:
  1. `solar.package`: Extended with `component_ids` and `component_count` ([`solar_package_ext.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L20)).
  2. `solar.project`: Extended with `stock_requirement_ids`, `dispatch_ids`, status flags, and action methods ([`solar_package_ext.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L53)).

---

### Q3: What is the difference between `product.template` and `product.product` in Odoo?
**Answer**:
In Odoo, `product.template` represents the abstract commercial concept of an item (e.g. "Mono PERC 550W Panel"), whereas `product.product` represents the specific purchaseable/storable variant. Physical inventory movements, serial numbers (`stock.lot`), and stock balances (`stock.quant`) **always reference `product.product`**. SunFlow's BOMs and requirements link to `product.product` for exact stock precision.

---

### Q4: How does a user generate stock requirements for a solar project?
**Answer**:
When a solar project reaches stage `'order'`, the user opens the project form view and clicks the button **"Generate Stock Requirements"** (`action_generate_stock_requirements`). This method inspects the assigned `package_id`, reads its `component_ids`, creates a `solar.stock.requirement` line for every component, triggers an initial stock check, and advances the project stage to `'procurement'`.

---

### Q5: What are the possible lifecycle statuses of a `solar.stock.requirement`?
**Answer**:
The field `status` in `solar.stock.requirement` has six states:
1. `draft`: Initial demand generated from package BOM.
2. `available`: Full required quantity is on-hand and unreserved in warehouse.
3. `partial`: Some stock is on-hand, but less than the full required quantity.
4. `shortage`: Zero available stock on-hand.
5. `reserved`: Inventory has been reserved for this project.
6. `dispatched`: Goods have been validated and left the warehouse.

---

### Q6: What does the `is_serialized` field do on a BOM component line?
**Answer**:
The boolean `is_serialized` indicates whether individual serial numbers must be recorded for that product. When set to `True` (e.g. on inverters or battery banks), this flag propagates from `solar.package.component` to `solar.stock.requirement` and down to `solar.equipment.dispatch.line`, where the dispatch validation gate blocks completion until a `stock.lot` is scanned.

---

### Q7: Where are serial numbers stored in Odoo?
**Answer**:
Serial and lot numbers are stored in Odoo's native `stock.lot` model (in Odoo versions prior to 16, known as `stock.production.lot`). Each lot record stores `name` (the scanned serial barcode), `product_id`, and `company_id`.

---

### Q8: What happens when a user clicks the "Refresh Stock" button on a requirement?
**Answer**:
It calls `action_check_stock()`, which executes a search on `stock.quant` for the active company warehouse. It computes physical on-hand quantity, subtracts reserved quantities, queries incoming purchase orders, re-calculates available stock and shortage deficit, and updates the requirement's `status`.

---

### Q9: How is a Purchase Order generated from an equipment shortage?
**Answer**:
Clicking the "Buy" button on a requirement in shortage triggers `action_create_purchase_order()`. The method reads `self.qty_shortage`, resolves the primary vendor from `product_tmpl_id.seller_ids`, creates a native `purchase.order` with a line pre-filled with the exact deficit quantity, links the PO line back to the requirement, and displays the draft PO in Odoo's form view.

---

### Q10: What security groups control access to Phase 4 models?
**Answer**:
Defined in `security/ir.model.access.csv`:
- `base.group_user` (Internal User / Technician): Read permissions on BOM components; Read, Create, and Write on Requirements and Dispatches; Unlink (deletion) is **denied** to preserve audit trails.
- `base.group_system` (Administrator / Operations Manager): Full Read, Write, Create, and Unlink permissions across all Phase 4 tables.

---

## Section B: Intermediate Questions (10 Questions)

### Q11: Why did we build a lightweight BOM model (`solar.package.component`) instead of using Odoo's native MRP module (`mrp.bom`)?
**Answer**:
1. **Module Bloat & Target Fit**: Odoo's native `mrp` module is designed for discrete shop-floor manufacturing with work centers, routing operations, production orders, and scrap management. Solar EPC companies assemble pre-manufactured kits at customer rooftops; they do not run factory workcenters.
2. **Community Edition Compatibility**: Relying on `mrp` creates heavy dependencies and overhead for small-to-medium solar contractors.
3. **Domain Ergonomics**: `solar.package.component` natively includes solar-specific fields like `component_type` (panel, inverter, battery, racking, cable) and direct `is_serialized` toggles that standard `mrp.bom.line` lacks.

---

### Q12: Why does SunFlow query `stock.quant` directly instead of reading `product_id.qty_available`?
**Answer**:
In Odoo, `product_id.qty_available` is a computed field whose value depends on the active context (`location_id`, `warehouse_id`, `company_id`). Calling it directly on `product.product` across multi-warehouse or multi-company environments often aggregates stock across all company locations (including transit and customer return scrap).
By querying `stock.quant` explicitly with:
```python
domain = [
    ('product_id', '=', product.id),
    ('location_id', 'child_of', warehouse.lot_stock_id.id),
]
```
SunFlow isolates the exact physical storable stock inside the **primary installation warehouse's internal storage location (`WH/Stock`)**, preventing false-positive stock assertions.

---

### Q13: What is the exact mathematical difference between on-hand, reserved, available, and incoming quantities?
**Answer**:
$$\text{qty\_on\_hand} = \sum \text{stock.quant.quantity inside WH/Stock}$$
$$\text{qty\_reserved} = \sum \text{stock.quant.reserved\_quantity (committed to other active pickings)}$$
$$\text{qty\_available} = \max(0.0, \text{qty\_on\_hand} - \text{qty\_reserved}) \quad \text{[Free, unallocated stock]}$$
$$\text{qty\_incoming} = \sum (\text{PO line product\_qty} - \text{qty\_received}) \quad \text{[Confirmed POs on-order]}$$
$$\text{qty\_shortage} = \max(0.0, \text{required\_qty} - \text{qty\_available})$$

---

### Q14: How does `_get_incoming_qty()` calculate on-order stock?
**Answer**:
In [`stock_requirement.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py#L183-L192):
```python
def _get_incoming_qty(self, product, warehouse):
    pol = self.env['purchase.order.line'].search([
        ('product_id', '=', product.id),
        ('order_id.state', 'in', ['purchase', 'done']),
    ])
    return sum(max(0.0, line.product_qty - line.qty_received) for line in pol)
```
It searches `purchase.order.line` filtered strictly to orders in confirmed `'purchase'` or `'done'` state, and calculates the delta `line.product_qty - line.qty_received`. Draft or cancelled POs are excluded.

---

### Q15: How does the system handle multiple requirements generated for the same project?
**Answer**:
When `action_generate_stock_requirements()` executes, it deletes previous `draft` requirements via `draft_reqs.unlink()`. However, if any requirement has already reached `'reserved'` or `'dispatched'` status, it is **preserved** to prevent deleting active material commitments while regenerating missing components.

---

### Q16: How does `solar.equipment.dispatch` ensure that serial numbers match the expected product?
**Answer**:
Via two layers of defense:
1. In `inventory_views.xml`, the tree line has an XML domain:
   ```xml
   <field name="lot_id" domain="[('product_id', '=', product_id)]"/>
   ```
2. In `equipment_dispatch.py`, model constraint `_check_lot_product_match` enforces:
   ```python
   @api.constrains('lot_id', 'product_id')
   def _check_lot_product_match(self):
       for rec in self:
           if rec.lot_id and rec.lot_id.product_id != rec.product_id:
               raise ValidationError(_('Serial/Lot "%s" belongs to "%s" but this line is for "%s".') % ...)
   ```

---

### Q17: What is the relationship between `solar.equipment.dispatch` and native `stock.picking`?
**Answer**:
`solar.equipment.dispatch` is an operational business manifest designed for solar project managers. `stock.picking` is Odoo's low-level ERP warehouse transfer.
When `action_validate_dispatch()` runs, it calls `_create_native_stock_picking()`, which creates a delivery order picking (`WH/OUT`), assigns lines, binds serial numbers to `stock.move.line`, and executes `picking.button_validate()`. The picking ID is stored in `dispatch.picking_id` with a smart button linking directly to the native Odoo delivery order.

---

### Q18: What is the purpose of `serial_validation_complete` on `solar.equipment.dispatch`?
**Answer**:
It is a computed boolean:
```python
@api.depends('line_ids', 'line_ids.lot_id', 'line_ids.is_serialized')
def _compute_serial_validation(self):
    for rec in self:
        serial_lines = rec.line_ids.filtered('is_serialized')
        rec.serial_validation_complete = all(line.lot_id for line in serial_lines)
```
In `inventory_views.xml`, this field drives dynamic UI alert banners: displaying a blue alert when serial numbers are pending, and a green success alert when all required serial numbers have been scanned.

---

### Q19: Why was `action_cancel()` on `solar.equipment.dispatch` designed to raise a `UserError` if state is `'dispatched'`?
**Answer**:
Once equipment is dispatched, physical stock has left the warehouse and `stock.picking` is committed in `'done'` state. Allowing a user to simply click "Cancel" on the dispatch header would desynchronize the custom dispatch record from Odoo's physical accounting and inventory ledger. If equipment is returned, a formal return picking / RMA workflow must be executed instead.

---

### Q20: How are sequences configured for equipment dispatches?
**Answer**:
In [`data/solar_data.xml`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/data/solar_data.xml#L7-L15):
```xml
<record id="seq_solar_equipment_dispatch" model="ir.sequence">
    <field name="name">Solar Equipment Dispatch</field>
    <field name="code">solar.equipment.dispatch</field>
    <field name="prefix">DISP-%(y)s%(month)s%(day)s-</field>
    <field name="padding">4</field>
</record>
```
In `equipment_dispatch.py`, `create()` overrides the default name `'New'` by calling `self.env['ir.sequence'].next_by_code('solar.equipment.dispatch')`.

---

## Section C: Advanced Architecture & Failure-Handling Questions (10 Questions)

### Q21: How does SunFlow strictly prevent duplicate serial number allocation across multiple customer projects?
**Answer**:
In [`equipment_dispatch.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/equipment_dispatch.py#L356-L375):
```python
@api.constrains('lot_id', 'dispatch_id')
def _check_duplicate_serial_across_projects(self):
    for rec in self:
        if rec.lot_id and rec.dispatch_id and rec.dispatch_id.project_id:
            dispatched_headers = self.env['solar.equipment.dispatch'].search([
                ('state', '=', 'dispatched'),
                ('project_id', '!=', rec.dispatch_id.project_id.id),
            ])
            conflicting = self.env['solar.equipment.dispatch.line'].search([
                ('lot_id', '=', rec.lot_id.id),
                ('dispatch_id', 'in', dispatched_headers.mapped('id')),
                ('id', '!=', rec.id),
            ])
            if conflicting:
                raise ValidationError(_(
                    'Serial/Lot "%s" has already been dispatched to project "%s" (Dispatch: %s). '
                    'Duplicate allocation is not permitted.'
                ) % (rec.lot_id.name, conflicting[0].dispatch_id.project_id.name, conflicting[0].dispatch_id.name))
```
**Why this is robust**:
1. It executes in PostgreSQL immediately during `create()` or `write()`.
2. It specifically checks other projects (`project_id != self.project_id`), allowing legitimate re-dispatches to the *same* project (e.g. warranty re-shipping or staged deliveries).
3. If a conflict is found, it raises `ValidationError`, triggering an immediate database rollback.

---

### Q22: What happens if native Odoo stock picking validation (`picking.button_validate()`) fails during dispatch?
**Answer**:
In Python and PostgreSQL, `action_validate_dispatch()` runs inside a **single atomic database transaction**.
If `picking.button_validate()` fails (for example, if physical quants were moved out-of-band, or if warehouse stock is locked):
1. Native Odoo raises an exception (`UserError` or `ValidationError`).
2. PostgreSQL issues a `ROLLBACK` to the transaction savepoint.
3. The custom `solar.equipment.dispatch` **does not** advance to `'dispatched'`.
4. The requirement lines **do not** change status.
5. No inconsistent phantom states are left in the database.

---

### Q23: Why do we bind serial numbers to `stock.move.line` rather than `stock.move` in `_create_native_stock_picking()`?
**Answer**:
In Odoo's internal stock architecture:
- `stock.move` represents the *commercial demand* (e.g. "Move 1 Inverter"). It does not store individual serial numbers.
- `stock.move.line` represents the *physical execution* (e.g. "Take Inverter SN `INV-9901` from Shelf A and put in Delivery Bay").
Assigning `lot_id` directly to `stock.move.line` guarantees that Odoo's native stock ledger, inventory valuation, and barcode tracking engines record the exact serialized asset deduction.

---

### Q24: What is the architectural difference between running Phase 4 in Docker Odoo 17 vs the standalone simulation harness?
**Answer**:
- **Simulation Harness (`scripts/verify_phase4_runtime.py`)**: Emulates the Odoo ORM environment using local Python mocks. It tests Python business logic, status transitions, and formula calculations without a running database daemon.
- **Genuine Odoo 17 Environment (`sunflow_odoo` Docker)**: Executes against real PostgreSQL 16. It validates native foreign key constraints, XML view compilation (`view_solar_project_form_phase4`), actual `stock.quant` database balances, `ir.sequence` locks, and native `stock.picking` state engines.
*All 25 tests pass in both environments, and genuine Odoo 17 was certified via [`verify_runtime_e2e.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/verify_runtime_e2e.py).*

---

### Q25: Why did Odoo 17 reject our view XML with `ParseError: Since 17.0, the "attrs" and "states" attributes are no longer used`?
**Answer**:
In Odoo 17.0, the framework revamped its web client and OWL compiler, completely removing Python-string evaluation of `attrs` dictionaries (`attrs="{'invisible': [('state', '=', 'draft')]}"`). View attributes must now be written as direct expressions (`invisible="state == 'draft'"`). Furthermore, Odoo 17 requires every field used in such dynamic expressions to be registered in the view architecture, prompting us to add `<field name="..." invisible="1"/>` declarations.

---

### Q26: How does the platform prevent race conditions when two technicians attempt to allocate the same serial number simultaneously?
**Answer**:
1. At the ORM level, `@api.constrains('lot_id', 'dispatch_id')` performs an active search across dispatched headers.
2. At the database level, `picking.action_assign()` and `picking.button_validate()` place row-level locks (`SELECT FOR UPDATE`) on the corresponding `stock.quant` records.
3. If Technician A validates dispatch for `INV-001`, the quant is decremented to 0. If Technician B attempts to validate dispatch for the same lot moments later, Odoo's native `_sanity_check()` blocks the transfer because available quant quantity is 0.

---

### Q27: How does SunFlow resolve vendor pricing when automatically creating a Purchase Order?
**Answer**:
In `action_create_purchase_order()`:
```python
tmpl = self.product_id.product_tmpl_id
vendor = tmpl.seller_ids[:1] if tmpl and hasattr(tmpl, 'seller_ids') and tmpl.seller_ids else False
partner_id = vendor.partner_id.id if vendor else False
price_unit = vendor.price if vendor else 0.0
```
It accesses `seller_ids` on the product template (which stores Odoo's `product.supplierinfo` supplier price lists). It resolves the primary vendor and contract price. If no vendor is pre-configured, it creates the PO without a vendor (`partner_id=False`, `price_unit=0.0`), allowing the procurement officer to select a supplier manually.

---

### Q28: How does the system handle partial deliveries from suppliers?
**Answer**:
When a supplier delivers only part of a PO (e.g. 6 out of 10 panels):
1. The warehouse receives 6 panels in the incoming `stock.picking`.
2. Odoo automatically creates a **Backorder** for the remaining 4 panels.
3. The warehouse's `stock.quant` increases by 6.
4. Calling `action_check_stock()` updates the project requirement:
   - `qty_on_hand` becomes 6.0.
   - `qty_incoming` becomes 4.0 (remaining on backorder).
   - `qty_shortage` drops to 4.0.
   - Status transitions from `'shortage'` to `'partial'`.

---

### Q29: What are the current architectural limitations of Phase 4?
**Answer**:
1. **Single Warehouse Default**: Current logic resolves `wh = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)`. In a company with multiple regional warehouses (e.g. Ahmedabad Central vs Surat Hub), multi-warehouse routing rules must be added.
2. **Batch Serial Scanning**: Currently requires scanning serial numbers line-by-line. A mobile camera barcode stream or bulk CSV upload in the frontend PWA will streamline high-volume panel scanning.
3. **Automated PO Grouping**: Currently creates 1 PO per shortage line. In production, shortages across multiple requirements for the same vendor should be consolidated into a single PO with multiple lines.

---

### Q30: How will Phase 4 inventory and dispatch records connect to Phase 5 (Installation & Warranty)?
**Answer**:
The serial numbers validated in Phase 4 are the **authoritative foundation** for the next lifecycle stages:
1. **Phase 5 (Installation Work Orders)**: The installation technician's mobile checklist imports the dispatched equipment serial numbers from `solar.equipment.dispatch.line`, verifying on-site physical possession before installation.
2. **Phase 5 (Digital Warranty Generation)**: Upon customer sign-off, the system reads the dispatched inverter and battery `stock.lot` records and automatically instantiates `solar.warranty` records linked to the customer, beginning the 5-year inverter and 25-year panel performance warranty clocks.

