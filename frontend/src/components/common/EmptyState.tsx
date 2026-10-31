export interface EmptyStateProps {
  title?: string;
  message?: string;
}

export function EmptyState({ title = 'No data', message }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-slate-500 gap-2">
      <div className="font-medium text-slate-900">{title}</div>
      {message && <div className="text-sm">{message}</div>}
    </div>
  );
}
export default EmptyState;
