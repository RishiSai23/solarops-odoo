# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # --- Solar Reference & Intake ---
    solar_lead_ref = fields.Char(
        string="Solar Lead Reference",
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: _('New'),
        help="Unique auto-generated reference number for this solar inquiry."
    )
    solar_lead_source = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('phone', 'Phone Call'),
        ('website', 'Website'),
        ('manual', 'Manual Entry'),
        ('other', 'Other'),
    ], string="Solar Lead Source", default='manual', tracking=True,
       help="Channel or medium through which the solar customer inquiry originated.")

    # --- Electricity & Consumption Profile ---
    monthly_bill_amount = fields.Monetary(
        string="Monthly Electricity Bill",
        currency_field="company_currency",
        tracking=True,
        help="Average monthly electricity bill amount paid by the customer to their utility."
    )
    avg_monthly_consumption_kwh = fields.Float(
        string="Monthly Consumption (kWh)",
        digits=(10, 2),
        tracking=True,
        help="Average monthly power consumption in kilowatt-hours (units) from electricity bills."
    )

    # --- Rooftop & Site Pre-Qualification ---
    roof_area_sqft = fields.Float(
        string="Available Roof Area (sq. ft.)",
        digits=(10, 2),
        tracking=True,
        help="Estimated usable shadow-free rooftop surface area in square feet."
    )
    roof_ownership = fields.Selection([
        ('owned', 'Self-Owned'),
        ('rented_noc', 'Rented (Owner NOC Obtained)'),
        ('rented_pending_noc', 'Rented (NOC Pending)'),
        ('shared', 'Shared / Society Rooftop'),
    ], string="Roof Ownership / NOC Status", default='owned', tracking=True,
       help="Roof ownership status or availability of landlord/society No-Objection Certificate.")
    roof_suitability = fields.Selection([
        ('suitable', 'Suitable (Unshaded & Structurally Sound)'),
        ('partially_shaded', 'Partially Shaded'),
        ('shaded', 'Heavily Shaded / Unsuitable'),
        ('structural_risk', 'Structural Repair Required'),
        ('pending_inspection', 'Pending Survey / Unverified'),
    ], string="Roof Feasibility Pre-Check", default='pending_inspection', tracking=True,
       help="Preliminary feasibility assessment of shading obstructions and roof structural integrity.")
    grid_connectivity = fields.Selection([
        ('connected_stable', 'Grid Connected (Stable Utility Power)'),
        ('connected_unstable', 'Grid Connected (Frequent Outages)'),
        ('off_grid', 'Off-Grid Area (No Grid Line)'),
    ], string="Grid Connectivity", default='connected_stable', tracking=True,
       help="Status and reliability of public electricity grid connection at customer location.")

    # --- Solar System Sizing Preferences ---
    solar_system_type = fields.Selection([
        ('on_grid', 'On-Grid (Grid-Tied / Net Metering)'),
        ('off_grid', 'Off-Grid (Battery Storage System)'),
        ('hybrid', 'Hybrid (Grid-Tied + Battery Backup)'),
    ], string="Preferred Solar System", default='on_grid', tracking=True,
       help="Customer-requested solar architecture: On-Grid, Off-Grid, or Hybrid.")
    expected_capacity_kw = fields.Float(
        string="Expected Capacity (kW)",
        digits=(6, 2),
        tracking=True,
        help="Desired or estimated preliminary solar plant capacity in kilowatts."
    )
    solar_remarks = fields.Text(
        string="Customer Requirements & Remarks",
        help="Customer-specific preferences, power backup needs, budgetary considerations, or site constraints."
    )

    # --- Qualification Workflow & State Management ---
    solar_qualification_status = fields.Selection([
        ('not_evaluated', 'Not Evaluated'),
        ('needs_info', 'Needs More Information'),
        ('qualified', 'Qualified'),
        ('not_suitable', 'Not Suitable'),
    ], string="Solar Qualification Status", default='not_evaluated', required=True, tracking=True, copy=False,
       help="Formal technical and commercial qualification state of the inquiry.")
    qualification_notes = fields.Text(
        string="Qualification Notes / Reason",
        tracking=True,
        help="Detailed notes explaining qualification outcome, missing data items, or rejection grounds."
    )
    qualification_date = fields.Datetime(
        string="Qualification Date",
        readonly=True,
        copy=False,
        help="Date and time when lead was officially qualified or evaluated."
    )
    qualified_user_id = fields.Many2one(
        'res.users',
        string="Qualified By",
        readonly=True,
        copy=False,
        help="Sales engineer or solar specialist who evaluated this inquiry."
    )
    is_survey_ready = fields.Boolean(
        string="Survey Ready",
        tracking=True,
        copy=False,
        help="Flag indicating this lead satisfies technical pre-qualification and is ready for site survey dispatch."
    )
    is_solar_converted = fields.Boolean(
        string="Converted to Solar Customer",
        tracking=True,
        copy=False,
        readonly=True,
        help="Set to True once this lead has been converted to a Solar Customer via the SolarOps workflow. "
             "Prevents duplicate conversions."
    )

    # -------------------------------------------------------------------------
    # DISPLAY NAME & SEQUENCE GENERATION
    # -------------------------------------------------------------------------

    @api.depends('solar_lead_ref', 'name')
    def _compute_display_name(self):
        super()._compute_display_name()
        for lead in self:
            if lead.solar_lead_ref and lead.solar_lead_ref != _('New'):
                lead.display_name = f"[{lead.solar_lead_ref}] {lead.name or ''}"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('solar_lead_ref') or vals.get('solar_lead_ref') == _('New'):
                vals['solar_lead_ref'] = self.env['ir.sequence'].next_by_code('solar.lead') or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # ORM VALIDATION CONSTRAINTS
    # -------------------------------------------------------------------------

    @api.constrains('monthly_bill_amount', 'avg_monthly_consumption_kwh', 'roof_area_sqft', 'expected_capacity_kw')
    def _check_solar_numerical_values(self):
        for record in self:
            if record.monthly_bill_amount < 0:
                raise ValidationError(_("Monthly electricity bill amount cannot be negative."))
            if record.avg_monthly_consumption_kwh < 0:
                raise ValidationError(_("Average monthly electricity consumption cannot be negative."))
            if record.roof_area_sqft < 0:
                raise ValidationError(_("Available roof area cannot be negative."))
            if record.expected_capacity_kw < 0:
                raise ValidationError(_("Expected solar capacity cannot be negative."))

    # -------------------------------------------------------------------------
    # BUSINESS WORKFLOW ACTIONS
    # -------------------------------------------------------------------------

    def action_qualify_lead(self):
        """Evaluate customer contact and site pre-requisites to qualify the lead."""
        for record in self:
            # 1. Contact information validation
            has_name = bool(record.partner_id or record.contact_name or record.name)
            has_contact = bool(record.phone or record.mobile or record.email_from)
            if not has_name or not has_contact:
                raise UserError(_(
                    "Cannot qualify lead '%s': Basic customer contact details (Name and Phone/Mobile or Email) "
                    "must be provided before qualification."
                ) % record.name)

            # 2. Solar energy requirements validation
            if record.monthly_bill_amount <= 0 and record.avg_monthly_consumption_kwh <= 0:
                raise UserError(_(
                    "Cannot qualify lead '%s': Please provide either the monthly electricity bill amount "
                    "or average monthly consumption (kWh) to determine system sizing."
                ) % record.name)

            # 3. Rooftop space validation
            if record.roof_area_sqft <= 0:
                raise UserError(_(
                    "Cannot qualify lead '%s': Available roof area must be specified and greater than 0 sq. ft."
                ) % record.name)

            # 4. Roof suitability checks
            if record.roof_suitability == 'shaded':
                raise UserError(_(
                    "Cannot qualify lead '%s': A rooftop evaluated as 'Heavily Shaded / Unsuitable' cannot be "
                    "marked as Qualified. Please reject the lead using 'Mark Not Suitable' or adjust feasibility."
                ) % record.name)

            if record.roof_suitability == 'structural_risk':
                raise UserError(_(
                    "Cannot qualify lead '%s': The rooftop requires structural repair. "
                    "Please set status to 'Needs More Information' until structural feasibility is addressed."
                ) % record.name)

            if record.roof_ownership == 'rented_pending_noc':
                raise UserError(_(
                    "Cannot qualify lead '%s': Tenant installation requires landlord NOC. "
                    "Please set status to 'Needs More Information' until NOC is confirmed."
                ) % record.name)

            # Mark Qualified
            record.write({
                'solar_qualification_status': 'qualified',
                'qualification_date': fields.Datetime.now(),
                'qualified_user_id': self.env.user.id,
            })

            # Update stage if 'Qualified' stage exists
            qualified_stage = self.env['crm.stage'].search([('name', 'ilike', 'Qualified')], limit=1)
            if qualified_stage:
                record.write({'stage_id': qualified_stage.id})

            record.message_post(
                body=_("<b>Solar Lead Pre-Qualified</b> by %s.<br/>"
                       "Monthly Bill: %s %s | Consumption: %s kWh | Roof Area: %s sq. ft. | Sizing: %s kW (%s)") % (
                    self.env.user.name,
                    record.company_currency.symbol or '',
                    record.monthly_bill_amount,
                    record.avg_monthly_consumption_kwh,
                    record.roof_area_sqft,
                    record.expected_capacity_kw or 'TBD',
                    dict(record._fields['solar_system_type'].selection).get(record.solar_system_type),
                ),
                subtype_xmlid="mail.mt_note",
            )
        return True

    def action_needs_more_info(self, notes=None):
        """Set lead qualification status to Needs More Information."""
        for record in self:
            if notes:
                record.qualification_notes = notes
            elif not record.qualification_notes:
                # Open wizard to capture missing information reason
                return {
                    'name': _('Specify Missing Information Needed'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'solar.lead.reason.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_lead_id': record.id,
                        'default_action_type': 'needs_info',
                    }
                }

            record.write({
                'solar_qualification_status': 'needs_info',
                'is_survey_ready': False,
            })

            # Move to Qualification Pending stage if present
            pending_stage = self.env['crm.stage'].search([('name', 'ilike', 'Qualification Pending')], limit=1)
            if pending_stage:
                record.write({'stage_id': pending_stage.id})

            record.message_post(
                body=_("Lead status set to <b>Needs More Information</b>.<br/><b>Checklist / Missing Details:</b><br/>%s") % (
                    record.qualification_notes or 'Not specified'
                ),
                subtype_xmlid="mail.mt_note",
            )
        return True

    def action_mark_not_suitable(self, reason=None):
        """Mark lead as Not Suitable for rooftop solar installation."""
        for record in self:
            if reason:
                record.qualification_notes = reason
            elif not record.qualification_notes:
                # Open wizard to capture rejection reason
                return {
                    'name': _('Reason for Rejection / Not Suitable'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'solar.lead.reason.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_lead_id': record.id,
                        'default_action_type': 'not_suitable',
                    }
                }

            record.write({
                'solar_qualification_status': 'not_suitable',
                'is_survey_ready': False,
            })

            record.message_post(
                body=_("Lead marked as <b>Not Suitable</b> for solar installation.<br/><b>Reason:</b><br/>%s") % (
                    record.qualification_notes or 'Not specified'
                ),
                subtype_xmlid="mail.mt_note",
            )
        return True

    def action_reset_qualification(self):
        """Reset qualification to Not Evaluated to allow re-assessment."""
        for record in self:
            record.write({
                'solar_qualification_status': 'not_evaluated',
                'is_survey_ready': False,
                'qualification_date': False,
                'qualified_user_id': False,
            })
            record.message_post(
                body=_("Solar qualification status has been reset to <b>Not Evaluated</b> for re-evaluation."),
                subtype_xmlid="mail.mt_note",
            )
        return True

    def action_mark_survey_ready(self):
        """Mark the qualified lead as ready for a technical rooftop survey."""
        for record in self:
            if record.solar_qualification_status != 'qualified':
                raise UserError(_(
                    "Only leads with 'Qualified' status can be marked as Survey Ready. "
                    "Current status is '%s'."
                ) % dict(record._fields['solar_qualification_status'].selection).get(record.solar_qualification_status))

            # Validate that physical location address is captured
            has_address = bool(
                record.street or record.city or
                (record.partner_id and (record.partner_id.street or record.partner_id.city))
            )
            if not has_address:
                raise UserError(_(
                    "Cannot mark as Survey Ready: Site address (Street/City) is required to dispatch "
                    "a rooftop survey engineer."
                ))

            record.write({'is_survey_ready': True})

            survey_stage = self.env['crm.stage'].search([('name', 'ilike', 'Survey Ready')], limit=1)
            if survey_stage:
                record.write({'stage_id': survey_stage.id})

            record.message_post(
                body=_("Lead marked as <b>Survey Ready</b>. Technical rooftop site survey can now be scheduled."),
                subtype_xmlid="mail.mt_note",
            )
        return True

    def action_solar_convert_to_customer(self):
        """Convert a qualified lead into a Solar Customer (res.partner), avoiding duplicate partner creation."""
        self.ensure_one()

        if self.is_solar_converted:
            raise UserError(_(
                "This lead has already been converted to a Solar Customer. "
                "The linked customer record is: %s."
            ) % (self.partner_id.display_name if self.partner_id else _('Unknown')))

        if self.solar_qualification_status != 'qualified':
            raise UserError(_(
                "Cannot convert to Solar Customer: Only leads with 'Qualified' status are eligible "
                "for customer conversion through the SolarOps workflow."
            ))

        partner = self.partner_id
        if not partner:
            # Duplicate prevention check based on email or phone
            domain = []
            if self.email_from:
                domain.append(('email', '=ilike', self.email_from.strip()))
            if self.mobile:
                domain.append(('mobile', '=', self.mobile.strip()))
            if self.phone:
                domain.append(('phone', '=', self.phone.strip()))

            if domain:
                or_domain = ['|'] * (len(domain) - 1) + domain if len(domain) > 1 else domain
                partner = self.env['res.partner'].search(or_domain, limit=1)

            if partner:
                self.partner_id = partner
                partner.write({'is_solar_customer': True})
                self.message_post(
                    body=_("Linked to existing customer: <b>%s</b> and marked as Solar Customer "
                           "(Duplicate partner creation prevented).") % partner.display_name,
                    subtype_xmlid="mail.mt_note",
                )
            else:
                customer_name = self.contact_name or self.partner_name or self.name
                partner_vals = {
                    'name': customer_name,
                    'is_company': bool(self.partner_name and not self.contact_name),
                    'email': self.email_from,
                    'phone': self.phone,
                    'mobile': self.mobile,
                    'street': self.street,
                    'street2': self.street2,
                    'city': self.city,
                    'state_id': self.state_id.id if self.state_id else False,
                    'zip': self.zip,
                    'country_id': self.country_id.id if self.country_id else False,
                    'is_solar_customer': True,
                    'user_id': self.user_id.id or self.env.uid,
                    'comment': self.solar_remarks or self.description,
                }
                partner = self.env['res.partner'].create(partner_vals)
                self.partner_id = partner
                self.message_post(
                    body=_("New Solar Customer profile created and linked: <b>%s</b>.") % partner.display_name,
                    subtype_xmlid="mail.mt_note",
                )
        else:
            # Partner already linked — mark as Solar Customer if not already
            if not partner.is_solar_customer:
                partner.write({'is_solar_customer': True})
                self.message_post(
                    body=_("Existing customer <b>%s</b> has been marked as a Solar Customer.") % partner.display_name,
                    subtype_xmlid="mail.mt_note",
                )
            else:
                self.message_post(
                    body=_("Customer <b>%s</b> is already a Solar Customer. Conversion recorded.") % partner.display_name,
                    subtype_xmlid="mail.mt_note",
                )

        # Update partner contact details from lead if missing on partner
        partner_updates = {}
        for lead_field, partner_field in [
            ('email_from', 'email'),
            ('phone', 'phone'),
            ('mobile', 'mobile'),
            ('street', 'street'),
            ('street2', 'street2'),
            ('city', 'city'),
            ('state_id', 'state_id'),
            ('zip', 'zip'),
            ('country_id', 'country_id'),
        ]:
            l_val = getattr(self, lead_field)
            p_val = getattr(partner, partner_field)
            if l_val and not p_val:
                partner_updates[partner_field] = l_val.id if hasattr(l_val, 'id') else l_val
        if partner_updates:
            partner.write(partner_updates)

        # If lead is of type 'lead', convert to opportunity
        if self.type == 'lead':
            self.convert_opportunity(partner, user_ids=self.user_id.ids, team_id=self.team_id.id)

        # Move to Converted / Opportunity stage if available
        converted_stage = self.env.ref('solar_management.stage_solar_converted', raise_if_not_found=False)
        if not converted_stage:
            converted_stage = self.env['crm.stage'].search([('name', 'ilike', 'Converted')], limit=1)
        if converted_stage:
            self.write({'stage_id': converted_stage.id})

        # Stamp the conversion state to prevent duplicate conversions
        self.write({'is_solar_converted': True})

        return {
            'type': 'ir.actions.act_window',
            'name': _('Solar Customer'),
            'res_model': 'res.partner',
            'res_id': partner.id,
            'view_mode': 'form',
            'target': 'current',
        }
