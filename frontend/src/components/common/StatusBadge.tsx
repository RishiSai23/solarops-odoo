import { clsx } from 'clsx';

export type StatusBadgeType = 'success' | 'danger' | 'warning' | 'info' | string;

export interface StatusBadgeProps { text: string; type?: StatusBadgeType; }

const typeClasses: Record<string, string> = {
  success: 'text-[#16865B] border-[#16865B]/40 bg-[#E8F5EE]',
  danger: 'text-[#D94B4B] border-[#D94B4B]/40 bg-[#FCECEC]',
  warning: 'text-[#E8A83E] border-[#E8A83E]/40 bg-[#FFF5E5]',
  info: 'text-[#2878C7] border-[#2878C7]/40 bg-[#EAF3FC]',
};

export function StatusBadge({ text, type }: StatusBadgeProps) {
  return (
    <span className={clsx('inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium', typeClasses[type || ''] || 'text-[#64748B] border-[#E2E8F0] bg-white')}>
      {text}
    </span>
  );
}
export default StatusBadge;
