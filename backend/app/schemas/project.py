from typing import Optional, List
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    partner_name: str = Field(..., description="Customer full name or business entity")
    kw_capacity: float = Field(..., ge=0.5, le=50.0, description="Solar capacity in kW")
    system_type: str = Field("on_grid", description="on_grid, off_grid, or hybrid")
    contract_amount: float = Field(..., ge=0.0)

class ProjectCreate(ProjectBase):
    lead_source: Optional[str] = "Website"
    assigned_technician: Optional[str] = None

class SurveyData(BaseModel):
    roof_type: str = Field("rcc_flat", description="rcc_flat, tin_shed, tile_sloped, ground_mount")
    azimuth_degrees: float = Field(180.0, description="Azimuth angle in degrees")
    tilt_degrees: float = Field(15.0, description="Optimal roof tilt in degrees")
    shading_factor_pct: float = Field(0.0, ge=0.0, le=100.0)
    sanctioned_load_kw: float = Field(..., ge=1.0)
    meter_phase: str = Field("single_phase", description="single_phase or three_phase")
    feasibility_status: str = Field("feasible", description="feasible, conditional, rejected")

class InstallationChecklist(BaseModel):
    check_structure_torque: bool = True
    check_dc_wiring_polar: bool = True
    check_earthing_installed: bool = True
    earthing_resistance_ohms: float = Field(..., le=5.0, description="Resistance in ohms (must be <= 5 ohms)")
    voc_measured_volts: float = Field(..., ge=0.0)
    customer_signature: Optional[str] = None

class WarrantyRegistration(BaseModel):
    equipment_type: str = Field(..., description="panel, inverter, battery, controller")
    serial_number: str = Field(..., min_length=4)
    warranty_years: int = Field(5, ge=1, le=30)

class ProjectResponse(ProjectBase):
    id: int
    name: str
    stage: str
    actual_cost: float
    gross_margin: float
    installation_date: Optional[str] = None
    completion_date: Optional[str] = None
