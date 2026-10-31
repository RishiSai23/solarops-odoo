export interface LoadingStateProps {
  title?: string;
  message?: string;
}

export function LoadingState({ title = 'Loading', message }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-slate-500 gap-2">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 border-t-emerald-500" />
      <div className="font-medium text-slate-900">{title}</div>
      {message && <div className="text-sm">{message}</div>}
    </div>
  );
}
export default LoadingState;
