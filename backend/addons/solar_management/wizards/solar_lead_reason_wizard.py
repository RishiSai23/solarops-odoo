# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SolarLeadReasonWizard(models.TransientModel):
    _name = 'solar.lead.reason.wizard'
    _description = 'Solar Lead Qualification Reason / Note Wizard'

    lead_id = fields.Many2one(
        'crm.lead',
        string="Solar Lead",
        required=True,
        ondelete='cascade',
        help="Solar inquiry being evaluated."
    )
    action_type = fields.Selection([
        ('needs_info', 'Needs More Information'),
        ('not_suitable', 'Not Suitable / Reject'),
    ], string="Action", required=True, default='needs_info')
    reason = fields.Text(
        string="Reason / Missing Information Details",
        required=True,
        help="Provide clear justification or checklist of missing requirements."
    )

    def action_confirm(self):
        """Apply the qualification outcome and record the reason on the lead."""
        self.ensure_one()
        if not self.reason or not self.reason.strip():
            raise UserError(_("Please provide detailed remarks or reasons."))

        if self.action_type == 'needs_info':
            self.lead_id.action_needs_more_info(notes=self.reason.strip())
        elif self.action_type == 'not_suitable':
            self.lead_id.action_mark_not_suitable(reason=self.reason.strip())

        return {'type': 'ir.actions.act_window_close'}
