import { useState } from 'react';
import { downloadCsv } from '../utils/csv';
import { WorkspaceLayout } from '../layouts/WorkspaceLayout';
import { KpiCard } from '../components/common/KpiCard';
import { useDirectorData } from '../context/DirectorDataContext';
import { FileText, Download, Calendar } from 'lucide-react';

const reportTypes = [
  { id: 'sales', label: 'Sales Reports', description: 'Revenue, quotations and orders' },
  { id: 'projects', label: 'Project Reports', description: 'Project status and pipeline' },
  { id: 'surveys', label: 'Survey Reports', description: 'Survey approvals and assignments' },
  { id: 'installations', label: 'Installation Reports', description: 'Installation progress and commissioning' },
  { id: 'financial', label: 'Financial Reports', description: 'Payments and outstanding' },
];

export default function ReportsPage() {
  const { projects, surveys, installations, packages } = useDirectorData();
  const [selectedReport, setSelectedReport] = useState('projects');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [feedback, setFeedback] = useState('');

  const exportProjects = () => {
    const data = projects.map(p => ({
      projectId: p.id,
      projectName: p.name,
      customer: p.customer,
      capacityKw: p.capacity,
      type: p.type,
      system: p.system,
      status: p.status,
      salesExec: p.salesExec,
      progress: p.progress,
      createdAt: p.createdAt,
    }));
    downloadCsv('projects-report.csv', data);
    setFeedback('Projects report exported successfully');
    setTimeout(() => setFeedback(''), 2500);
  };

  const exportSurveys = () => {
    const data = surveys.map(s => ({
      surveyId: s.id,
      projectId: s.projectId,
      customer: s.customer,
      location: s.location,
      technician: s.technician,
      scheduled: s.scheduled,
      submitted: s.submitted || '',
      status: s.status,
      notes: s.notes || '',
    }));
    downloadCsv('surveys-report.csv', data);
    setFeedback('Surveys report exported successfully');
    setTimeout(() => setFeedback(''), 2500);
  };

  const exportInstallations = () => {
    const data = installations.map(i => ({
      installationId: i.id,
      projectId: i.projectId,
      customer: i.customer,
      location: i.location,
      capacityKw: i.capacity,
      technician: i.technician,
      scheduled: i.scheduled,
      status: i.status,
      progress: i.progress,
      commissioning: i.commissioning,
    }));
    downloadCsv('installations-report.csv', data);
    setFeedback('Installations report exported successfully');
    setTimeout(() => setFeedback(''), 2500);
  };

  const exportPackages = () => {
    const data = packages.map(p => ({
      packageId: p.id,
      name: p.name,
      capacityKw: p.capacity,
      config: p.config,
      price: p.price,
      available: p.available ? 'Yes' : 'No',
      panels: p.panels,
      inverter: p.inverter,
      battery: p.battery,
    }));
    downloadCsv('packages-report.csv', data);
    setFeedback('Packages report exported successfully');
    setTimeout(() => setFeedback(''), 2500);
  };

  const handleExport = () => {
    if (selectedReport === 'projects') exportProjects();
    else if (selectedReport === 'surveys') exportSurveys();
    else if (selectedReport === 'installations') exportInstallations();
    else if (selectedReport === 'packages') exportPackages();
    else {
      alert('This report type is under preparation');
    }
  };

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-[#1E293B]">Reports</h1>
          <p className="text-sm text-[#64748B] mt-1">Generate and export business reports</p>
        </div>

        {feedback && (
          <div className="bg-[#F0FDF4] border border-[#86EFAC] text-[#166534] px-4 py-2 rounded-md text-sm">
            {feedback}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Total Projects" value={projects.length} accent="blue" />
          <KpiCard label="Total Surveys" value={surveys.length} accent="blue" />
          <KpiCard label="Total Installations" value={installations.length} accent="amber" />
          <KpiCard label="Total Packages" value={packages.length} accent="green" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
              <h2 className="font-semibold text-[#1E293B]">Report Categories</h2>
              <p className="text-sm text-[#64748B] mt-1">Select a report type to generate and export</p>
            </div>
            <div className="p-5 space-y-2">
              {reportTypes.map((rt) => (
                <button
                  key={rt.id}
                  onClick={() => setSelectedReport(rt.id)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                    selectedReport === rt.id
                      ? 'border-[#2878C7] bg-blue-50/50 shadow-sm'
                      : 'border-[#E2E8F0] hover:border-[#CBD5E1] hover:bg-[#F8FAFC]'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <FileText className={`h-5 w-5 mt-0.5 ${selectedReport === rt.id ? 'text-[#2878C7]' : 'text-[#64748B]'}`} />
                    <div>
                      <div className={`font-medium ${selectedReport === rt.id ? 'text-[#1E293B]' : 'text-[#1E293B]'}`}>{rt.label}</div>
                      <div className="text-sm text-[#64748B] mt-0.5">{rt.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden h-fit">
            <div className="px-5 py-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
              <h2 className="font-semibold text-[#1E293B]">Filters & Export</h2>
              <p className="text-sm text-[#64748B] mt-1">Configure and download report</p>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Selected Report</label>
                <div className="px-3 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-md text-sm text-[#1E293B]">
                  {reportTypes.find(r => r.id === selectedReport)?.label}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Date Range</label>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-[#64748B]" />
                    <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className="flex-1 border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-[#64748B]" />
                    <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} className="flex-1 border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
                  </div>
                </div>
                <p className="text-xs text-[#64748B] mt-1">Date filters apply where applicable</p>
              </div>
              <button onClick={handleExport} className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52] transition-colors shadow-sm">
                <Download className="h-4 w-4" /> Export as CSV
              </button>
              <p className="text-xs text-[#64748B] text-center">Exports are generated from current shared data</p>
            </div>
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}
