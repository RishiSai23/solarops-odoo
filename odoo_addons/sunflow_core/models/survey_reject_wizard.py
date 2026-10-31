# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SurveyRejectWizard(models.TransientModel):
    _name = 'solar.survey.reject.wizard'
    _description = 'Reject Site Survey'

    survey_id = fields.Many2one(
        'solar.survey',
        string='Survey',
        required=True,
        readonly=True,
    )
    remarks = fields.Text(
        string='Rejection Remarks',
        required=True,
        help='Enter the reason for rejecting this survey. These remarks are stored on the survey record.',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        if active_model == 'solar.survey' and active_id:
            res['survey_id'] = active_id
        return res

    def action_reject_confirm(self):
        self.ensure_one()
        if not self.survey_id:
            raise ValidationError(_("No survey reference provided."))
        if self.survey_id.state != 'submitted':
            raise ValidationError(_("Only a submitted survey can be rejected."))
        if self.survey_id.surveyor_id and self.survey_id.surveyor_id == self.env.user:
            raise ValidationError(_("A surveyor cannot reject their own survey."))
        if not self.remarks:
            raise ValidationError(_("Rejection remarks are required."))
        self.survey_id.action_reject(self.remarks)
        return {'type': 'ir.actions.act_window_close'}
