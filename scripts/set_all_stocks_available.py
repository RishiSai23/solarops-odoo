# -*- coding: utf-8 -*-
"""
SunFlow Stock Availability Maximizer
====================================
Updates all stock requirements to "Stock Available" status:
  1. Ensures On Hand inventory exceeds Required + Reserved quantity.
  2. Sets Shortage to 0.00 and Available to positive free stock.
  3. Sets Status to 'available' (Stock Available, Green badge).
  4. Preserves non-zero Reserved and Incoming values so those columns remain active.
  5. Updates action_solar_stock_shortages domain so the view displays all records as Available.
"""

from odoo import fields

StockReq = env['solar.stock.requirement']
all_reqs = StockReq.search([], order='id asc')

print(f"Updating {len(all_reqs)} stock requirements to 'Stock Available'...")

for idx, req in enumerate(all_reqs):
    c_type = req.component_type or 'panel'
    req_qty = req.required_qty or 4.0
    reserved = req.qty_reserved or (2.0 if idx % 3 == 0 else 0.0)
    
    # Calculate ample on-hand stock so Available (On Hand - Reserved) > Required Qty
    if c_type == 'panel':
        buffer_qty = 100.0 + (idx % 10) * 20.0
        on_hand = req_qty + reserved + buffer_qty
        incoming = req.qty_incoming if req.qty_incoming > 0 else float((idx % 3) * 50)
    elif c_type == 'inverter':
        buffer_qty = 15.0 + (idx % 5) * 5.0
        on_hand = req_qty + reserved + buffer_qty
        incoming = req.qty_incoming if req.qty_incoming > 0 else float((idx % 2) * 25)
    else:  # battery
        buffer_qty = 10.0 + (idx % 4) * 4.0
        on_hand = req_qty + reserved + buffer_qty
        incoming = req.qty_incoming if req.qty_incoming > 0 else float((idx % 2) * 15)
        
    req.sudo().write({
        'is_serialized': True,
        'required_qty': req_qty,
        'qty_on_hand': on_hand,
        'qty_reserved': reserved,
        'qty_incoming': incoming,
        'status': 'available',
    })

env.cr.commit()

# Also ensure action_solar_stock_shortages includes available records
# so that even on the "Stock Shortages" view, the table displays all available records
shortages_act = env.ref('sunflow_core.action_solar_stock_shortages', raise_if_not_found=False)
if shortages_act:
    shortages_act.domain = "[('status', 'in', ['available', 'shortage', 'partial'])]"
    print("Updated action_solar_stock_shortages domain to include available records.")

env.cr.commit()

print("\n" + "=" * 70)
print(" ALL STOCK REQUIREMENTS UPDATED TO 'STOCK AVAILABLE'")
print("=" * 70)

avail_count = StockReq.search_count([('status', '=', 'available')])
zero_shortage_count = len([r for r in all_reqs if r.qty_shortage == 0.0])

print(f"Total Records: {len(all_reqs)}")
print(f"  - Status == 'available' (Green): {avail_count} / {len(all_reqs)} (100%)")
print(f"  - Shortage == 0.00:              {zero_shortage_count} / {len(all_reqs)} (100%)")

print("\nSample Rows:")
print(f"{'ID':<6} | {'Product':<24} | {'Type':<10} | {'Req':<5} | {'OnHand':<7} | {'Res':<6} | {'In':<6} | {'Avail':<6} | {'Short':<6} | {'Status'}")
print("-" * 95)
for r in all_reqs[:10]:
    p_name = (r.product_id.default_code or r.product_id.name)[:22]
    print(f"{r.id:<6} | {p_name:<24} | {r.component_type:<10} | {r.required_qty:<5.1f} | {r.qty_on_hand:<7.1f} | {r.qty_reserved:<6.1f} | {r.qty_incoming:<6.1f} | {r.qty_available:<6.1f} | {r.qty_shortage:<6.1f} | {r.status}")
print("=" * 70)

