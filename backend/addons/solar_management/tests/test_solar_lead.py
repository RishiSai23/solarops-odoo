# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError


@tagged('post_install', '-at_install')
class TestSolarLead(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lead_model = cls.env['crm.lead']
        cls.partner_model = cls.env['res.partner']

        # Pre-create test customer
        cls.test_partner = cls.partner_model.create({
            'name': 'Alpha Industries Ltd',
            'email': 'procurement@alphaindustries.test',
            'phone': '+15550100100',
            'street': '42 Industrial Park Road',
            'city': 'Metropolis',
        })

    # -------------------------------------------------------------------------
    # 1. Lead Creation & Auto-Sequence
    # -------------------------------------------------------------------------
    def test_01_lead_creation(self):
        """Test lead creation, initial states, and sequence auto-generation."""
        lead = self.lead_model.create({
            'name': 'Residential 5kW Inquiry - John Doe',
            'contact_name': 'John Doe',
            'email_from': 'john.doe@solarexample.test',
            'phone': '+15550199001',
            'street': '123 Sunshine Boulevard',
            'city': 'Sunnyvale',
            'solar_lead_source': 'whatsapp',
            'monthly_bill_amount': 3500.0,
            'avg_monthly_consumption_kwh': 320.0,
            'roof_area_sqft': 500.0,
            'solar_system_type': 'on_grid',
            'expected_capacity_kw': 5.0,
        })

        self.assertTrue(lead.solar_lead_ref, "Solar lead reference must be populated.")
        self.assertNotEqual(lead.solar_lead_ref, 'New', "Reference must not remain placeholder.")
        self.assertTrue(lead.solar_lead_ref.startswith('LEAD/'), "Reference should start with LEAD/ prefix.")
        self.assertEqual(lead.solar_qualification_status, 'not_evaluated', "Default qualification status must be not_evaluated.")
        self.assertFalse(lead.is_survey_ready, "Initial lead must not be marked survey ready.")
        self.assertEqual(lead.solar_lead_source, 'whatsapp')

    # -------------------------------------------------------------------------
    # 2. Solar Qualification Field Validation
    # -------------------------------------------------------------------------
    def test_02_solar_qualification_field_validation(self):
        """Test valid selection values and defaults for solar qualification fields."""
        lead = self.lead_model.create({
            'name': 'Commercial 50kW Feasibility',
            'contact_name': 'Factory Manager',
            'phone': '+15550188002',
            'solar_lead_source': 'website',
            'solar_system_type': 'hybrid',
            'roof_ownership': 'owned',
            'roof_suitability': 'suitable',
            'grid_connectivity': 'connected_stable',
        })

        self.assertEqual(lead.solar_system_type, 'hybrid')
        self.assertEqual(lead.roof_ownership, 'owned')
        self.assertEqual(lead.roof_suitability, 'suitable')
        self.assertEqual(lead.grid_connectivity, 'connected_stable')
        self.assertEqual(lead.solar_qualification_status, 'not_evaluated')

    # -------------------------------------------------------------------------
    # 3. Qualification With Complete Information
    # -------------------------------------------------------------------------
    def test_03_qualification_with_complete_information(self):
        """Test successful qualification when complete customer and rooftop data is provided."""
        lead = self.lead_model.create({
            'name': 'Rooftop Solar - Complete Info',
            'contact_name': 'Eleanor Vance',
            'phone': '+15550177003',
            'email_from': 'eleanor@solarexample.test',
            'street': '742 Evergreen Terrace',
            'city': 'Springfield',
            'monthly_bill_amount': 4800.0,
            'avg_monthly_consumption_kwh': 420.0,
            'roof_area_sqft': 650.0,
            'roof_ownership': 'owned',
            'roof_suitability': 'suitable',
            'solar_system_type': 'on_grid',
            'expected_capacity_kw': 6.0,
        })

        # Execute qualification action
        lead.action_qualify_lead()

        self.assertEqual(lead.solar_qualification_status, 'qualified')
        self.assertTrue(lead.qualification_date, "Qualification date must be set.")
        self.assertEqual(lead.qualified_user_id, self.env.user, "Qualifying user must be current user.")

    # -------------------------------------------------------------------------
    # 4. Qualification With Missing Information
    # -------------------------------------------------------------------------
    def test_04_qualification_with_missing_information(self):
        """Test that qualification fails with clear UserError when mandatory data is missing."""
        # Case A: Missing contact details
        lead_no_contact = self.lead_model.create({
            'name': 'Inquiry Without Phone or Email',
            'roof_area_sqft': 500.0,
            'monthly_bill_amount': 3000.0,
        })
        with self.assertRaises(UserError):
            lead_no_contact.action_qualify_lead()
        self.assertEqual(lead_no_contact.solar_qualification_status, 'not_evaluated')

        # Case B: Missing consumption and bill
        lead_no_energy = self.lead_model.create({
            'name': 'Inquiry Without Energy Data',
            'contact_name': 'Bob Smith',
            'phone': '+15550166004',
            'roof_area_sqft': 500.0,
            'monthly_bill_amount': 0.0,
            'avg_monthly_consumption_kwh': 0.0,
        })
        with self.assertRaises(UserError):
            lead_no_energy.action_qualify_lead()

        # Case C: Missing roof area
        lead_no_roof = self.lead_model.create({
            'name': 'Inquiry Without Roof Area',
            'contact_name': 'Bob Smith',
            'phone': '+15550166004',
            'monthly_bill_amount': 3500.0,
            'roof_area_sqft': 0.0,
        })
        with self.assertRaises(UserError):
            lead_no_roof.action_qualify_lead()

        # Case D: Heavily shaded roof (ineligible for qualification)
        lead_shaded = self.lead_model.create({
            'name': 'Shaded Roof Inquiry',
            'contact_name': 'Bob Smith',
            'phone': '+15550166004',
            'monthly_bill_amount': 3500.0,
            'roof_area_sqft': 400.0,
            'roof_suitability': 'shaded',
        })
        with self.assertRaises(UserError):
            lead_shaded.action_qualify_lead()

        # Case E: Tenant pending owner NOC
        lead_no_noc = self.lead_model.create({
            'name': 'Tenant Without NOC',
            'contact_name': 'Tenant User',
            'phone': '+15550166004',
            'monthly_bill_amount': 3500.0,
            'roof_area_sqft': 400.0,
            'roof_ownership': 'rented_pending_noc',
        })
        with self.assertRaises(UserError):
            lead_no_noc.action_qualify_lead()

    # -------------------------------------------------------------------------
    # 5. Needs More Information Outcome
    # -------------------------------------------------------------------------
    def test_05_needs_more_info_outcome(self):
        """Test marking lead as Needs More Information with recorded notes."""
        lead = self.lead_model.create({
            'name': 'Pending NOC Inquiry',
            'contact_name': 'Mark Tenant',
            'phone': '+15550155005',
            'monthly_bill_amount': 2500.0,
            'roof_area_sqft': 350.0,
            'qualification_notes': 'Awaiting signed society NOC from housing society committee.',
        })

        lead.action_needs_more_info()
        self.assertEqual(lead.solar_qualification_status, 'needs_info')
        self.assertFalse(lead.is_survey_ready)

    # -------------------------------------------------------------------------
    # 6. Not Suitable Outcome
    # -------------------------------------------------------------------------
    def test_06_not_suitable_outcome(self):
        """Test marking lead as Not Suitable with justification note."""
        lead = self.lead_model.create({
            'name': 'Forest Cabin Inquiry',
            'contact_name': 'Cabin Owner',
            'phone': '+15550144006',
            'qualification_notes': 'Property is surrounded by dense forest canopy with 95% permanent shadow.',
        })

        lead.action_mark_not_suitable()
        self.assertEqual(lead.solar_qualification_status, 'not_suitable')
        self.assertFalse(lead.is_survey_ready)

    # -------------------------------------------------------------------------
    # 7. Negative or Invalid Numerical Values Validation
    # -------------------------------------------------------------------------
    def test_07_negative_numerical_values(self):
        """Verify that ORM constraints prevent negative bill, consumption, area, and capacity."""
        lead = self.lead_model.create({
            'name': 'Constraint Test Lead',
            'contact_name': 'Test User',
            'phone': '+15550133007',
        })

        with self.assertRaises(ValidationError):
            lead.write({'monthly_bill_amount': -150.0})

        with self.assertRaises(ValidationError):
            lead.write({'avg_monthly_consumption_kwh': -25.0})

        with self.assertRaises(ValidationError):
            lead.write({'roof_area_sqft': -100.0})

        with self.assertRaises(ValidationError):
            lead.write({'expected_capacity_kw': -2.5})

    # -------------------------------------------------------------------------
    # 8. Qualified Lead Conversion
    # -------------------------------------------------------------------------
    def test_08_qualified_lead_conversion(self):
        """Test converting a qualified lead into a customer and opportunity."""
        lead = self.lead_model.create({
            'name': 'Residential 8kW Installation',
            'contact_name': 'Sarah Connor',
            'email_from': 'sarah.connor@solartest.org',
            'phone': '+15550122008',
            'street': '800 Cyber Road',
            'city': 'Los Angeles',
            'monthly_bill_amount': 7200.0,
            'roof_area_sqft': 900.0,
            'roof_ownership': 'owned',
            'roof_suitability': 'suitable',
            'expected_capacity_kw': 8.0,
        })

        # Cannot convert un-qualified lead
        with self.assertRaises(UserError):
            lead.action_solar_convert_to_customer()

        # Qualify first
        lead.action_qualify_lead()
        self.assertEqual(lead.solar_qualification_status, 'qualified')

        # Convert to customer
        res = lead.action_solar_convert_to_customer()
        self.assertTrue(lead.partner_id, "Customer partner must be linked to lead.")
        self.assertEqual(lead.partner_id.name, 'Sarah Connor')
        self.assertTrue(lead.partner_id.is_solar_customer, "Partner must be marked as solar customer.")
        self.assertEqual(lead.type, 'opportunity', "Lead type should be converted to opportunity.")
        self.assertEqual(lead.partner_id.id, res.get('res_id'))

    # -------------------------------------------------------------------------
    # 9. Existing Customer Association
    # -------------------------------------------------------------------------
    def test_09_existing_customer_association(self):
        """Test that converting a lead with an existing partner links to it without creating a new partner."""
        initial_partner_count = self.partner_model.search_count([])

        lead = self.lead_model.create({
            'name': 'Alpha Factory Warehouse Solar',
            'partner_id': self.test_partner.id,
            'monthly_bill_amount': 45000.0,
            'roof_area_sqft': 5000.0,
            'roof_ownership': 'owned',
            'roof_suitability': 'suitable',
            'expected_capacity_kw': 40.0,
        })

        lead.action_qualify_lead()
        lead.action_solar_convert_to_customer()

        final_partner_count = self.partner_model.search_count([])
        self.assertEqual(initial_partner_count, final_partner_count, "No new partner should be created.")
        self.assertEqual(lead.partner_id.id, self.test_partner.id)
        self.assertTrue(self.test_partner.is_solar_customer)

    # -------------------------------------------------------------------------
    # 10. Duplicate Customer Prevention
    # -------------------------------------------------------------------------
    def test_10_duplicate_customer_prevention(self):
        """Test that converting a lead matching an existing partner email/phone reuses the existing partner."""
        initial_partner_count = self.partner_model.search_count([])

        # New lead with no partner_id, but email matches test_partner
        lead = self.lead_model.create({
            'name': 'Alpha Expansion Inquiry',
            'contact_name': 'Alpha Procurement',
            'email_from': 'procurement@alphaindustries.test',
            'phone': '+15550100100',
            'monthly_bill_amount': 25000.0,
            'roof_area_sqft': 3000.0,
            'roof_ownership': 'owned',
            'roof_suitability': 'suitable',
        })

        lead.action_qualify_lead()
        lead.action_solar_convert_to_customer()

        final_partner_count = self.partner_model.search_count([])
        self.assertEqual(initial_partner_count, final_partner_count, "Existing partner should be matched, avoiding duplication.")
        self.assertEqual(lead.partner_id.id, self.test_partner.id)

    # -------------------------------------------------------------------------
    # 11. Multiple Leads Associated With The Same Customer
    # -------------------------------------------------------------------------
    def test_11_multiple_leads_same_customer(self):
        """Test customer record supporting multiple inquiries and proper count computation."""
        lead_one = self.lead_model.create({
            'name': 'Alpha Site 1 - Main Plant',
            'partner_id': self.test_partner.id,
            'monthly_bill_amount': 30000.0,
            'roof_area_sqft': 4000.0,
        })

        lead_two = self.lead_model.create({
            'name': 'Alpha Site 2 - Logistics Hub',
            'partner_id': self.test_partner.id,
            'monthly_bill_amount': 15000.0,
            'roof_area_sqft': 2200.0,
        })

        self.test_partner._compute_solar_lead_count()
        self.assertGreaterEqual(self.test_partner.solar_lead_count, 2)
        self.assertIn(lead_one, self.test_partner.solar_lead_ids)
        self.assertIn(lead_two, self.test_partner.solar_lead_ids)

        # Test action to view customer's solar leads
        action = self.test_partner.action_view_solar_leads()
        self.assertEqual(action.get('domain'), [('partner_id', '=', self.test_partner.id)])
