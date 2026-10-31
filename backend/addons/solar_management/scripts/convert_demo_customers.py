Lead = env['crm.lead']

leads = Lead.search([
    ('name', 'like', 'SOLAR-DEMO-%'),
    ('solar_qualification_status', '=', 'qualified'),
    ('is_solar_converted', '=', False),
], order='id')

converted = 0
failed = []

for lead in leads:
    try:
        with env.cr.savepoint():
            lead.action_solar_convert_to_customer()
        converted += 1
        print('Converted:', lead.name)
    except Exception as exc:
        failed.append((lead.name, str(exc)))
        print('FAILED:', lead.name, str(exc))

env.cr.commit()

print('====================================')
print('SOLAR CUSTOMER CONVERSION SUMMARY')
print('====================================')
print('Successfully converted:', converted)
print('Failed:', len(failed))
print('====================================')
