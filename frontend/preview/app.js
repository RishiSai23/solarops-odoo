const data = {
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
    { project: "SPF-0128", customer: "Acme Industries", capacity: "5.0 kW", type: "On-Grid", stage: "Installation", technician: "Ravi Kumar" },
    { project: "SPF-0127", customer: "Green Homes Ltd", capacity: "3.0 kW", type: "Off-Grid", stage: "Survey", technician: "Priya Sharma" },
    { project: "SPF-0126", customer: "Sunrise Retail", capacity: "4.0 kW", type: "On-Grid", stage: "Approved", technician: "Amit Patel" },
    { project: "SPF-0125", customer: "Metro Factory", capacity: "5.0 kW", type: "Hybrid", stage: "Completed", technician: "Suresh Nair" },
    { project: "SPF-0124", customer: "Lakeview Villa", capacity: "2.0 kW", type: "On-Grid", stage: "Enquiry", technician: "Unassigned" },
  ],
  pendingActivities: [
    { description: "Site survey awaiting approval", reference: "SPF-0127", priority: "High" },
    { description: "Project awaiting installation scheduling", reference: "SPF-0126", priority: "Medium" },
    { description: "Installation requiring completion review", reference: "SPF-0128", priority: "High" },
    { description: "Project with overdue milestone", reference: "SPF-0123", priority: "High" },
  ],
  insights: { residential:72, commercial:28, onGrid:64, offGrid:36, completionRate:78 },
};

const app = document.getElementById('app');
app.innerHTML = `
<div class="o_sunflow_page_intro">
  <h1 class="o_sunflow_page_title">Director Dashboard</h1>
  <p class="o_sunflow_page_subtitle">Monitor solar projects, installation progress and business performance. (Demo data)</p>
</div>
<div class="o_sunflow_kpi_grid">
  ${data.kpis.map(k=>`<div class="o_sunflow_kpi_card"><span class="o_sunflow_kpi_label">${k.label}</span><span class="o_sunflow_kpi_value">${k.value}</span><span class="o_sunflow_kpi_delta">${k.delta}</span></div>`).join('')}
</div>
<div class="o_sunflow_section">
  <h2 class="o_sunflow_section_title">Project Pipeline (Demo)</h2>
  <div class="o_sunflow_pipeline">
    ${data.pipeline.map(p=>`<div class="o_sunflow_pipeline_stage"><span class="o_sunflow_pipeline_label">${p.stage}</span><span class="o_sunflow_pipeline_count">${p.count}</span></div>`).join('')}
  </div>
</div>
<div class="o_sunflow_section">
  <h2 class="o_sunflow_section_title">Installation Overview (Demo)</h2>
  <div class="o_sunflow_install_grid">
    ${data.installation.map(i=>`<div class="o_sunflow_install_card"><span class="o_sunflow_install_label">${i.status}</span><span class="o_sunflow_install_count">${i.count}</span></div>`).join('')}
  </div>
</div>
<div class="o_sunflow_section">
  <h2 class="o_sunflow_section_title">Recent Projects (Demo)</h2>
  <div class="o_sunflow_table_wrapper">
    <table class="o_sunflow_table">
      <thead><tr><th>Project ID</th><th>Customer</th><th>System Capacity</th><th>System Type</th><th>Project Stage</th><th>Assigned Technician</th></tr></thead>
      <tbody>
        ${data.recentProjects.map(r=>`<tr><td>${r.project}</td><td>${r.customer}</td><td>${r.capacity}</td><td>${r.type}</td><td>${r.stage}</td><td>${r.technician}</td></tr>`).join('')}
      </tbody>
    </table>
  </div>
</div>
<div class="o_sunflow_section">
  <h2 class="o_sunflow_section_title">Requires Attention (Demo)</h2>
  <div class="o_sunflow_activity_list">
    ${data.pendingActivities.map(a=>`<div class="o_sunflow_activity_item"><span class="o_sunflow_activity_desc">${a.description}</span><span class="o_sunflow_activity_ref">${a.reference}</span><span class="o_sunflow_badge ${a.priority==='High'?'danger':'warning'}">${a.priority}</span></div>`).join('')}
  </div>
</div>
<div class="o_sunflow_section">
  <h2 class="o_sunflow_section_title">Solar Business Insights (Demo)</h2>
  <div class="o_sunflow_insights">
    ${[['Residential',data.insights.residential],['Commercial',data.insights.commercial],['On-Grid',data.insights.onGrid],['Off-Grid',data.insights.offGrid],['Completion Rate',data.insights.completionRate]].map(([l,v])=>`<div class="o_sunflow_insight"><span>${l}</span><div class="o_sunflow_bar"><div class="o_sunflow_bar_fill" style="width:${v}%"></div></div><span>${v}%</span></div>`).join('')}
  </div>
</div>
`;
