import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FolderKanban, ClipboardCheck, Wrench, Package, FileBarChart, Sun } from 'lucide-react';

interface NavItem { label: string; to: string; icon: React.ComponentType<{ className?: string }>; }

const directorNav: NavItem[] = [
  { label: 'Overview', to: '/director', icon: LayoutDashboard },
  { label: 'Projects', to: '/director/projects', icon: FolderKanban },
  { label: 'Surveys', to: '/director/surveys', icon: ClipboardCheck },
  { label: 'Installations', to: '/director/installations', icon: Wrench },
  { label: 'Packages', to: '/director/packages', icon: Package },
  { label: 'Reports', to: '/director/reports', icon: FileBarChart },
];

interface SidebarProps { open: boolean; onClose: () => void; }

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {open && <div className="fixed inset-0 bg-black/40 z-20 md:hidden" onClick={onClose} />}
      <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:static z-30 w-64 h-full bg-[#14243B] text-slate-100 flex flex-col border-r border-[#0b152d] transition-transform`}>
        <div className="px-5 py-4 border-b border-white/10 flex items-center gap-2">
          <Sun className="h-6 w-6 text-[#16865B]" />
          <div>
            <div className="font-semibold">SunFlow Solar</div>
            <div className="text-xs text-slate-300">SunPower Solutions</div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {directorNav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.label} to={item.to} onClick={onClose} className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${isActive ? 'bg-[#1D3553] text-white' : 'text-slate-200 hover:bg-[#1D3553]/60'}`
              }>
                <Icon className="h-4 w-4" />{item.label}
              </NavLink>
            );
          })}
        </nav>
        <div className="p-4 border-t border-white/10 flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-[#16865B] flex items-center justify-center text-sm font-semibold">AD</div>
          <div className="text-sm">
            <div className="font-medium">Admin User</div>
            <div className="text-xs text-slate-300">Director</div>
          </div>
        </div>
      </aside>
    </>
  );
}
export default Sidebar;
