# -*- coding: utf-8 -*-
"""
SunFlow Realistic Data Harmonizer for Stock Requirements Table
==============================================================
Populates and assigns realistic, solar-EPC-appropriate values across
ALL columns of solar.stock.requirement:
  - Required Qty (kw_capacity-based engineering counts)
  - Serial Required (True for Panels, Inverters, Batteries)
  - On Hand (realistic warehouse batch levels)
  - Reserved (active allocation for site installations)
  - Incoming (active vendor purchase orders)
  - Status (Available, Partial, Shortage, Reserved, Dispatched)
"""

from odoo import fields

StockReq = env['solar.stock.requirement']
all_reqs = StockReq.search([], order='id asc')

print(f"Processing {len(all_reqs)} Stock Requirements...")

# Status cycle to ensure rich visual variety across all statuses
# available (35%), partial (25%), shortage (20%), reserved (12%), dispatched (8%)
status_palette = (
    ['available'] * 7 +
    ['partial'] * 5 +
    ['shortage'] * 4 +
    ['reserved'] * 3 +
    ['dispatched'] * 2
)

panel_capacities = [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0]

for idx, req in enumerate(all_reqs):
    c_type = req.component_type or 'panel'
    st = status_palette[idx % len(status_palette)]
    
    # 1. Serial Required: True for all high-value serialized solar hardware
    is_serialized = True
    
    # 2. Required Qty: realistic engineering specifications
    if c_type == 'panel':
        req_qty = panel_capacities[idx % len(panel_capacities)]
    elif c_type == 'inverter':
        req_qty = 2.0 if (idx % 10 == 0) else 1.0
    elif c_type == 'battery':
        req_qty = 2.0 if (idx % 4 == 0) else 1.0
    else:
        req_qty = 10.0 + (idx % 10)

    # 3. On Hand, Reserved, Incoming tailored to status
    if st == 'available':
        # Abundant stock: on_hand >> required_qty, reserved is small or zero
        if c_type == 'panel':
            on_hand = float(120 + (idx % 10) * 40)
            reserved = float((idx % 4) * 4)  # 0, 4, 8, 12
            incoming = float((idx % 3) * 50)
        elif c_type == 'inverter':
            on_hand = float(15 + (idx % 5) * 5)
            reserved = float(idx % 2)  # 0 or 1
            incoming = float((idx % 2) * 20)
        else:  # battery
            on_hand = float(10 + (idx % 4) * 4)
            reserved = float(idx % 2)
            incoming = float((idx % 3) * 10)

    elif st == 'partial':
        # Constrained stock: 0 < available < req_qty
        if c_type == 'panel':
            # Needs e.g. 10, has 6 on hand, 0 reserved -> available = 6
            on_hand = max(2.0, req_qty - 4.0)
            reserved = 0.0 if (idx % 2 == 0) else 2.0
            on_hand += reserved  # ensures (on_hand - reserved) is partial
            incoming = 50.0 + (idx % 4) * 25.0
        elif c_type == 'inverter':
            # Needs 2, has 1 on hand, 0 reserved
            req_qty = 2.0
            on_hand = 1.0
            reserved = 0.0
            incoming = 25.0
        else:  # battery
            req_qty = 2.0
            on_hand = 1.0
            reserved = 0.0
            incoming = 15.0

    elif st == 'shortage':
        # Zero free stock: on_hand = 0 or on_hand == reserved
        if idx % 3 == 0:
            on_hand = 2.0 if c_type == 'panel' else 1.0
            reserved = on_hand  # fully reserved by another order -> available = 0
        else:
            on_hand = 0.0
            reserved = 0.0
        # High incoming PO quantity
        incoming = 100.0 if c_type == 'panel' else (30.0 if c_type == 'inverter' else 20.0)

    elif st == 'reserved':
        # Material physically staged in warehouse for this project
        on_hand = req_qty + float((idx % 3) * 5)
        reserved = req_qty  # exact required amount is allocated/reserved
        incoming = float((idx % 2) * 25)

    elif st == 'dispatched':
        # Material has left the warehouse towards the installation site
        on_hand = 0.0
        reserved = 0.0
        incoming = 0.0

    # Write all columns directly to the record
    req.sudo().write({
        'is_serialized': is_serialized,
        'required_qty': req_qty,
        'qty_on_hand': on_hand,
        'qty_reserved': reserved,
        'qty_incoming': incoming,
        'status': st,
    })

env.cr.commit()

# Recompute and verify
print("\n" + "=" * 70)
print(" STOCK REQUIREMENTS TABLE SUCCESSFULLY HARMONIZED ACROSS ALL COLUMNS")
print("=" * 70)

status_dist = {
    'available': StockReq.search_count([('status', '=', 'available')]),
    'partial': StockReq.search_count([('status', '=', 'partial')]),
    'shortage': StockReq.search_count([('status', '=', 'shortage')]),
    'reserved': StockReq.search_count([('status', '=', 'reserved')]),
    'dispatched': StockReq.search_count([('status', '=', 'dispatched')]),
}

serialized_count = StockReq.search_count([('is_serialized', '=', True)])
non_zero_reserved = StockReq.search_count([('qty_reserved', '>', 0)])
non_zero_incoming = StockReq.search_count([('qty_incoming', '>', 0)])

print(f"Total Records: {len(all_reqs)}")
print(f"  - Serial Required (True):     {serialized_count} / {len(all_reqs)}")
print(f"  - Non-Zero Reserved Rows:     {non_zero_reserved} / {len(all_reqs)}")
print(f"  - Non-Zero Incoming Rows:     {non_zero_incoming} / {len(all_reqs)}")
print("\nStatus Distribution:")
for s, c in status_dist.items():
    print(f"  - {s.capitalize():<12}: {c} records ({round(c*100/len(all_reqs), 1)}%)")

print("\nSample Diverse Rows:")
print(f"{'ID':<6} | {'Product':<24} | {'Type':<10} | {'Req':<5} | {'OnHand':<7} | {'Res':<6} | {'In':<6} | {'Avail':<6} | {'Short':<6} | {'Serial':<6} | {'Status'}")
print("-" * 105)
for r in all_reqs[:15]:
    p_name = (r.product_id.default_code or r.product_id.name)[:22]
    print(f"{r.id:<6} | {p_name:<24} | {r.component_type:<10} | {r.required_qty:<5.1f} | {r.qty_on_hand:<7.1f} | {r.qty_reserved:<6.1f} | {r.qty_incoming:<6.1f} | {r.qty_available:<6.1f} | {r.qty_shortage:<6.1f} | {str(r.is_serialized):<6} | {r.status}")
print("=" * 70)

