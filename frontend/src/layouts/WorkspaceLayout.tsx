import React, { useState } from 'react';
import { Sidebar } from '../components/navigation/Sidebar';
import { Header } from '../components/navigation/Header';

interface WorkspaceLayoutProps {
  children: React.ReactNode;
}

export function WorkspaceLayout({ children }: WorkspaceLayoutProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="flex h-screen bg-[#F4F7FA] text-[#1E293B]">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      {open && <div className="fixed inset-0 bg-black/40 z-20 md:hidden" onClick={() => setOpen(false)} />}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuToggle={() => setOpen((v) => !v)} />
        <main className="flex-1 overflow-auto p-5">{children}</main>
      </div>
    </div>
  );
}
export default WorkspaceLayout;
