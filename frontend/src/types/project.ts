export type SystemType = 'on_grid' | 'off_grid' | 'hybrid';

export type LifecycleStage = 
  | 'lead'
  | 'survey'
  | 'feasibility'
  | 'quotation'
  | 'order'
  | 'procurement'
  | 'dispatch'
  | 'installation'
  | 'commissioning'
  | 'handover'
  | 'warranty'
  | 'closed'
  | 'cancelled';

export interface SolarProject {
  id: number;
  name: string;
  partner_name: string;
  kw_capacity: number;
  system_type: SystemType;
  stage: LifecycleStage;
  contract_amount: number;
  actual_cost: number;
  gross_margin: number;
  installation_date?: string | null;
  completion_date?: string | null;
  assigned_technician?: string;
}

export interface DashboardMetrics {
  kpis: {
    active_projects: number;
    total_capacity_kw: number;
    total_revenue_inr: number;
    gross_margin_inr: number;
    avg_margin_pct: number;
  };
  stage_distribution: Record<string, number>;
}
