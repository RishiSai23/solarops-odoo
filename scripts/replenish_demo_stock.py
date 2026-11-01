# -*- coding: utf-8 -*-
"""
SunFlow Demo Stock Replenishment & Recomputation Script
=======================================================
Replenishes warehouse inventory (stock.quant) and creates incoming PO lines
for DEMO-SOLAR-* products, then runs action_check_stock() across all
stock requirements so the table displays realistic On-Hand, Incoming,
Available, and Shortage figures.
"""

from odoo import fields

company = env.company
wh = env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1) or env['stock.warehouse'].search([], limit=1)
if not wh:
    raise RuntimeError("No warehouse found!")
stock_loc = wh.lot_stock_id

Quant = env['stock.quant']
Product = env['product.product']
PurchaseOrder = env['purchase.order']
PurchaseOrderLine = env['purchase.order.line']
Partner = env['res.partner']
StockReq = env['solar.stock.requirement']

p_panel = Product.search([('default_code', '=', 'DEMO-SOLAR-PANEL')], limit=1)
p_inv = Product.search([('default_code', '=', 'DEMO-SOLAR-INVERTER')], limit=1)
p_bat = Product.search([('default_code', '=', 'DEMO-SOLAR-BATTERY')], limit=1)

print("[1/4] Updating Warehouse On-Hand Quantities in WH/Stock...")
# 1. Panels: 5,000 units on hand (Abundant -> Available)
if p_panel:
    cur = sum(Quant.search([('product_id', '=', p_panel.id), ('location_id', '=', stock_loc.id)]).mapped('quantity'))
    if cur < 5000:
        Quant._update_available_quantity(p_panel, stock_loc, 5000.0 - cur)
        print(f"  -> DEMO-SOLAR-PANEL: On Hand set to 5,000.0 units.")

# 2. Inverters: 18 units on hand (Constrained -> Partial for requirements > 18)
if p_inv:
    cur = sum(Quant.search([('product_id', '=', p_inv.id), ('location_id', '=', stock_loc.id)]).mapped('quantity'))
    if cur < 18:
        Quant._update_available_quantity(p_inv, stock_loc, 18.0 - cur)
        print(f"  -> DEMO-SOLAR-INVERTER: On Hand set to 18.0 units.")

# 3. Batteries: 0 units on hand (Critical Shortage -> Shortage status)
print("  -> DEMO-SOLAR-BATTERY: Kept at 0 units on hand (Simulates genuine shortage).")

env.cr.commit()

# ---------------------------------------------------------
# 2. Create Confirmed Purchase Order for Incoming Quantities
# ---------------------------------------------------------
print("[2/4] Setting up Incoming Stock via Confirmed Purchase Order...")
vendor = Partner.search([('name', '=', 'SunFlow Tier-1 Hardware Supplies')], limit=1)
if not vendor:
    vendor = Partner.create({
        'name': 'SunFlow Tier-1 Hardware Supplies',
        'supplier_rank': 1,
        'email': 'procurement@sunflowsupplies.test',
        'phone': '+91 80000 12345',
        'city': 'Chennai',
    })

po_ref = 'PO-DEMO-REPLENISH-001'
po = PurchaseOrder.search([('partner_ref', '=', po_ref)], limit=1)
if not po and p_inv and p_bat:
    po = PurchaseOrder.create({
        'partner_id': vendor.id,
        'partner_ref': po_ref,
        'date_order': fields.Datetime.now(),
        'order_line': [
            (0, 0, {
                'product_id': p_inv.id,
                'name': p_inv.name,
                'product_qty': 100.0,
                'product_uom': p_inv.uom_id.id,
                'price_unit': p_inv.standard_price or 35000.0,
                'date_planned': fields.Datetime.now(),
            }),
            (0, 0, {
                'product_id': p_bat.id,
                'name': p_bat.name,
                'product_qty': 50.0,
                'product_uom': p_bat.uom_id.id,
                'price_unit': p_bat.standard_price or 95000.0,
                'date_planned': fields.Datetime.now(),
            }),
        ]
    })
    # Confirm PO to make state = 'purchase'
    po.button_confirm()
    print("  -> Created and confirmed Purchase Order PO-DEMO-REPLENISH-001 with 100 inverters & 50 batteries incoming.")

env.cr.commit()

# ---------------------------------------------------------
# 3. Refresh action_check_stock across ALL stock requirements
# ---------------------------------------------------------
print("[3/4] Recomputing Stock Snapshot across all Stock Requirements...")
all_reqs = StockReq.search([])
print(f"  -> Found {len(all_reqs)} requirements to refresh.")

# Batch execute
count = 0
for req in all_reqs:
    req.action_check_stock()
    count += 1
    if count % 50 == 0:
        env.cr.commit()

env.cr.commit()
print(f"  -> Successfully refreshed {count} stock requirements.")

# ---------------------------------------------------------
# 4. Verification and Summary
# ---------------------------------------------------------
print("\n[4/4] Verification Summary:")
print("=" * 60)
avail_count = StockReq.search_count([('status', '=', 'available')])
partial_count = StockReq.search_count([('status', '=', 'partial')])
shortage_count = StockReq.search_count([('status', '=', 'shortage')])

print(f"Total Stock Requirements in DB: {len(all_reqs)}")
print(f"  - Green  (Stock Available):      {avail_count}")
print(f"  - Orange (Partially Available):  {partial_count}")
print(f"  - Red    (Stock Shortage):       {shortage_count}")

# Sample inspections
sample_panel = StockReq.search([('product_id', '=', p_panel.id)], limit=1)
if sample_panel:
    print(f"\nSample Panel Requirement (ID {sample_panel.id}):")
    print(f"  Product: {sample_panel.product_id.display_name}")
    print(f"  Required: {sample_panel.required_qty} | On Hand: {sample_panel.qty_on_hand} | Incoming: {sample_panel.qty_incoming} | Available: {sample_panel.qty_available} | Shortage: {sample_panel.qty_shortage} | Status: {sample_panel.status}")

sample_inv = StockReq.search([('product_id', '=', p_inv.id)], limit=1)
if sample_inv:
    print(f"\nSample Inverter Requirement (ID {sample_inv.id}):")
    print(f"  Product: {sample_inv.product_id.display_name}")
    print(f"  Required: {sample_inv.required_qty} | On Hand: {sample_inv.qty_on_hand} | Incoming: {sample_inv.qty_incoming} | Available: {sample_inv.qty_available} | Shortage: {sample_inv.qty_shortage} | Status: {sample_inv.status}")

sample_bat = StockReq.search([('product_id', '=', p_bat.id)], limit=1)
if sample_bat:
    print(f"\nSample Battery Requirement (ID {sample_bat.id}):")
    print(f"  Product: {sample_bat.product_id.display_name}")
    print(f"  Required: {sample_bat.required_qty} | On Hand: {sample_bat.qty_on_hand} | Incoming: {sample_bat.qty_incoming} | Available: {sample_bat.qty_available} | Shortage: {sample_bat.qty_shortage} | Status: {sample_bat.status}")
print("=" * 60)

