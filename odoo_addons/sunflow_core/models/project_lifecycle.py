# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SolarProject(models.Model):
    _name = 'solar.project'
    _description = 'Solar Project Operational Lifecycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Project Code',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True
    )
    stage = fields.Selection([
        ('lead', 'Enquiry / Lead'),
        ('survey', 'Site Survey'),
        ('feasibility', 'Feasibility Review'),
        ('quotation', 'Quotation & BOM'),
        ('order', 'Sales Order Approved'),
        ('procurement', 'Inventory Reserved'),
        ('dispatch', 'Dispatched to Site'),
        ('installation', 'Installation in Progress'),
        ('commissioning', 'Testing & Commissioning'),
        ('handover', 'Customer Accepted'),
        ('warranty', 'Warranty Active'),
        ('closed', 'Completed & Closed'),
        ('cancelled', 'Cancelled')
    ], string='Lifecycle Stage', default='lead', tracking=True)

    kw_capacity = fields.Float(string='System Capacity (kW)', tracking=True)
    system_type = fields.Selection([
        ('on_grid', 'On-Grid'),
        ('off_grid', 'Off-Grid'),
        ('hybrid', 'Hybrid')
    ], string='System Type', default='on_grid')

    contract_amount = fields.Monetary(string='Contract Amount', currency_field='currency_id')
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id')
    gross_margin = fields.Monetary(
        string='Gross Margin',
        compute='_compute_gross_margin',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    lead_id = fields.Many2one('crm.lead', string='Source CRM Lead')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    survey_ids = fields.One2many('solar.survey', 'project_id', string='Surveys')
    installation_ids = fields.One2many('solar.installation', 'project_id', string='Installation Work Orders')
    warranty_ids = fields.One2many('solar.warranty', 'project_id', string='Warranties')

    assigned_technician_id = fields.Many2one('res.users', string='Lead Technician', tracking=True)
    installation_date = fields.Date(string='Scheduled Installation Date')
    completion_date = fields.Date(string='Actual Completion Date')

    @api.depends('contract_amount', 'actual_cost')
    def _compute_gross_margin(self):
        for rec in self:
            rec.gross_margin = rec.contract_amount - rec.actual_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.project') or _('SPF-%04d') % self.search_count([])
        return super().create(vals_list)
