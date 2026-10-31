# Phase 4: Stock & Procurement Management — Reverse Engineering & Technical Deep-Dive

This document provides a comprehensive, code-level technical breakdown of **Phase 4 (Stock & Procurement Management)** of Project SunFlow (`sunflow_core` Odoo addon).

---

## 1. Architectural Role in Project SunFlow

In a rooftop solar EPC installation company (reference: SunPower Solutions, 40+ installations/month, 15 field technicians), material management is not a simple retail sale. It connects:
1. **Commercial Engineering**: Sizing solar packages (1 kW to 5 kW On-Grid / Off-Grid / Hybrid) with a precise Bill of Materials (BOM).
2. **Dynamic Demand Generation**: Instantiating required component lines directly from confirmed projects without manual data entry.
3. **Live Quant Inspection**: Checking actual physical availability in the warehouse via native `stock.quant` without artificial or fake stock manipulations.
4. **Shortage Procurement**: Raising purchase orders (`purchase.order`) directly from shortages with vendor auto-resolution.
5. **High-Value Serial Traceability**: Enforcing serial number tracking (`stock.lot`) for inverters and batteries before site dispatch to prevent warranty loss and legal liabilities.
6. **Cross-Project Duplicate Allocation Defense**: Prohibiting the same serial number from being allocated or dispatched to multiple active projects.

```
+-------------------------------------------------------------------------------------------------------+
|                                    PHASE 4 DATA & WORKFLOW TOPOLOGY                                   |
|                                                                                                       |
|  [ solar.package ]                                                                                    |
|         │ 1                                                                                           |
|         │ One2many (component_ids)                                                                    |
|         ▼ *                                                                                           |
|  [ solar.package.component ] ──► Many2one ──► [ product.product ]                                     |
|         │                                             ▲                                               |
|         │ Generates (on project stage = 'order')      │                                               |
|         ▼                                             │                                               |
|  [ solar.stock.requirement ] ──► Many2one ────────────┘                                               |
|         │                                                                                             |
|         ├── Reads ──► [ stock.quant ] (on-hand, reserved, free)                                       |
|         ├── Reads ──► [ purchase.order.line ] (incoming on-order)                                     |
|         └── Creates ─► [ purchase.order ] (if shortage detected)                                      |
|                                                                                                       |
|  [ solar.equipment.dispatch ]                                                                         |
|         │ 1                                                                                           |
|         │ One2many (line_ids)                                                                         |
|         ▼ *                                                                                           |
|  [ solar.equipment.dispatch.line ] ──► Many2one ──► [ stock.lot ] (Serial / Lot Validation)          |
|         │                                                                                             |
|         └── Creates & Validates ──► [ stock.picking ] (Native Delivery Order -> WH/Stock to Customer) |
+-------------------------------------------------------------------------------------------------------+
```

---

## 2. Models & Fields Reverse Engineering

### 2.1. `solar.package.component` (File: [`package_bom.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/package_bom.py))

Represents a single Bill of Materials (BOM) line for a standardized modular solar package template.

```python
class SolarPackageComponent(models.Model):
    _name = 'solar.package.component'
    _description = 'Solar Package — Bill of Materials Component Line'
    _order = 'sequence, id'
```

#### Field Specifications:

| Field | Type | Attributes | Purpose & Architectural Connections |
|---|---|---|---|
| `sequence` | `Integer` | `default=10` | Display order in BOM tree views and touch interfaces. |
| `package_id` | `Many2one` | `'solar.package'`, `required=True`, `ondelete='cascade'`, `index=True` | Parent package reference. Cascades deletion if the package template is dropped. |
| `product_id` | `Many2one` | `'product.product'`, `required=True`, `domain=[('type', 'in', ['product', 'consu'])]` | Odoo catalog product. Domain filters strictly to storable or consumable items (excluding service products). |
| `product_tmpl_id` | `Many2one` | `'product.template'`, `related='product_id.product_tmpl_id'`, `store=True` | Stored related field providing fast indexing back to the product template. |
| `product_uom_id` | `Many2one` | `'uom.uom'`, `related='product_id.uom_id'`, `readonly=True` | Related unit of measure (Units, Meters, Sets) resolved from the master product. |
| `quantity` | `Float` | `required=True`, `default=1.0` | Quantity of this component required per 1 package installation. |
| `component_type` | `Selection` | `required=True`, `default='other'` | Solar operational taxonomy: `panel`, `inverter`, `battery`, `controller`, `mounting`, `cable`, `connector`, `db_box`, `earthing`, `other`. |
| `is_serialized` | `Boolean` | `default=False` | Flags whether individual serial numbers (`stock.lot`) must be captured during field dispatch. |
| `notes` | `Char` | — | Technical sizing notes (e.g. "550W Tier-1 Bifacial", "MC4 IP68 Rated"). |

#### Model Constraints:

##### `_check_quantity_positive(self)`
```python
@api.constrains('quantity')
def _check_quantity_positive(self):
    for rec in self:
        if rec.quantity <= 0:
            raise ValidationError(_(
                'Component quantity must be greater than zero. '
                'Check the BOM line for "%s".'
            ) % rec.product_id.display_name)
```
- **Purpose**: Prevents configuration of zero or negative component demands in a solar BOM.
- **Input**: Recordset of `solar.package.component`.
- **Output**: None (`void`).
- **Records Read**: `rec.quantity`, `rec.product_id.display_name`.
- **Validation**: Checks `rec.quantity <= 0`.
- **Failure**: Raises `odoo.exceptions.ValidationError`.
- **Corresponding Test**: [`TestPackageBOM.test_03_bom_quantity_constraint`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L88-L101).

---

### 2.2. Package & Project Extensions (File: [`solar_package_ext.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py))

Extends `solar.package` and `solar.project` via classical Odoo model inheritance (`_inherit`).

#### A. `solar.package` Extension:

| Field | Type | Attributes | Purpose |
|---|---|---|---|
| `component_ids` | `One2many` | `'solar.package.component'`, `'package_id'` | Relational collection of BOM component lines for the package. |
| `component_count` | `Integer` | `compute='_compute_component_count'`, `store=True` | Stored count of BOM lines for fast UI smart-button rendering. |

#### B. `solar.project` Extension:

| Field | Type | Attributes | Purpose |
|---|---|---|---|
| `package_id` | `Many2one` | `'solar.package'` | Solar package template assigned to this operational installation project. |
| `stock_requirement_ids` | `One2many` | `'solar.stock.requirement'`, `'project_id'` | Active inventory demand lines derived from the package BOM. |
| `dispatch_ids` | `One2many` | `'solar.equipment.dispatch'`, `'project_id'` | Dispatches issued for physical site delivery of materials. |
| `requirement_count` | `Integer` | `compute='_compute_requirement_count'`, `store=False` | Dynamic line count for smart buttons. |
| `dispatch_count` | `Integer` | `compute='_compute_dispatch_count'`, `store=False` | Count of dispatches issued for the project. |
| `has_shortage` | `Boolean` | `compute='_compute_stock_status'`, `store=False` | Flags `True` if any linked stock requirement has `qty_shortage > 0`. Triggers danger alert in UI. |
| `stock_ready` | `Boolean` | `compute='_compute_stock_status'`, `store=False` | Flags `True` if requirements exist and all lines have `status in ('available', 'reserved', 'dispatched')`. |

#### Detailed Method Reverse Engineering:

##### 1. `action_generate_stock_requirements(self)`
```python
def action_generate_stock_requirements(self):
    self.ensure_one()
    if not self.package_id:
        raise UserError(_('Please assign a Solar Package to this project before generating stock requirements.'))
    if not self.package_id.component_ids:
        raise UserError(_('The selected package "%s" has no BOM components defined...') % self.package_id.name)

    draft_reqs = self.stock_requirement_ids.filtered(lambda r: r.status == 'draft')
    draft_reqs.unlink()

    for comp in self.package_id.component_ids:
        self.env['solar.stock.requirement'].create({
            'project_id': self.id,
            'package_component_id': comp.id,
            'product_id': comp.product_id.id,
            'component_type': comp.component_type,
            'required_qty': comp.quantity,
            'is_serialized': comp.is_serialized,
            'status': 'draft',
        })

    self.stock_requirement_ids.action_check_stock()
    if self.stage == 'order':
        self.stage = 'procurement'
...
```
1. **Purpose**: Automatically generates granular component stock demand lines (`solar.stock.requirement`) from the linked package's BOM components.
2. **Input**: Single `solar.project` record (`self.ensure_one()`).
3. **Output**: Client action dictionary (`display_notification`) showing success message in Odoo web client.
4. **Records Read**: `self.package_id`, `self.package_id.component_ids`, `self.stage`.
5. **Records Created/Modified**:
   - Deletes prior draft requirements (`self.stock_requirement_ids.filtered(lambda r: r.status == 'draft').unlink()`).
   - Creates `N` new `solar.stock.requirement` records where `N = len(package.component_ids)`.
   - Modifies `self.stage` from `'order'` to `'procurement'`.
6. **Validations**:
   - Raises `UserError` if `not self.package_id`.
   - Raises `UserError` if `not self.package_id.component_ids`.
   - Protects already reserved or dispatched requirements from deletion.
7. **Other Methods/Models Called**:
   - `self.stock_requirement_ids.action_check_stock()` (queries native `stock.quant`).
8. **What Happens if It Fails**: Entire transaction rolls back; no partial requirement records or stage transitions are committed.
9. **Corresponding Test**: [`TestStockRequirementGeneration.test_05_generate_requirements_from_bom`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L153-L167) & [`TestProjectStockIntegration.test_21_generate_requirements_advances_project_stage`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L510-L519).

---

##### 2. `action_create_dispatch(self)`
```python
def action_create_dispatch(self):
    self.ensure_one()
    if not self.stock_requirement_ids:
        raise UserError(_('Generate stock requirements before creating a dispatch.'))

    dispatch = self.env['solar.equipment.dispatch'].create({
        'project_id': self.id,
    })

    for req in self.stock_requirement_ids.filtered(lambda r: r.status not in ('dispatched',)):
        self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': dispatch.id,
            'product_id': req.product_id.id,
            'component_type': req.component_type,
            'quantity': req.required_qty,
            'is_serialized': req.is_serialized,
            'stock_requirement_id': req.id,
        })
...
```
1. **Purpose**: Prepares a dispatch delivery manifest pre-populated with components that have not yet been dispatched.
2. **Input**: Single `solar.project` record.
3. **Output**: Window action dictionary navigating the user directly to the newly created dispatch form view.
4. **Records Read**: `self.stock_requirement_ids`.
5. **Records Created/Modified**: Creates 1 `solar.equipment.dispatch` header and `M` `solar.equipment.dispatch.line` items.
6. **Validations**: Raises `UserError` if `not self.stock_requirement_ids`.
7. **Other Methods/Models Called**: `self.env['solar.equipment.dispatch'].create(...)`.
8. **What Happens if It Fails**: Transaction rolls back; no orphan dispatch header is created.
9. **Corresponding Test**: [`TestProjectStockIntegration.test_22_create_dispatch_from_project`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L522-L545).

---

### 2.3. `solar.stock.requirement` (File: [`stock_requirement.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py))

Represents the inventory demand line for a specific solar component required by an active project.

```python
class SolarStockRequirement(models.Model):
    _name = 'solar.stock.requirement'
    _description = 'Solar Project — Inventory Stock Requirement'
    _order = 'sequence, id'
```

#### Field Specifications:

| Field | Type | Attributes | Purpose & Architectural Connections |
|---|---|---|---|
| `project_id` | `Many2one` | `'solar.project'`, `required=True`, `ondelete='cascade'`, `index=True` | Project to which this material demand belongs. |
| `package_component_id` | `Many2one` | `'solar.package.component'`, `ondelete='set null'` | Originating BOM line (if generated from a standard package). |
| `product_id` | `Many2one` | `'product.product'`, `required=True`, `index=True` | Storable component product. |
| `product_uom_id` | `Many2one` | `'uom.uom'`, `related='product_id.uom_id'`, `readonly=True` | Master unit of measure. |
| `component_type` | `Selection` | `required=True` | Solar equipment classification (`panel`, `inverter`, `battery`, etc.). |
| `required_qty` | `Float` | `required=True`, `default=1.0` | Total quantity required for the solar installation. |
| `qty_on_hand` | `Float` | `default=0.0`, `readonly=True` | Physical stock present in the company's internal warehouse locations. |
| `qty_reserved` | `Float` | `default=0.0`, `readonly=True` | Quantity currently reserved by other outgoing stock pickings. |
| `qty_incoming` | `Float` | `default=0.0`, `readonly=True` | Quantity on confirmed purchase orders not yet physically received. |
| `qty_available` | `Float` | `compute='_compute_availability'`, `store=True` | Free unreserved stock (`max(0.0, qty_on_hand - qty_reserved)`). |
| `qty_shortage` | `Float` | `compute='_compute_availability'`, `store=True` | Shortage deficit (`max(0.0, required_qty - qty_available)`). |
| `has_shortage` | `Boolean` | `compute='_compute_availability'`, `store=True` | Fast boolean indicator (`qty_shortage > 0`). |
| `status` | `Selection` | `draft`, `available`, `partial`, `shortage`, `reserved`, `dispatched` | Lifecycle tracking status of this specific material requirement line. |
| `is_serialized` | `Boolean` | `default=False` | Carries serial tracking requirement forward from the BOM. |
| `purchase_order_line_ids` | `Many2many` | `'purchase.order.line'` | Links to procurement lines created to replenish shortages. |

#### Detailed Method Reverse Engineering:

##### 1. `action_check_stock(self)`
```python
def action_check_stock(self):
    for rec in self:
        product = rec.product_id
        company_id = self.env.company.id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1) or self.env['stock.warehouse'].search([], limit=1)
        stock_location = warehouse.lot_stock_id if warehouse else self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        if not stock_location:
            rec.qty_on_hand = 0.0
            rec.qty_reserved = 0.0
            rec.qty_incoming = 0.0
            rec.status = 'shortage'
            continue

        domain = [('product_id', '=', product.id), ('location_id', 'child_of', stock_location.id)]
        quants = self.env['stock.quant'].search(domain)
        on_hand = sum(quants.mapped('quantity'))
        reserved = sum(quants.mapped('reserved_quantity'))
        incoming = self._get_incoming_qty(product, warehouse)

        rec.qty_on_hand = on_hand
        rec.qty_reserved = reserved
        rec.qty_incoming = incoming

        available = max(0.0, on_hand - reserved)
        if rec.status == 'dispatched':
            pass
        elif available >= rec.required_qty:
            rec.status = 'available'
        elif available > 0:
            rec.status = 'partial'
        else:
            rec.status = 'shortage'
```
1. **Purpose**: Queries native Odoo `stock.quant` to determine physical on-hand and reserved quantities, checks incoming POs, and updates status flags.
2. **Input**: Recordset of `solar.stock.requirement`.
3. **Output**: None (`void`).
4. **Records Read**:
   - `stock.warehouse` and `stock.location` for the active company.
   - `stock.quant` matching `location_id child_of stock_location.id` and `product_id`.
   - `purchase.order.line` via `_get_incoming_qty`.
5. **Records Created/Modified**: Updates `qty_on_hand`, `qty_reserved`, `qty_incoming`, and `status` on `solar.stock.requirement`.
6. **Validations**: Defensive fallback if warehouse is unconfigured (defaults to 0/shortage rather than crashing). Preserves `'dispatched'` status if goods have already left the warehouse.
7. **Other Methods/Models Called**: `stock.quant.search()`, `_get_incoming_qty()`.
8. **What Happens if It Fails**: Database rollback; requirement keeps prior snapshot.
9. **Corresponding Test**: [`TestStockRequirementGeneration.test_08_shortage_computed_correctly`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L196-L210) & [`TestStockRequirementGeneration.test_09_no_shortage_when_sufficient`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L211-L224).

---

##### 2. `action_create_purchase_order(self)`
```python
def action_create_purchase_order(self):
    self.ensure_one()
    if not self.has_shortage:
        raise UserError(_('No stock shortage detected for %s.') % self.product_id.display_name)

    tmpl = self.product_id.product_tmpl_id
    vendor = tmpl.seller_ids[:1] if tmpl and hasattr(tmpl, 'seller_ids') and tmpl.seller_ids else False
    partner_id = vendor.partner_id.id if vendor else False

    po_uom = self.product_id.uom_po_id or self.product_id.uom_id
    po_vals = {
        'partner_id': partner_id,
        'order_line': [(0, 0, {
            'product_id': self.product_id.id,
            'product_qty': self.qty_shortage,
            'price_unit': vendor.price if vendor else 0.0,
            'name': self.product_id.display_name,
            'product_uom': po_uom.id if po_uom else False,
            'date_planned': fields.Datetime.now(),
        })],
    }
    po = self.env['purchase.order'].create(po_vals)
    self.purchase_order_line_ids = [(4, po.order_line[0].id)]
...
```
1. **Purpose**: Instantly creates a native Odoo Draft Purchase Order (`purchase.order`) sized exactly to cover the component shortage deficit.
2. **Input**: Single `solar.stock.requirement` with `has_shortage == True`.
3. **Output**: Window action dictionary opening the newly created PO in form view.
4. **Records Read**: `self.product_id`, `product.template.seller_ids` (Tier-1 vendor list), `self.qty_shortage`.
5. **Records Created/Modified**:
   - Creates 1 `purchase.order` with 1 `purchase.order.line`.
   - Links PO line to `self.purchase_order_line_ids` via Many2many ORM tuple `(4, po_line.id)`.
6. **Validations**: Raises `UserError` if `not self.has_shortage`. Defensively checks whether vendor sellers are configured on the template.
7. **Other Methods/Models Called**: `self.env['purchase.order'].create(po_vals)`.
8. **What Happens if It Fails**: Entire transaction rolls back; no orphan PO or broken requirement links are left.
9. **Corresponding Test**: Verified in [`scripts/verify_runtime_e2e.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/verify_runtime_e2e.py#L123-L132) (Step 8 & 9) and simulated in `verify_phase4_runtime.py`.

---

### 2.4. `solar.equipment.dispatch` & `solar.equipment.dispatch.line` (File: [`equipment_dispatch.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/equipment_dispatch.py))

Manages the serialized site delivery lifecycle, bridging solar business operations with Odoo's native `stock.picking` warehouse transfer engine.

```python
class SolarEquipmentDispatch(models.Model):
    _name = 'solar.equipment.dispatch'
    _description = 'Solar Equipment Dispatch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'dispatch_date desc, id desc'
```

#### Field Specifications:

| Field | Type | Attributes | Purpose |
|---|---|---|---|
| `name` | `Char` | `required=True`, `copy=False`, `readonly=True`, `default='New'` | Unique sequential identifier (`DISP-%(y)s%(month)s%(day)s-XXXX`). |
| `project_id` | `Many2one` | `'solar.project'`, `required=True`, `index=True` | Destination solar project. |
| `partner_id` | `Many2one` | `'res.partner'`, `related='project_id.partner_id'`, `store=True` | Customer recipient. |
| `picking_id` | `Many2one` | `'stock.picking'`, `readonly=True`, `copy=False` | Native Odoo delivery order generated to commit stock out of warehouse. |
| `state` | `Selection` | `draft`, `ready`, `dispatched`, `cancelled` | Dispatch state machine. |
| `line_ids` | `One2many` | `'solar.equipment.dispatch.line'`, `'dispatch_id'` | Itemized list of materials and serial numbers in this delivery. |
| `serial_validation_complete`| `Boolean` | `compute='_compute_serial_validation'`, `store=False` | Flags `True` if all lines with `is_serialized=True` have `lot_id` assigned. |
| `total_lines` | `Integer` | `compute='_compute_line_counts'` | Total lines in dispatch manifest. |
| `validated_lines` | `Integer` | `compute='_compute_line_counts'` | Count of lines with assigned lots or non-serialized lines. |

#### Detailed Method Reverse Engineering:

##### 1. `action_validate_dispatch(self)`
```python
def action_validate_dispatch(self):
    self.ensure_one()
    if self.state != 'ready':
        raise UserError(_('Dispatch can only be validated from "Ready for Dispatch" state.'))

    unvalidated = self.line_ids.filtered(lambda l: l.is_serialized and not l.lot_id)
    if unvalidated:
        names = '\n• '.join(unvalidated.mapped('product_id.display_name'))
        raise UserError(_(
            'The following components require serial numbers before dispatch can be validated:\n• %s'
        ) % names)

    for line in self.line_ids:
        line._validate_serial()

    picking = self._create_native_stock_picking()
    self.write({
        'state': 'dispatched',
        'actual_dispatch_date': fields.Datetime.now(),
        'dispatched_by': self.env.user.id,
        'picking_id': picking.id,
    })

    for line in self.line_ids:
        if line.stock_requirement_id:
            line.stock_requirement_id.status = 'dispatched'
...
```
1. **Purpose**: Final operational gate for equipment dispatch. Validates serial numbers, verifies warehouse physical availability, generates and validates native Odoo `stock.picking`, deducts stock from `stock.quant`, and updates requirement statuses.
2. **Input**: Single `solar.equipment.dispatch` in `'ready'` state.
3. **Output**: Success dictionary notification.
4. **Records Read**: `self.line_ids`, `self.line_ids.lot_id`, `self.project_id`, `self.picking_id`.
5. **Records Created/Modified**:
   - Creates 1 native `stock.picking` (type: delivery order) with `stock.move` and `stock.move.line` items.
   - Modifies `self.state = 'dispatched'`.
   - Modifies `self.actual_dispatch_date = now()`, `self.dispatched_by = uid`.
   - Modifies linked `stock_requirement_id.status = 'dispatched'`.
6. **Validations**:
   - Blocks validation if `state != 'ready'`.
   - Blocks validation if any line has `is_serialized=True` and `lot_id=False` (lists missing products).
   - Calls `line._validate_serial()` for each line: checks product matching, warehouse availability, and cross-project duplicate allocation.
7. **Other Methods/Models Called**:
   - `line._validate_serial()`.
   - `self._create_native_stock_picking()`.
   - Native `picking.button_validate()`.
8. **What Happens if It Fails**: Entire transaction rolls back. Neither Odoo stock movements nor dispatch state transitions occur.
9. **Corresponding Test**: [`TestDispatchWorkflow.test_17_validate_dispatch_requires_serial_numbers`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L427-L448) & E2E verification Step 12 & 13.

---

##### 2. `_create_native_stock_picking(self)`
```python
def _create_native_stock_picking(self):
    self.ensure_one()
    company_id = self.env.company.id
    warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1) or self.env['stock.warehouse'].search([], limit=1)
    if not warehouse:
        raise UserError(_('No warehouse found for company %s.') % self.env.company.name)

    customer_loc = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
    picking_type = warehouse.out_type_id
    src_loc = warehouse.lot_stock_id

    move_vals = []
    for line in self.line_ids:
        move_vals.append((0, 0, {
            'name': _('Solar Dispatch — %s') % line.product_id.display_name,
            'product_id': line.product_id.id,
            'product_uom': line.product_id.uom_id.id,
            'product_uom_qty': line.quantity,
            'location_id': src_loc.id,
            'location_dest_id': customer_loc.id,
        }))

    picking = self.env['stock.picking'].create({
        'picking_type_id': picking_type.id,
        'location_id': src_loc.id,
        'location_dest_id': customer_loc.id,
        'origin': _('Solar Dispatch %s for Project %s') % (self.name, self.project_id.name),
        'partner_id': self.partner_id.id if self.partner_id else False,
        'move_ids': move_vals,
    })

    picking.action_confirm()
    picking.action_assign()

    for line in self.line_ids.filtered('lot_id'):
        matching_ml = picking.move_line_ids.filtered(lambda ml: ml.product_id == line.product_id)
        if matching_ml:
            matching_ml[0].write({'lot_id': line.lot_id.id, 'quantity': line.quantity})
        else:
            matching_move = picking.move_ids.filtered(lambda m: m.product_id == line.product_id)
            self.env['stock.move.line'].create({
                'picking_id': picking.id,
                'move_id': matching_move[0].id if matching_move else False,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'quantity': line.quantity,
                'lot_id': line.lot_id.id,
                'location_id': src_loc.id,
                'location_dest_id': customer_loc.id,
            })

    for ml in picking.move_line_ids:
        if not ml.quantity:
            ml.quantity = ml.move_id.product_uom_qty

    picking.button_validate()
    return picking
```
1. **Purpose**: Bridges custom solar operations directly with Odoo's core inventory engine. Creates, reserves, lot-binds, and confirms a standard Delivery Order picking.
2. **Input**: Validated `solar.equipment.dispatch` record.
3. **Output**: Validated `stock.picking` record in `'done'` state.
4. **Records Read**: Company warehouse, customer location (`usage='customer'`), outgoing picking type (`warehouse.out_type_id`), warehouse lot stock location (`warehouse.lot_stock_id`).
5. **Records Created/Modified**:
   - Creates 1 `stock.picking`.
   - Creates `stock.move` lines for every equipment component.
   - Creates or updates `stock.move.line` binding specific serial numbers (`lot_id`) to the picking.
   - Odoo's internal stock quant engine deducts quantities from `WH/Stock` and credits `Partner Locations/Customers`.
6. **Validations**: Confirms warehouse existence. Verifies that picking moves can be confirmed and assigned.
7. **Other Methods/Models Called**: `stock.picking.create()`, `action_confirm()`, `action_assign()`, `button_validate()`.
8. **What Happens if It Fails**: Entire transaction rolls back; dispatch remains unconfirmed.
9. **Corresponding Test**: Verified in genuine Odoo 17 E2E workflow script Step 12 & 13.

---

##### 3. `_check_duplicate_serial_across_projects(self)` (Line Model Constraint)
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
                ) % (
                    rec.lot_id.name,
                    conflicting[0].dispatch_id.project_id.name,
                    conflicting[0].dispatch_id.name,
                ))
```
1. **Purpose**: Enforces real-time asset exclusivity across projects. Prevents allocating an expensive inverter or battery that has already been dispatched to another customer.
2. **Input**: Recordset of `solar.equipment.dispatch.line`.
3. **Output**: None (`void`).
4. **Records Read**: Search on `solar.equipment.dispatch` for dispatched records on other projects, search on `solar.equipment.dispatch.line` for matching lots.
5. **Validations**: Checks whether `rec.lot_id` is present in any other dispatched project.
6. **Failure**: Raises `ValidationError` immediately at record creation or update.
7. **Corresponding Test**: [`TestSerialNumberValidation.test_12_duplicate_lot_dispatched_to_different_project`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/tests/test_phase4_inventory.py#L294-L325) & E2E script Step 14.

---

## 3. UI Views & Actions Architecture ([`inventory_views.xml`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/views/inventory_views.xml))

### View Structure:
1. **BOM Component Views**:
   - `view_solar_package_component_tree`: Editable bottom tree showing product, component type, quantity, UoM, and serial tracking flag.
   - `view_solar_package_form`: Smart button extension displaying BOM Line count on `solar.package`.
2. **Stock Requirement Views**:
   - `view_solar_stock_requirement_tree`: Color-coded tree (`decoration-danger="has_shortage == True"`, `decoration-success="status == 'available'"`). Features in-row actions for "Refresh Stock" and direct "Buy" (Purchase Order creation).
   - `view_solar_stock_requirement_form`: Status bar (`draft`, `available`, `shortage`, `reserved`, `dispatched`), snapshot groups, and linked PO tags.
   - Filter action `action_solar_stock_shortages`: Pre-filtered window action displaying only requirements with `status in ('shortage', 'partial')`.
3. **Equipment Dispatch Views**:
   - `view_solar_equipment_dispatch_form`: Header state machine (`draft` -> `ready` -> `dispatched`), smart button to native `stock.picking` delivery order, serial validation alert boxes (dynamic green/blue status), and editable bottom line tree requiring `lot_id` for serialized items.
4. **Project Lifecycle Form Integration (`view_solar_project_form_phase4`)**:
   - Inherits `view_solar_project_form` via xpath.
   - Smart buttons for Requirements count (`oe_stat_button` icon `fa-cubes`) and Dispatches count (`fa-truck`).
   - "Inventory & Dispatch" notebook tab featuring Shortage Warning banner, Action Buttons (`Generate Stock Requirements`, `Refresh Stock`, `Create Dispatch`), and embedded Requirements tree.

---

## 4. Odoo Framework Mechanics Used in Phase 4

| Odoo Concept | Exact Usage in Phase 4 | File & Line Reference |
|---|---|---|
| `models.Model` | Base classes for all entities (`SolarPackageComponent`, `SolarStockRequirement`, `SolarEquipmentDispatch`, etc.). | [`package_bom.py:18`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/package_bom.py#L18) |
| `_inherit` (Classical) | Extends `solar.package` and `solar.project` with Phase 4 inventory tabs and relational links. | [`solar_package_ext.py:22`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L22), [`53`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L53) |
| `fields.One2many` | Links `solar.package` -> `component_ids` and `solar.project` -> `stock_requirement_ids`. | [`solar_package_ext.py:24`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L24) |
| `fields.Many2one` | Links requirements/lines back to `product.product`, `solar.project`, and `stock.lot`. | [`stock_requirement.py:33`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py#L33) |
| `fields.Many2many` | Links `solar.stock.requirement` -> `purchase.order.line` via tuple syntax `(4, po_line.id)`. | [`stock_requirement.py:108`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py#L108) |
| `@api.depends` | Computes availability (`qty_available = max(0, on_hand - reserved)`) and validation progress. | [`stock_requirement.py:117`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py#L117) |
| `@api.constrains` | Enforces positive BOM quantities and cross-project duplicate serial number blocks. | [`package_bom.py:74`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/package_bom.py#L74), [`equipment_dispatch.py:356`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/equipment_dispatch.py#L356) |
| `filtered()` & `mapped()` | Traverses recordsets: `reqs.filtered(lambda r: r.status == 'draft')`, `conflicting.mapped('id')`. | [`solar_package_ext.py:144`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L144) |
| `self.env` & Context | Queries native models: `self.env['stock.quant']`, `self.env['stock.warehouse']`. | [`stock_requirement.py:148`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/stock_requirement.py#L148) |
| `UserError` vs `ValidationError` | `UserError` for business workflow blocks; `ValidationError` for field-level data integrity constraint failures. | Throughout all model files. |
| `ir.model.access.csv` | Explicit ACL matrix for users (`base.group_user`) and administrators (`base.group_system`). | [`ir.model.access.csv`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/security/ir.model.access.csv) |
| `ir.sequence` | Auto-generates sequential dispatch references (`DISP-%(y)s%(month)s%(day)s-XXXX`). | [`solar_data.xml:7`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/data/solar_data.xml#L7) |
| Native Stock Engine | Calls `action_confirm()`, `action_assign()`, and `button_validate()` on `stock.picking`. | [`equipment_dispatch.py:246`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/equipment_dispatch.py#L246) |

