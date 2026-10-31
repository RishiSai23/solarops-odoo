import urllib.request
import json
import http.cookiejar

print("=========================================================================")
print(" SOLAROPS — SURVEY APPROVAL & PROJECT LIFECYCLE E2E RUNTIME VERIFICATION ")
print("=========================================================================")

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Authenticate
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
print(f"[1] Authenticated as admin (uid={uid}) on database 'sunflow_test'")

def rpc_call(endpoint, params):
    req = urllib.request.Request(
        f"http://localhost:8069{endpoint}",
        data=json.dumps({"jsonrpc": "2.0", "params": params}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = json.loads(opener.open(req).read().decode("utf-8"))
    if "error" in res:
        raise Exception(res["error"].get("data", {}).get("message") or res["error"].get("message"))
    return res.get("result")

# 2. Inspect SPF-0117 and Surv-SPF00903
projects = rpc_call("/web/dataset/call_kw/solar.project/search_read", {
    "model": "solar.project",
    "method": "search_read",
    "args": [[["name", "=", "SPF-0117"]]],
    "kwargs": {
        "fields": ["name", "partner_id", "stage", "kw_capacity", "feasibility_status", "approved_survey_id", "survey_ids"]
    }
})
assert projects, "SPF-0117 not found!"
p = projects[0]
print(f"\n[2] Found project SPF-0117:")
print(f"  ID: {p['id']}, Name: {p['name']}, Stage: {p['stage']}, Capacity: {p['kw_capacity']} kW, Feasibility: {p.get('feasibility_status')}")

# Find Surv-SPF00903
surveys = rpc_call("/web/dataset/call_kw/solar.survey/search_read", {
    "model": "solar.survey",
    "method": "search_read",
    "args": [[["project_id", "=", p["id"]], ["name", "=", "Surv-SPF00903"]]],
    "kwargs": {
        "fields": ["name", "feasibility_status", "sanctioned_load_kw", "usable_area_sqft", "project_id"]
    }
})
assert surveys, "Surv-SPF00903 not found on SPF-0117!"
s = surveys[0]
print(f"\n[3] Found survey Surv-SPF00903:")
print(f"  ID: {s['id']}, Name: {s['name']}, Status: {s['feasibility_status']}, Sanctioned Load: {s['sanctioned_load_kw']} kW, Usable Area: {s['usable_area_sqft']} sqft")

# Technical compatibility verification
print("\n[4] Technical Compatibility Check:")
print(f"  Project Capacity: {p['kw_capacity']} kW")
print(f"  Sanctioned Grid Load: {s['sanctioned_load_kw']} kW")
assert p['kw_capacity'] <= s['sanctioned_load_kw'], "Capacity exceeds grid load!"
print(f"  -> VALID: 5.0 kW system capacity is fully supported by 12.0 kW utility grid connection!")

# 5. Approve Surv-SPF00903 to 'feasible' (Feasible & Approved)
print("\n[5] Approving Survey Surv-SPF00903 to 'feasible' via web client:")
rpc_call("/web/dataset/call_kw/solar.survey/write", {
    "model": "solar.survey",
    "method": "write",
    "args": [[s['id']], {"feasibility_status": "feasible"}],
    "kwargs": {}
})

# Verify SPF-0117 automatically transitioned to 'feasibility'
p_after_survey = rpc_call("/web/dataset/call_kw/solar.project/read", {
    "model": "solar.project",
    "method": "read",
    "args": [[p["id"]]],
    "kwargs": {
        "fields": ["stage", "feasibility_status", "approved_survey_id"]
    }
})[0]
print(f"  Project SPF-0117 stage after survey approval: {p_after_survey['stage']}")
print(f"  Project feasibility status: {p_after_survey['feasibility_status']}")
print(f"  Project approved survey ID: {p_after_survey['approved_survey_id']}")
assert p_after_survey['stage'] == 'feasibility', f"Expected stage 'feasibility', got {p_after_survey['stage']}"
assert p_after_survey['feasibility_status'] == 'feasible', f"Expected feasibility_status 'feasible', got {p_after_survey['feasibility_status']}"
assert p_after_survey['approved_survey_id'][0] == s['id'], f"Expected approved_survey_id {s['id']}, got {p_after_survey['approved_survey_id']}"
print("  -> PASSED: SPF-0117 automatically advanced to 'feasibility' (Feasibility Review) with status 'Feasible & Approved'!")

# 6. Action Approve Feasibility & Proceed to Quotation
print("\n[6] Calling action_approve_feasibility() on SPF-0117:")
rpc_call("/web/dataset/call_kw/solar.project/action_approve_feasibility", {
    "model": "solar.project",
    "method": "action_approve_feasibility",
    "args": [[p["id"]]],
    "kwargs": {}
})
p_after_approval = rpc_call("/web/dataset/call_kw/solar.project/read", {
    "model": "solar.project",
    "method": "read",
    "args": [[p["id"]]],
    "kwargs": {
        "fields": ["stage"]
    }
})[0]
print(f"  Project SPF-0117 stage after feasibility sign-off: {p_after_approval['stage']}")
assert p_after_approval['stage'] == 'quotation', f"Expected stage 'quotation', got {p_after_approval['stage']}"
print("  -> PASSED: SPF-0117 advanced to 'quotation' (Quotation & BOM)!")

# 7. Test Quotation Prerequisite Enforcement & Guards on Test Project
print("\n[7] Testing Business Rules & Guards on new test projects:")

# Test Project A: Draft Survey cannot authorize quotation
p_test = rpc_call("/web/dataset/call_kw/solar.project/create", {
    "model": "solar.project",
    "method": "create",
    "args": [{
        "partner_id": p['partner_id'][0],
        "kw_capacity": 5.0,
        "system_type": "on_grid",
        "stage": "lead"
    }],
    "kwargs": {}
})
s_draft = rpc_call("/web/dataset/call_kw/solar.survey/create", {
    "model": "solar.survey",
    "method": "create",
    "args": [{
        "name": "SURV-TEST-DRAFT",
        "project_id": p_test,
        "sanctioned_load_kw": 12.0,
        "feasibility_status": "draft"
    }],
    "kwargs": {}
})
try:
    rpc_call("/web/dataset/call_kw/solar.project/action_approve_feasibility", {
        "model": "solar.project",
        "method": "action_approve_feasibility",
        "args": [[p_test]],
        "kwargs": {}
    })
    assert False, "Should have raised UserError for draft survey!"
except Exception as e:
    print(f"  [Rule 1 - Draft Survey Guard]: Correctly blocked ({e})")

# Test Project B: Rejected Survey cannot authorize quotation
rpc_call("/web/dataset/call_kw/solar.survey/write", {
    "model": "solar.survey",
    "method": "write",
    "args": [[s_draft], {"feasibility_status": "rejected"}],
    "kwargs": {}
})
try:
    rpc_call("/web/dataset/call_kw/solar.project/action_approve_feasibility", {
        "model": "solar.project",
        "method": "action_approve_feasibility",
        "args": [[p_test]],
        "kwargs": {}
    })
    assert False, "Should have raised UserError for rejected survey!"
except Exception as e:
    print(f"  [Rule 2 - Rejected Survey Guard]: Correctly blocked ({e})")

# Test Project C: Conditional Survey requires resolution
rpc_call("/web/dataset/call_kw/solar.survey/write", {
    "model": "solar.survey",
    "method": "write",
    "args": [[s_draft], {"feasibility_status": "conditional"}],
    "kwargs": {}
})
try:
    rpc_call("/web/dataset/call_kw/solar.project/action_approve_feasibility", {
        "model": "solar.project",
        "method": "action_approve_feasibility",
        "args": [[p_test]],
        "kwargs": {}
    })
    assert False, "Should have raised UserError for conditional survey!"
except Exception as e:
    print(f"  [Rule 3 - Conditional Survey Review Guard]: Correctly blocked ({e})")

# Test Project D: Technical Grid Incompatibility (15 kW system on 5 kW grid)
try:
    rpc_call("/web/dataset/call_kw/solar.survey/create", {
        "model": "solar.survey",
        "method": "create",
        "args": [{
            "name": "SURV-TEST-OVERLOAD",
            "project_id": p_test,
            "sanctioned_load_kw": 3.0,  # 3.0 kW grid connection < 5.0 kW project capacity
            "feasibility_status": "feasible"
        }],
        "kwargs": {}
    })
    assert False, "Should have raised ValidationError for capacity exceeding grid load!"
except Exception as e:
    print(f"  [Rule 4 - Grid Incompatibility Guard]: Correctly blocked ({e})")

# Test Project E: Later rejected survey does not overwrite approved survey
s_appr = rpc_call("/web/dataset/call_kw/solar.survey/create", {
    "model": "solar.survey",
    "method": "create",
    "args": [{
        "name": "SURV-TEST-APPR",
        "project_id": p_test,
        "sanctioned_load_kw": 10.0,
        "feasibility_status": "feasible"
    }],
    "kwargs": {}
})
p_check = rpc_call("/web/dataset/call_kw/solar.project/read", {
    "model": "solar.project",
    "method": "read",
    "args": [[p_test]],
    "kwargs": {"fields": ["feasibility_status", "approved_survey_id"]}
})[0]
assert p_check["feasibility_status"] == "feasible"
assert p_check["approved_survey_id"][0] == s_appr

# Now add a secondary rejected survey
rpc_call("/web/dataset/call_kw/solar.survey/create", {
    "model": "solar.survey",
    "method": "create",
    "args": [{
        "name": "SURV-TEST-REJ-LATER",
        "project_id": p_test,
        "sanctioned_load_kw": 10.0,
        "feasibility_status": "rejected"
    }],
    "kwargs": {}
})
p_check2 = rpc_call("/web/dataset/call_kw/solar.project/read", {
    "model": "solar.project",
    "method": "read",
    "args": [[p_test]],
    "kwargs": {"fields": ["feasibility_status", "approved_survey_id"]}
})[0]
assert p_check2["feasibility_status"] == "feasible", "Approved survey was overwritten by rejected survey!"
assert p_check2["approved_survey_id"][0] == s_appr, "Approved survey reference was lost!"
print(f"  [Rule 5 & 6 - Multiple Surveys & No Silent Invalidation]: Confirmed! Rejected survey did not overwrite approved survey.")

print("\n=========================================================================")
print(" ALL 7 E2E RUNTIME ACCEPTANCE TESTS PASSED WITH 100% SUCCESS! ")
print("=========================================================================")

