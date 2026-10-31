# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_solar_customer = fields.Boolean(
        string="Is Solar Customer",
        default=False,
        index=True,
        help="Indicates whether this partner is a prospective or active rooftop solar customer."
    )
    solar_lead_ids = fields.One2many(
        'crm.lead',
        'partner_id',
        string="Solar Inquiries",
        readonly=True,
        help="All rooftop solar inquiries, feasibility evaluations, and opportunities associated with this customer."
    )
    solar_lead_count = fields.Integer(
        string="Solar Inquiries Count",
        compute='_compute_solar_lead_count',
        help="Total number of solar inquiries associated with this customer record."
    )

    @api.depends('solar_lead_ids')
    def _compute_solar_lead_count(self):
        for partner in self:
            partner.solar_lead_count = len(partner.solar_lead_ids)

    def action_view_solar_leads(self):
        """Open the list of solar leads/inquiries linked to this customer."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("solar_management.action_solar_leads")
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {
            'default_partner_id': self.id,
        }
        return action
