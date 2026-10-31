import { useMemo, useState } from 'react';
import { WorkspaceLayout } from '../layouts/WorkspaceLayout';
import { KpiCard } from '../components/common/KpiCard';
import { DataTable } from '../components/common/DataTable';
import { EmptyState } from '../components/common/EmptyState';
import { StatusBadge } from '../components/common/StatusBadge';
import type { Package } from '../data/directorModulesData';
import { useDirectorData } from '../context/DirectorDataContext';
import { Pencil, Power, Plus, X } from 'lucide-react';

export default function PackagesPage() {
  const { packages, setPackages } = useDirectorData();
  const [search, setSearch] = useState('');
  const [config, setConfig] = useState('All');
  const [availability, setAvailability] = useState('All');
  const [form, setForm] = useState<Partial<Package>>({});
  const [editing, setEditing] = useState<Package | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [feedback, setFeedback] = useState('');

  const filtered = useMemo(() => packages.filter((p) => {
    const q = search.toLowerCase();
    const matchSearch = !q || p.name.toLowerCase().includes(q) || p.id.toLowerCase().includes(q);
    const matchConfig = config === 'All' || p.config === config;
    const matchAvail = availability === 'All' || (availability === 'Available' ? p.available : !p.available);
    return matchSearch && matchConfig && matchAvail;
  }), [packages, search, config, availability]);

  const toggle = (id: string) => {
    setPackages((prev) => prev.map((p) => (p.id === id ? { ...p, available: !p.available } : p)));
    setFeedback('Package status updated');
    setTimeout(() => setFeedback(''), 2500);
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!form.name?.trim()) newErrors.name = 'Package name is required';
    if (form.capacity === undefined || form.capacity === null || Number(form.capacity) <= 0) newErrors.capacity = 'Valid capacity is required';
    if (form.price === undefined || form.price === null || Number(form.price) < 0) newErrors.price = 'Valid price is required';
    if (!form.panels?.trim()) newErrors.panels = 'Panel specification is required';
    if (!form.inverter?.trim()) newErrors.inverter = 'Inverter specification is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const openCreate = () => {
    setEditing(null);
    setForm({ config: 'On-Grid', available: true, battery: 'N/A' });
    setErrors({});
    setShowForm(true);
    setFeedback('');
  };

  const openEdit = (p: Package) => {
    setEditing(p);
    setForm({ ...p });
    setErrors({});
    setShowForm(true);
    setFeedback('');
  };

  const save = () => {
    if (!validate()) return;
    if (editing) {
      setPackages((prev) => prev.map((p) => (p.id === editing.id ? { ...p, ...form, capacity: Number(form.capacity), price: Number(form.price) } as Package : p)));
      setFeedback('Package updated successfully');
    } else {
      const np: Package = {
        id: form.id?.trim() || `PKG-${Date.now()}`,
        name: form.name!.trim(),
        capacity: Number(form.capacity),
        config: (form.config as any) || 'On-Grid',
        price: Number(form.price),
        available: form.available ?? true,
        panels: form.panels!.trim(),
        inverter: form.inverter!.trim(),
        battery: form.battery?.trim() || 'N/A',
      };
      setPackages((prev) => [np, ...prev]);
      setFeedback('Package created successfully');
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
    { key: 'id', label: 'Package ID' },
    { key: 'name', label: 'Name' },
    { key: 'capacity', label: 'Capacity (kW)' },
    { key: 'config', label: 'Config' },
    { key: 'price', label: 'Price' },
    { key: 'panels', label: 'Panels' },
    { key: 'inverter', label: 'Inverter' },
    { key: 'battery', label: 'Battery' },
    { key: 'available', label: 'Status' },
    { key: 'actions', label: 'Actions' },
  ];

  const rows = filtered.map((p) => ({
    ...p,
    price: `₹${p.price.toLocaleString('en-IN')}`,
    available: p.available ? <StatusBadge text="Available" type="success" /> : <StatusBadge text="Inactive" type="neutral" />,
    actions: (
      <div className="flex items-center gap-2">
        <button onClick={() => openEdit(p)} className="inline-flex items-center gap-1 px-2 py-1 text-xs text-[#1E293B] hover:bg-[#F4F7FA] rounded-md transition-colors" title="Edit package">
          <Pencil className="h-3.5 w-3.5" /> Edit
        </button>
        <button onClick={() => toggle(p.id)} className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors ${p.available ? 'text-[#E8A83E] hover:bg-amber-50' : 'text-[#16865B] hover:bg-green-50'}`} title={p.available ? 'Deactivate package' : 'Activate package'}>
          <Power className="h-3.5 w-3.5" /> {p.available ? 'Deactivate' : 'Activate'}
        </button>
      </div>
    ),
  }));

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold text-[#1E293B]">Packages</h1>
            <p className="text-sm text-[#64748B] mt-1">Manage solar package offerings and pricing</p>
          </div>
          <button onClick={openCreate} className="inline-flex items-center gap-2 px-4 py-2 bg-[#16865B] text-white rounded-md text-sm hover:bg-[#147a52] transition-colors shadow-sm">
            <Plus className="h-4 w-4" /> New Package
          </button>
        </div>

        {feedback && (
          <div className="bg-[#F0FDF4] border border-[#86EFAC] text-[#166534] px-4 py-2 rounded-md text-sm">
            {feedback}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard label="Total Packages" value={packages.length} accent="blue" />
          <KpiCard label="Available" value={packages.filter(p => p.available).length} accent="green" />
          <KpiCard label="On-Grid" value={packages.filter(p => p.config === 'On-Grid').length} accent="blue" />
        </div>

        {showForm && (
          <div className="bg-white rounded-lg border border-[#E2E8F0] shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0] bg-[#F8FAFC]">
              <h2 className="font-semibold text-[#1E293B]">{editing ? 'Edit Package' : 'Create Package'}</h2>
              <button onClick={closeForm} className="text-[#64748B] hover:text-[#1E293B] transition-colors" title="Close">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Package Name *</label>
                  <input value={form.name || ''} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g., 3 kW Hybrid Home" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.name ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.name && <p className="text-xs text-[#D94B4B] mt-1">{errors.name}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Package ID</label>
                  <input value={form.id || ''} onChange={(e) => setForm({ ...form, id: e.target.value })} placeholder="Auto-generated if empty" className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Capacity (kW) *</label>
                  <input type="number" min="1" max="5" value={form.capacity ?? ''} onChange={(e) => setForm({ ...form, capacity: e.target.value as any })} placeholder="1-5" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.capacity ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.capacity && <p className="text-xs text-[#D94B4B] mt-1">{errors.capacity}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Configuration</label>
                  <select value={form.config || 'On-Grid'} onChange={(e) => setForm({ ...form, config: e.target.value as any })} className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                    <option value="On-Grid">On-Grid</option>
                    <option value="Off-Grid">Off-Grid</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Price (₹) *</label>
                  <input type="number" min="0" value={form.price ?? ''} onChange={(e) => setForm({ ...form, price: e.target.value as any })} placeholder="e.g., 135000" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.price ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.price && <p className="text-xs text-[#D94B4B] mt-1">{errors.price}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Availability</label>
                  <select value={form.available === false ? 'false' : 'true'} onChange={(e) => setForm({ ...form, available: e.target.value === 'true' })} className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                    <option value="true">Available</option>
                    <option value="false">Inactive</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Panels *</label>
                  <input value={form.panels || ''} onChange={(e) => setForm({ ...form, panels: e.target.value })} placeholder="e.g., 8x 375W" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.panels ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.panels && <p className="text-xs text-[#D94B4B] mt-1">{errors.panels}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Inverter *</label>
                  <input value={form.inverter || ''} onChange={(e) => setForm({ ...form, inverter: e.target.value })} placeholder="e.g., 3kW Hybrid" className={`w-full border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7] ${errors.inverter ? 'border-[#D94B4B]' : 'border-[#E2E8F0]'}`} />
                  {errors.inverter && <p className="text-xs text-[#D94B4B] mt-1">{errors.inverter}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Battery</label>
                  <input value={form.battery || ''} onChange={(e) => setForm({ ...form, battery: e.target.value })} placeholder="e.g., 5kWh LFP or N/A" className="w-full border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
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
            <h2 className="font-semibold text-[#1E293B] mb-3">Package List</h2>
            <div className="flex flex-wrap items-center gap-3">
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by package name or ID" className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm flex-1 min-w-[240px] focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]" />
              <select value={config} onChange={(e) => setConfig(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All configs</option>
                <option value="On-Grid">On-Grid</option>
                <option value="Off-Grid">Off-Grid</option>
              </select>
              <select value={availability} onChange={(e) => setAvailability(e.target.value)} className="border border-[#E2E8F0] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2878C7]/20 focus:border-[#2878C7]">
                <option value="All">All status</option>
                <option value="Available">Available</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
          </div>
          <div className="p-5">
            {filtered.length === 0 ? (
              <EmptyState title="No packages found" message="Try adjusting your search or filters." />
            ) : (
              <DataTable columns={columns} rows={rows as any} />
            )}
          </div>
        </div>
      </div>
    </WorkspaceLayout>
  );
}
