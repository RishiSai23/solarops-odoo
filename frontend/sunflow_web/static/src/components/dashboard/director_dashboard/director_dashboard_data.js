/** @odoo-module **/

export const directorDemoData = {
    kpis: [
        { label: "Total Projects", value: 128, delta: "Demo data" },
        { label: "Active Installations", value: 18, delta: "Demo data" },
        { label: "Monthly Revenue", value: "₹12.8L", delta: "Demo data" },
        { label: "Pending Surveys", value: 9, delta: "Demo data" },
    ],
    pipeline: [
        { stage: "Enquiry", count: 24 },
        { stage: "Survey", count: 18 },
        { stage: "Approved", count: 31 },
        { stage: "Installation", count: 18 },
        { stage: "Completed", count: 37 },
    ],
    installation: [
        { status: "Scheduled", count: 7 },
        { status: "In Progress", count: 18 },
        { status: "Completed", count: 37 },
    ],
    recentProjects: [
        { id: 1, project: "SPF-0128", customer: "Acme Industries", capacity: "5.0 kW", type: "On-Grid", stage: "Installation", technician: "Ravi Kumar" },
        { id: 2, project: "SPF-0127", customer: "Green Homes Ltd", capacity: "3.0 kW", type: "Off-Grid", stage: "Survey", technician: "Priya Sharma" },
        { id: 3, project: "SPF-0126", customer: "Sunrise Retail", capacity: "4.0 kW", type: "On-Grid", stage: "Approved", technician: "Amit Patel" },
        { id: 4, project: "SPF-0125", customer: "Metro Factory", capacity: "5.0 kW", type: "Hybrid", stage: "Completed", technician: "Suresh Nair" },
        { id: 5, project: "SPF-0124", customer: "Lakeview Villa", capacity: "2.0 kW", type: "On-Grid", stage: "Enquiry", technician: "Unassigned" },
    ],
    pendingActivities: [
        { description: "Site survey awaiting approval", reference: "SPF-0127", priority: "High" },
        { description: "Project awaiting installation scheduling", reference: "SPF-0126", priority: "Medium" },
        { description: "Installation requiring completion review", reference: "SPF-0128", priority: "High" },
        { description: "Project with overdue milestone", reference: "SPF-0123", priority: "High" },
    ],
    insights: {
        residential: 72,
        commercial: 28,
        onGrid: 64,
        offGrid: 36,
        completionRate: 78,
    },
};
