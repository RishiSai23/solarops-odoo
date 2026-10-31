# -*- coding: utf-8 -*-
from odoo import models, fields

class SolarPackage(models.Model):
    _name = 'solar.package'
    _description = 'Modular Solar Package Template'

    name = fields.Char(string='Package Name', required=True)
    capacity_kw = fields.Float(string='Capacity (kW)', required=True)
    system_type = fields.Selection([
        ('on_grid', 'On-Grid'),
        ('off_grid', 'Off-Grid'),
        ('hybrid', 'Hybrid')
    ], string='System Type', default='on_grid', required=True)

    panel_wattage = fields.Integer(string='Panel Wattage (Wp)', default=550)
    panel_count = fields.Integer(string='Panel Quantity', required=True)
    inverter_capacity_kw = fields.Float(string='Inverter Rating (kW)', required=True)
    battery_bank_kwh = fields.Float(string='Battery Bank Capacity (kWh)', default=0.0)

    base_price = fields.Float(string='Base Package Price', required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Package Specifications')
