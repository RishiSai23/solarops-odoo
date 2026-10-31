# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

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

    feasibility_status = fields.Selection([
        ('pending', 'Pending Survey'),
        ('feasible', 'Feasible & Approved'),
        ('conditional', 'Conditional / Requires Review'),
        ('rejected', 'Not Feasible / Rejected')
    ], string='Technical Feasibility', compute='_compute_feasibility_status', store=True, tracking=True)

    approved_survey_id = fields.Many2one(
        'solar.survey',
        string='Approved Site Survey',
        compute='_compute_feasibility_status',
        store=True,
        tracking=True
    )
    survey_count = fields.Integer(
        string='# Surveys',
        compute='_compute_survey_count',
        store=True
    )

    assigned_technician_id = fields.Many2one('res.users', string='Lead Technician', tracking=True)
    installation_date = fields.Date(string='Scheduled Installation Date')
    completion_date = fields.Date(string='Actual Completion Date')

    @api.depends('contract_amount', 'actual_cost')
    def _compute_gross_margin(self):
        for rec in self:
            rec.gross_margin = rec.contract_amount - rec.actual_cost

    @api.depends('survey_ids')
    def _compute_survey_count(self):
        for rec in self:
            rec.survey_count = len(rec.survey_ids)

    @api.depends('survey_ids', 'survey_ids.feasibility_status')
    def _compute_feasibility_status(self):
        """
        Evaluate overall project feasibility from linked site surveys:
        - If any survey is 'feasible', project feasibility is 'feasible'
          and approved_survey_id points to the approved feasible survey.
        - A later rejected survey does NOT invalidate an existing approved survey.
        - If no feasible survey exists but conditional exists: 'conditional'.
        - If all surveys are rejected: 'rejected'.
        - Otherwise 'pending'.
        """
        for project in self:
            surveys = project.survey_ids
            if not surveys:
                project.feasibility_status = 'pending'
                project.approved_survey_id = False
                continue

            feasible_surveys = surveys.filtered(lambda s: s.feasibility_status == 'feasible')
            if feasible_surveys:
                project.approved_survey_id = feasible_surveys[-1]
                project.feasibility_status = 'feasible'
            elif any(s.feasibility_status == 'conditional' for s in surveys):
                project.approved_survey_id = False
                project.feasibility_status = 'conditional'
            elif all(s.feasibility_status == 'rejected' for s in surveys):
                project.approved_survey_id = False
                project.feasibility_status = 'rejected'
            else:
                project.approved_survey_id = False
                project.feasibility_status = 'pending'

    def _sync_survey_feasibility(self):
        """
        Synchronize project lifecycle stage with survey creation and feasibility updates:
        - Moves 'lead' -> 'survey' when surveys exist.
        - Moves 'lead'/'survey' -> 'feasibility' when a survey is marked feasible or conditional.
        """
        for project in self:
            if not project.survey_ids:
                continue

            has_feasible = any(s.feasibility_status == 'feasible' for s in project.survey_ids)
            has_conditional = any(s.feasibility_status == 'conditional' for s in project.survey_ids)

            if (has_feasible or has_conditional) and project.stage in ('lead', 'survey'):
                project.write({'stage': 'feasibility'})
                status_desc = _('Feasible & Approved') if has_feasible else _('Conditional (Requires Review)')
                project.message_post(body=_(
                    "Site survey updated to <b>%s</b>. Project transitioned to Feasibility Review."
                ) % status_desc)
            elif project.stage == 'lead':
                project.write({'stage': 'survey'})
                project.message_post(body=_(
                    "Site survey linked. Project transitioned to Site Survey stage."
                ))

    def action_approve_feasibility(self):
        """
        Approve Feasibility Review and advance project to 'quotation'.
        Enforces Business Rules:
          - Prerequisite: At least one survey must be 'Feasible & Approved'.
          - Draft or Rejected surveys cannot authorize quotation generation.
          - Conditional surveys require resolution before progression.
          - Grid compatibility: Project kW capacity cannot exceed utility sanctioned load.
        """
        self.ensure_one()
        if self.feasibility_status != 'feasible':
            if self.feasibility_status == 'conditional':
                raise UserError(_(
                    "Cannot advance to Quotation: Site survey is 'Conditional / Requires Review'. "
                    "Technical obstacles must be resolved and approved before quotation generation."
                ))
            elif self.feasibility_status == 'rejected':
                raise UserError(_(
                    "Cannot advance to Quotation: Site survey feasibility was rejected. "
                    "Project cannot proceed with an unfeasible rooftop."
                ))
            else:
                raise UserError(_(
                    "Cannot advance to Quotation: No site survey has been marked 'Feasible & Approved' yet. "
                    "A completed and approved site survey is a mandatory prerequisite."
                ))

        approved_survey = self.approved_survey_id or self.survey_ids.filtered(lambda s: s.feasibility_status == 'feasible')[:1]
        if approved_survey and self.kw_capacity > 0 and approved_survey.sanctioned_load_kw > 0:
            if self.kw_capacity > approved_survey.sanctioned_load_kw:
                raise UserError(_(
                    "Technical Incompatibility: Proposed system capacity (%.2f kW) exceeds the utility "
                    "sanctioned load (%.2f kW). The customer must apply for a sanctioned load enhancement "
                    "or the system capacity must be reduced before quotation."
                ) % (self.kw_capacity, approved_survey.sanctioned_load_kw))

        self.write({'stage': 'quotation'})
        self.message_post(body=_(
            "Technical Feasibility Review approved (Survey: <b>%s</b>). Project advanced to Quotation & BOM."
        ) % (approved_survey.name if approved_survey else ''))
        return True

    def action_reject_feasibility(self):
        """Reject project feasibility and mark cancelled."""
        self.ensure_one()
        self.write({'stage': 'cancelled'})
        self.message_post(body=_("Project cancelled following feasibility review rejection."))
        return True

    def action_create_quotation(self):
        """
        Creates or navigates to a customer quotation for this project.
        Enforces survey feasibility prerequisite.
        """
        self.ensure_one()
        if self.stage in ('lead', 'survey'):
            raise UserError(_(
                "Cannot create quotation: Project has not completed Feasibility Review. "
                "An approved site survey is required before commercial proposal generation."
            ))
        if self.stage == 'feasibility':
            self.action_approve_feasibility()

        if self.sale_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Quotation'),
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

        order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
        })
        self.write({
            'sale_order_id': order.id,
            'stage': 'quotation',
        })
        self.message_post(body=_(
            "Quotation <b>%s</b> created and linked to project."
        ) % order.name)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Quotation'),
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.project') or _('SPF-%04d') % self.search_count([])
        return super().create(vals_list)
