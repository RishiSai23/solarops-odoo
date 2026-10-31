
# SolarOps - Generate 300 demo CRM leads and contacts
# Run inside Odoo shell. Uses Odoo ORM, not direct SQL.

from odoo import fields

Partner = env['res.partner']
Lead = env['crm.lead']

cities = [
    ('Chennai', '600001'),
    ('Coimbatore', '641001'),
    ('Madurai', '625001'),
    ('Tiruchirappalli', '620001'),
    ('Salem', '636001'),
    ('Bengaluru', '560001'),
    ('Hyderabad', '500001'),
    ('Erode', '638001'),
    ('Vellore', '632001'),
    ('Tirunelveli', '627001'),
]

first_names = [
    'Arun', 'Priya', 'Karthik', 'Divya', 'Vijay',
    'Meena', 'Sanjay', 'Anitha', 'Rahul', 'Kavya',
    'Suresh', 'Nithya', 'Ramesh', 'Deepa', 'Hari',
]

last_names = [
    'Kumar', 'Sharma', 'Rajan', 'Krishnan', 'Reddy',
    'Iyer', 'Nair', 'Patel', 'Das', 'Menon',
]

sources = ['whatsapp', 'phone', 'website', 'manual', 'other']
system_types = ['on_grid', 'off_grid', 'hybrid']
grid_types = ['connected_stable', 'connected_unstable', 'off_grid']

created_contacts = 0
created_leads = 0
already_existing = 0

country = env.ref('base.in', raise_if_not_found=False)

for i in range(1, 301):

    first = first_names[(i - 1) % len(first_names)]
    last = last_names[((i - 1) // len(first_names)) % len(last_names)]
    city, postal_code = cities[(i - 1) % len(cities)]

    customer_name = f'{first} {last} Demo {i:03d}'
    email = f'solar.demo.{i:03d}@example.test'
    mobile = str(9000000000 + i)
    phone = '+91 ' + mobile
    lead_name = f'SOLAR-DEMO-{i:03d} | {customer_name}'

    # Avoid creating duplicate demo leads when rerunning the script.
    existing_lead = Lead.search([
        ('name', '=', lead_name)
    ], limit=1)

    if existing_lead:
        already_existing += 1
        continue

    # Reuse an existing demo contact if one already exists.
    partner = Partner.search([
        ('email', '=', email)
    ], limit=1)

    if not partner:
        partner = Partner.create({
            'name': customer_name,
            'email': email,
            'phone': phone,
            'mobile': phone,
            'street': f'{i}, Solar Avenue, Main Road',
            'city': city,
            'zip': postal_code,
            'country_id': country.id if country else False,
            'is_company': False,
            'is_solar_customer': False,
            'comment': 'SolarOps synthetic demonstration contact.',
        })
        created_contacts += 1

    # Assign the 300 leads to four realistic business categories.
    if i <= 150:
        # Qualified and ready for the future Survey module.
        qualification_status = 'not_evaluated'
        roof_ownership = 'owned'
        roof_suitability = 'suitable'
        bill = 2500 + (i % 15) * 350
        consumption = 180 + (i % 20) * 18
        roof_area = 500 + (i % 15) * 100
        capacity = round(2 + (i % 8) * 0.5, 2)
        notes = 'Synthetic demo lead with complete pre-qualification details.'

    elif i <= 200:
        # Missing landlord NOC.
        qualification_status = 'needs_info'
        roof_ownership = 'rented_pending_noc'
        roof_suitability = 'pending_inspection'
        bill = 0
        consumption = 0
        roof_area = 0
        capacity = 0
        notes = 'Landlord NOC and electricity consumption details are pending.'

    elif i <= 250:
        # Unsuitable rooftop.
        qualification_status = 'not_suitable'
        roof_ownership = 'owned'
        roof_suitability = 'shaded'
        bill = 3000 + (i % 10) * 200
        consumption = 250 + (i % 10) * 15
        roof_area = 700
        capacity = 3
        notes = 'Demo rejection: rooftop is heavily shaded.'

    else:
        # New enquiry not yet evaluated.
        qualification_status = 'not_evaluated'
        roof_ownership = 'owned'
        roof_suitability = 'pending_inspection'
        bill = 2000 + (i % 10) * 250
        consumption = 150 + (i % 10) * 20
        roof_area = 600
        capacity = 3
        notes = 'New demo enquiry awaiting initial evaluation.'

    lead = Lead.create({
        'name': lead_name,
        'type': 'lead',
        'partner_id': partner.id,
        'contact_name': customer_name,
        'email_from': email,
        'phone': phone,
        'mobile': phone,
        'street': f'{i}, Solar Avenue, Main Road',
        'city': city,
        'zip': postal_code,
        'country_id': country.id if country else False,
        'solar_lead_source': sources[(i - 1) % len(sources)],
        'monthly_bill_amount': bill,
        'avg_monthly_consumption_kwh': consumption,
        'roof_area_sqft': roof_area,
        'roof_ownership': roof_ownership,
        'roof_suitability': roof_suitability,
        'grid_connectivity': grid_types[(i - 1) % len(grid_types)],
        'solar_system_type': system_types[(i - 1) % len(system_types)],
        'expected_capacity_kw': capacity,
        'solar_remarks': 'Synthetic SolarOps demonstration enquiry.',
        'solar_qualification_status': qualification_status,
        'qualification_notes': notes,
        'description': 'SOLAROPS_DEMO_DATA_300',
    })

    # Execute the actual Odoo qualification and survey-readiness workflow.
    if i <= 150:
        lead.action_qualify_lead()
        lead.action_mark_survey_ready()

    created_leads += 1

# Commit the generated records.
env.cr.commit()

print('==========================================')
print('SOLAROPS DEMO DATA GENERATION COMPLETED')
print('==========================================')
print('New contacts created :', created_contacts)
print('New leads created    :', created_leads)
print('Existing leads skipped:', already_existing)
print('==========================================')
