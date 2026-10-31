# -*- coding: utf-8 -*-
"""
solar.stock.requirement — Per-Order Inventory Demand Lines
===========================================================
When a solar sales order is confirmed, the system generates one
solar.stock.requirement record per BOM component. This provides
a clear, queryable view of what stock is needed for each project
without modifying Odoo's native stock.move records directly.

These records:
  - Link a solar.project + sale.order to a product + required qty.
  - Cache available/reserved/incoming quantities for quick shortage reporting.
  - Link to the Odoo stock.picking created for outgoing dispatch.
  - Are refreshed when stock quantities change (manual refresh button).

We do NOT store authoritative stock figures here — we read them from
Odoo's native stock.quant at the time of the check. The cached fields
are convenience snapshots only.
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SolarStockRequirement(models.Model):
    """Inventory demand line generated from a confirmed solar sales order."""
    _name = 'solar.stock.requirement'
    _description = 'Solar Project — Stock Requirement Line'
    _order = 'project_id, sequence'
    _rec_name = 'product_id'

    sequence = fields.Integer(string='Seq', default=10)
    project_id = fields.Many2one(
        'solar.project',
        string='Solar Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        related='project_id.sale_order_id',
        store=True,
        readonly=True,
    )
    package_component_id = fields.Many2one(
        'solar.package.component',
        string='Package BOM Line',
        ondelete='set null',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        index=True,
    )
    component_type = fields.Selection([
        ('panel', 'Solar PV Panel'),
        ('inverter', 'Solar Inverter'),
        ('battery', 'Battery Storage'),
        ('controller', 'Charge Controller'),
        ('mounting', 'Mounting Structure'),
        ('cable', 'Electrical Cable'),
        ('connector', 'DC/AC Connector'),
        ('db_box', 'Distribution Box / ACDB / DCDB'),
        ('earthing', 'Earthing & Surge Protection'),
        ('other', 'Other / Miscellaneous'),
    ], string='Component Type')
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
        related='product_id.uom_id',
        readonly=True,
    )
    required_qty = fields.Float(string='Required Qty', required=True, default=1.0)
    is_serialized = fields.Boolean(string='Serial Required', default=False)

    # --- Snapshot: read from stock.quant at check time ---
    qty_on_hand = fields.Float(string='On Hand', readonly=True, digits='Product Unit of Measure')
    qty_reserved = fields.Float(string='Reserved', readonly=True, digits='Product Unit of Measure')
    qty_incoming = fields.Float(string='Incoming', readonly=True, digits='Product Unit of Measure')
    qty_available = fields.Float(
        string='Available (Free)',
        compute='_compute_qty_available',
        store=False,
        digits='Product Unit of Measure',
    )
    qty_shortage = fields.Float(
        string='Shortage',
        compute='_compute_qty_shortage',
        store=False,
        digits='Product Unit of Measure',
    )
    has_shortage = fields.Boolean(
        string='Shortage?',
        compute='_compute_qty_shortage',
        store=False,
    )

    # --- Status ---
    status = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Stock Available'),
        ('partial', 'Partially Available'),
        ('shortage', 'Stock Shortage'),
        ('reserved', 'Reserved'),
        ('dispatched', 'Dispatched'),
    ], string='Status', default='draft')

    # --- Links to Odoo native stock operations ---
    picking_id = fields.Many2one(
        'stock.picking',
        string='Outgoing Delivery',
        readonly=True,
        help='The Odoo delivery order (OUT) associated with this requirement.',
    )
    purchase_order_line_ids = fields.Many2many(
        'purchase.order.line',
        'solar_req_pol_rel',
        'requirement_id',
        'pol_id',
        string='Purchase Order Lines',
        help='Purchase order lines created to cover this shortage.',
    )

    @api.depends('qty_on_hand', 'qty_reserved')
    def _compute_qty_available(self):
        for rec in self:
            rec.qty_available = max(0.0, rec.qty_on_hand - rec.qty_reserved)

    @api.depends('qty_available', 'required_qty')
    def _compute_qty_shortage(self):
        for rec in self:
            shortage = rec.required_qty - rec.qty_available
            rec.qty_shortage = max(0.0, shortage)
            rec.has_shortage = shortage > 0.0

    def action_check_stock(self):
        """
        Refresh stock snapshot from Odoo's native stock.quant.
        Called manually by the inventory manager or triggered after
        order confirmation.
        """
        for rec in self:
            product = rec.product_id
            company_id = self.env.company.id
            warehouse = self.env['stock.warehouse'].search(
                [('company_id', '=', company_id)], limit=1
            ) or self.env['stock.warehouse'].search([], limit=1)

            stock_location = warehouse.lot_stock_id if warehouse else self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
            if not stock_location:
                rec.qty_on_hand = 0.0
                rec.qty_reserved = 0.0
                rec.qty_incoming = 0.0
                rec.status = 'shortage'
                continue

            # Read from stock.quant — native Odoo authoritative source
            domain = [
                ('product_id', '=', product.id),
                ('location_id', 'child_of', stock_location.id),
            ]
            quants = self.env['stock.quant'].search(domain)
            on_hand = sum(quants.mapped('quantity'))
            reserved = sum(quants.mapped('reserved_quantity'))

            # Incoming: confirmed purchase order lines not yet received
            incoming = self._get_incoming_qty(product, warehouse)

            rec.qty_on_hand = on_hand
            rec.qty_reserved = reserved
            rec.qty_incoming = incoming

            # Update status
            available = max(0.0, on_hand - reserved)
            if rec.status == 'dispatched':
                pass  # Do not change dispatched status
            elif available >= rec.required_qty:
                rec.status = 'available'
            elif available > 0:
                rec.status = 'partial'
            else:
                rec.status = 'shortage'

    def _get_incoming_qty(self, product, warehouse):
        """
        Return the total quantity of a product on confirmed purchase orders
        not yet received, for the given warehouse's input location.
        """
        pol = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['purchase', 'done']),
        ])
        return sum(max(0.0, line.product_qty - line.qty_received) for line in pol)

    def action_create_purchase_order(self):
        """
        Open a wizard-like PO creation form pre-filled with the shortage
        quantity and the product's first vendor. Returns an action.
        """
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

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
            'target': 'current',
        }
