import { useMemo, useState } from 'react';
import { FolderKanban, Activity, CheckCircle2, AlertTriangle, IndianRupee, Wallet } from 'lucide-react';
import { WorkspaceLayout } from '../layouts/WorkspaceLayout';
import { KpiCard } from '../components/common/KpiCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { DataTable } from '../components/common/DataTable';
import { EmptyState } from '../components/common/EmptyState';
import {
  directorKpis,
  directorAlerts,
  directorActivities,
  directorInsights,
  type ProjectStatus,
} from '../data/directorDashboardData';
import { useDirectorData } from '../context/DirectorDataContext';

const statuses: ProjectStatus[] = ['Enquiry', 'Survey', 'Approved', 'Installation', 'Completed'];

export default function DirectorDashboard() {
  const { projects } = useDirectorData();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [sortKey, setSortKey] = useState<'capacity' | 'progress'>('progress');
  const [page, setPage] = useState(1);
  const pageSize = 4;

  const statusCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    statuses.forEach((s) => (counts[s] = 0));
    projects.forEach((p) => { counts[p.status] = (counts[p.status] || 0) + 1; });
    return counts;
  }, []);

  const filtered = useMemo(() => {
    return projects.filter((p) => {
      const q = search.toLowerCase();
      const matchSearch = !q || p.name.toLowerCase().includes(q) || p.customer.toLowerCase().includes(q) || p.id.toLowerCase().includes(q);
      const matchStatus = statusFilter === 'All' || p.status === statusFilter;
      const matchFrom = !fromDate || p.createdAt >= fromDate;
      const matchTo = !toDate || p.createdAt <= toDate;
      return matchSearch && matchStatus && matchFrom && matchTo;
    }).sort((a, b) => b[sortKey] - a[sortKey]);
  }, [search, statusFilter, fromDate, toDate, sortKey]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const columns = [
    { key: 'id', label: 'Project ID' },
    { key: 'name', label: 'Project' },
    { key: 'customer', label: 'Customer' },
    { key: 'capacity', label: 'Capacity (kW)' },
    { key: 'type', label: 'Type' },
    { key: 'status', label: 'Status' },
    { key: 'salesExec', label: 'Sales Exec' },
    { key: 'progress', label: 'Progress' },
  ];

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-[#1E293B]">Director Dashboard</h1>
          <p className="text-[#64748B]">Monitor solar projects, installation progress and business performance. (Demo data)</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <KpiCard label="Total Projects" value={projects.length} accent="blue" icon={<FolderKanban className="h-4 w-4" />} />
          <KpiCard label="Active Projects" value={projects.filter(p=>p.status!=='Completed').length} accent="green" icon={<Activity className="h-4 w-4" />} />
          <KpiCard label="Completed Installations" value={directorKpis.completedInstallations} accent="green" icon={<CheckCircle2 className="h-4 w-4" />} />
          <KpiCard label="Pending Approvals" value={directorKpis.pendingApprovals} accent="amber" icon={<AlertTriangle className="h-4 w-4" />} />
          <KpiCard label="Total Revenue" value={directorKpis.totalRevenue} accent="blue" icon={<IndianRupee className="h-4 w-4" />} />
          <KpiCard label="Outstanding Payments" value={directorKpis.outstandingPayments} accent="red" icon={<Wallet className="h-4 w-4" />} />
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] p-5 shadow-sm">
          <h2 className="font-semibold text-[#1E293B] mb-3">Business Analytics</h2>
          <div className="flex flex-wrap gap-3 mb-4">
            <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm bg-white" />
            <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm bg-white" />
            <select value={sortKey} onChange={(e) => setSortKey(e.target.value as any)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm bg-white">
              <option value="progress">Sort by progress</option>
              <option value="capacity">Sort by capacity</option>
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-[#64748B] mb-2">Monthly project creation (demo)</div>
              {[6, 9, 12, 8, 14].map((v, i) => (
                <div key={i} className="flex items-center gap-2 mb-1.5">
                  <span className="text-xs w-12 text-[#64748B]">M{i + 1}</span>
                  <div className="flex-1 h-2 bg-[#E2E8F0] rounded"><div className="h-2 bg-[#16865B] rounded" style={{ width: `${v * 5}%` }} /></div>
                  <span className="text-xs w-6 text-[#64748B]">{v}</span>
                </div>
              ))}
            </div>
            <div>
              <div className="text-sm text-[#64748B] mb-2">Project status distribution</div>
              {statuses.map((s) => {
                const count = statusCounts[s] || 0;
                const pct = projects.length ? Math.round((count / projects.length) * 100) : 0;
                return (
                  <div key={s} className="flex items-center gap-2 mb-1.5">
                    <span className="text-xs w-24 text-[#64748B]">{s}</span>
                    <div className="flex-1 h-2 bg-[#E2E8F0] rounded"><div className="h-2 bg-[#2878C7] rounded" style={{ width: `${pct}%` }} /></div>
                    <span className="text-xs w-10 text-[#64748B]">{count} ({pct}%)</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] p-5 shadow-sm">
          <h2 className="font-semibold text-[#1E293B] mb-3">Project Management</h2>
          <div className="flex flex-wrap gap-3 mb-3">
            <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder="Search projects" className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm flex-1 min-w-[200px] bg-white" />
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm bg-white">
              <option value="All">All statuses</option>
              {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          {pageRows.length === 0 ? (
            <EmptyState title="No projects found" message="Adjust filters or search." />
          ) : (
            <DataTable columns={columns} rows={pageRows.map((p) => ({ ...p, capacity: `${p.capacity} kW`, progress: `${p.progress}%`, status: p.status }))} />
          )}
          <div className="flex items-center justify-between mt-4 text-sm text-[#64748B]">
            <span>Page {currentPage} of {totalPages}</span>
            <div className="flex gap-2">
              <button disabled={currentPage <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))} className="px-3 py-1.5 border border-[#E2E8F0] rounded-md disabled:opacity-50 hover:bg-[#F4F7FA]">Prev</button>
              <button disabled={currentPage >= totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))} className="px-3 py-1.5 border border-[#E2E8F0] rounded-md disabled:opacity-50 hover:bg-[#F4F7FA]">Next</button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border border-[#E2E8F0] p-5 shadow-sm">
            <h2 className="font-semibold text-[#1E293B] mb-3">Operations Monitoring</h2>
            <ul className="text-sm space-y-2 text-[#1E293B]">
              <li className="flex justify-between"><span>Surveys awaiting approval</span><StatusBadge text="4" type="warning" /></li>
              <li className="flex justify-between"><span>Quotations awaiting approval</span><StatusBadge text="3" type="warning" /></li>
              <li className="flex justify-between"><span>Pending installations</span><StatusBadge text="7" type="info" /></li>
              <li className="flex justify-between"><span>Scheduled installations</span><StatusBadge text="5" type="info" /></li>
              <li className="flex justify-between"><span>Delayed projects</span><StatusBadge text="2" type="danger" /></li>
              <li className="flex justify-between"><span>Technician workload</span><StatusBadge text="15 active" type="success" /></li>
            </ul>
          </div>
          <div className="bg-white rounded-lg border border-[#E2E8F0] p-5 shadow-sm">
            <h2 className="font-semibold text-[#1E293B] mb-3">Important Alerts</h2>
            <ul className="text-sm space-y-2">
              {directorAlerts.map((a) => (
                <li key={a.id} className="flex items-center justify-between gap-2">
                  <span className="text-[#1E293B]">{a.text}</span>
                  <StatusBadge text={a.ref} type="danger" />
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border border-[#E2E8F0] p-5 shadow-sm">
            <h2 className="font-semibold text-[#1E293B] mb-3">Recent Activities</h2>
            <ul className="text-sm space-y-3">
              {directorActivities.map((a) => (
                <li key={a.id} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-[#16865B]" />
                  <div className="flex-1">
                    <div className="text-[#1E293B]">{a.text}</div>
                    <div className="text-xs text-[#64748B]">{a.ref} · {a.date}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-white rounded-lg border border-[#E2E8F0] p-5 shadow-sm">
            <h2 className="font-semibold text-[#1E293B] mb-3">Solar Business Insights</h2>
            <div className="text-sm space-y-2 text-[#1E293B]">
              <div>Total installed capacity: <strong>{directorInsights.totalCapacity}</strong></div>
              {[
                ['Residential', directorInsights.residential, '#16865B'],
                ['Factory', directorInsights.factory, '#2878C7'],
                ['On-Grid', directorInsights.onGrid, '#16865B'],
                ['Off-Grid', directorInsights.offGrid, '#E8A83E'],
              ].map(([label, val, color]) => (
                <div key={label as string} className="flex items-center gap-2">
                  <span className="w-20 text-[#64748B]">{label}</span>
                  <div className="flex-1 h-2 bg-[#E2E8F0] rounded"><div className="h-2 rounded" style={{ width: `${val}%`, backgroundColor: color as string }} /></div>
                  <span className="text-xs text-[#64748B] w-8">{val}%</span>
                </div>
              ))}
              <div className="mt-2 text-[#64748B]">Package performance</div>
              {directorInsights.packagePerformance.map((p) => (
                <div key={p.name} className="flex items-center gap-2">
                  <span className="w-16 text-xs text-[#64748B]">{p.name}</span>
                  <div className="flex-1 h-2 bg-[#E2E8F0] rounded"><div className="h-2 bg-[#E8A83E] rounded" style={{ width: `${p.value}%` }} /></div>
                  <span className="text-xs text-[#64748B] w-8">{p.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}
