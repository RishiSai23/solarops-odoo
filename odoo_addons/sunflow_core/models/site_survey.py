# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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
    service_voltage = fields.Integer(string='Service Voltage (V)', default=230)

    feasibility_status = fields.Selection([
        ('draft', 'Draft'),
        ('feasible', 'Feasible & Approved'),
        ('conditional', 'Conditional / Requires Reinforcement'),
        ('rejected', 'Not Feasible')
    ], string='Feasibility Status', default='draft', tracking=True)

    shading_notes = fields.Text(string='Shading Notes')
    remarks = fields.Text(string='Remarks')
    survey_notes = fields.Text(string='Technical Observations')

    @api.constrains('feasibility_status', 'sanctioned_load_kw', 'project_id')
    def _check_grid_load_compatibility(self):
        """
        Verify technical grid load compatibility:
        In solar EPC regulations, system capacity cannot exceed utility sanctioned load.
        If system capacity > sanctioned load, it cannot be marked unconditionally 'feasible';
        it must be 'conditional' pending sanctioned load enhancement or capacity adjustment.
        """
        for survey in self:
            if survey.feasibility_status == 'feasible' and survey.project_id:
                if survey.project_id.kw_capacity > 0 and survey.sanctioned_load_kw > 0:
                    if survey.project_id.kw_capacity > survey.sanctioned_load_kw:
                        raise ValidationError(_(
                            "Technical Incompatibility: Proposed system capacity (%.2f kW) exceeds "
                            "the utility sanctioned grid load (%.2f kW). The survey cannot be marked "
                            "'Feasible & Approved' as-is. Please mark as 'Conditional / Requires Reinforcement' "
                            "pending grid load enhancement, or reduce project capacity."
                        ) % (survey.project_id.kw_capacity, survey.sanctioned_load_kw))

    def action_set_feasible(self):
        self.ensure_one()
        self.write({'feasibility_status': 'feasible'})
        return True

    def action_set_conditional(self):
        self.ensure_one()
        self.write({'feasibility_status': 'conditional'})
        return True

    def action_set_rejected(self):
        self.ensure_one()
        self.write({'feasibility_status': 'rejected'})
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.project_id:
                rec.project_id._sync_survey_feasibility()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'feasibility_status' in vals or 'project_id' in vals:
            for rec in self:
                if rec.project_id:
                    rec.project_id._sync_survey_feasibility()
        return res
