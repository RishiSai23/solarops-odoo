# -*- coding: utf-8 -*-
from odoo import models, fields

class SolarSurvey(models.Model):
    _name = 'solar.survey'
    _description = 'Rooftop Site Feasibility Survey'
    _inherit = ['mail.thread']

    name = fields.Char(string='Survey Reference', required=True, copy=False, default='New Survey')
    project_id = fields.Many2one('solar.project', string='Solar Project', required=True, ondelete='cascade')
    surveyor_id = fields.Many2one('res.users', string='Surveyor', default=lambda self: self.env.user)
    survey_date = fields.Date(string='Survey Date', default=fields.Date.context_today)

    roof_type = fields.Selection([
        ('rcc_flat', 'RCC Flat Roof'),
        ('tin_shed', 'Industrial Tin Shed'),
        ('tile_sloped', 'Sloped Tile Roof'),
        ('ground_mount', 'Ground Mount')
    ], string='Rooftop Type', default='rcc_flat')

    azimuth_degrees = fields.Float(string='Azimuth (°)', help='True South = 180°')
    tilt_degrees = fields.Float(string='Optimal Tilt (°)', default=15.0)
    shading_factor_pct = fields.Float(string='Shading Factor (%)', default=0.0)

    usable_area_sqft = fields.Float(string='Usable Rooftop Area (sq.ft)')
    sanctioned_load_kw = fields.Float(string='Sanctioned Grid Load (kW)')
    meter_phase = fields.Selection([
        ('single_phase', 'Single Phase (230V)'),
        ('three_phase', 'Three Phase (415V)')
    ], string='Utility Meter Phase', default='single_phase')

    feasibility_status = fields.Selection([
        ('draft', 'Draft'),
        ('feasible', 'Feasible & Approved'),
        ('conditional', 'Conditional / Requires Reinforcement'),
        ('rejected', 'Not Feasible')
    ], string='Feasibility Status', default='draft')

    survey_notes = fields.Text(string='Technical Observations')
