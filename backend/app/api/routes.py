from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    SurveyData,
    InstallationChecklist,
    WarrantyRegistration
)
from app.odoo.client import odoo_client

router = APIRouter(prefix="/api/v1")

@router.get("/health", tags=["System"])
def health_check():
    """Health status and Odoo connection state."""
    is_odoo_live = not odoo_client.use_mock and odoo_client.uid is not None
    return {
        "status": "healthy",
        "service": "SunFlow Gateway",
        "odoo_connected": is_odoo_live,
        "mode": "Live Odoo ERP" if is_odoo_live else "Sandbox / Mock Engine"
    }

@router.get("/projects", response_model=List[ProjectResponse], tags=["Projects"])
def list_projects(stage: Optional[str] = Query(None, description="Filter by lifecycle stage")):
    """Retrieve active solar projects."""
    return odoo_client.get_projects(stage=stage)

@router.post("/projects", response_model=ProjectResponse, status_code=201, tags=["Projects"])
def create_project(payload: ProjectCreate):
    """Create a new solar project lifecycle record."""
    created = odoo_client.create_project(payload.model_dump())
    return created

@router.get("/projects/{project_id}", tags=["Projects"])
def get_project_details(project_id: int):
    """Retrieve complete 360-degree project lifecycle details."""
    project = odoo_client.mock_adapter.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project record not found")
    return project

@router.post("/projects/{project_id}/survey", tags=["Field Survey"])
def submit_survey(project_id: int, survey: SurveyData):
    """Submit rooftop site feasibility survey."""
    updated = odoo_client.mock_adapter.update_survey(project_id, survey.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Project record not found")
    return {"message": "Survey submitted successfully", "project": updated}

@router.post("/projects/{project_id}/warranty", tags=["Warranties"])
def register_warranty(project_id: int, warranty: WarrantyRegistration):
    """Register equipment serial numbers for active warranty coverage."""
    updated = odoo_client.mock_adapter.register_warranty(project_id, warranty.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Project record not found")
    return {"message": "Equipment warranty registered successfully", "project": updated}

@router.get("/analytics/dashboard", tags=["Analytics"])
def get_dashboard_metrics():
    """Aggregated operational metrics for executive overview."""
    projects = odoo_client.get_projects()
    total_projects = len(projects)
    total_kw = sum([p.get("kw_capacity", 0.0) for p in projects])
    total_revenue = sum([p.get("contract_amount", 0.0) for p in projects])
    total_margin = sum([p.get("gross_margin", 0.0) for p in projects])

    stages = {}
    for p in projects:
        st = p.get("stage", "other")
        stages[st] = stages.get(st, 0) + 1

    return {
        "kpis": {
            "active_projects": total_projects,
            "total_capacity_kw": round(total_kw, 1),
            "total_revenue_inr": total_revenue,
            "gross_margin_inr": total_margin,
            "avg_margin_pct": round((total_margin / total_revenue * 100) if total_revenue > 0 else 0.0, 1),
        },
        "stage_distribution": stages
    }
