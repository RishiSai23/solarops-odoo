# -*- coding: utf-8 -*-
"""
solar.package.component — Bill of Materials Lines for Solar Packages
=====================================================================
Extends the solar.package model with component line items (BOM).
Each line references a native Odoo product.product and specifies the
required quantity per package. This replaces the need for the mrp module.

Architectural decision: We intentionally avoid the mrp dependency to keep
sunflow_core compatible with Odoo Community without Manufacturing. Instead
we implement lightweight package-level BOMs using a dedicated one2many model.
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SolarPackageComponent(models.Model):
    """One BOM line: product + quantity required for a solar package."""
    _name = 'solar.package.component'
    _description = 'Solar Package — Bill of Materials Component Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    package_id = fields.Many2one(
        'solar.package',
        string='Solar Package',
        required=True,
        ondelete='cascade',
        index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Component Product',
        required=True,
        domain=[('type', 'in', ['product', 'consu'])],
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        related='product_id.product_tmpl_id',
        store=True,
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True,
    )
    quantity = fields.Float(
        string='Required Quantity',
        required=True,
        default=1.0,
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
    ], string='Component Category', required=True, default='other')
    is_serialized = fields.Boolean(
        string='Requires Serial Tracking',
        help='If checked, individual serial numbers must be captured during dispatch.',
        default=False,
    )
    notes = fields.Char(string='Notes / Specification')

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_(
                    'Component quantity must be greater than zero. '
                    'Check the BOM line for "%s".'
                ) % rec.product_id.display_name)

