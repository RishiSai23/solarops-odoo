import { useMemo, useState } from 'react';
import { WorkspaceLayout } from '../layouts/WorkspaceLayout';
import { KpiCard } from '../components/common/KpiCard';
import { DataTable } from '../components/common/DataTable';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import type { DirectorProject } from '../data/directorDashboardData';
import { useDirectorData } from '../context/DirectorDataContext';
import { Eye, Pencil, Plus, X } from 'lucide-react';

const projectStatuses = ['Enquiry', 'Survey', 'Approved', 'Installation', 'Completed'] as const;

export default function ProjectsPage() {
  const { projects, setProjects } = useDirectorData();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [sortKey, setSortKey] = useState<'createdAt' | 'capacity' | 'progress'>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const pageSize = 6;

  const [editing, setEditing] = useState<DirectorProject | null>(null);
  const [form, setForm] = useState<Partial<DirectorProject>>({});
  const [showForm, setShowForm] = useState(false);
  const [viewing, setViewing] = useState<DirectorProject | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState<string>('');

  const filtered = useMemo(() => {
    const result = projects.filter((p) => {
      const q = search.toLowerCase();
      const matchSearch = !q || p.name.toLowerCase().includes(q) || p.customer.toLowerCase().includes(q) || p.id.toLowerCase().includes(q);
      const matchStatus = status === 'All' || p.status === status;
      const matchType = typeFilter === 'All' || p.type === typeFilter;
      return matchSearch && matchStatus && matchType;
    });
    return result.sort((a, b) => {
      if (sortKey === 'createdAt') {
        return sortOrder === 'desc' ? b.createdAt.localeCompare(a.createdAt) : a.createdAt.localeCompare(b.createdAt);
      }
      if (sortKey === 'capacity') {
        return sortOrder === 'desc' ? b.capacity - a.capacity : a.capacity - b.capacity;
      }
      if (sortKey === 'progress') {
        return sortOrder === 'desc' ? b.progress - a.progress : a.progress - b.progress;
      }
      return 0;
    });
  }, [projects, search, status, typeFilter, sortKey, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!form.name?.trim()) newErrors.name = 'Project name is required';
    if (!form.customer?.trim()) newErrors.customer = 'Customer name is required';
    if (form.capacity === undefined || form.capacity === null || Number(form.capacity) <= 0) newErrors.capacity = 'Valid capacity is required';
    if (!form.salesExec?.trim()) newErrors.salesExec = 'Sales executive is required';
    if (form.progress !== undefined && (Number(form.progress) < 0 || Number(form.progress) > 100)) newErrors.progress = 'Progress must be between 0 and 100';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const openCreate = () => {
    setEditing(null);
    setForm({ type: 'Residential', system: 'On-Grid', status: 'Enquiry', progress: 0 });
    setErrors({});
    setShowForm(true);
    setFeedback('');
  };

  const openEdit = (p: DirectorProject) => {
    setEditing(p);
    setForm({ ...p });
    setErrors({});
    setShowForm(true);
    setFeedback('');
  };

  const save = () => {
    if (!validate()) return;
    if (editing) {
      setProjects((prev) => prev.map((p) => (p.id === editing.id ? { ...p, ...form, capacity: Number(form.capacity), progress: Number(form.progress) || 0 } as DirectorProject : p)));
      setFeedback('Project updated successfully');
    } else {
      const newP: DirectorProject = {
        id: form.id?.trim() || `SPF-${Date.now()}`,
        name: form.name!.trim(),
        customer: form.customer!.trim(),
        capacity: Number(form.capacity),
        type: (form.type as any) || 'Residential',
        system: (form.system as any) || 'On-Grid',
        status: (form.status as any) || 'Enquiry',
        salesExec: form.salesExec!.trim(),
        progress: Number(form.progress) || 0,
        createdAt: new Date().toISOString().slice(0, 10),
      };
      setProjects((prev) => [newP, ...prev]);
      setFeedback('Project created successfully');
    }
    setEditing(null);
    setShowForm(false);
    setForm({});
    setErrors({});
    setTimeout(() => setFeedback(''), 2500);
  };

  const closeForm = () => {
    setEditing(null);
    setShowForm(false);
    setForm({});
    setErrors({});
  };

  const columns = [
    { key: 'id', label: 'Project ID' },
    { key: 'name', label: 'Project' },
    { key: 'customer', label: 'Customer' },
    { key: 'capacity', label: 'Capacity (kW)' },
    { key: 'type', label: 'Type' },
    { key: 'system', label: 'Config' },
    { key: 'salesExec', label: 'Sales Exec' },
    { key: 'status', label: 'Status' },
    { key: 'progress', label: 'Progress' },
    { key: 'createdAt', label: 'Created' },
    { key: 'actions', label: 'Actions' },
  ];

  const getStatusBadge = (status: string) => {
    if (status === 'Completed') return <StatusBadge text={status} type="success" />;
    if (status === 'Installation') return <StatusBadge text={status} type="info" />;
    if (status === 'Approved') return <StatusBadge text={status} type="info" />;
    if (status === 'Survey') return <StatusBadge text={status} type="warning" />;
    if (status === 'Enquiry') return <StatusBadge text={status} type="neutral" />;
    return <StatusBadge text={status} type="neutral" />;
  };

  const rows = pageRows.map((p) => ({
    ...p,
    capacity: `${p.capacity}`,
    system: p.system,
    status: getStatusBadge(p.status),
    progress: `${p.progress}%`,
    actions: (
      <div className="flex items-center gap-2">
        <button onClick={() => setViewing(p)} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#2878C7] hover:bg-blue-50 rounded-md transition-colors" title="View details">
          <Eye className="h-3.5 w-3.5" /> View
        </button>
        <button onClick={() => openEdit(p)} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#1E293B] hover:bg-[#F4F7FA] rounded-md transition-colors" title="Edit project">
          <Pencil className="h-3.5 w-3.5" /> Edit
        </button>
      </div>
    ),
  }));

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-[#1E293B]">Projects</h1>
            <p className="text-sm text-[#64748B] mt-1">Manage solar projects, assignments and lifecycle</p>
          </div>
          <button onClick={openCreate} className="inline-flex items-center gap-2 px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52] transition-colors shadow-sm">
            <Plus className="h-4 w-4" /> New Project
          </button>
        </div>

        {feedback && (
          <div className="bg-[#F0FDF4] border border-[#86EFAC] text-[#166534] px-4 py-2 rounded-md text-sm">
            {feedback}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Total Projects" value={projects.length} accent="blue" />
          <KpiCard label="Active Projects" value={projects.filter(p => p.status !== 'Completed').length} accent="green" />
          <KpiCard label="Completed Projects" value={projects.filter(p => p.status === 'Completed').length} accent="green" />
          <KpiCard label="Delayed Projects" value={projects.filter(p => p.status === 'Installation' && p.progress < 70).length} accent="red" />
        </div>

        {showForm && (
          <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
              <h2 className="font-semibold text-[#1E293B]">{editing ? 'Edit Project' : 'Create Project'}</h2>
              <button onClick={closeForm} className="text-[#64748B] hover:text-[#1E293B] transition-colors" title="Close">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Project Name *</label>
                  <input value={form.name || ''} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., Acme Industries Rooftop" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.name ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.name && <p className="text-xs text-[#D94B4B] mt-1">{errors.name}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Customer *</label>
                  <input value={form.customer || ''} onChange={(e) => setForm({ ...form, customer: e.target.value })} placeholder="Customer name" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.customer ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.customer && <p className="text-xs text-[#D94B4B] mt-1">{errors.customer}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Capacity (kW) *</label>
                  <input type="number" min="1" value={form.capacity ?? ''} onChange={(e) => setForm({ ...form, capacity: e.target.value as any })} placeholder="e.g., 5" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.capacity ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.capacity && <p className="text-xs text-[#D94B4B] mt-1">{errors.capacity}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Project Type</label>
                  <select value={form.type || 'Residential'} onChange={(e) => setForm({ ...form, type: e.target.value as any })} className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                    <option value="Residential">Residential</option>
                    <option value="Factory">Factory</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">System Config</label>
                  <select value={form.system || 'On-Grid'} onChange={(e) => setForm({ ...form, system: e.target.value as any })} className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                    <option value="On-Grid">On-Grid</option>
                    <option value="Off-Grid">Off-Grid</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Status</label>
                  <select value={form.status || 'Enquiry'} onChange={(e) => setForm({ ...form, status: e.target.value as any })} className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                    {projectStatuses.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Sales Executive *</label>
                  <input value={form.salesExec || ''} onChange={(e) => setForm({ ...form, salesExec: e.target.value })} placeholder="Executive name" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.salesExec ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.salesExec && <p className="text-xs text-[#D94B4B] mt-1">{errors.salesExec}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Progress (%)</label>
                  <input type="number" min="0" max="100" value={form.progress ?? 0} onChange={(e) => setForm({ ...form, progress: e.target.value as any })} className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.progress ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.progress && <p className="text-xs text-[#D94B4B] mt-1">{errors.progress}</p>}
                </div>
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                <button onClick={save} className="px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52] transition-colors">Save</button>
                <button onClick={closeForm} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA] transition-colors">Cancel</button>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden">
          <div className="p-5 border-b border-[#E2E8F0] bg-[#F8FAFC]">
            <h2 className="font-semibold text-[#1E293B] mb-3">Project List</h2>
            <div className="flex flex-wrap items-center gap-3">
              <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder="Search by project, customer or ID" className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm flex-1 min-w-[240px] focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
              <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All statuses</option>
                {projectStatuses.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <select value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All types</option>
                <option value="Residential">Residential</option>
                <option value="Factory">Factory</option>
              </select>
              <select value={`${sortKey}-${sortOrder}`} onChange={(e) => { const [k, o] = e.target.value.split('-'); setSortKey(k as any); setSortOrder(o as any); }} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="createdAt-desc">Newest first</option>
                <option value="createdAt-asc">Oldest first</option>
                <option value="capacity-desc">Capacity: High to Low</option>
                <option value="capacity-asc">Capacity: Low to High</option>
                <option value="progress-desc">Progress: High to Low</option>
                <option value="progress-asc">Progress: Low to High</option>
              </select>
            </div>
          </div>
          <div className="p-5">
            {pageRows.length === 0 ? (
              <EmptyState title="No projects found" message="Try adjusting your search or filters." />
            ) : (
              <DataTable columns={columns} rows={rows as any} />
            )}
            {filtered.length > 0 && (
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mt-4 text-sm text-[#64748B]">
                <span>Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, filtered.length)} of {filtered.length} results</span>
                <div className="flex items-center gap-2">
                  <button disabled={currentPage <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))} className="px-3 py-1.5 border border-[#E2E8F0] rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#F4F7FA] transition-colors">Prev</button>
                  <span className="px-2">Page {currentPage} of {totalPages}</span>
                  <button disabled={currentPage >= totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))} className="px-3 py-1.5 border border-[#E2E8F0] rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#F4F7FA] transition-colors">Next</button>
                </div>
              </div>
            )}
          </div>
        </div>

        {viewing && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-auto">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
                <h2 className="font-semibold text-[#1E293B]">Project Details</h2>
                <button onClick={() => setViewing(null)} className="text-[#64748B] hover:text-[#1E293B]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-5 space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-[#64748B]">Project ID</span><span className="font-medium text-[#1E293B]">{viewing.id}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Project Name</span><span className="font-medium text-[#1E293B] text-right">{viewing.name}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Customer</span><span className="font-medium text-[#1E293B]">{viewing.customer}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Capacity</span><span className="font-medium text-[#1E293B]">{viewing.capacity} kW</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Type</span><span className="font-medium text-[#1E293B]">{viewing.type}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">System</span><span className="font-medium text-[#1E293B]">{viewing.system}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Status</span><span className="font-medium text-[#1E293B]">{viewing.status}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Sales Executive</span><span className="font-medium text-[#1E293B]">{viewing.salesExec}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Progress</span><span className="font-medium text-[#1E293B]">{viewing.progress}%</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Created</span><span className="font-medium text-[#1E293B]">{viewing.createdAt}</span></div>
              </div>
              <div className="px-5 py-4 border-t border-[#E2E8F0] flex gap-2">
                <button onClick={() => { setViewing(null); openEdit(viewing); }} className="px-4 py-2 bg-[#2878C7] text-white rounded-md text-sm hover:bg-[#236bb3]">Edit Project</button>
                <button onClick={() => setViewing(null)} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Close</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </WorkspaceLayout>
  );
}
