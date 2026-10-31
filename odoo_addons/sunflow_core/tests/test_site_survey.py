# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError, AccessError, UserError


class TestSolarSurveyWorkflow(TransactionCase):
    """End-to-end tests for the solar.survey workflow and quotation integration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Survey = cls.env['solar.survey']
        cls.Project = cls.env['solar.project']
        cls.User = cls.env['res.users']
        cls.Partner = cls.env['res.partner']
        cls.Wizard = cls.env['solar.survey.reject.wizard']

        # Reference groups
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_system = cls.env.ref('base.group_system')
        cls.group_sale_salesman = cls.env.ref('sales_team.group_sale_salesman')

        # Create a customer partner
        cls.partner = cls.Partner.create({'name': 'Test Customer'})

        # Create a surveyor user (base.group_user only)
        cls.surveyor = cls.User.create({
            'name': 'Surveyor User',
            'login': 'surveyor_test',
            'groups_id': [(6, 0, [cls.group_user.id])],
        })

        # Create an approver/manager user (base.group_system implies group_user;
        # sales_team.group_sale_salesman is required to create sale.order records).
        cls.manager = cls.User.create({
            'name': 'Manager User',
            'login': 'manager_test',
            'groups_id': [(6, 0, [cls.group_system.id, cls.group_sale_salesman.id])],
        })

        # Create a solar project linked to the partner
        cls.project = cls.Project.create({
            'name': 'TEST-PROJ-001',
            'partner_id': cls.partner.id,
            'kw_capacity': 3.0,
            'system_type': 'on_grid',
            'stage': 'lead',
        })

    def _create_survey(self, state='draft', surveyor=None, **overrides):
        vals = {
            'name': 'SURV-TEST-001',
            'project_id': self.project.id,
            'surveyor_id': (surveyor or self.surveyor).id,
            'roof_type': 'rcc_flat',
            'tilt_degrees': 15.0,
            'usable_area_sqft': 500.0,
            'sanctioned_load_kw': 5.0,
            'meter_phase': 'single_phase',
            'state': state,
        }
        vals.update(overrides)
        return self.Survey.with_user(self.env.user).create(vals)

    # ------------------------------------------------------------------
    # Approval authorization
    # ------------------------------------------------------------------
    def test_ordinary_user_cannot_approve(self):
        survey = self._create_survey(state='submitted', surveyor=self.manager)
        with self.assertRaises(AccessError):
            survey.with_user(self.surveyor).action_approve()

    def test_manager_can_approve(self):
        survey = self._create_survey(state='submitted', surveyor=self.surveyor)
        survey.with_user(self.manager).action_approve()
        self.assertEqual(survey.state, 'approved')
        self.assertEqual(survey.approved_by.id, self.manager.id)
        self.assertIsNotNone(survey.approved_date)

    def test_surveyor_cannot_approve_own_survey(self):
        survey = self._create_survey(state='submitted', surveyor=self.surveyor)
        with self.assertRaises(AccessError):
            survey.with_user(self.surveyor).action_approve()

    def test_invalid_transition_blocked_on_approve(self):
        survey = self._create_survey(state='draft')
        with self.assertRaises(ValidationError):
            survey.with_user(self.manager).action_approve()

    # ------------------------------------------------------------------
    # Valid state transitions
    # ------------------------------------------------------------------
    def test_valid_transition_draft_to_scheduled(self):
        survey = self._create_survey(state='draft')
        survey.action_schedule()
        self.assertEqual(survey.state, 'scheduled')

    def test_valid_transition_scheduled_to_in_progress(self):
        survey = self._create_survey(state='scheduled')
        survey.action_start()
        self.assertEqual(survey.state, 'in_progress')

    def test_valid_transition_in_progress_to_submitted(self):
        survey = self._create_survey(state='in_progress')
        survey.action_submit()
        self.assertEqual(survey.state, 'submitted')

    # ------------------------------------------------------------------
    # Rejection authorization
    # ------------------------------------------------------------------
    def test_ordinary_user_cannot_reject_another_survey(self):
        survey = self._create_survey(state='submitted', surveyor=self.manager)
        with self.assertRaises(AccessError):
            survey.with_user(self.surveyor).action_reject(remarks='Some remarks.')

    def test_surveyor_cannot_reject_own_survey(self):
        survey = self._create_survey(state='submitted', surveyor=self.surveyor)
        with self.assertRaises(AccessError):
            survey.with_user(self.surveyor).action_reject(remarks='Some remarks.')

    def test_manager_can_reject(self):
        survey = self._create_survey(state='submitted', surveyor=self.surveyor)
        survey.with_user(self.manager).action_reject(remarks='Not feasible.')
        self.assertEqual(survey.state, 'rejected')
        self.assertEqual(survey.approval_remarks, 'Not feasible.')
        self.assertEqual(survey.rejected_by.id, self.manager.id)
        self.assertIsNotNone(survey.rejected_date)

    def test_reject_requires_remarks(self):
        survey = self._create_survey(state='submitted')
        with self.assertRaises(ValidationError):
            survey.with_user(self.manager).action_reject(remarks='')

    def test_invalid_transition_blocked_on_reject(self):
        survey = self._create_survey(state='draft')
        with self.assertRaises(ValidationError):
            survey.with_user(self.manager).action_reject(remarks='Some remarks.')

    # ------------------------------------------------------------------
    # Submission mandatory validations
    # ------------------------------------------------------------------
    def test_submit_missing_required_fields(self):
        survey = self.Survey.with_user(self.env.user).create({
            'name': 'SURV-TEST-002',
            'project_id': self.project.id,
            'surveyor_id': self.surveyor.id,
            'state': 'in_progress',
        })
        with self.assertRaises(ValidationError):
            survey.action_submit()

    def test_submit_all_required_fields_ok(self):
        survey = self._create_survey(state='in_progress')
        survey.action_submit()
        self.assertEqual(survey.state, 'submitted')

    # ------------------------------------------------------------------
    # Approval / rejection history preservation
    # ------------------------------------------------------------------
    def test_approval_history_preserved(self):
        survey = self._create_survey(state='submitted')
        survey.with_user(self.manager).action_approve()
        self.assertEqual(survey.approved_by.id, self.manager.id)
        self.assertEqual(survey.state, 'approved')

    def test_rejection_history_preserved(self):
        survey = self._create_survey(state='submitted')
        survey.with_user(self.manager).action_reject(remarks='Rejection remarks test.')
        self.assertEqual(survey.approval_remarks, 'Rejection remarks test.')
        self.assertEqual(survey.rejected_by.id, self.manager.id)
        self.assertEqual(survey.state, 'rejected')

    # ------------------------------------------------------------------
    # Rejection wizard
    # ------------------------------------------------------------------
    def test_wizard_create_with_valid_survey(self):
        survey = self._create_survey(state='submitted')
        wizard = self.Wizard.with_user(self.manager).create({
            'survey_id': survey.id,
            'remarks': 'Test rejection remarks.',
        })
        self.assertEqual(wizard.survey_id.id, survey.id)
        self.assertEqual(wizard.remarks, 'Test rejection remarks.')

    def test_wizard_missing_remarks_rejected(self):
        survey = self._create_survey(state='submitted')
        form = Form(
            self.Wizard.with_user(self.manager).with_context(
                default_survey_id=survey.id
            )
        )
        # remarks intentionally not set; required field should reject save
        with self.assertRaises(AssertionError):
            form.save()

    def test_manager_can_reject_through_wizard(self):
        survey = self._create_survey(state='submitted', surveyor=self.surveyor)
        wizard = self.Wizard.with_user(self.manager).create({
            'survey_id': survey.id,
            'remarks': 'Rejected via wizard.',
        })
        wizard.action_reject_confirm()
        self.assertEqual(survey.state, 'rejected')
        self.assertEqual(survey.approval_remarks, 'Rejected via wizard.')
        self.assertEqual(survey.rejected_by.id, self.manager.id)

    def test_unauthorized_user_cannot_reject_through_wizard(self):
        survey = self._create_survey(state='submitted', surveyor=self.manager)
        wizard = self.Wizard.with_user(self.surveyor).create({
            'survey_id': survey.id,
            'remarks': 'Unauthorized rejection.',
        })
        with self.assertRaises(AccessError):
            wizard.action_reject_confirm()

    def test_wizard_reject_invalid_state(self):
        draft_survey = self._create_survey(state='draft')
        wizard = self.Wizard.with_user(self.manager).create({
            'survey_id': draft_survey.id,
            'remarks': 'Test.',
        })
        with self.assertRaises(ValidationError):
            wizard.action_reject_confirm()

    # ------------------------------------------------------------------
    # Reset to draft requires manager
    # ------------------------------------------------------------------
    def test_reset_draft_requires_manager(self):
        survey = self._create_survey(state='approved')
        with self.assertRaises(ValidationError):
            survey.with_user(self.surveyor).action_reset_draft()

    def test_reset_draft_permitted_for_manager(self):
        survey = self._create_survey(state='approved')
        survey.with_user(self.manager).action_reset_draft()
        self.assertEqual(survey.state, 'draft')

    # ------------------------------------------------------------------
    # Quotation integration (regression)
    # ------------------------------------------------------------------
    def test_quotation_blocked_when_no_survey(self):
        project = self.Project.create({
            'name': 'TEST-PROJ-NOSURVEY',
            'partner_id': self.partner.id,
            'stage': 'feasibility',
        })
        with self.assertRaises(UserError):
            project.with_user(self.manager).action_create_quotation()

    def test_quotation_blocked_when_survey_not_approved(self):
        self._create_survey(state='submitted', feasibility_status='feasible')
        with self.assertRaises(UserError):
            self.project.with_user(self.manager).action_create_quotation()

    def test_quotation_blocked_when_feasibility_not_feasible(self):
        self._create_survey(state='approved', feasibility_status='conditional')
        with self.assertRaises(UserError):
            self.project.with_user(self.manager).action_create_quotation()

    def test_quotation_blocked_when_state_approved_but_feasibility_rejected(self):
        self._create_survey(state='approved', feasibility_status='rejected')
        with self.assertRaises(UserError):
            self.project.with_user(self.manager).action_create_quotation()

    def test_quotation_permitted_when_approved_and_feasible(self):
        self._create_survey(state='approved', feasibility_status='feasible')
        result = self.project.with_user(self.manager).action_create_quotation()
        self.assertTrue(result)
        self.assertIsNotNone(self.project.sale_order_id)
        self.assertEqual(self.project.stage, 'quotation')

    def test_quotation_linked_to_correct_project(self):
        self._create_survey(state='approved', feasibility_status='feasible')
        self.project.with_user(self.manager).action_create_quotation()
        self.assertEqual(self.project.sale_order_id.partner_id.id, self.partner.id)
