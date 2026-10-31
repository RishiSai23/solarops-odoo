import { useMemo, useState } from 'react';
import { WorkspaceLayout } from '../layouts/WorkspaceLayout';
import { KpiCard } from '../components/common/KpiCard';
import { DataTable } from '../components/common/DataTable';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import type { Survey } from '../data/directorModulesData';
import { useDirectorData } from '../context/DirectorDataContext';
import { Eye, CheckCircle, XCircle, Calendar, UserCheck, X } from 'lucide-react';

export default function SurveysPage() {
  const { surveys, setSurveys } = useDirectorData();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('All');
  const [tech, setTech] = useState('All');
  const [selected, setSelected] = useState<Survey | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [scheduleModal, setScheduleModal] = useState<Survey | null>(null);
  const [assignModal, setAssignModal] = useState<Survey | null>(null);
  const [newDate, setNewDate] = useState('');
  const [newTech, setNewTech] = useState('');
  const [feedback, setFeedback] = useState('');

  const filtered = useMemo(() => surveys.filter((s) =>
    (!search || s.id.toLowerCase().includes(search.toLowerCase()) || s.customer.toLowerCase().includes(search.toLowerCase()) || s.projectId.toLowerCase().includes(search.toLowerCase())) &&
    (status === 'All' || s.status === status) &&
    (tech === 'All' || s.technician === tech)
  ), [surveys, search, status, tech]);

  const approve = (id: string) => {
    setSurveys((prev) => prev.map((s) => (s.id === id ? { ...s, status: 'Approved' } : s)));
    setFeedback('Survey approved successfully');
    setTimeout(() => setFeedback(''), 2500);
  };

  const reject = (id: string) => {
    if (!rejectReason.trim()) { alert('Rejection reason is required'); return; }
    setSurveys((prev) => prev.map((s) => (s.id === id ? { ...s, status: 'Rejected', notes: rejectReason } : s)));
    setFeedback('Survey rejected');
    setRejectReason('');
    setSelected(null);
    setTimeout(() => setFeedback(''), 2500);
  };

  const schedule = () => {
    if (!scheduleModal || !newDate) { alert('Please select a date'); return; }
    setSurveys((prev) => prev.map((s) => (s.id === scheduleModal.id ? { ...s, scheduled: newDate, status: 'Scheduled' } : s)));
    setFeedback('Survey scheduled successfully');
    setScheduleModal(null);
    setNewDate('');
    setTimeout(() => setFeedback(''), 2500);
  };

  const assign = () => {
    if (!assignModal || !newTech.trim()) { alert('Please select/enter a technician'); return; }
    setSurveys((prev) => prev.map((s) => (s.id === assignModal.id ? { ...s, technician: newTech.trim() } : s)));
    setFeedback('Technician assigned successfully');
    setAssignModal(null);
    setNewTech('');
    setTimeout(() => setFeedback(''), 2500);
  };

  const getStatusBadge = (s: string) => {
    if (s === 'Approved') return <StatusBadge text={s} type="success" />;
    if (s === 'Submitted') return <StatusBadge text={s} type="warning" />;
    if (s === 'Scheduled') return <StatusBadge text={s} type="info" />;
    if (s === 'Rejected') return <StatusBadge text={s} type="danger" />;
    return <StatusBadge text={s} type="neutral" />;
  };

  const columns = [
    { key: 'id', label: 'Survey ID' },
    { key: 'projectId', label: 'Project ID' },
    { key: 'customer', label: 'Customer' },
    { key: 'location', label: 'Location' },
    { key: 'technician', label: 'Technician' },
    { key: 'scheduled', label: 'Scheduled' },
    { key: 'submitted', label: 'Submitted' },
    { key: 'status', label: 'Status' },
    { key: 'actions', label: 'Actions' },
  ];

  const technicianList = Array.from(new Set(surveys.map(s => s.technician).filter(Boolean)));

  const rows = filtered.map((s) => ({
    ...s,
    submitted: s.submitted || '-',
    status: getStatusBadge(s.status),
    actions: (
      <div className="flex flex-wrap items-center gap-1.5">
        <button onClick={() => setSelected(s)} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#2878C7] hover:bg-blue-50 rounded-md transition-colors" title="View details">
          <Eye className="h-3.5 w-3.5" /> View
        </button>
        <button onClick={() => { setScheduleModal(s); setNewDate(s.scheduled || ''); }} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#1E293B] hover:bg-[#F4F7FA] rounded-md transition-colors" title="Schedule/Reschedule">
          <Calendar className="h-3.5 w-3.5" /> Schedule
        </button>
        <button onClick={() => { setAssignModal(s); setNewTech(s.technician || ''); }} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#1E293B] hover:bg-[#F4F7FA] rounded-md transition-colors" title="Assign/Reassign">
          <UserCheck className="h-3.5 w-3.5" /> Assign
        </button>
        {s.status === 'Submitted' && (
          <>
            <button onClick={() => approve(s.id)} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#16865B] hover:bg-green-50 rounded-md transition-colors" title="Approve survey">
              <CheckCircle className="h-3.5 w-3.5" /> Approve
            </button>
            <button onClick={() => { setSelected(s); setRejectReason(''); }} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#D94B4B] hover:bg-red-50 rounded-md transition-colors" title="Reject survey">
              <XCircle className="h-3.5 w-3.5" /> Reject
            </button>
          </>
        )}
      </div>
    ),
  }));

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-[#1E293B]">Surveys</h1>
          <p className="text-sm text-[#64748B] mt-1">Manage site surveys, assignments and approvals</p>
        </div>

        {feedback && (
          <div className="bg-[#F0FDF4] border border-[#86EFAC] text-[#166534] px-4 py-2 rounded-md text-sm">
            {feedback}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Total Surveys" value={surveys.length} accent="blue" />
          <KpiCard label="Scheduled" value={surveys.filter(s => s.status === 'Scheduled').length} accent="blue" />
          <KpiCard label="Submitted" value={surveys.filter(s => s.status === 'Submitted').length} accent="amber" />
          <KpiCard label="Pending Approvals" value={surveys.filter(s => s.status === 'Submitted').length} accent="amber" />
        </div>

        <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden">
          <div className="p-5 border-b border-[#E2E8F0] bg-[#F8FAFC]">
            <h2 className="font-semibold text-[#1E293B] mb-3">Survey List</h2>
            <div className="flex flex-wrap items-center gap-3">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by survey, project or customer" className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm flex-1 min-w-[240px] focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
              <select value={status} onChange={(e) => setStatus(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All statuses</option>
                {['Scheduled', 'Submitted', 'Approved', 'Rejected'].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
              <select value={tech} onChange={(e) => setTech(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All technicians</option>
                {technicianList.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div className="p-5">
            {filtered.length === 0 ? (
              <EmptyState title="No surveys found" message="Try adjusting your search or filters." />
            ) : (
              <DataTable columns={columns} rows={rows as any} />
            )}
          </div>
        </div>

        {selected && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-auto">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
                <h2 className="font-semibold text-[#1E293B]">Survey Details - {selected.id}</h2>
                <button onClick={() => { setSelected(null); setRejectReason(''); }} className="text-[#64748B] hover:text-[#1E293B]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-5 space-y-3 text-sm">
                <div className="flex justify-between"><span className="text-[#64748B]">Project ID</span><span className="font-medium text-[#1E293B]">{selected.projectId}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Customer</span><span className="font-medium text-[#1E293B]">{selected.customer}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Location</span><span className="font-medium text-[#1E293B]">{selected.location}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Technician</span><span className="font-medium text-[#1E293B]">{selected.technician}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Scheduled</span><span className="font-medium text-[#1E293B]">{selected.scheduled || '-'}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Submitted</span><span className="font-medium text-[#1E293B]">{selected.submitted || '-'}</span></div>
                <div className="flex justify-between"><span className="text-[#64748B]">Status</span><span className="font-medium text-[#1E293B]">{selected.status}</span></div>
                <div>
                  <div className="text-[#64748B] mb-1">Notes</div>
                  <div className="p-3 bg-[#F8FAFC] rounded-md text-[#1E293B]">{selected.notes || 'No notes available'}</div>
                </div>
                {selected.status === 'Submitted' && (
                  <div className="pt-2 space-y-2">
                    <label className="block text-sm font-medium text-[#1E293B]">Rejection Reason *</label>
                    <textarea value={rejectReason} onChange={(e) => setRejectReason(e.target.value)} placeholder="Enter reason for rejection" className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" rows={3} />
                  </div>
                )}
              </div>
              <div className="px-5 py-4 border-t border-[#E2E8F0] flex flex-wrap gap-2">
                {selected.status === 'Submitted' && (
                  <>
                    <button onClick={() => approve(selected.id)} className="px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52]">Approve</button>
                    <button onClick={() => reject(selected.id)} className="px-4 py-2 bg-[#D94B4B] text-white rounded-md text-sm hover:bg-[#c43f3f]">Reject with Reason</button>
                  </>
                )}
                <button onClick={() => { setSelected(null); setRejectReason(''); }} className="px-4 py-2 border border-[#E2E8F0] text-[#1E293B] rounded-md text-sm hover:bg-[#F4F7FA]">Close</button>
              </div>
            </div>
          </div>
        )}

        {scheduleModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
                <h2 className="font-semibold text-[#1E293B]">Schedule/Reschedule Survey</h2>
                <button onClick={() => { setScheduleModal(null); setNewDate(''); }} className="text-[#64748B] hover:text-[#1E293B]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-5 space-y-3">
                <div>
                  <div className="text-sm text-[#64748B] mb-1">Survey: {scheduleModal.id}</div>
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
                  <div className="text-sm text-[#64748B] mb-1">Survey: {assignModal.id}</div>
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
