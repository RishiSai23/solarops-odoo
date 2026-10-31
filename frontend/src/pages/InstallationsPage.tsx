import { useMemo, useState } from 'react';
import { WorkspaceLayout } from '../layouts/WorkspaceLayout';
import { KpiCard } from '../components/common/KpiCard';
import { DataTable } from '../components/common/DataTable';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import type { Installation } from '../data/directorModulesData';
import { useDirectorData } from '../context/DirectorDataContext';
import { Eye, Calendar, UserCheck, CheckCircle, X } from 'lucide-react';

export default function InstallationsPage() {
  const { installations, setInstallations } = useDirectorData();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('All');
  const [selected, setSelected] = useState<Installation | null>(null);
  const [scheduleModal, setScheduleModal] = useState<Installation | null>(null);
  const [assignModal, setAssignModal] = useState<Installation | null>(null);
  const [newDate, setNewDate] = useState('');
  const [newTech, setNewTech] = useState('');
  const [feedback, setFeedback] = useState('');

  const filtered = useMemo(() => installations.filter((i) =>
    (!search || i.id.toLowerCase().includes(search.toLowerCase()) || i.customer.toLowerCase().includes(search.toLowerCase()) || i.projectId.toLowerCase().includes(search.toLowerCase())) &&
    (status === 'All' || i.status === status)
  ), [installations, search, status]);

  const updateStatus = (id: string, newStatus: Installation['status']) => {
    setInstallations((prev) => prev.map((i) => {
      if (i.id !== id) return i;
      const updated = { ...i, status: newStatus };
      if (newStatus === 'Completed') {
        updated.progress = 100;
        updated.commissioning = 'Completed';
      } else if (newStatus === 'In Progress' && i.progress < 50) {
        updated.progress = 60;
      } else if (newStatus === 'Scheduled') {
        updated.commissioning = 'Pending';
      }
      return updated;
    }));
    setFeedback('Installation status updated');
    setTimeout(() => setFeedback(''), 2500);
  };

  const schedule = () => {
    if (!scheduleModal || !newDate) { alert('Please select a date'); return; }
    setInstallations((prev) => prev.map((i) => (i.id === scheduleModal.id ? { ...i, scheduled: newDate, status: 'Scheduled' } : i)));
    setFeedback('Installation scheduled successfully');
    setScheduleModal(null);
    setNewDate('');
    setTimeout(() => setFeedback(''), 2500);
  };

  const assign = () => {
    if (!assignModal || !newTech.trim()) { alert('Please select/enter a technician'); return; }
    setInstallations((prev) => prev.map((i) => (i.id === assignModal.id ? { ...i, technician: newTech.trim() } : i)));
    setFeedback('Technician assigned successfully');
    setAssignModal(null);
    setNewTech('');
    setTimeout(() => setFeedback(''), 2500);
  };

  const recordCommissioning = (id: string) => {
    setInstallations((prev) => prev.map((i) => (i.id === id ? { ...i, commissioning: 'Completed', status: 'Completed', progress: 100 } : i)));
    setFeedback('Commissioning completed & installation marked done');
    setSelected(null);
    setTimeout(() => setFeedback(''), 2500);
  };

  const getStatusBadge = (s: string) => {
    if (s === 'Completed') return <StatusBadge text={s} type="success" />;
    if (s === 'In Progress') return <StatusBadge text={s} type="info" />;
    if (s === 'Scheduled') return <StatusBadge text={s} type="warning" />;
    if (s === 'Delayed') return <StatusBadge text={s} type="danger" />;
    return <StatusBadge text={s} type="neutral" />;
  };

  const technicianList = Array.from(new Set(installations.map(i => i.technician).filter(Boolean)));

  const columns = [
    { key: 'id', label: 'Installation ID' },
    { key: 'projectId', label: 'Project ID' },
    { key: 'customer', label: 'Customer' },
    { key: 'location', label: 'Location' },
    { key: 'capacity', label: 'Capacity (kW)' },
    { key: 'technician', label: 'Technician' },
    { key: 'scheduled', label: 'Scheduled' },
    { key: 'status', label: 'Status' },
    { key: 'progress', label: 'Progress' },
    { key: 'commissioning', label: 'Commissioning' },
    { key: 'actions', label: 'Actions' },
  ];

  const rows = filtered.map((i) => ({
    ...i,
    progress: `${i.progress}%`,
    status: getStatusBadge(i.status),
    commissioning: i.commissioning === 'Completed' ? <span className="text-[#16865B] font-medium">Completed</span> : <span className="text-[#E8A83E]">Pending</span>,
    actions: (
      <div className="flex flex-wrap items-center gap-1.5">
        <button onClick={() => setSelected(i)} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#2878C7] hover:bg-blue-50 rounded-md transition-colors" title="View details">
          <Eye className="h-3.5 w-3.5" /> View
        </button>
        <button onClick={() => { setScheduleModal(i); setNewDate(i.scheduled || ''); }} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#1E293B] hover:bg-[#F4F7FA] rounded-md transition-colors" title="Schedule/Reschedule">
          <Calendar className="h-3.5 w-3.5" /> Schedule
        </button>
        <button onClick={() => { setAssignModal(i); setNewTech(i.technician || ''); }} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#1E293B] hover:bg-[#F4F7FA] rounded-md transition-colors" title="Assign/Reassign">
          <UserCheck className="h-3.5 w-3.5" /> Assign
        </button>
        {i.status !== 'Completed' && (
          <select value={i.status} onChange={(e) => updateStatus(i.id, e.target.value as Installation['status'])} className="border border-[#E2E8F0] rounded-md text-xs px-2 py-1 hover:bg-[#F4F7FA] transition-colors">
            {['Scheduled', 'In Progress', 'Delayed'].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        )}
      </div>
    ),
  }));

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-[#1E293B]">Installations</h1>
          <p className="text-sm text-[#64748B] mt-1">Track installation progress, scheduling and commissioning</p>
        </div>

        {feedback && (
          <div className="bg-[#F0FDF4] border border-[#86EFAC] text-[#166534] px-4 py-2 rounded-md text-sm">
            {feedback}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <KpiCard label="Total" value={installations.length} accent="blue" />
          <KpiCard label="Scheduled" value={installations.filter(i => i.status === 'Scheduled').length} accent="amber" />
          <KpiCard label="In Progress" value={installations.filter(i => i.status === 'In Progress').length} accent="blue" />
          <KpiCard label="Completed" value={installations.filter(i => i.status === 'Completed').length} accent="green" />
          <KpiCard label="Delayed" value={installations.filter(i => i.status === 'Delayed').length} accent="red" />
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden">
          <div className="p-5 border-b border-[#E2E8F0] bg-[#F8FAFC]">
            <h2 className="font-semibold text-[#1E293B] mb-3">Installation List</h2>
            <div className="flex flex-wrap items-center gap-3">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by installation, project or customer" className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm flex-1 min-w-[240px] focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
              <select value={status} onChange={(e) => setStatus(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All statuses</option>
                {['Scheduled', 'In Progress', 'Completed', 'Delayed'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div className="p-5">
            {filtered.length === 0 ? (
              <EmptyState title="No installations found" message="Try adjusting your search or filters." />
            ) : (
              <DataTable columns={columns} rows={rows as any} />
            )}
          </div>
        </div>

        {selected && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-auto">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
                <h2 className="font-semibold text-[#1E293B]">Installation Details - {selected.id}</h2>
                <button onClick={() => setSelected(null)} className="text-[#64748B] hover:text-[#1E293B]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-5 space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-[#64748B]">Project ID</span><span className="font-medium text-[#1E293B]">{selected.projectId}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Customer</span><span className="font-medium text-[#1E293B]">{selected.customer}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Location</span><span className="font-medium text-[#1E293B]">{selected.location}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Capacity</span><span className="font-medium text-[#1E293B]">{selected.capacity} kW</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Technician</span><span className="font-medium text-[#1E293B]">{selected.technician}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Scheduled</span><span className="font-medium text-[#1E293B]">{selected.scheduled}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Status</span><span className="font-medium text-[#1E293B]">{selected.status}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Progress</span><span className="font-medium text-[#1E293B]">{selected.progress}%</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Commissioning</span><span className="font-medium text-[#1E293B]">{selected.commissioning}</span></div>
              </div>
              <div className="px-5 py-4 border-t border-[#E2E8F0] flex flex-wrap gap-2">
                {selected.commissioning === 'Pending' && selected.status !== 'Completed' && (
                  <button onClick={() => recordCommissioning(selected.id)} className="inline-flex items-center gap-1 px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52]">
                    <CheckCircle className="h-4 w-4" /> Record Commissioning & Sign-off
                  </button>
                )}
                <button onClick={() => { setSelected(null); setScheduleModal(selected); setNewDate(selected.scheduled || ''); }} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Schedule/Reschedule</button>
                <button onClick={() => { setSelected(null); setAssignModal(selected); setNewTech(selected.technician || ''); }} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Assign/Reassign</button>
                <button onClick={() => setSelected(null)} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Close</button>
              </div>
            </div>
          </div>
        )}

        {scheduleModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
                <h2 className="font-semibold text-[#1E293B]">Schedule/Reschedule Installation</h2>
                <button onClick={() => { setScheduleModal(null); setNewDate(''); }} className="text-[#64748B] hover:text-[#1E293B]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-5 space-y-3">
                <div>
                  <div className="text-sm text-[#64748B] mb-1">Installation: {scheduleModal.id}</div>
                  <div className="text-sm text-[#64748B]">Customer: {scheduleModal.customer}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Schedule Date *</label>
                  <input type="date" value={newDate} onChange={(e) => setNewDate(e.target.value)} className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
                </div>
              </div>
              <div className="px-5 py-4 border-t border-[#E2E8F0] flex gap-2">
                <button onClick={schedule} className="px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52]">Save</button>
                <button onClick={() => { setScheduleModal(null); setNewDate(''); }} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Cancel</button>
              </div>
            </div>
          </div>
        )}

        {assignModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
                <h2 className="font-semibold text-[#1E293B]">Assign/Reassign Technician</h2>
                <button onClick={() => { setAssignModal(null); setNewTech(''); }} className="text-[#64748B] hover:text-[#1E293B]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-5 space-y-3">
                <div>
                  <div className="text-sm text-[#64748B] mb-1">Installation: {assignModal.id}</div>
                  <div className="text-sm text-[#64748B]">Customer: {assignModal.customer}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Technician *</label>
                  <input value={newTech} onChange={(e) => setNewTech(e.target.value)} placeholder="Enter technician name" className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {technicianList.map(t => (
                      <button key={t} onClick={() => setNewTech(t)} className="px-2 py-1 text-xs border border-[#E2E8F0] rounded-md hover:bg-[#F4F7FA] transition-colors">{t}</button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="px-5 py-4 border-t border-[#E2E8F0] flex gap-2">
                <button onClick={assign} className="px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52]">Assign</button>
                <button onClick={() => { setAssignModal(null); setNewTech(''); }} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Cancel</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </WorkspaceLayout>
  );
}
