# -*- coding: utf-8 -*-
"""
solar.equipment.dispatch — Project-Linked Equipment Dispatch Record
====================================================================
Tracks which serialized equipment items (identified by stock.lot) are
dispatched from the warehouse to a specific solar project and customer.

This model sits BETWEEN the native stock.picking (Odoo delivery order)
and the solar.project. It records the mandatory serial number validation
step that field warehouse personnel must complete before approving dispatch.

Workflow:
  1. A solar.stock.requirement signals shortage → resolved.
  2. Warehouse manager opens the dispatch record linked to the project.
  3. For serialized items (inverters, batteries, controllers): scans/enters
     the stock.lot (serial number) and the model validates:
       a) Lot belongs to the correct product.
       b) Lot is physically present in the outgoing stock.picking move lines.
       c) Lot is not already dispatched to another active project.
  4. Manager clicks "Validate Dispatch" — triggers native picking.button_validate().
  5. Dispatch status becomes 'dispatched', equipment is linked to the project
     for future warranty and service lookups.

We deliberately do NOT bypass Odoo's stock.picking validation workflow.
All physical inventory movements happen through stock.picking.button_validate().
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SolarEquipmentDispatch(models.Model):
    """Header record for a project-level equipment dispatch operation."""
    _name = 'solar.equipment.dispatch'
    _description = 'Solar Project — Equipment Dispatch Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Dispatch Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    project_id = fields.Many2one(
        'solar.project',
        string='Solar Project',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='project_id.partner_id',
        store=True,
        readonly=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sales Order',
        related='project_id.sale_order_id',
        store=True,
        readonly=True,
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery Order (Odoo)',
        tracking=True,
        help='The native Odoo stock picking (OUT) for this dispatch.',
    )
    dispatch_date = fields.Date(
        string='Planned Dispatch Date',
        default=fields.Date.context_today,
    )
    actual_dispatch_date = fields.Datetime(
        string='Actual Dispatch Timestamp',
        readonly=True,
    )
    dispatched_by = fields.Many2one(
        'res.users',
        string='Dispatched By',
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready for Dispatch'),
        ('dispatched', 'Dispatched'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True)

    line_ids = fields.One2many(
        'solar.equipment.dispatch.line',
        'dispatch_id',
        string='Equipment Lines',
    )
    notes = fields.Text(string='Dispatch Notes')

    serial_validation_complete = fields.Boolean(
        string='Serial Validation Complete',
        compute='_compute_serial_validation',
        store=False,
    )
    total_lines = fields.Integer(compute='_compute_line_counts', store=False)
    validated_lines = fields.Integer(compute='_compute_line_counts', store=False)

    @api.depends('line_ids', 'line_ids.lot_id', 'line_ids.is_serialized')
    def _compute_serial_validation(self):
        for rec in self:
            serial_lines = rec.line_ids.filtered('is_serialized')
            rec.serial_validation_complete = all(
                line.lot_id for line in serial_lines
            )

    @api.depends('line_ids', 'line_ids.lot_id', 'line_ids.is_serialized')
    def _compute_line_counts(self):
        for rec in self:
            rec.total_lines = len(rec.line_ids)
            rec.validated_lines = len(
                rec.line_ids.filtered(lambda l: not l.is_serialized or l.lot_id)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'solar.equipment.dispatch'
                ) or _('DISP-%04d') % self.search_count([])
        return super().create(vals_list)

    def action_mark_ready(self):
        """Mark the dispatch as ready — all stock requirements should be met."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft dispatches can be marked ready.'))
            if not rec.line_ids:
                raise UserError(_('Cannot mark dispatch ready: no equipment lines defined.'))
            rec.state = 'ready'

    def action_validate_dispatch(self):
        """
        Validate the dispatch:
          1. Check all serialized lines have lot numbers assigned.
          2. Verify lots are valid (correct product, available, not double-dispatched).
          3. Trigger Odoo's native picking validation.
          4. Mark the dispatch as dispatched and record the timestamp.
        """
        self.ensure_one()
        if self.state != 'ready':
            raise UserError(_('Only "Ready for Dispatch" records can be validated.'))

        # Step 1: Serial number completeness check
        serial_lines = self.line_ids.filtered('is_serialized')
        missing = serial_lines.filtered(lambda l: not l.lot_id)
        if missing:
            raise UserError(_(
                'The following components require serial numbers before dispatch can '
                'be validated:\n%s'
            ) % '\n'.join('• %s' % l.product_id.display_name for l in missing))

        # Step 2: Validate each serial line
        for line in serial_lines:
            line._validate_serial()

        # Step 3: Validate the Odoo stock picking if linked
        if self.picking_id and self.picking_id.state not in ('done', 'cancel'):
            # Set lot info on move lines before validation
            self._sync_lots_to_picking()
            try:
                self.picking_id.button_validate()
            except Exception as e:
                raise UserError(_(
                    'Odoo delivery order validation failed: %s'
                ) % str(e))

        # Step 4: Mark dispatched
        self.write({
            'state': 'dispatched',
            'actual_dispatch_date': fields.Datetime.now(),
            'dispatched_by': self.env.user.id,
        })

        # Update project stage
        if self.project_id.stage not in ('installation', 'commissioning', 'handover', 'warranty', 'closed'):
            self.project_id.write({'stage': 'dispatch'})

    def _sync_lots_to_picking(self):
        """
        Synchronise the lot numbers entered on dispatch lines back into the
        Odoo stock.move.line records of the associated picking.
        This ensures Odoo records the correct serial numbers in its native
        stock.lot traceability.
        """
        if not self.picking_id:
            return
        for line in self.line_ids.filtered(lambda l: l.lot_id):
            move_line = self.picking_id.move_line_ids.filtered(
                lambda ml: ml.product_id == line.product_id
            )
            if move_line:
                move_line[0].lot_id = line.lot_id
                move_line[0].quantity = line.quantity

    def action_cancel(self):
        for rec in self:
            if rec.state == 'dispatched':
                raise UserError(_('A dispatched record cannot be cancelled. Raise a return picking instead.'))
            rec.state = 'cancelled'

    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError(_('No delivery order is linked to this dispatch.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class SolarEquipmentDispatchLine(models.Model):
    """One line per component in a solar equipment dispatch."""
    _name = 'solar.equipment.dispatch.line'
    _description = 'Solar Equipment Dispatch — Component Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Seq', default=10)
    dispatch_id = fields.Many2one(
        'solar.equipment.dispatch',
        string='Dispatch',
        required=True,
        ondelete='cascade',
        index=True,
    )
    project_id = fields.Many2one(
        'solar.project',
        related='dispatch_id.project_id',
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
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
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    is_serialized = fields.Boolean(string='Serial Required', default=False)
    lot_id = fields.Many2one(
        'stock.lot',
        string='Serial / Lot Number',
        domain="[('product_id', '=', product_id)]",
        help='Scan or select the serial/lot number for this equipment item.',
    )
    stock_requirement_id = fields.Many2one(
        'solar.stock.requirement',
        string='Stock Requirement',
        ondelete='set null',
    )

    def _validate_serial(self):
        """
        Validate a single serialized dispatch line:
          1. Lot product matches line product.
          2. Lot is present in the warehouse (not already at a customer location).
          3. Lot is not already dispatched to another active project.
        """
        self.ensure_one()
        if not self.lot_id:
            return  # Non-serialized — no check needed

        # Check 1: Product match
        if self.lot_id.product_id != self.product_id:
            raise ValidationError(_(
                'Serial/Lot "%s" belongs to product "%s", '
                'but this dispatch line expects "%s".'
            ) % (
                self.lot_id.name,
                self.lot_id.product_id.display_name,
                self.product_id.display_name,
            ))

        # Check 2: Not already dispatched to another project
        dispatched_headers = self.env['solar.equipment.dispatch'].search([
            ('state', '=', 'dispatched'),
            ('project_id', '!=', self.dispatch_id.project_id.id),
        ])
        conflicting = self.env['solar.equipment.dispatch.line'].search([
            ('lot_id', '=', self.lot_id.id),
            ('dispatch_id', 'in', dispatched_headers.mapped('id')),
            ('id', '!=', self.id),
        ])
        if conflicting:
            raise ValidationError(_(
                'Serial/Lot "%s" has already been dispatched to project "%s" (Dispatch: %s). '
                'Duplicate allocation is not permitted.'
            ) % (
                self.lot_id.name,
                conflicting[0].dispatch_id.project_id.name,
                conflicting[0].dispatch_id.name,
            ))

        # Check 3: Available in stock (quant check)
        company_id = self.env.company.id
        warehouse = self.env['stock.warehouse'].search(
            [('company_id', '=', company_id)], limit=1
        )
        if warehouse:
            quant = self.env['stock.quant'].search([
                ('lot_id', '=', self.lot_id.id),
                ('product_id', '=', self.product_id.id),
                ('location_id', 'child_of', warehouse.lot_stock_id.id),
                ('quantity', '>', 0),
            ])
            if not quant:
                raise ValidationError(_(
                    'Serial/Lot "%s" is not available in the warehouse stock location. '
                    'Verify that the incoming delivery was validated before dispatch.'
                ) % self.lot_id.name)

    @api.constrains('lot_id', 'product_id')
    def _check_lot_product_match(self):
        for rec in self:
            if rec.lot_id and rec.lot_id.product_id != rec.product_id:
                raise ValidationError(_(
                    'Serial/Lot "%s" belongs to "%s" but this line is for "%s". '
                    'Please scan the correct serial number.'
                ) % (
                    rec.lot_id.name,
                    rec.lot_id.product_id.display_name,
                    rec.product_id.display_name,
                ))

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
