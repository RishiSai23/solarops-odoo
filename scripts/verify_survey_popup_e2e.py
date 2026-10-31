import urllib.request
import json
import http.cookiejar
import re

print("=================================================================")
print(" SOLAROPS — SITE SURVEY ONE2MANY POPUP E2E RUNTIME VERIFICATION ")
print("=================================================================")

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Authenticate via web session
auth_payload = {
    "jsonrpc": "2.0",
    "params": {
        "db": "sunflow_test",
        "login": "admin",
        "password": "admin"
    }
}
req = urllib.request.Request(
    "http://localhost:8069/web/session/authenticate",
    data=json.dumps(auth_payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
auth_res = json.loads(opener.open(req).read().decode("utf-8")).get("result", {})
uid = auth_res.get("uid")
print(f"[1] Authenticated successfully as user id {uid} (db: sunflow_test)")

def rpc_call(endpoint, params):
    req = urllib.request.Request(
        f"http://localhost:8069{endpoint}",
        data=json.dumps({"jsonrpc": "2.0", "params": params}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    return json.loads(opener.open(req).read().decode("utf-8")).get("result")

# 2. Check solar.project get_views arch for embedded form
proj_views = rpc_call("/web/dataset/call_kw/solar.project/get_views", {
    "model": "solar.project",
    "method": "get_views",
    "args": [],
    "kwargs": {
        "views": [[False, "form"]],
        "options": {"action_id": False, "load_filters": False, "toolbar": False}
    }
})

arch = proj_views["views"]["form"]["arch"]
survey_field_match = re.search(r'<field[^>]*name=["\']survey_ids["\'][^>]*>(.*?)</field>', arch, re.DOTALL)
assert survey_field_match, "survey_ids field not found in solar.project form arch!"
survey_field_xml = survey_field_match.group(0)

print("\n[2] Inspected solar.project form arch:")
assert '<form string="Site Survey">' in survey_field_xml, "Embedded <form> NOT found inside survey_ids!"
print("  - Embedded <form string=\"Site Survey\"> present: YES")

expected_fields = [
    'name', 'project_id', 'surveyor_id', 'survey_date', 'sanctioned_load_kw',
    'meter_phase', 'service_voltage', 'roof_type', 'usable_area_sqft',
    'azimuth_degrees', 'tilt_degrees', 'shading_factor_pct', 'shading_notes',
    'remarks', 'feasibility_status'
]
missing_fields = [f for f in expected_fields if f'<field name="{f}"' not in survey_field_xml and f'<field name=\'{f}\'' not in survey_field_xml]
print("  - Checking 15 expected fields in embedded form:")
for f in expected_fields:
    assert f not in missing_fields, f"Missing field in embedded form: {f}"
    print(f"    * {f}: OK")

assert 'context="{\'default_project_id\': id, \'form_view_ref\': \'sunflow_core.view_solar_survey_form\'}"' in survey_field_xml or 'default_project_id' in survey_field_xml, "default_project_id missing from context!"
print("  - default_project_id in context: OK")

# 3. Check standalone solar.survey get_views with user web client context
survey_views = rpc_call("/web/dataset/call_kw/solar.survey/get_views", {
    "model": "solar.survey",
    "method": "get_views",
    "args": [],
    "kwargs": {
        "views": [[False, "form"]],
        "options": {"action_id": False, "load_filters": False, "toolbar": False},
        "context": {
            "lang": "en_US",
            "tz": "UTC",
            "uid": uid,
            "allowed_company_ids": [1],
            "default_project_id": 124
        }
    }
})
form_id = survey_views["views"]["form"]["id"]
print(f"\n[3] Standalone solar.survey get_views resolved form view id: {form_id}")
assert form_id, "Form view id is False!"
assert '<form string="Site Survey">' in survey_views["views"]["form"]["arch"], "Arch does not match Site Survey form!"

# 4. Open project SPF-0117 (id: 124) via web_read
proj_read = rpc_call("/web/dataset/call_kw/solar.project/web_read", {
    "model": "solar.project",
    "method": "web_read",
    "args": [[124]],
    "kwargs": {
        "specification": {
            "name": {},
            "partner_id": {},
            "stage": {},
            "survey_ids": {"fields": {"name": {}, "feasibility_status": {}, "survey_date": {}}}
        }
    }
})
print(f"\n[4] Loaded Project SPF-0117:")
proj = proj_read[0]
print(f"  Name: {proj.get('name')}, Partner: {proj.get('partner_id')}, Stage: {proj.get('stage')}")
initial_survey_count = len(proj.get("survey_ids", []))
print(f"  Existing surveys count: {initial_survey_count}")

# 5. Simulate "Add a line" clicking in browser: call onchange / default_get
default_vals = rpc_call("/web/dataset/call_kw/solar.survey/default_get", {
    "model": "solar.survey",
    "method": "default_get",
    "args": [expected_fields],
    "kwargs": {
        "context": {
            "lang": "en_US",
            "tz": "UTC",
            "uid": uid,
            "allowed_company_ids": [1],
            "default_project_id": 124
        }
    }
})
print(f"\n[5] default_get evaluation on clicking 'Add a line':")
print(f"  project_id default: {default_vals.get('project_id')}")
assert default_vals.get("project_id") == 124, f"Expected project_id 124, got {default_vals.get('project_id')}"
print("  -> PASSED: project_id defaults to SPF-0117 (ID 124)")

# 6. Save a new survey through the web client (web_save)
survey_payload = {
    "name": "SURV-SPF0117-VERIF",
    "project_id": 124,
    "surveyor_id": uid,
    "sanctioned_load_kw": 8.5,
    "meter_phase": "three_phase",
    "service_voltage": 415,
    "roof_type": "tin_shed",
    "usable_area_sqft": 1500.0,
    "azimuth_degrees": 180.0,
    "tilt_degrees": 18.0,
    "shading_factor_pct": 2.5,
    "shading_notes": "Minimal morning shadow from east parapet",
    "remarks": "Roof structure validated with M10 anchor studs",
    "feasibility_status": "feasible"
}

saved_survey = rpc_call("/web/dataset/call_kw/solar.survey/web_save", {
    "model": "solar.survey",
    "method": "web_save",
    "args": [[]],
    "kwargs": {
        "vals": survey_payload,
        "specification": {f: {} for f in expected_fields}
    }
})
survey_id = saved_survey[0]["id"]
print(f"\n[6] Saved new survey via web_save: ID={survey_id}, Name={saved_survey[0].get('name')}")

# 7. Verify it appears in SPF-0117's Site Surveys list
proj_read_after = rpc_call("/web/dataset/call_kw/solar.project/web_read", {
    "model": "solar.project",
    "method": "web_read",
    "args": [[124]],
    "kwargs": {
        "specification": {
            "name": {},
            "survey_ids": {"fields": {"id": {}, "name": {}, "feasibility_status": {}}}
        }
    }
})
updated_surveys = proj_read_after[0].get("survey_ids", [])
survey_ids_in_proj = [s["id"] for s in updated_surveys]
print(f"\n[7] Project SPF-0117 updated survey_ids count: {len(updated_surveys)}")
assert survey_id in survey_ids_in_proj, f"Created survey {survey_id} not found in project.survey_ids!"
print("  -> PASSED: New survey appears in SPF-0117's Site Surveys list!")

# 8. Open the saved survey and verify all fields persist
survey_read = rpc_call("/web/dataset/call_kw/solar.survey/web_read", {
    "model": "solar.survey",
    "method": "web_read",
    "args": [[survey_id]],
    "kwargs": {
        "specification": {f: {} for f in expected_fields}
    }
})
survey_data = survey_read[0]
print(f"\n[8] Verified persisted survey fields on ID {survey_id}:")
for f in expected_fields:
    val = survey_data.get(f)
    print(f"  - {f}: {val}")
    if f in survey_payload and f != 'project_id' and f != 'surveyor_id':
        assert val == survey_payload[f], f"Mismatch in {f}: expected {survey_payload[f]}, got {val}"

print("\n=================================================================")
print(" ALL 8 RUNTIME ACCEPTANCE TESTS PASSED SUCCESSFULLY! ")
print("=================================================================")

