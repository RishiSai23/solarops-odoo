# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError


class SolarSurvey(models.Model):
    _name = 'solar.survey'
    _description = 'Rooftop Site Feasibility Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Survey Reference',
        required=True,
        copy=False,
        default=lambda self: _('New'),
    )
    project_id = fields.Many2one(
        'solar.project',
        string='Solar Project',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='CRM Lead',
        help='Direct link to the source CRM lead. Must remain consistent with the linked project source lead.',
    )
    surveyor_id = fields.Many2one(
        'res.users',
        string='Surveyor',
        default=lambda self: self.env.user,
        tracking=True,
    )
    survey_date = fields.Date(
        string='Survey Date',
        default=fields.Date.context_today,
        tracking=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Workflow State', default='draft', tracking=True, copy=False)

    feasibility_status = fields.Selection([
        ('draft', 'Draft'),
        ('feasible', 'Feasible & Approved'),
        ('conditional', 'Conditional / Requires Reinforcement'),
        ('rejected', 'Not Feasible')
    ], string='Feasibility Status', default='draft')

    roof_type = fields.Selection([
        ('rcc_flat', 'RCC Flat Roof'),
        ('tin_shed', 'Industrial Tin Shed'),
        ('tile_sloped', 'Sloped Tile Roof'),
        ('ground_mount', 'Ground Mount')
    ], string='Rooftop Type', default='rcc_flat')

    roof_direction = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('north_east', 'North-East'),
        ('north_west', 'North-West'),
        ('south_east', 'South-East'),
        ('south_west', 'South-West'),
        ('flat', 'Flat / No Direction'),
    ], string='Roof Direction')

    azimuth_degrees = fields.Float(string='Azimuth (°)', help='True South = 180°')
    tilt_degrees = fields.Float(string='Optimal Tilt (°)', default=15.0)
    shading_factor_pct = fields.Float(string='Shading Factor (%)', default=0.0)

    usable_area_sqft = fields.Float(string='Usable Rooftop Area (sq.ft)')
    cable_distance = fields.Float(
        string='Cable Distance (ft)',
        help='Distance from the rooftop array to the main distribution panel.',
    )
    sanctioned_load_kw = fields.Float(string='Sanctioned Grid Load (kW)')
    meter_phase = fields.Selection([
        ('single_phase', 'Single Phase (230V)'),
        ('three_phase', 'Three Phase (415V)')
    ], string='Utility Meter Phase', default='single_phase')
    grid_suitability = fields.Selection([
        ('not_assessed', 'Not Assessed'),
        ('suitable', 'Suitable'),
        ('not_suitable', 'Not Suitable'),
    ], string='Grid Suitability', default='not_assessed', tracking=True)
    recommended_system_capacity_kw = fields.Float(string='Recommended System Capacity (kW)')

    electricity_bill_attachment_ids = fields.Many2many(
        'ir.attachment', 'sunflow_core_survey_electricity_bill_rel',
        'survey_id', 'attachment_id',
        string='Electricity Bill Attachments',
    )
    site_photo_attachment_ids = fields.Many2many(
        'ir.attachment', 'sunflow_core_survey_site_photo_rel',
        'survey_id', 'attachment_id',
        string='Site Photo Attachments',
    )
    document_attachment_ids = fields.Many2many(
        'ir.attachment', 'sunflow_core_survey_document_rel',
        'survey_id', 'attachment_id',
        string='Document Attachments',
    )

    survey_notes = fields.Text(string='Technical Observations')
    technician_observations = fields.Text(string='Technician Observations')
    approval_remarks = fields.Text(string='Approval / Rejection Remarks')

    approved_by = fields.Many2one(
        'res.users', string='Approved By', readonly=True, copy=False)
    approved_date = fields.Datetime(
        string='Approved Date', readonly=True, copy=False)
    rejected_by = fields.Many2one(
        'res.users', string='Rejected By', readonly=True, copy=False)
    rejected_date = fields.Datetime(
        string='Rejected Date', readonly=True, copy=False)

    _TRANSITIONS = {
        'draft': ['scheduled'],
        'scheduled': ['in_progress'],
        'in_progress': ['submitted'],
        'submitted': ['approved', 'rejected'],
        'approved': ['draft'],
        'rejected': ['draft'],
    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                sequence = self.env['ir.sequence'].next_by_code('sunflow_core.site_survey')
                vals['name'] = sequence or _('New')
        records = super().create(vals_list)
        for rec in records:
            rec._sync_attachment_links()
        return records

    def write(self, vals):
        result = super().write(vals)
        attachment_fields = (
            'electricity_bill_attachment_ids',
            'site_photo_attachment_ids',
            'document_attachment_ids',
        )
        if any(field in vals for field in attachment_fields):
            for rec in self:
                rec._sync_attachment_links()
        return result

    def _sync_attachment_links(self):
        for rec in self:
            for field_name in (
                'electricity_bill_attachment_ids',
                'site_photo_attachment_ids',
                'document_attachment_ids',
            ):
                attachments = rec[field_name]
                if attachments:
                    attachments.write({
                        'res_model': 'solar.survey',
                        'res_id': rec.id,
                    })

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.lead_id = self.project_id.lead_id

    @api.constrains('lead_id', 'project_id')
    def _check_lead_project_consistency(self):
        for rec in self:
            if (rec.project_id and rec.project_id.lead_id
                    and rec.lead_id and rec.lead_id.id != rec.project_id.lead_id.id):
                raise ValidationError(_(
                    "The survey CRM lead must match the source CRM lead of the linked solar project."))

    @api.constrains('tilt_degrees')
    def _check_tilt_range(self):
        for rec in self:
            if rec.tilt_degrees is not None and (rec.tilt_degrees < 0 or rec.tilt_degrees > 90):
                raise ValidationError(_("Tilt angle must be between 0 and 90 degrees."))

    @api.constrains('azimuth_degrees')
    def _check_azimuth_range(self):
        for rec in self:
            if rec.azimuth_degrees is not None and (rec.azimuth_degrees < 0 or rec.azimuth_degrees > 360):
                raise ValidationError(_("Azimuth must be between 0 and 360 degrees."))

    @api.constrains('shading_factor_pct')
    def _check_shading_range(self):
        for rec in self:
            if rec.shading_factor_pct is not None and (rec.shading_factor_pct < 0 or rec.shading_factor_pct > 100):
                raise ValidationError(_("Shading factor must be between 0 and 100 percent."))

    @api.constrains('usable_area_sqft')
    def _check_usable_area_non_negative(self):
        for rec in self:
            if rec.usable_area_sqft is not None and rec.usable_area_sqft < 0:
                raise ValidationError(_("Usable rooftop area cannot be negative."))

    @api.constrains('cable_distance')
    def _check_cable_distance_non_negative(self):
        for rec in self:
            if rec.cable_distance is not None and rec.cable_distance < 0:
                raise ValidationError(_("Cable distance cannot be negative."))

    @api.constrains('sanctioned_load_kw')
    def _check_sanctioned_load_non_negative(self):
        for rec in self:
            if rec.sanctioned_load_kw is not None and rec.sanctioned_load_kw < 0:
                raise ValidationError(_("Sanctioned grid load cannot be negative."))

    @api.constrains('recommended_system_capacity_kw')
    def _check_recommended_capacity_non_negative(self):
        for rec in self:
            if rec.recommended_system_capacity_kw is not None and rec.recommended_system_capacity_kw < 0:
                raise ValidationError(_("Recommended system capacity cannot be negative."))

    @api.constrains('state', 'roof_type', 'tilt_degrees', 'usable_area_sqft',
                    'sanctioned_load_kw', 'meter_phase')
    def _check_submission_requirements(self):
        for rec in self:
            if rec.state == 'submitted':
                missing = []
                if not rec.roof_type:
                    missing.append(_('Rooftop Type'))
                if not rec.tilt_degrees:
                    missing.append(_('Optimal Tilt'))
                if not rec.usable_area_sqft:
                    missing.append(_('Usable Rooftop Area'))
                if not rec.sanctioned_load_kw:
                    missing.append(_('Sanctioned Grid Load'))
                if not rec.meter_phase:
                    missing.append(_('Meter Phase'))
                if missing:
                    raise ValidationError(_(
                        "Survey cannot be submitted. Missing required information: %s") % ', '.join(missing))

    def _validate_transition(self, new_state):
        for rec in self:
            allowed = self._TRANSITIONS.get(rec.state, [])
            if new_state not in allowed:
                raise ValidationError(_(
                    "Invalid workflow transition from '%s' to '%s' for survey %s."
                ) % (rec.state, new_state, rec.name))

    def _check_manager_rights(self):
        for rec in self:
            if not self.env.user.has_group('base.group_system'):
                raise ValidationError(_(
                    "Resetting an approved or rejected survey is restricted to an authorized manager."))

    def action_schedule(self):
        self._validate_transition('scheduled')
        self.write({'state': 'scheduled'})

    def action_start(self):
        self._validate_transition('in_progress')
        self.write({'state': 'in_progress'})

    def action_submit(self):
        for rec in self:
            rec._validate_transition('submitted')
            missing = []
            if not rec.roof_type:
                missing.append(_('Rooftop Type'))
            if not rec.tilt_degrees:
                missing.append(_('Optimal Tilt'))
            if not rec.usable_area_sqft:
                missing.append(_('Usable Rooftop Area'))
            if not rec.sanctioned_load_kw:
                missing.append(_('Sanctioned Grid Load'))
            if not rec.meter_phase:
                missing.append(_('Meter Phase'))
            if missing:
                raise ValidationError(_(
                    "Survey cannot be submitted. Missing required information: %s") % ', '.join(missing))
        self.write({'state': 'submitted'})

    def action_approve(self):
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only an authorized manager may approve surveys."))
        for rec in self:
            rec._validate_transition('approved')
            if rec.surveyor_id and rec.surveyor_id == self.env.user:
                raise ValidationError(_(
                    "A surveyor cannot approve their own survey."))
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })

    def action_reject(self, remarks=''):
        if not self.env.user.has_group('base.group_system'):
            raise AccessError(_("Only an authorized manager may reject surveys."))
        for rec in self:
            rec._validate_transition('rejected')
            if rec.surveyor_id and rec.surveyor_id == self.env.user:
                raise ValidationError(_(
                    "A surveyor cannot reject their own survey."))
            if not remarks:
                raise ValidationError(_("Rejection remarks are required."))
        self.write({
            'state': 'rejected',
            'approval_remarks': remarks,
            'rejected_by': self.env.user.id,
            'rejected_date': fields.Datetime.now(),
        })

    def action_reset_draft(self):
        self._check_manager_rights()
        for rec in self:
            rec._validate_transition('draft')
        self.write({'state': 'draft'})
