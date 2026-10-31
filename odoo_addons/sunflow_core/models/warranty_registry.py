# -*- coding: utf-8 -*-
from odoo import models, fields

class SolarWarranty(models.Model):
    _name = 'solar.warranty'
    _description = 'Solar Equipment Serialized Warranty Registry'
    _inherit = ['mail.thread']

    name = fields.Char(string='Warranty Certificate ID', required=True, copy=False, default='New Cert')
    project_id = fields.Many2one('solar.project', string='Solar Project', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Customer', related='project_id.partner_id', store=True)

    equipment_type = fields.Selection([
        ('panel', 'Solar PV Panel'),
        ('inverter', 'Solar Inverter'),
        ('battery', 'Battery Storage'),
        ('controller', 'Charge Controller')
    ], string='Equipment Type', required=True)

    serial_number = fields.Char(string='Scanned Serial Number', required=True, index=True)
    lot_id = fields.Many2one('stock.lot', string='Warehouse Stock Lot')

    warranty_years = fields.Integer(string='Warranty Term (Years)', default=5)
    start_date = fields.Date(string='Warranty Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='Warranty Expiration Date')

    warranty_status = fields.Selection([
        ('active', 'Active & Valid'),
        ('claim_in_progress', 'Warranty Claim Under Review'),
        ('replaced', 'Replaced via RMA'),
        ('expired', 'Expired'),
        ('void', 'Void / Tampered')
    ], string='Status', default='active', tracking=True)
