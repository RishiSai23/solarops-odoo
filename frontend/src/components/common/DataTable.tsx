import React from 'react';

export interface Column<T = Record<string, unknown>> {
  key: keyof T | string;
  label: string;
}

export interface DataTableProps<T = Record<string, unknown>> {
  columns: Column<T>[];
  rows: T[];
}

export function DataTable<T extends Record<string, unknown>>({ columns, rows }: DataTableProps<T>) {
  return (
    <div className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
      <table className="w-full border-collapse text-sm">
        <thead className="bg-[#F4F7FA]">
          <tr>
            {columns.map((c) => (
              <th key={String(c.key)} className="text-left px-4 py-3 border-b border-[#E2E8F0] font-semibold text-[#1E293B]">{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={(row as any).id ?? i} className="hover:bg-[#F4F7FA]">
              {columns.map((c) => (
                <td key={String(c.key)} className="px-4 py-3 border-b border-[#E2E8F0] text-[#1E293B]">{row[c.key as keyof T] as React.ReactNode}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export default DataTable;
