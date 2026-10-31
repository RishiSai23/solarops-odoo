# Odoo Internals Explained — Theory & Practical Application in SolarOps

This document explains the core internal architecture of the Odoo framework as leveraged in Project SunFlow. Concepts are divided into **Actively Used in Implementation** and **Background Context**.

---

## 1. Model Inheritance (`_inherit`)

### Internal Mechanism
Odoo offers three distinct inheritance mechanisms:
1. **Classical Extension (`_inherit = 'existing.model'`)** — *USED IN SUNFLOW*
   - Modifies or extends an existing model in-place without creating a new database table.
   - New fields are added as columns directly to the existing PostgreSQL table.
   - Methods defined in the subclass override or extend parent methods via `super()`.
   - **Where SunFlow uses it**: In [`solar_package_ext.py`](file:///k:/Projects/solarops-odoo/odoo_addons/sunflow_core/models/solar_package_ext.py#L20-L55), `SolarPackageExtended` inherits `solar.package` to add `component_ids` and `component_count`, while `SolarProjectExtended` inherits `solar.project` to add `stock_requirement_ids`, `dispatch_ids`, and inventory action methods.
2. **Prototype Inheritance (`_name = 'new.model'`, `_inherit = 'existing.model'`)**
   - Creates a new standalone table with copies of the fields and methods of the parent.
3. **Delegation Inheritance (`_inherits = {'parent.model': 'parent_id'}`)**
   - Implements composition (has-a) using a foreign key pointer (e.g. `product.product` inherits `product.template`).

```python
# Real code from solar_package_ext.py:
class SolarProjectExtended(models.Model):
    _inherit = 'solar.project'

    package_id = fields.Many2one('solar.package', string='Solar Package')
    stock_requirement_ids = fields.One2many('solar.stock.requirement', 'project_id', string='Stock Requirements')
```

---

## 2. ORM Recordsets & Environment (`self.env`)

### Internal Mechanism
- **Recordsets**: In Odoo, `self` is never a single object pointer; it is an **immutable, ordered collection of database records** belonging to the same model. Even when pointing to a single record, it is a recordset of length 1.
- **The Environment (`self.env`)**: An encapsulation object that holds:
  - `env.cr`: Active PostgreSQL database cursor for raw SQL execution.
  - `env.uid` & `env.user`: ID and record of the currently authenticated user.
  - `env.company`: Active working company (essential for multi-company warehouse resolution).
  - `env.context`: Frozen dictionary containing UI flags, default values (`default_project_id`), timezone, and language.

### Core Recordset Methods Used in SunFlow:
1. `self.ensure_one()`: Asserts that `len(self) == 1`, preventing batch logic corruption. Used at the beginning of all action methods (`action_generate_stock_requirements`, `action_create_dispatch`).
2. `recordset.filtered(func)`: Returns a new recordset matching the predicate without database querying:
   ```python
   draft_reqs = self.stock_requirement_ids.filtered(lambda r: r.status == 'draft')
   ```
3. `recordset.mapped(path)`: Traverses relational fields across recordsets and extracts lists or merged recordsets:
   ```python
   on_hand = sum(quants.mapped('quantity'))
   dispatched_ids = dispatched_headers.mapped('id')
   ```
4. `recordset.search(domain, limit=N)`: Executes an SQL query against PostgreSQL through the Odoo query builder.
5. `recordset.write(vals)`: Issues an SQL `UPDATE` statement. In Odoo, calling `rec.field = val` executes an in-memory cache update that is flushed to PostgreSQL via `write()` at transaction commit.

---

## 3. Relational Fields & ORM Command Tuples

Odoo represents relational database connections using three field descriptors:

### Many2one
Stores a foreign key integer column in the PostgreSQL table:
```python
package_id = fields.Many2one('solar.package', string='Solar Package', ondelete='cascade', index=True)
```
- Creates column `package_id INT REFERENCES solar_package(id)`.
- `ondelete='cascade'` deletes child components if the package template is dropped.

### One2many
A virtual bidirectional link backed by a `Many2one` on the target model. It adds **no column** to the parent table:
```python
component_ids = fields.One2many('solar.package.component', 'package_id', string='Bill of Materials')
```

### Many2many & Special Command Tuples
Represents an N:M relationship backed by an intermediate cross-reference table. In SunFlow, `solar.stock.requirement` links to `purchase.order.line`:
```python
purchase_order_line_ids = fields.Many2many('purchase.order.line', string='Purchase Order Lines')
```

When creating or modifying relational fields in Odoo, **ORM Command Tuples** are passed to `create()` or `write()`:
- `(0, 0, vals)`: Create a new record and link it immediately. Used in SunFlow when populating package components:
  ```python
  'component_ids': [(0, 0, {'product_id': panel.id, 'quantity': 10.0})]
  ```
- `(4, id)`: Link an existing record by ID without deleting or creating. Used in SunFlow when linking generated PO lines to stock requirements:
  ```python
  self.purchase_order_line_ids = [(4, po.order_line[0].id)]
  ```
- `(6, 0, [ids])`: Replace all existing linked records with the provided ID list.

---

## 4. Computed Fields & `@api.depends`

### How Odoo Computes Fields
A computed field defines `compute='_method_name'`. 
- **Volatile Computed Fields (`store=False`)**: Computed on-the-fly in Python RAM whenever accessed by UI or API. They do not occupy an SQL column.
- **Stored Computed Fields (`store=True`)**: Stored in a physical PostgreSQL column. Odoo's dependency graph evaluates them and updates the database **only** when one of the fields declared in `@api.depends(...)` changes.

### Real Example from `stock_requirement.py`:
```python
qty_available = fields.Float(
    string='Available Stock',
    compute='_compute_availability',
    store=True,
)

@api.depends('qty_on_hand', 'qty_reserved', 'required_qty')
def _compute_availability(self):
    for rec in self:
        avail = max(0.0, rec.qty_on_hand - rec.qty_reserved)
        rec.qty_available = avail
        shortage = max(0.0, rec.required_qty - avail)
        rec.qty_shortage = shortage
        rec.has_shortage = (shortage > 0.0)
```
- Whenever `qty_on_hand` or `qty_reserved` changes (e.g. after a physical receipt), Odoo automatically re-computes `qty_available`, `qty_shortage`, and `has_shortage`, persisting the new values to PostgreSQL in the same database transaction.

---

## 5. Validation Constraints (`@api.constrains`)

### Python Constraints vs SQL Constraints
- **SQL Constraints (`_sql_constraints`)**: Evaluated at PostgreSQL database engine level (e.g. `UNIQUE (name)`). Fast, but cannot execute cross-model Python logic.
- **Python Constraints (`@api.constrains('field1', 'field2')`)**: Evaluated by the Odoo ORM whenever specified fields are modified. Allows complex database queries, cross-record checks, and user-friendly error formatting.

### Real Example from `equipment_dispatch.py`:
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
                    'Serial/Lot "%s" has already been dispatched to project "%s"...'
                ) % (rec.lot_id.name, conflicting[0].dispatch_id.project_id.name))
```
- If an operator tries to assign a serial number that was already dispatched to another project, Odoo immediately aborts the SQL transaction and surfaces the `ValidationError` modal in the browser.

---

## 6. Exceptions: `UserError` vs `ValidationError`

Odoo provides specific exception classes in `odoo.exceptions`:
1. `ValidationError`: Raised when business data violates an internal consistency constraint (e.g. negative quantities, duplicate serial numbers, lot-product mismatch). Always triggers a database rollback.
2. `UserError`: Raised when a user initiates an invalid operational action (e.g. trying to validate a dispatch without serial numbers, trying to create a PO when there is no shortage, generating requirements without a package). Surfaced to users as an informative warning.
3. `AccessError`: Raised by the security engine when an operation violates `ir.model.access.csv` or an `ir.rule` record rule.

---

## 7. Security: Access Control Lists (`ir.model.access.csv`)

### Internal Mechanism
Every custom model in Odoo **must** have explicit permissions defined in `security/ir.model.access.csv`. If no rule exists, non-superuser access is completely denied by default.

The CSV structure has 8 columns:
`id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink`

### Phase 4 Security Configuration:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_solar_package_comp_user,solar.package.component.user,model_solar_package_component,base.group_user,1,0,0,0
access_solar_package_comp_mgr,solar.package.component.mgr,model_solar_package_component,base.group_system,1,1,1,1
access_solar_stock_req_user,solar.stock.requirement.user,model_solar_stock_requirement,base.group_user,1,1,1,0
access_solar_stock_req_mgr,solar.stock.requirement.mgr,model_solar_stock_requirement,base.group_system,1,1,1,1
access_solar_equip_disp_user,solar.equipment.dispatch.user,model_solar_equipment_dispatch,base.group_user,1,1,1,0
access_solar_equip_disp_mgr,solar.equipment.dispatch.mgr,model_solar_equipment_dispatch,base.group_system,1,1,1,1
access_solar_equip_disp_line_user,solar.equipment.dispatch.line.user,model_solar_equipment_dispatch_line,base.group_user,1,1,1,0
access_solar_equip_disp_line_mgr,solar.equipment.dispatch.line.mgr,model_solar_equipment_dispatch_line,base.group_system,1,1,1,1
```
- Standard users (`base.group_user` / field engineers) have **Read** access on BOMs, and **Read, Write, Create** on Requirements and Dispatches, but **cannot Unlink (delete)** audit-trail dispatch manifests.
- System administrators (`base.group_system`) retain full CRUD permissions across all tables.

---

## 8. Native Inventory & Purchase Architecture

To avoid building brittle duplicate logic, SunFlow integrates directly with Odoo's core inventory models:

### A. The Stock Quant (`stock.quant`)
- **Key Realization**: In Odoo, `product.product` **does not have a physical stock column in PostgreSQL**.
- Physical stock is computed dynamically by summing rows in `stock.quant`.
- A quant is a physical tuple: `(product_id, location_id, lot_id, package_id, owner_id) -> quantity, reserved_quantity`.
- In SunFlow's `action_check_stock()`:
  ```python
  domain = [('product_id', '=', product.id), ('location_id', 'child_of', stock_location.id)]
  quants = self.env['stock.quant'].search(domain)
  on_hand = sum(quants.mapped('quantity'))
  reserved = sum(quants.mapped('reserved_quantity'))
  ```
  This queries PostgreSQL for the exact physical reality of the warehouse.

### B. Serial Tracking (`stock.lot`)
- Stored in `stock.lot`.
- Represents an individual serialized asset (e.g. Inverter SN `INV-HYB-5K-9901`).
- Linked to `stock.move.line` to record the physical movement of that exact serialized asset from `WH/Stock` to `Partner Locations/Customers`.

### C. Material Transfers (`stock.picking`, `stock.move`, `stock.move.line`)
- **`stock.picking`**: The physical transfer header (e.g. Delivery Order `WH/OUT/00042` or Receipt `WH/IN/00017`).
- **`stock.move`**: The planned commercial intent line (e.g. "Move 1 unit of Inverter from Stock to Customer").
- **`stock.move.line`**: The detailed execution line recording which exact lot (`lot_id`) was picked and packed.
- In SunFlow's `_create_native_stock_picking()`:
  1. Creates `stock.picking` linked to `stock.warehouse.out_type_id`.
  2. Confirms picking (`action_confirm()`).
  3. Assigns stock (`action_assign()`).
  4. Sets specific serial numbers (`move_line.write({'lot_id': line.lot_id.id})`).
  5. Validates transfer via native Odoo logic (`button_validate()`).
  6. Native Odoo automatically updates `stock.quant` and closes the picking.

---

## 9. XML View Architecture in Odoo 17

Odoo 17 introduced significant architectural changes to its view compiler:

1. **Complete Removal of `attrs` and `states`**:
   - Legacy: `attrs="{'invisible': [('has_shortage', '=', False)]}"`
   - Odoo 17: `invisible="not has_shortage"`
2. **View Field Registration Requirement**:
   - Every field referenced inside an `invisible="..."` or `required="..."` expression must be declared as a field in that view:
   ```xml
   <field name="has_shortage" invisible="1"/>
   <button name="action_create_purchase_order" type="object" invisible="not has_shortage"/>
   ```
3. **Robust XPath Inheritance**:
   - Translatable attributes like `string` are forbidden in xpath selectors (`page[@string='...']` fails).
   - Elements must be selected by `name` (`<page name="inventory">`) or hierarchical container (`<xpath expr="//notebook" position="inside">`).
   - Classes must be matched using the XPath function `hasclass()`:
     ```xml
     <xpath expr="//sheet/div[hasclass('oe_title')]" position="before">
     ```

