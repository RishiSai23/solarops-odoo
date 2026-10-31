import { SolarProject, DashboardMetrics } from '../types/project';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<{ status: string; odoo_connected: boolean; mode: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to reach backend gateway');
  return res.json();
}

export async function fetchProjects(stage?: string): Promise<SolarProject[]> {
  const url = stage ? `${API_BASE}/projects?stage=${encodeURIComponent(stage)}` : `${API_BASE}/projects`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/analytics/dashboard`);
  if (!res.ok) throw new Error('Failed to fetch dashboard metrics');
  return res.json();
}
