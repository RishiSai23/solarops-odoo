# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestSurveyLifecycleIntegration(TransactionCase):
    """
    Test suite for Site Survey approval and Project Lifecycle integration.
    Verifies:
      - Automatic transition: Lead -> Survey on survey creation
      - Automatic transition: Survey -> Feasibility on survey feasibility update
      - Draft surveys cannot authorize quotation generation
      - Not Feasible (rejected) surveys cannot authorize quotation generation
      - Conditional surveys move to Feasibility Review and require resolution
      - Feasible & Approved surveys satisfy quotation prerequisite
      - Technical grid compatibility (sanctioned load >= system capacity)
      - Multiple surveys resolution without ambiguity
      - Later rejected survey does not silently invalidate an approved survey
      - Quotation creation and sales order linkage
    """

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Green Villa Solar Customer',
            'email': 'customer@greenvilla.com',
            'phone': '+91 98765 43210',
        })
        self.project = self.env['solar.project'].create({
            'partner_id': self.partner.id,
            'kw_capacity': 5.0,
            'system_type': 'on_grid',
            'stage': 'lead',
        })

    def test_01_survey_creation_advances_stage_to_survey(self):
        """Creating a survey on a 'lead' project automatically transitions it to 'survey'."""
        self.assertEqual(self.project.stage, 'lead')
        survey = self.env['solar.survey'].create({
            'name': 'SURV-001-DRAFT',
            'project_id': self.project.id,
            'roof_type': 'rcc_flat',
            'usable_area_sqft': 1000.0,
            'sanctioned_load_kw': 10.0,
            'feasibility_status': 'draft',
        })
        self.assertEqual(self.project.stage, 'survey')
        self.assertEqual(self.project.feasibility_status, 'pending')
        self.assertFalse(self.project.approved_survey_id)

    def test_02_draft_survey_cannot_authorize_quotation(self):
        """Draft surveys cannot authorize advancing to quotation or creating quotations."""
        self.env['solar.survey'].create({
            'name': 'SURV-002-DRAFT',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'draft',
        })
        with self.assertRaises(UserError):
            self.project.action_approve_feasibility()
        with self.assertRaises(UserError):
            self.project.action_create_quotation()
        self.assertIn(self.project.stage, ('lead', 'survey'))

    def test_03_rejected_survey_cannot_authorize_quotation(self):
        """Not Feasible (rejected) surveys cannot authorize quotation generation."""
        survey = self.env['solar.survey'].create({
            'name': 'SURV-003-REJ',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'rejected',
        })
        self.assertEqual(self.project.feasibility_status, 'rejected')
        with self.assertRaises(UserError):
            self.project.action_approve_feasibility()

    def test_04_conditional_survey_moves_to_feasibility_review(self):
        """Conditional survey transitions project to Feasibility Review and blocks quotation."""
        survey = self.env['solar.survey'].create({
            'name': 'SURV-004-COND',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'conditional',
        })
        self.assertEqual(self.project.stage, 'feasibility')
        self.assertEqual(self.project.feasibility_status, 'conditional')
        with self.assertRaises(UserError):
            self.project.action_approve_feasibility()

    def test_05_feasible_survey_advances_to_feasibility_and_approves_to_quotation(self):
        """Feasible survey advances project to feasibility, and action_approve_feasibility advances to quotation."""
        survey = self.env['solar.survey'].create({
            'name': 'SURV-005-OK',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,  # 12 kW grid load >= 5 kW capacity
            'usable_area_sqft': 1500.0,
            'feasibility_status': 'feasible',
        })
        self.assertEqual(self.project.stage, 'feasibility')
        self.assertEqual(self.project.feasibility_status, 'feasible')
        self.assertEqual(self.project.approved_survey_id, survey)

        # Advance to Quotation
        res = self.project.action_approve_feasibility()
        self.assertTrue(res)
        self.assertEqual(self.project.stage, 'quotation')

    def test_06_technical_compatibility_load_exceeded_raises_validation_error(self):
        """If project capacity exceeds sanctioned load, survey cannot be marked 'feasible' as-is."""
        self.project.kw_capacity = 15.0  # 15 kW system
        with self.assertRaises(ValidationError):
            self.env['solar.survey'].create({
                'name': 'SURV-006-OVERLOAD',
                'project_id': self.project.id,
                'sanctioned_load_kw': 5.0,  # Only 5 kW grid connection
                'feasibility_status': 'feasible',
            })

    def test_07_technical_compatibility_load_compatible_passes(self):
        """If project capacity <= sanctioned load (e.g. 5 kW on 12 kW grid), validation passes."""
        self.project.kw_capacity = 5.0
        survey = self.env['solar.survey'].create({
            'name': 'SURV-007-COMPATIBLE',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,  # 12 kW >= 5 kW
            'feasibility_status': 'feasible',
        })
        self.assertEqual(survey.feasibility_status, 'feasible')
        self.assertEqual(self.project.feasibility_status, 'feasible')

    def test_08_multiple_surveys_no_ambiguity(self):
        """Multiple surveys correctly resolve to the approved feasible survey."""
        s1 = self.env['solar.survey'].create({
            'name': 'SURV-008-S1',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'conditional',
        })
        self.assertEqual(self.project.feasibility_status, 'conditional')

        s2 = self.env['solar.survey'].create({
            'name': 'SURV-008-S2',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'feasible',
        })
        self.assertEqual(self.project.feasibility_status, 'feasible')
        self.assertEqual(self.project.approved_survey_id, s2)

    def test_09_later_rejected_survey_does_not_overwrite_approved_survey(self):
        """A later rejected survey does NOT silently invalidate an existing approved survey."""
        s_approved = self.env['solar.survey'].create({
            'name': 'SURV-009-APPROVED',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'feasible',
        })
        self.assertEqual(self.project.feasibility_status, 'feasible')
        self.assertEqual(self.project.approved_survey_id, s_approved)

        # Create a second survey that is rejected
        s_rejected = self.env['solar.survey'].create({
            'name': 'SURV-009-REJECTED',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'rejected',
        })
        # The project must still have feasibility_status == 'feasible' and approved_survey_id == s_approved
        self.assertEqual(self.project.feasibility_status, 'feasible')
        self.assertEqual(self.project.approved_survey_id, s_approved)

    def test_10_quotation_creation_creates_and_links_sale_order(self):
        """action_create_quotation creates a sale.order and transitions stage to 'quotation'."""
        self.env['solar.survey'].create({
            'name': 'SURV-010-OK',
            'project_id': self.project.id,
            'sanctioned_load_kw': 12.0,
            'feasibility_status': 'feasible',
        })
        action = self.project.action_create_quotation()
        self.assertEqual(self.project.stage, 'quotation')
        self.assertTrue(self.project.sale_order_id)
        self.assertEqual(self.project.sale_order_id.partner_id, self.partner)
        self.assertEqual(action['res_id'], self.project.sale_order_id.id)

