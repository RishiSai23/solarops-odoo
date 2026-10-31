export type ProjectStatus = 'Enquiry' | 'Survey' | 'Approved' | 'Installation' | 'Completed';

export interface DirectorProject {
  id: string;
  name: string;
  customer: string;
  capacity: number;
  type: 'Residential' | 'Factory';
  system: 'On-Grid' | 'Off-Grid';
  status: ProjectStatus;
  salesExec: string;
  progress: number;
  createdAt: string;
}

export const directorKpis = {
  totalProjects: 128,
  activeProjects: 42,
  completedInstallations: 37,
  pendingApprovals: 11,
  totalRevenue: '₹12.8L',
  outstandingPayments: '₹1.9L',
};

export const directorProjects: DirectorProject[] = [
  { id: 'SPF-0128', name: 'Acme Industries Rooftop', customer: 'Acme Industries', capacity: 5, type: 'Factory', system: 'On-Grid', status: 'Installation', salesExec: 'Ravi Kumar', progress: 72, createdAt: '2026-09-12' },
  { id: 'SPF-0127', name: 'Green Homes Villa', customer: 'Green Homes Ltd', capacity: 3, type: 'Residential', system: 'Off-Grid', status: 'Survey', salesExec: 'Priya Sharma', progress: 28, createdAt: '2026-09-20' },
  { id: 'SPF-0126', name: 'Sunrise Retail Array', customer: 'Sunrise Retail', capacity: 4, type: 'Factory', system: 'On-Grid', status: 'Approved', salesExec: 'Amit Patel', progress: 45, createdAt: '2026-09-25' },
  { id: 'SPF-0125', name: 'Metro Factory Plant', customer: 'Metro Factory', capacity: 5, type: 'Factory', system: 'Hybrid' as any, status: 'Completed', salesExec: 'Suresh Nair', progress: 100, createdAt: '2026-08-30' },
  { id: 'SPF-0124', name: 'Lakeview Villa', customer: 'Lakeview Villa', capacity: 2, type: 'Residential', system: 'On-Grid', status: 'Enquiry', salesExec: 'Unassigned', progress: 8, createdAt: '2026-10-02' },
  { id: 'SPF-0123', name: 'Hilltop Residence', customer: 'Hilltop Residence', capacity: 3, type: 'Residential', system: 'Off-Grid', status: 'Installation', salesExec: 'Ravi Kumar', progress: 60, createdAt: '2026-09-05' },
];

export const directorAlerts = [
  { id: 1, text: '2 projects overdue milestone', ref: 'SPF-0123' },
  { id: 2, text: '3 quotations awaiting approval', ref: 'SPF-0126' },
  { id: 3, text: 'Outstanding payments: ₹1.9L', ref: 'SPF-0128' },
];

export const directorActivities = [
  { id: 1, text: 'New enquiry received', ref: 'SPF-0124', date: '2026-10-02' },
  { id: 2, text: 'Survey submitted', ref: 'SPF-0127', date: '2026-09-22' },
  { id: 3, text: 'Order confirmed', ref: 'SPF-0126', date: '2026-09-26' },
  { id: 4, text: 'Installation update', ref: 'SPF-0128', date: '2026-10-01' },
  { id: 5, text: 'Payment received', ref: 'SPF-0125', date: '2026-09-30' },
];

export const directorInsights = {
  totalCapacity: '32 kW',
  residential: 58,
  factory: 42,
  onGrid: 64,
  offGrid: 36,
  packagePerformance: [
    { name: '1-2 kW', value: 22 },
    { name: '3 kW', value: 31 },
    { name: '4 kW', value: 25 },
    { name: '5 kW', value: 22 },
  ],
};
