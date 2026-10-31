# -*- coding: utf-8 -*-
"""
Phase 4 — Inventory & Procurement Test Suite
=============================================
Tests for:
  - solar.package.component (BOM configuration)
  - solar.stock.requirement (demand generation)
  - solar.equipment.dispatch + solar.equipment.dispatch.line (dispatch workflow)
  - serial number validation (duplicate rejection, product mismatch)
  - integration: package → requirements → stock check → dispatch

These are Odoo-style unit tests using odoo.tests.common.TransactionCase.
They run inside a database transaction that is rolled back after each test,
so they do not pollute production data.

Run with:
    ./odoo-bin -d <db> --test-enable -u sunflow_core --stop-after-init
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestPackageBOM(TransactionCase):
    """Tests for solar.package and solar.package.component (BOM lines)."""

    def setUp(self):
        super().setUp()
        # Create a storable product for panels (no serial tracking for basic BOM tests)
        self.panel_product = self.env['product.product'].create({
            'name': 'Solar PV Panel 550Wp',
            'type': 'product',
            'tracking': 'none',
            'standard_price': 8500.0,
        })
        self.inverter_product = self.env['product.product'].create({
            'name': 'String Inverter 3kW',
            'type': 'product',
            'tracking': 'serial',
            'standard_price': 25000.0,
        })
        self.package = self.env['solar.package'].create({
            'name': '3 kW On-Grid Standard',
            'capacity_kw': 3.0,
            'system_type': 'on_grid',
            'panel_wattage': 550,
            'panel_count': 6,
            'inverter_capacity_kw': 3.0,
            'base_price': 120000.0,
        })

    def test_01_create_bom_component(self):
        """A BOM component line can be created and linked to a package."""
        comp = self.env['solar.package.component'].create({
            'package_id': self.package.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'quantity': 6.0,
            'is_serialized': False,
        })
        self.assertEqual(comp.package_id, self.package)
        self.assertEqual(comp.quantity, 6.0)
        self.assertEqual(comp.product_uom_id, self.panel_product.uom_id)

    def test_02_bom_component_count(self):
        """solar.package.component_count is computed correctly."""
        self.env['solar.package.component'].create({
            'package_id': self.package.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'quantity': 6.0,
        })
        self.env['solar.package.component'].create({
            'package_id': self.package.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
        })
        self.package.invalidate_recordset()
        self.assertEqual(self.package.component_count, 2)

    def test_03_bom_quantity_constraint(self):
        """A BOM line with quantity ≤ 0 must raise a ValidationError."""
        with self.assertRaises(ValidationError):
            self.env['solar.package.component'].create({
                'package_id': self.package.id,
                'product_id': self.panel_product.id,
                'component_type': 'panel',
                'quantity': 0.0,
            })

    def test_04_serialized_flag_propagated(self):
        """is_serialized flag is stored correctly on BOM lines."""
        comp = self.env['solar.package.component'].create({
            'package_id': self.package.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
        })
        self.assertTrue(comp.is_serialized)


class TestStockRequirementGeneration(TransactionCase):
    """Tests for solar.stock.requirement — demand generation from BOM."""

    def setUp(self):
        super().setUp()
        self.panel_product = self.env['product.product'].create({
            'name': 'Test Panel 400Wp',
            'type': 'product',
            'tracking': 'none',
        })
        self.inverter_product = self.env['product.product'].create({
            'name': 'Test Inverter 3kW',
            'type': 'product',
            'tracking': 'serial',
        })
        self.package = self.env['solar.package'].create({
            'name': 'Test 3kW Package',
            'capacity_kw': 3.0,
            'system_type': 'on_grid',
            'panel_count': 6,
            'inverter_capacity_kw': 3.0,
            'base_price': 100000.0,
        })
        self.env['solar.package.component'].create([
            {
                'package_id': self.package.id,
                'product_id': self.panel_product.id,
                'component_type': 'panel',
                'quantity': 6.0,
                'is_serialized': False,
            },
            {
                'package_id': self.package.id,
                'product_id': self.inverter_product.id,
                'component_type': 'inverter',
                'quantity': 1.0,
                'is_serialized': True,
            },
        ])
        self.customer = self.env['res.partner'].create({'name': 'Test Customer'})
        self.project = self.env['solar.project'].create({
            'partner_id': self.customer.id,
            'kw_capacity': 3.0,
            'system_type': 'on_grid',
            'package_id': self.package.id,
            'contract_amount': 100000.0,
        })

    def test_05_generate_requirements_from_bom(self):
        """Generating requirements creates one line per BOM component."""
        self.project.action_generate_stock_requirements()
        reqs = self.project.stock_requirement_ids
        self.assertEqual(len(reqs), 2)

        panel_req = reqs.filtered(lambda r: r.product_id == self.panel_product)
        inverter_req = reqs.filtered(lambda r: r.product_id == self.inverter_product)
        self.assertTrue(panel_req)
        self.assertTrue(inverter_req)
        self.assertEqual(panel_req.required_qty, 6.0)
        self.assertEqual(inverter_req.required_qty, 1.0)
        self.assertTrue(inverter_req.is_serialized)
        self.assertFalse(panel_req.is_serialized)

    def test_06_generate_requirements_no_package(self):
        """Generating requirements without a package raises UserError."""
        project_no_pkg = self.env['solar.project'].create({
            'partner_id': self.customer.id,
            'kw_capacity': 2.0,
            'system_type': 'on_grid',
            'contract_amount': 80000.0,
        })
        with self.assertRaises(UserError):
            project_no_pkg.action_generate_stock_requirements()

    def test_07_generate_requirements_empty_bom(self):
        """Generating requirements for a package with no BOM raises UserError."""
        empty_pkg = self.env['solar.package'].create({
            'name': 'Empty Package',
            'capacity_kw': 1.0,
            'system_type': 'on_grid',
            'panel_count': 2,
            'inverter_capacity_kw': 1.0,
            'base_price': 50000.0,
        })
        self.project.package_id = empty_pkg
        with self.assertRaises(UserError):
            self.project.action_generate_stock_requirements()

    def test_08_shortage_computed_correctly(self):
        """qty_shortage is correctly calculated as required - available."""
        req = self.env['solar.stock.requirement'].create({
            'project_id': self.project.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'required_qty': 6.0,
            'qty_on_hand': 4.0,
            'qty_reserved': 0.0,
            'status': 'partial',
        })
        self.assertEqual(req.qty_available, 4.0)
        self.assertEqual(req.qty_shortage, 2.0)
        self.assertTrue(req.has_shortage)

    def test_09_no_shortage_when_sufficient(self):
        """No shortage when on-hand >= required."""
        req = self.env['solar.stock.requirement'].create({
            'project_id': self.project.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'required_qty': 6.0,
            'qty_on_hand': 10.0,
            'qty_reserved': 0.0,
            'status': 'available',
        })
        self.assertEqual(req.qty_shortage, 0.0)
        self.assertFalse(req.has_shortage)


class TestSerialNumberValidation(TransactionCase):
    """Tests for serial number validation in solar.equipment.dispatch.line."""

    def setUp(self):
        super().setUp()
        self.inverter_product = self.env['product.product'].create({
            'name': 'Inverter SN Test',
            'type': 'product',
            'tracking': 'serial',
        })
        self.battery_product = self.env['product.product'].create({
            'name': 'Battery SN Test',
            'type': 'product',
            'tracking': 'serial',
        })
        self.customer = self.env['res.partner'].create({'name': 'SN Test Customer'})
        self.project = self.env['solar.project'].create({
            'partner_id': self.customer.id,
            'kw_capacity': 3.0,
            'system_type': 'on_grid',
            'contract_amount': 100000.0,
        })
        # Create a stock.lot (serial number) for inverter
        self.inverter_lot = self.env['stock.lot'].create({
            'name': 'INV-SN-001',
            'product_id': self.inverter_product.id,
            'company_id': self.env.company.id,
        })
        self.battery_lot = self.env['stock.lot'].create({
            'name': 'BAT-SN-001',
            'product_id': self.battery_product.id,
            'company_id': self.env.company.id,
        })
        # Create dispatch
        self.dispatch = self.env['solar.equipment.dispatch'].create({
            'project_id': self.project.id,
        })

    def test_10_lot_product_mismatch_raises_validation_error(self):
        """
        Assigning a battery lot to an inverter line must raise ValidationError.
        This is enforced by both @api.constrains and _validate_serial().
        """
        with self.assertRaises(ValidationError):
            self.env['solar.equipment.dispatch.line'].create({
                'dispatch_id': self.dispatch.id,
                'product_id': self.inverter_product.id,
                'component_type': 'inverter',
                'quantity': 1.0,
                'is_serialized': True,
                'lot_id': self.battery_lot.id,  # Wrong lot!
            })

    def test_11_correct_lot_product_passes(self):
        """A lot assigned to the matching product must pass validation."""
        line = self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': self.dispatch.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
            'lot_id': self.inverter_lot.id,
        })
        self.assertEqual(line.lot_id, self.inverter_lot)

    def test_12_duplicate_lot_dispatched_to_different_project(self):
        """
        A serial/lot already dispatched to project A cannot be dispatched
        to project B. Duplicate allocation must raise ValidationError.
        """
        # Dispatch to project A (mark as 'dispatched' directly for test isolation)
        dispatch_a = self.env['solar.equipment.dispatch'].create({
            'project_id': self.project.id,
            'state': 'dispatched',
        })
        self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': dispatch_a.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
            'lot_id': self.inverter_lot.id,
        })

        # Now try dispatching the same lot to project B
        customer_b = self.env['res.partner'].create({'name': 'Customer B'})
        project_b = self.env['solar.project'].create({
            'partner_id': customer_b.id,
            'kw_capacity': 3.0,
            'system_type': 'on_grid',
            'contract_amount': 100000.0,
        })
        dispatch_b = self.env['solar.equipment.dispatch'].create({
            'project_id': project_b.id,
        })
        # Creating line with already-dispatched lot to another project should raise ValidationError
        with self.assertRaises(ValidationError):
            self.env['solar.equipment.dispatch.line'].create({
                'dispatch_id': dispatch_b.id,
                'product_id': self.inverter_product.id,
                'component_type': 'inverter',
                'quantity': 1.0,
                'is_serialized': True,
                'lot_id': self.inverter_lot.id,
            })

    def test_13_same_lot_same_project_allowed(self):
        """
        A lot dispatched (or being dispatched) to the same project should
        not trigger the duplicate-allocation check.
        """
        dispatch_same = self.env['solar.equipment.dispatch'].create({
            'project_id': self.project.id,
            'state': 'dispatched',
        })
        self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': dispatch_same.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
            'lot_id': self.inverter_lot.id,
        })
        # Re-dispatching same lot to same project is allowed
        new_dispatch = self.env['solar.equipment.dispatch'].create({
            'project_id': self.project.id,
        })
        line = self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': new_dispatch.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
            'lot_id': self.inverter_lot.id,
        })
        # The serial validation for duplicate-cross-project check should pass
        # (stock check will be skipped since no warehouse quant in test env)
        # We only test the duplicate check (check 2), not the quant check (check 3)
        dispatched_headers = self.env['solar.equipment.dispatch'].search([
            ('state', '=', 'dispatched'),
            ('project_id', '!=', new_dispatch.project_id.id),
        ])
        conflicting = self.env['solar.equipment.dispatch.line'].search([
            ('lot_id', '=', self.inverter_lot.id),
            ('dispatch_id', 'in', dispatched_headers.mapped('id')),
            ('id', '!=', line.id),
        ])
        self.assertFalse(
            conflicting,
            'Same project duplicate allocation should not be flagged.'
        )


class TestDispatchWorkflow(TransactionCase):
    """Tests for solar.equipment.dispatch state machine and business rules."""

    def setUp(self):
        super().setUp()
        self.panel_product = self.env['product.product'].create({
            'name': 'Panel for Dispatch Test',
            'type': 'product',
            'tracking': 'none',
        })
        self.inverter_product = self.env['product.product'].create({
            'name': 'Inverter for Dispatch Test',
            'type': 'product',
            'tracking': 'serial',
        })
        self.customer = self.env['res.partner'].create({'name': 'Dispatch Test Customer'})
        self.project = self.env['solar.project'].create({
            'partner_id': self.customer.id,
            'kw_capacity': 3.0,
            'system_type': 'on_grid',
            'contract_amount': 100000.0,
        })
        self.dispatch = self.env['solar.equipment.dispatch'].create({
            'project_id': self.project.id,
        })

    def test_14_dispatch_ref_auto_generated(self):
        """Dispatch reference is auto-generated (not 'New')."""
        self.assertNotEqual(self.dispatch.name, 'New')
        self.assertTrue(self.dispatch.name.startswith('DISP-'))

    def test_15_mark_ready_requires_lines(self):
        """action_mark_ready raises UserError when no equipment lines exist."""
        with self.assertRaises(UserError):
            self.dispatch.action_mark_ready()

    def test_16_mark_ready_with_lines_succeeds(self):
        """action_mark_ready succeeds when lines are present."""
        self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': self.dispatch.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'quantity': 6.0,
            'is_serialized': False,
        })
        self.dispatch.action_mark_ready()
        self.assertEqual(self.dispatch.state, 'ready')

    def test_17_validate_dispatch_requires_serial_numbers(self):
        """
        action_validate_dispatch must raise UserError when a serialized line
        has no lot_id assigned.
        """
        self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': self.dispatch.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
            # lot_id intentionally omitted
        })
        self.dispatch.action_mark_ready()
        self.assertEqual(self.dispatch.state, 'ready')
        with self.assertRaises(UserError):
            self.dispatch.action_validate_dispatch()

    def test_18_serial_validation_complete_flag(self):
        """serial_validation_complete is True only when all serial lines have lots."""
        inverter_lot = self.env['stock.lot'].create({
            'name': 'INV-DISP-001',
            'product_id': self.inverter_product.id,
            'company_id': self.env.company.id,
        })
        # Line without lot — incomplete
        line = self.env['solar.equipment.dispatch.line'].create({
            'dispatch_id': self.dispatch.id,
            'product_id': self.inverter_product.id,
            'component_type': 'inverter',
            'quantity': 1.0,
            'is_serialized': True,
        })
        self.assertFalse(self.dispatch.serial_validation_complete)

        # Assign lot — now complete
        line.lot_id = inverter_lot
        self.assertTrue(self.dispatch.serial_validation_complete)

    def test_19_cancel_dispatched_raises_error(self):
        """Cancelling a dispatched dispatch must raise UserError."""
        self.dispatch.state = 'dispatched'
        with self.assertRaises(UserError):
            self.dispatch.action_cancel()

    def test_20_cancel_draft_succeeds(self):
        """Cancelling a draft dispatch changes state to cancelled."""
        self.dispatch.action_cancel()
        self.assertEqual(self.dispatch.state, 'cancelled')


class TestProjectStockIntegration(TransactionCase):
    """Integration tests: package → requirements → dispatch → project stage."""

    def setUp(self):
        super().setUp()
        self.panel_product = self.env['product.product'].create({
            'name': 'Integration Panel',
            'type': 'product',
            'tracking': 'none',
        })
        self.package = self.env['solar.package'].create({
            'name': 'Integration 2kW Package',
            'capacity_kw': 2.0,
            'system_type': 'on_grid',
            'panel_count': 4,
            'inverter_capacity_kw': 2.0,
            'base_price': 80000.0,
        })
        self.env['solar.package.component'].create({
            'package_id': self.package.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'quantity': 4.0,
            'is_serialized': False,
        })
        self.customer = self.env['res.partner'].create({'name': 'Integration Customer'})
        self.project = self.env['solar.project'].create({
            'partner_id': self.customer.id,
            'kw_capacity': 2.0,
            'system_type': 'on_grid',
            'package_id': self.package.id,
            'contract_amount': 80000.0,
            'stage': 'order',
        })

    def test_21_generate_requirements_advances_project_stage(self):
        """
        After generating stock requirements from a confirmed order (stage='order'),
        the project advances to 'procurement'.
        """
        self.project.action_generate_stock_requirements()
        self.assertEqual(self.project.stage, 'procurement')

    def test_22_create_dispatch_from_project(self):
        """
        action_create_dispatch creates a dispatch pre-populated with
        one line per non-dispatched stock requirement.
        """
        req = self.env['solar.stock.requirement'].create({
            'project_id': self.project.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'required_qty': 4.0,
            'status': 'available',
        })

        result = self.project.action_create_dispatch()
        dispatch_id = result.get('res_id')
        self.assertTrue(dispatch_id)

        dispatch = self.env['solar.equipment.dispatch'].browse(dispatch_id)
        self.assertEqual(dispatch.project_id, self.project)
        self.assertEqual(len(dispatch.line_ids), 1)
        self.assertEqual(dispatch.line_ids[0].product_id, self.panel_product)
        self.assertEqual(dispatch.line_ids[0].quantity, 4.0)

    def test_23_requirement_count_smart_button(self):
        """requirement_count is updated when requirements are added."""
        self.assertEqual(self.project.requirement_count, 0)
        self.env['solar.stock.requirement'].create({
            'project_id': self.project.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'required_qty': 4.0,
        })
        self.project.invalidate_recordset()
        self.assertEqual(self.project.requirement_count, 1)

    def test_24_has_shortage_flag(self):
        """has_shortage is True when any requirement has status 'shortage'."""
        self.env['solar.stock.requirement'].create({
            'project_id': self.project.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'required_qty': 4.0,
            'qty_on_hand': 0.0,
            'status': 'shortage',
        })
        self.assertTrue(self.project.has_shortage)

    def test_25_stock_ready_flag(self):
        """stock_ready is True when all requirements are in available/reserved/dispatched."""
        self.env['solar.stock.requirement'].create({
            'project_id': self.project.id,
            'product_id': self.panel_product.id,
            'component_type': 'panel',
            'required_qty': 4.0,
            'qty_on_hand': 10.0,
            'status': 'available',
        })
        self.assertTrue(self.project.stock_ready)
        self.assertFalse(self.project.has_shortage)

