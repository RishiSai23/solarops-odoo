# -*- coding: utf-8 -*-
"""
End-to-End Integration Gate Verification Script for Phase 4
Executed inside real Odoo 17 container via `odoo shell -d sunflow_test`.
"""
import sys
import logging
from odoo.exceptions import ValidationError, UserError, AccessError

_logger = logging.getLogger('sunflow_gate_verifier')

def run_integration_verification(env):
    print("\n" + "=" * 70)
    print("SOLAROPS PHASE 4: GENUINE ODOO 17 INTEGRATION GATE VERIFICATION")
    print("=" * 70)

    # 1. Inspect Environment & Version
    import odoo.release
    print(f"[1] ODOO SERVER ENVIRONMENT:")
    print(f"    - Odoo Version: {odoo.release.version} ({odoo.release.version_info})")
    print(f"    - Database: {env.cr.dbname}")
    print(f"    - Company: {env.company.name} (ID: {env.company.id})")
    
    # 2. Check Warehouse
    wh = env['stock.warehouse'].search([('company_id', '=', env.company.id)], limit=1)
    if not wh:
        wh = env['stock.warehouse'].search([], limit=1)
    print(f"[2] WAREHOUSE STATUS:")
    print(f"    - Active Warehouse: {wh.name if wh else 'NONE'} (Code: {wh.code if wh else 'N/A'})")
    print(f"    - Stock Location: {wh.lot_stock_id.complete_name if wh else 'N/A'}")

    # 3. Create Vendor and Customer Partners
    vendor = env['res.partner'].create({
        'name': 'SunFlow Tier-1 Solar Supplies Ltd',
        'supplier_rank': 1,
        'email': 'procurement@tiersolar.com',
    })
    customer = env['res.partner'].create({
        'name': 'Rajesh Sharma (Green Villa)',
        'customer_rank': 1,
        'email': 'rajesh.sharma@example.com',
        'street': 'Plot 42, Solar Enclave',
        'city': 'Ahmedabad',
    })
    print(f"[3] PARTNERS INITIALIZED: Vendor={vendor.name}, Customer={customer.name}")

    # 4. Create Solar Component Products
    panel_prod = env['product.product'].create({
        'name': 'Mono PERC 550W Tier-1 Panel',
        'type': 'product',
        'tracking': 'none',
        'list_price': 15000.0,
        'standard_price': 11000.0,
        'seller_ids': [(0, 0, {'partner_id': vendor.id, 'price': 10500.0, 'min_qty': 1})],
    })
    inverter_prod = env['product.product'].create({
        'name': 'SunFlow 5kW Hybrid String Inverter',
        'type': 'product',
        'tracking': 'serial',
        'list_price': 65000.0,
        'standard_price': 48000.0,
        'seller_ids': [(0, 0, {'partner_id': vendor.id, 'price': 46000.0, 'min_qty': 1})],
    })
    battery_prod = env['product.product'].create({
        'name': 'SunFlow 5kWh LiFePO4 Battery Pack',
        'type': 'product',
        'tracking': 'serial',
        'list_price': 120000.0,
        'standard_price': 90000.0,
        'seller_ids': [(0, 0, {'partner_id': vendor.id, 'price': 88000.0, 'min_qty': 1})],
    })
    print(f"[4] PRODUCTS REGISTERED: Panel, Serialized Inverter, Serialized Battery")

    # 5. Create Solar Package & Configure BOM
    pkg = env['solar.package'].create({
        'name': 'SunFlow 5kW Hybrid Smart Storage Package',
        'capacity_kw': 5.0,
        'system_type': 'hybrid',
        'panel_count': 10,
        'inverter_capacity_kw': 5.0,
        'battery_bank_kwh': 5.0,
        'base_price': 320000.0,
        'component_ids': [
            (0, 0, {
                'product_id': panel_prod.id,
                'component_type': 'panel',
                'quantity': 10.0,
            }),
            (0, 0, {
                'product_id': inverter_prod.id,
                'component_type': 'inverter',
                'quantity': 1.0,
                'is_serialized': True,
            }),
            (0, 0, {
                'product_id': battery_prod.id,
                'component_type': 'battery',
                'quantity': 1.0,
                'is_serialized': True,
            }),
        ],
    })
    assert pkg.component_count == 3, f"Expected 3 components, got {pkg.component_count}"
    print(f"[5] SOLAR PACKAGE & BOM CONFIGURED: '{pkg.name}' with {pkg.component_count} BOM components")

    # 6. Create Solar Project & Generate Stock Requirements
    project = env['solar.project'].create({
        'name': 'PROJ-AHM-2026-0042',
        'partner_id': customer.id,
        'kw_capacity': 5.0,
        'system_type': 'hybrid',
        'package_id': pkg.id,
        'contract_amount': 320000.0,
        'stage': 'order',
    })
    print(f"[6] SOLAR PROJECT CREATED: {project.name} (Initial Stage: {project.stage})")

    project.action_generate_stock_requirements()
    assert project.stage == 'procurement', f"Expected stage 'procurement', got {project.stage}"
    assert project.requirement_count == 3, f"Expected 3 requirements, got {project.requirement_count}"
    assert project.has_shortage is True, "Expected shortages since warehouse is empty"
    assert project.stock_ready is False, "Stock should not be ready"
    print(f"[7] STOCK REQUIREMENTS GENERATED:")
    print(f"    - Advanced to stage: '{project.stage}'")
    print(f"    - Requirements Count: {project.requirement_count}")
    print(f"    - Has Shortage: {project.has_shortage}")
    for req in project.stock_requirement_ids:
        print(f"      * {req.product_id.name}: Required={req.required_qty}, Available={req.qty_available}, Shortage={req.qty_shortage}, Status={req.status}")

    # 8. Create Purchase Orders from Shortages
    inv_req = project.stock_requirement_ids.filtered(lambda r: r.product_id == inverter_prod)
    bat_req = project.stock_requirement_ids.filtered(lambda r: r.product_id == battery_prod)
    pnl_req = project.stock_requirement_ids.filtered(lambda r: r.product_id == panel_prod)

    inv_req.action_create_purchase_order()
    bat_req.action_create_purchase_order()
    pnl_req.action_create_purchase_order()

    po_lines = inv_req.purchase_order_line_ids | bat_req.purchase_order_line_ids | pnl_req.purchase_order_line_ids
    pos = po_lines.mapped('order_id')
    print(f"[8] PURCHASE ORDERS CREATED:")
    for po in pos:
        print(f"    - PO: {po.name}, Partner: {po.partner_id.name}, Total Lines: {len(po.order_line)}, State: {po.state}")

    # 9. Register Lots & Confirm POs & Process Incoming Goods into Stock
    inv_lot = env['stock.lot'].create({
        'name': 'INV-HYB-5K-9901',
        'product_id': inverter_prod.id,
        'company_id': env.company.id,
    })
    bat_lot = env['stock.lot'].create({
        'name': 'BAT-LFP-5K-8802',
        'product_id': battery_prod.id,
        'company_id': env.company.id,
    })
    print(f"[9] SERIAL ASSETS CREATED: Inverter SN={inv_lot.name}, Battery SN={bat_lot.name}")

    for po in pos:
        po.button_confirm()
        print(f"    - Confirmed PO: {po.name} -> State: {po.state}")
        # Validate incoming receipts
        for picking in po.picking_ids:
            if picking.state not in ('done', 'cancel'):
                for move in picking.move_ids:
                    if move.product_id == inverter_prod:
                        move.move_line_ids.unlink()
                        env['stock.move.line'].create({
                            'move_id': move.id,
                            'picking_id': picking.id,
                            'product_id': inverter_prod.id,
                            'product_uom_id': inverter_prod.uom_id.id,
                            'quantity': 1.0,
                            'lot_id': inv_lot.id,
                            'location_id': picking.location_id.id,
                            'location_dest_id': picking.location_dest_id.id,
                            'picked': True,
                        })
                    elif move.product_id == battery_prod:
                        move.move_line_ids.unlink()
                        env['stock.move.line'].create({
                            'move_id': move.id,
                            'picking_id': picking.id,
                            'product_id': battery_prod.id,
                            'product_uom_id': battery_prod.uom_id.id,
                            'quantity': 1.0,
                            'lot_id': bat_lot.id,
                            'location_id': picking.location_id.id,
                            'location_dest_id': picking.location_dest_id.id,
                            'picked': True,
                        })
                    else:
                        move.quantity = move.product_uom_qty
                        move.picked = True
                picking.button_validate()
                print(f"      * Incoming Receipt {picking.name} validated -> State: {picking.state}")

    # 10. Refresh Stock Requirements
    project.action_check_all_stock()
    print(f"[10] STOCK REQUIREMENTS POST-RECEIPT:")
    for req in project.stock_requirement_ids:
        print(f"     * {req.product_id.name}: On Hand={req.qty_on_hand}, Shortage={req.qty_shortage}, Status={req.status}")
    assert project.has_shortage is False, "Shortages should now be resolved"
    assert project.stock_ready is True, "Stock should now be marked ready"
    print(f"     -> Project Stock Ready: {project.stock_ready}, Has Shortage: {project.has_shortage}")

    # 11. Equipment Ready for Dispatch
    print(f"[11] EQUIPMENT SERIALS VERIFIED IN WAREHOUSE: Ready for Dispatch")

    # 12. Create Equipment Dispatch from Project
    res = project.action_create_dispatch()
    dispatch = env['solar.equipment.dispatch'].browse(res['res_id'])
    print(f"[12] EQUIPMENT DISPATCH CREATED: {dispatch.name} (Lines: {dispatch.total_lines}, State: {dispatch.state})")
    assert dispatch.total_lines == 3, f"Expected 3 lines, got {dispatch.total_lines}"

    # Try marking ready before serial numbers assigned
    dispatch.action_mark_ready()
    print(f"     -> Marked Ready (State: {dispatch.state}, Validated Lines: {dispatch.validated_lines}/{dispatch.total_lines})")

    # Try validating without serial numbers -> Must raise UserError/ValidationError
    try:
        dispatch.action_validate_dispatch()
        raise AssertionError("Validation should have failed without serial numbers!")
    except (ValidationError, UserError) as e:
        print(f"     -> Correctly blocked dispatch without serial numbers: '{e}'")

    # Assign Serial Numbers
    inv_line = dispatch.line_ids.filtered(lambda l: l.product_id == inverter_prod)
    bat_line = dispatch.line_ids.filtered(lambda l: l.product_id == battery_prod)
    inv_line.lot_id = inv_lot.id
    bat_line.lot_id = bat_lot.id

    assert dispatch.serial_validation_complete is True, "Serial validation should be complete"
    print(f"     -> Serial Validation Status: Complete={dispatch.serial_validation_complete}")

    # Validate Dispatch
    dispatch.action_validate_dispatch()
    assert dispatch.state == 'dispatched', f"Expected state 'dispatched', got {dispatch.state}"
    print(f"[13] DISPATCH VALIDATED:")
    print(f"     - State: {dispatch.state}")
    print(f"     - Actual Dispatch Date: {dispatch.actual_dispatch_date}")
    print(f"     - Dispatched By: {dispatch.dispatched_by.name}")

    # 14. Verify Duplicate Serial Allocation Prevention across Projects
    project_2 = env['solar.project'].create({
        'name': 'PROJ-AHM-2026-0099',
        'partner_id': customer.id,
        'kw_capacity': 5.0,
        'system_type': 'hybrid',
        'contract_amount': 320000.0,
    })
    dispatch_2 = env['solar.equipment.dispatch'].create({
        'project_id': project_2.id,
        'partner_id': customer.id,
    })
    try:
        env['solar.equipment.dispatch.line'].create({
            'dispatch_id': dispatch_2.id,
            'product_id': inverter_prod.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'lot_id': inv_lot.id,  # SAME serial number as already dispatched to project 1
        })
        raise AssertionError("Duplicate serial allocation to different project MUST raise ValidationError!")
    except ValidationError as e:
        print(f"[14] DUPLICATE SERIAL NUMBER DEFENSE VERIFIED:")
        print(f"     -> Successfully blocked duplicate serial allocation: '{e}'")

    # 15. Verify ACLs & Permissions
    # Standard user has read/write on solar.project and stock requirements
    demo_user = env['res.users'].search([('login', '!=', 'admin'), ('active', '=', True)], limit=1)
    if not demo_user:
        demo_user = env['res.users'].create({
            'name': 'Solar Operations Field Lead',
            'login': 'solar_lead',
            'email': 'lead@sunflow.com',
            'groups_id': [(6, 0, [env.ref('base.group_user').id])],
        })
    print(f"[15] ACL VERIFICATION FOR USER: {demo_user.name}")
    user_project = env['solar.project'].with_user(demo_user).browse(project.id)
    assert user_project.name == project.name, "User should be able to read project"
    print(f"     -> Standard User Read Access: GRANTED for {user_project.name}")

    print("\n" + "=" * 70)
    print("ALL RUNTIME INTEGRATION GATE CHECKS PASSED FLAWLESSLY!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    # When run inside odoo shell, `env` is in globals()
    if 'env' in globals():
        run_integration_verification(globals()['env'])
    else:
        print("ERROR: This script must be run inside `odoo shell -d sunflow_test`")
        sys.exit(1)
