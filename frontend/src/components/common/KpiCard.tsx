import { clsx } from 'clsx';

export interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string;
  accent?: 'green' | 'blue' | 'amber' | 'red';
  icon?: React.ReactNode;
}

const accentMap: Record<string, string> = {
  green: 'bg-[#E8F5EE] text-[#16865B]',
  blue: 'bg-[#EAF3FC] text-[#2878C7]',
  amber: 'bg-[#FFF5E5] text-[#E8A83E]',
  red: 'bg-[#FCECEC] text-[#D94B4B]',
};

export function KpiCard({ label, value, delta, accent = 'green', icon }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-[#E2E8F0] bg-white p-4 shadow-sm flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-[#64748B]">{label}</span>
        {icon && <span className={clsx('h-8 w-8 rounded-md flex items-center justify-center', accentMap[accent])}>{icon}</span>}
      </div>
      <span className="text-2xl font-semibold text-[#1E293B]">{value}</span>
      {delta && <span className="text-xs text-[#64748B]">{delta}</span>}
    </div>
  );
}
export default KpiCard;
