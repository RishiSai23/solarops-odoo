# -*- coding: utf-8 -*-
from odoo import models, fields

class SolarInstallation(models.Model):
    _name = 'solar.installation'
    _description = 'Field Solar Installation Work Order'
    _inherit = ['mail.thread']

    name = fields.Char(string='Work Order Ref', required=True, copy=False, default='New WO')
    project_id = fields.Many2one('solar.project', string='Solar Project', required=True, ondelete='cascade')
    technician_lead_id = fields.Many2one('res.users', string='Field Lead Technician', required=True)
    scheduled_date = fields.Date(string='Scheduled Date')
    completion_date = fields.Date(string='Actual Completion Date')

    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('tested', 'Electrically Tested'),
        ('accepted', 'Customer Accepted'),
        ('failed', 'Inspection Failed')
    ], string='Status', default='scheduled', tracking=True)

    # Electrical Verification Checklists
    check_structure_torque = fields.Boolean(string='Mechanical Structure Torque Checked', default=False)
    check_dc_wiring_polar = fields.Boolean(string='DC Cable Polarity Verified', default=False)
    check_earthing_installed = fields.Boolean(string='Dual Earthing Pit Installed', default=False)
    earthing_resistance_ohms = fields.Float(string='Measured Earthing Resistance (Ω)')
    voc_measured_volts = fields.Float(string='Measured Open Circuit Voltage (Voc)')

    customer_signature = fields.Binary(string='Digital Acceptance Signature')
    customer_feedback = fields.Text(string='Customer Acceptance Notes')
