# -*- coding: utf-8 -*-
"""
SunFlow Vibrant Tri-Color Status Distributer
============================================
Interleaves realistic inventory figures to display all three visual badges:
  - Green:  Stock Available
  - Orange: Partially Available
  - Red:    Stock Shortage (Not Available)
All mathematical fields (On Hand, Reserved, Incoming, Available, Shortage)
are strictly synchronized with each status.
"""

from odoo import fields

StockReq = env['solar.stock.requirement']
all_reqs = StockReq.search([], order='id asc')

print(f"Distributing tri-color status mix across {len(all_reqs)} stock requirements...")

# Interleaved pattern: Available (Green), Partial (Orange), Shortage (Red)
# E.g., [Green, Green, Orange, Red, Green, Orange, Red] -> ~45% Green, ~30% Orange, ~25% Red
pattern = ['available', 'available', 'partial', 'shortage', 'available', 'partial', 'shortage']

panel_capacities = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0]

for idx, req in enumerate(all_reqs):
    c_type = req.component_type or 'panel'
    st = pattern[idx % len(pattern)]
    
    # Base engineering requirements
    if c_type == 'panel':
        req_qty = panel_capacities[idx % len(panel_capacities)]
    elif c_type == 'inverter':
        req_qty = 2.0 if (idx % 8 == 0) else 1.0
    elif c_type == 'battery':
        req_qty = 2.0 if (idx % 3 == 0) else 1.0
    else:
        req_qty = 10.0

    if st == 'available':
        # Green: Ample On Hand, Free Available >= Required, Shortage = 0
        if c_type == 'panel':
            reserved = float((idx % 4) * 2)  # 0.0, 2.0, 4.0, 6.0
            on_hand = req_qty + reserved + 80.0 + (idx % 5) * 20.0
            incoming = float((idx % 3) * 50)
        elif c_type == 'inverter':
            reserved = float(idx % 2)
            on_hand = req_qty + reserved + 15.0 + (idx % 4) * 5.0
            incoming = float((idx % 2) * 20)
        else:  # battery
            reserved = float(idx % 2)
            on_hand = req_qty + reserved + 10.0 + (idx % 3) * 4.0
            incoming = float((idx % 2) * 15)

    elif st == 'partial':
        # Orange: Constrained stock, 0 < Available < Required, Shortage > 0
        if c_type == 'panel':
            # E.g. requires 10, has 4 available -> shortage = 6
            available_qty = max(2.0, req_qty / 2.0)
            reserved = 0.0 if (idx % 2 == 0) else 2.0
            on_hand = available_qty + reserved
            incoming = 50.0 + (idx % 4) * 25.0
        elif c_type == 'inverter':
            # Requires 2.0, has 1.0 available -> shortage = 1.0
            req_qty = 2.0
            reserved = 0.0
            on_hand = 1.0
            incoming = 25.0
        else:  # battery
            # Requires 2.0, has 1.0 available -> shortage = 1.0
            req_qty = 2.0
            reserved = 0.0
            on_hand = 1.0
            incoming = 20.0

    elif st == 'shortage':
        # Red: Zero free stock, Available = 0, Shortage = Required
        if idx % 2 == 0:
            # Zero on hand in warehouse
            on_hand = 0.0
            reserved = 0.0
        else:
            # 2 units on hand, but both already reserved by another order -> Available = 0
            on_hand = 2.0 if c_type == 'panel' else 1.0
            reserved = on_hand
        incoming = 100.0 if c_type == 'panel' else 30.0

    req.sudo().write({
        'is_serialized': True,
        'required_qty': req_qty,
        'qty_on_hand': on_hand,
        'qty_reserved': reserved,
        'qty_incoming': incoming,
        'status': st,
    })

env.cr.commit()

# Ensure action_solar_stock_shortages displays this rich mix
shortages_act = env.ref('sunflow_core.action_solar_stock_shortages', raise_if_not_found=False)
if shortages_act:
    shortages_act.domain = "[('status', 'in', ['available', 'shortage', 'partial'])]"

env.cr.commit()

print("\n" + "=" * 75)
print(" VIBRANT TRI-COLOR STATUS MIX APPLIED")
print("=" * 75)

green_count = StockReq.search_count([('status', '=', 'available')])
orange_count = StockReq.search_count([('status', '=', 'partial')])
red_count = StockReq.search_count([('status', '=', 'shortage')])

print(f"Total Records: {len(all_reqs)}")
print(f"  - 🟢 Green  (Stock Available):      {green_count} records ({round(green_count*100/len(all_reqs), 1)}%)")
print(f"  - 🟠 Orange (Partially Available):  {orange_count} records ({round(orange_count*100/len(all_reqs), 1)}%)")
print(f"  - 🔴 Red    (Stock Shortage):       {red_count} records ({round(red_count*100/len(all_reqs), 1)}%)")

print("\nFirst 15 Rows (Direct View in Odoo):")
print(f"{'ID':<5} | {'Product':<23} | {'Type':<8} | {'Req':<4} | {'OnHand':<6} | {'Res':<5} | {'In':<5} | {'Avail':<5} | {'Short':<5} | {'Visual Status'}")
print("-" * 95)
for r in all_reqs[:15]:
    p_name = (r.product_id.default_code or r.product_id.name)[:21]
    color_label = "🟢 Stock Available" if r.status == 'available' else ("🟠 Partially Available" if r.status == 'partial' else "🔴 Stock Shortage")
    print(f"{r.id:<5} | {p_name:<23} | {r.component_type:<8} | {r.required_qty:<4.1f} | {r.qty_on_hand:<6.1f} | {r.qty_reserved:<5.1f} | {r.qty_incoming:<5.1f} | {r.qty_available:<5.1f} | {r.qty_shortage:<5.1f} | {color_label}")
print("=" * 75)

