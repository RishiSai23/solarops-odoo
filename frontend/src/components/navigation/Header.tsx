import { Search, Bell, Menu, User } from 'lucide-react';

interface HeaderProps { onMenuToggle?: () => void; }

export function Header({ onMenuToggle }: HeaderProps) {
  return (
    <header className="bg-white border-b border-[#E2E8F0] px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button className="md:hidden" onClick={onMenuToggle} aria-label="Toggle menu"><Menu className="h-5 w-5 text-[#1E293B]" /></button>
        <div>
          <div className="font-semibold text-[#1E293B]">Director / Admin</div>
          <div className="text-sm text-[#64748B]">Home / Overview</div>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 border border-[#E2E8F0] rounded-md px-2 py-1 bg-white focus-within:ring-2 focus-within:ring-[#16865B]">
          <Search className="h-4 w-4 text-[#64748B]" />
          <input className="outline-none text-sm w-44 bg-transparent" placeholder="Search" />
        </div>
        <div className="relative">
          <Bell className="h-5 w-5 text-[#64748B]" />
          <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-[#D94B4B]" />
        </div>
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-[#E8F5EE] flex items-center justify-center"><User className="h-4 w-4 text-[#16865B]" /></div>
          <span className="hidden sm:block text-sm text-[#1E293B]">Admin User</span>
        </div>
      </div>
    </header>
  );
}
export default Header;
