"""
SunFlow Mock & Sandbox Adapter
------------------------------
Provides an in-memory realistic simulation of the Odoo solar lifecycle database.
Used when Odoo is offline, in CI/CD automated test runs, or for rapid frontend demonstrations.
"""

from typing import List, Dict, Any, Optional

DEMO_PROJECTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "SPF-2026-0001",
        "partner_name": "Dr. Ramesh Verma (Villa 14)",
        "kw_capacity": 3.0,
        "system_type": "on_grid",
        "stage": "installation",
        "contract_amount": 210000.0,
        "actual_cost": 142000.0,
        "gross_margin": 68000.0,
        "installation_date": "2026-11-02",
        "completion_date": None,
        "assigned_technician": "Pawan Kumar (Lead)",
        "surveys": [
            {
                "roof_type": "rcc_flat",
                "azimuth_degrees": 180.0,
                "tilt_degrees": 15.0,
                "shading_factor_pct": 2.5,
                "sanctioned_load_kw": 5.0,
                "meter_phase": "single_phase",
                "feasibility_status": "feasible"
            }
        ],
        "warranties": [
            {
                "equipment_type": "inverter",
                "serial_number": "DEYE-3KW-994821",
                "warranty_years": 5,
                "status": "active"
            }
        ]
    },
    {
        "id": 2,
        "name": "SPF-2026-0002",
        "partner_name": "Apex Auto Components Ltd",
        "kw_capacity": 5.0,
        "system_type": "hybrid",
        "stage": "quotation",
        "contract_amount": 395000.0,
        "actual_cost": 265000.0,
        "gross_margin": 130000.0,
        "installation_date": "2026-11-10",
        "completion_date": None,
        "assigned_technician": "Vikram Singh",
        "surveys": [
            {
                "roof_type": "tin_shed",
                "azimuth_degrees": 175.0,
                "tilt_degrees": 10.0,
                "shading_factor_pct": 0.0,
                "sanctioned_load_kw": 10.0,
                "meter_phase": "three_phase",
                "feasibility_status": "feasible"
            }
        ],
        "warranties": []
    },
    {
        "id": 3,
        "name": "SPF-2026-0003",
        "partner_name": "Mrs. Sunita Deshmukh",
        "kw_capacity": 2.0,
        "system_type": "on_grid",
        "stage": "warranty",
        "contract_amount": 145000.0,
        "actual_cost": 98000.0,
        "gross_margin": 47000.0,
        "installation_date": "2026-10-20",
        "completion_date": "2026-10-22",
        "assigned_technician": "Amit Sharma",
        "surveys": [],
        "warranties": [
            {
                "equipment_type": "panel",
                "serial_number": "WARI-550W-883190",
                "warranty_years": 25,
                "status": "active"
            },
            {
                "equipment_type": "inverter",
                "serial_number": "GROWATT-2K-11204",
                "warranty_years": 5,
                "status": "active"
            }
        ]
    }
]

class MockOdooAdapter:
    def __init__(self):
        self.projects = list(DEMO_PROJECTS)

    def is_connected(self) -> bool:
        return True

    def get_projects(self, stage: Optional[str] = None) -> List[Dict[str, Any]]:
        if stage:
            return [p for p in self.projects if p["stage"] == stage]
        return self.projects

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        for p in self.projects:
            if p["id"] == project_id:
                return p
        return None

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = max([p["id"] for p in self.projects], default=0) + 1
        new_project = {
            "id": new_id,
            "name": f"SPF-2026-{new_id:04d}",
            "partner_name": data["partner_name"],
            "kw_capacity": data["kw_capacity"],
            "system_type": data.get("system_type", "on_grid"),
            "stage": "lead",
            "contract_amount": data["contract_amount"],
            "actual_cost": data["contract_amount"] * 0.68,
            "gross_margin": data["contract_amount"] * 0.32,
            "installation_date": None,
            "completion_date": None,
            "assigned_technician": data.get("assigned_technician", "Unassigned"),
            "surveys": [],
            "warranties": []
        }
        self.projects.append(new_project)
        return new_project

    def update_survey(self, project_id: int, survey_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        project["surveys"].append(survey_data)
        if project["stage"] == "lead":
            project["stage"] = "survey"
        return project

    def register_warranty(self, project_id: int, warranty_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        project = self.get_project_by_id(project_id)
        if not project:
            return None
        project["warranties"].append({
            **warranty_data,
            "status": "active"
        })
        return project
