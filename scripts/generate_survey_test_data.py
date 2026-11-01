# -*- coding: utf-8 -*-
"""
SunFlow Site Survey — Synthetic Test Data Generator
====================================================

Generates exactly 400 synthetic solar.survey records in the `sunflow_demo`
database using the Odoo ORM only. No direct SQL, no attachment records, no
transient rejection wizard records, no modification of existing business data.

Execution (PowerShell, from repository root):

    docker cp scripts/generate_survey_test_data.py sunflow_odoo:/tmp/generate_survey_test_data.py
    docker exec -i sunflow_odoo bash -c "odoo shell -d sunflow_demo -c /etc/odoo/odoo.conf < /tmp/generate_survey_test_data.py"

The script is transactional: all writes are staged and committed only after
verification passes. On failure, the transaction is rolled back.

Safety guarantees enforced in code:
  * Duplicate detection via the SURV-TEST- prefix — aborts if any exist.
  * The pre-existing project SPF-0000 is never touched (survey creation would
    trigger _sync_survey_feasibility() and change its stage).
  * All 400 surveys are created on freshly-created synthetic projects.
  * Feasible surveys always satisfy sanctioned_load_kw >= project.kw_capacity.
  * Zero ir.attachment records linked to generated surveys.
  * Zero solar.survey.reject.wizard records linked to generated surveys.
  * Approval metadata fields (approved_by, rejected_by, etc.) are never set.
"""

from datetime import date, timedelta
from collections import Counter
import random

TEST_PREFIX = 'SURV-TEST-'
TARGET_COUNT = 400

# Distribution: (workflow_state, feasibility_status, count)
# Totals: state -> draft=80, scheduled=60, in_progress=50, submitted=60,
#         approved=100, rejected=50  (grand total 400)
#         feasibility -> draft=110, feasible=160, conditional=60, rejected=70
DISTRIBUTION = [
    ('draft', 'draft', 80),
    ('scheduled', 'draft', 20),
    ('scheduled', 'feasible', 20),
    ('scheduled', 'conditional', 20),
    ('in_progress', 'draft', 10),
    ('in_progress', 'conditional', 20),
    ('in_progress', 'feasible', 20),
    ('submitted', 'conditional', 20),
    ('submitted', 'rejected', 20),
    ('submitted', 'feasible', 20),
    ('approved', 'feasible', 100),
    ('rejected', 'rejected', 50),
]

ROOF_TYPES = ['rcc_flat', 'tin_shed', 'tile_sloped', 'ground_mount']
ROOF_DIRECTIONS = ['south', 'south_east', 'south_west', 'east', 'west', 'north', 'flat']
METER_PHASES = ['single_phase', 'three_phase']
SYSTEM_TYPES = ['on_grid', 'off_grid', 'hybrid']

random.seed(20261031)

assert sum(count for _, _, count in DISTRIBUTION) == TARGET_COUNT, \
    f"Distribution totals {sum(c for _, _, c in DISTRIBUTION)}, expected {TARGET_COUNT}"


def main():
    # ------------------------------------------------------------------
    # Preflight: capture SPF-0000 identity and key fields before generation
    # (read-only, no writes yet)
    # ------------------------------------------------------------------
    Project = env['solar.project']
    spf0000 = Project.search([('name', '=', 'SPF-0000')], limit=1)
    spf0000_id = spf0000.id if spf0000 else None
    spf0000_name_before = spf0000.name if spf0000 else None
    spf0000_stage_before = spf0000.stage if spf0000 else None
    spf0000_partner_id_before = spf0000.partner_id.id if spf0000 else None
    spf0000_kw_capacity_before = spf0000.kw_capacity if spf0000 else None

    # ------------------------------------------------------------------
    # Preflight: duplicate detection (read-only, no writes yet)
    # ------------------------------------------------------------------
    existing_count = env['solar.survey'].search_count(
        [('name', 'ilike', TEST_PREFIX + '%')]
    )
    if existing_count > 0:
        raise RuntimeError(
            f"ABORT: {existing_count} existing records with prefix "
            f"'{TEST_PREFIX}' already exist. Remove them first to avoid "
            f"duplicates."
        )

    # ------------------------------------------------------------------
    # Preflight: verify required models and users exist (read-only)
    # ------------------------------------------------------------------
    Survey = env['solar.survey']
    Partner = env['res.partner']
    User = env['res.users']

    # Only internal (non-portal) users are valid surveyors.
    # ID 7 (Joel Willis, portal, share=True) is excluded.
    users = User.search([('active', '=', True), ('share', '=', False)], order='id')
    if not users:
        raise RuntimeError("No active internal users found to assign as surveyors.")

    # ------------------------------------------------------------------
    # Create synthetic partners (new records only — existing data untouched)
    # ------------------------------------------------------------------
    partner_names = [
        'Green Villa Residency', 'Sunrise Apartments', 'Meadow View Homes',
        'Silver Oak Society', 'Azure Heights',
    ]
    partner_vals_list = [
        {
            'name': name,
            'email': f'contact@{name.lower().replace(" ", "")}.example.com',
            'phone': f'+91 9{random.randint(100000000, 999999999)}',
        }
        for name in partner_names
    ]
    partners = Partner.create(partner_vals_list)

    # ------------------------------------------------------------------
    # Create synthetic projects (new records only — existing data untouched)
    # ------------------------------------------------------------------
    project_vals_list = []
    for i, partner in enumerate(partners):
        kw = 3.0 + (i * 0.5)  # 3.0, 3.5, 4.0, 4.5, 5.0
        project_vals_list.append({
            'name': f'SPF-TEST-{i + 1:03d}',
            'partner_id': partner.id,
            'kw_capacity': kw,
            'system_type': SYSTEM_TYPES[i % 3],
            'stage': 'lead',
        })
    projects = Project.create(project_vals_list)

    # ------------------------------------------------------------------
    # Generate 400 survey value dicts (deterministic synthetic data)
    # ------------------------------------------------------------------
    survey_vals_list = []
    counter = 0
    base_date = date(2026, 5, 1)

    for state, feasibility, count in DISTRIBUTION:
        for _ in range(count):
            counter += 1
            project = projects[(counter - 1) % len(projects)]
            surveyor = users[(counter - 1) % len(users)]

            # Grid compatibility: feasible requires sanctioned_load_kw >= kw_capacity.
            # For non-feasible surveys, sanctioned load can be any value.
            if feasibility == 'feasible':
                sanctioned_load = round(project.kw_capacity + random.uniform(2.0, 8.0), 2)
            else:
                sanctioned_load = round(random.uniform(1.0, 20.0), 2)

            survey_date = base_date + timedelta(days=random.randint(0, 180))

            vals = {
                'name': f'{TEST_PREFIX}{counter:04d}',
                'project_id': project.id,
                'surveyor_id': surveyor.id,
                'survey_date': survey_date,
                'state': state,
                'feasibility_status': feasibility,
                'roof_type': random.choice(ROOF_TYPES),
                'roof_direction': random.choice(ROOF_DIRECTIONS),
                'azimuth_degrees': round(random.uniform(150.0, 210.0), 1),
                'tilt_degrees': round(random.uniform(10.0, 30.0), 1),
                'shading_factor_pct': round(random.uniform(0.0, 35.0), 1),
                'usable_area_sqft': round(random.uniform(300.0, 1200.0), 0),
                'cable_distance': round(random.uniform(10.0, 100.0), 0),
                'sanctioned_load_kw': sanctioned_load,
                'meter_phase': random.choice(METER_PHASES),
                'service_voltage': random.choice([230, 415]),
                'shading_notes': 'Synthetic test data — shading assessment.',
                'remarks': 'Synthetic test data — generated for Site Survey testing.',
                'survey_notes': 'Synthetic test data — technical observations.',
            }
            survey_vals_list.append(vals)

    assert len(survey_vals_list) == TARGET_COUNT, \
        f"Generated {len(survey_vals_list)} vals, expected {TARGET_COUNT}"

    # ------------------------------------------------------------------
    # Batch create via Odoo ORM (single create(vals_list) call)
    # ------------------------------------------------------------------
    surveys = Survey.create(survey_vals_list)

    # ------------------------------------------------------------------
    # Verification (read-only, within same transaction)
    # ------------------------------------------------------------------

    # Re-fetch all generated surveys for full verification
    all_surveys = env['solar.survey'].search([('name', 'ilike', TEST_PREFIX + '%')])
    survey_ids = set(all_surveys.ids)

    # 1. Exactly 400 surveys
    if len(all_surveys) != TARGET_COUNT:
        raise RuntimeError(
            f"VERIFICATION FAILED: expected {TARGET_COUNT} surveys, "
            f"found {len(all_surveys)}"
        )

    # 2. Exactly five newly created partners
    if len(partners) != 5:
        raise RuntimeError(
            f"VERIFICATION FAILED: expected 5 partners, found {len(partners)}"
        )

    # 3. Exactly five newly created projects
    if len(projects) != 5:
        raise RuntimeError(
            f"VERIFICATION FAILED: expected 5 projects, found {len(projects)}"
        )

    # 4. Every generated project belongs to one of the five newly created partners
    partner_ids = set(partners.ids)
    for p in projects:
        if p.partner_id.id not in partner_ids:
            raise RuntimeError(
                f"VERIFICATION FAILED: project {p.name} links to partner "
                f"{p.partner_id.id} which is not one of the created partners."
            )

    # 5. Every generated survey references one of the five newly created projects
    project_ids = set(projects.ids)
    for s in all_surveys:
        if s.project_id.id not in project_ids:
            raise RuntimeError(
                f"VERIFICATION FAILED: survey {s.name} links to project "
                f"{s.project_id.id} which is not one of the created projects."
            )

    # 6. Every generated survey references an active internal surveyor
    internal_user_ids = set(users.ids)
    for s in all_surveys:
        if s.surveyor_id.id not in internal_user_ids:
            raise RuntimeError(
                f"VERIFICATION FAILED: survey {s.name} assigned to user "
                f"{s.surveyor_id.id} which is not an active internal user."
            )

    # 7. Exact workflow-state distribution
    expected_state_counts = {}
    for state, _feasibility, count in DISTRIBUTION:
        expected_state_counts[state] = expected_state_counts.get(state, 0) + count

    actual_state_counts = Counter(s.state for s in all_surveys)
    for state, expected_count in expected_state_counts.items():
        actual_count = actual_state_counts.get(state, 0)
        if actual_count != expected_count:
            raise RuntimeError(
                f"VERIFICATION FAILED: state '{state}' expected {expected_count}, "
                f"found {actual_count}"
            )

    # 8. Exact feasibility-status distribution
    expected_feasibility_counts = {}
    for _state, feasibility, count in DISTRIBUTION:
        expected_feasibility_counts[feasibility] = expected_feasibility_counts.get(feasibility, 0) + count

    actual_feasibility_counts = Counter(s.feasibility_status for s in all_surveys)
    for feasibility, expected_count in expected_feasibility_counts.items():
        actual_count = actual_feasibility_counts.get(feasibility, 0)
        if actual_count != expected_count:
            raise RuntimeError(
                f"VERIFICATION FAILED: feasibility '{feasibility}' expected "
                f"{expected_count}, found {actual_count}"
            )

    # 9. Grid compatibility for every feasible survey
    for s in all_surveys:
        if s.feasibility_status == 'feasible':
            if s.project_id.kw_capacity > 0 and s.sanctioned_load_kw > 0:
                if s.project_id.kw_capacity > s.sanctioned_load_kw:
                    raise RuntimeError(
                        f"VERIFICATION FAILED: survey {s.name} is 'feasible' but "
                        f"project capacity {s.project_id.kw_capacity} kW exceeds "
                        f"sanctioned load {s.sanctioned_load_kw} kW."
                    )

    # 10. No attachments linked to generated surveys
    attachment_count = env['ir.attachment'].search_count([
        ('res_model', '=', 'solar.survey'),
        ('res_id', 'in', list(survey_ids)),
    ])
    if attachment_count != 0:
        raise RuntimeError(
            f"VERIFICATION FAILED: {attachment_count} attachment records "
            f"linked to generated surveys (expected 0)"
        )

    # 11. No rejection wizard records linked to generated surveys
    wizard_count = env['solar.survey.reject.wizard'].search_count([
        ('survey_id', 'in', list(survey_ids)),
    ])
    if wizard_count != 0:
        raise RuntimeError(
            f"VERIFICATION FAILED: {wizard_count} reject wizard records "
            f"linked to generated surveys (expected 0)"
        )

    # 12. Existing project SPF-0000 remains unchanged
    if spf0000_id:
        # No generated survey references the existing project SPF-0000
        spf0000_survey_count = env['solar.survey'].search_count([
            ('project_id', '=', spf0000_id),
            ('name', 'ilike', TEST_PREFIX + '%'),
        ])
        if spf0000_survey_count != 0:
            raise RuntimeError(
                f"VERIFICATION FAILED: {spf0000_survey_count} generated surveys "
                f"reference existing project SPF-0000 (id={spf0000_id})."
            )

        # Reload SPF-0000 to read current field values within this transaction
        spf0000_after = Project.browse(spf0000_id)
        if spf0000_after.name != spf0000_name_before:
            raise RuntimeError(
                "VERIFICATION FAILED: existing project SPF-0000 name changed "
                f"from '{spf0000_name_before}' to '{spf0000_after.name}'."
            )
        if spf0000_after.stage != spf0000_stage_before:
            raise RuntimeError(
                "VERIFICATION FAILED: existing project SPF-0000 stage changed "
                f"from '{spf0000_stage_before}' to '{spf0000_after.stage}'."
            )
        if spf0000_after.partner_id.id != spf0000_partner_id_before:
            raise RuntimeError(
                "VERIFICATION FAILED: existing project SPF-0000 partner_id changed "
                f"from {spf0000_partner_id_before} to {spf0000_after.partner_id.id}."
            )
        if spf0000_after.kw_capacity != spf0000_kw_capacity_before:
            raise RuntimeError(
                "VERIFICATION FAILED: existing project SPF-0000 kw_capacity changed "
                f"from {spf0000_kw_capacity_before} to {spf0000_after.kw_capacity}."
            )

    # ------------------------------------------------------------------
    # Commit only after all verifications pass
    # ------------------------------------------------------------------
    env.cr.commit()

    # ------------------------------------------------------------------
    # Summary report
    # ------------------------------------------------------------------
    print('=' * 62)
    print('SUNFLOW SITE SURVEY TEST DATA GENERATION — SUMMARY')
    print('=' * 62)
    print(f"Target survey count : {TARGET_COUNT}")
    print(f"Actual survey count : {len(all_surveys)}")
    print(f"Partners created    : {len(partners)}")
    print(f"Projects created    : {len(projects)}")
    print(f"Surveyor users used : {len(users)}")
    print(f"Reject wizard rows  : {wizard_count} (expected 0)")
    print(f"Attachment rows     : {attachment_count} (expected 0)")
    print(f"Test prefix         : {TEST_PREFIX}")
    print()
    print("Distribution (workflow_state / feasibility / count):")
    for state, feasibility, count in DISTRIBUTION:
        print(f"  {state:<16s} / {feasibility:<12s} / {count:3d}")
    print()
    print("Grid compliance: every 'feasible' survey has")
    print("  sanctioned_load_kw >= project.kw_capacity.")
    print()
    print("Existing project SPF-0000 was NOT modified.")
    print("SUCCESS: 400 synthetic survey records created and committed.")
    print('=' * 62)


try:
    main()
except Exception:
    env.cr.rollback()
    raise
