export interface Survey { id: string; projectId: string; customer: string; location: string; technician: string; scheduled: string; submitted: string; status: 'Scheduled' | 'Submitted' | 'Approved' | 'Rejected'; notes: string; }
export interface Installation { id: string; projectId: string; customer: string; location: string; capacity: number; technician: string; scheduled: string; status: 'Scheduled' | 'In Progress' | 'Completed' | 'Delayed'; progress: number; commissioning: 'Pending' | 'Completed'; }
export interface Package { id: string; name: string; capacity: number; config: 'On-Grid' | 'Off-Grid'; price: number; available: boolean; panels: string; inverter: string; battery: string; }

export const surveys: Survey[] = [
  { id: 'SUR-001', projectId: 'SPF-0127', customer: 'Green Homes Ltd', location: 'Pune', technician: 'Priya Sharma', scheduled: '2026-09-24', submitted: '2026-09-26', status: 'Submitted', notes: 'Roof suitable, minor shading.' },
  { id: 'SUR-002', projectId: 'SPF-0126', customer: 'Sunrise Retail', location: 'Nashik', technician: 'Amit Patel', scheduled: '2026-09-28', submitted: '', status: 'Scheduled', notes: '' },
];
export const installations: Installation[] = [
  { id: 'INS-001', projectId: 'SPF-0128', customer: 'Acme Industries', location: 'Mumbai', capacity: 5, technician: 'Ravi Kumar', scheduled: '2026-10-05', status: 'In Progress', progress: 60, commissioning: 'Pending' },
  { id: 'INS-002', projectId: 'SPF-0125', customer: 'Metro Factory', location: 'Thane', capacity: 5, technician: 'Suresh Nair', scheduled: '2026-09-15', status: 'Completed', progress: 100, commissioning: 'Completed' },
];
export const packages: Package[] = [
  { id: 'PKG-1K', name: '1 kW On-Grid Starter', capacity: 1, config: 'On-Grid', price: 45000, available: true, panels: '4x 250W', inverter: '1kW String', battery: 'N/A' },
  { id: 'PKG-3K', name: '3 kW Hybrid Home', capacity: 3, config: 'Off-Grid', price: 135000, available: true, panels: '8x 375W', inverter: '3kW Hybrid', battery: '5kWh LFP' },
  { id: 'PKG-5K', name: '5 kW Factory', capacity: 5, config: 'On-Grid', price: 210000, available: true, panels: '12x 415W', inverter: '5kW String', battery: 'N/A' },
];
