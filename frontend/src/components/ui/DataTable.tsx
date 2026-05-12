import { useState } from "react";

import { formatCurrency, formatNumber, formatPercent } from "@/lib/formatters";

type ColFormat = "text" | "currency" | "percent" | "number" | "integer";
type ColAlign = "left" | "center" | "right";

export interface Column<T> {
  key: keyof T & string;
  label: string;
  sortable?: boolean;
  format?: ColFormat;
  align?: ColAlign;
  render?: (value: T[keyof T & string], row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: keyof T & string;
  onRowClick?: (row: T) => void;
  emptyText?: string;
}

function formatCell(value: unknown, format: ColFormat): string {
  if (value == null) return "—";
  const n = Number(value);
  if (format === "currency") return formatCurrency(n, { compact: true });
  if (format === "percent") return formatPercent(n);
  if (format === "number") return formatNumber(n, 2);
  if (format === "integer") return formatNumber(n, 0);
  return String(value);
}

const alignClasses: Record<ColAlign, string> = {
  left: "text-left",
  center: "text-center",
  right: "text-right",
};

export function DataTable<T>({
  columns,
  data,
  rowKey,
  onRowClick,
  emptyText = "No data",
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  function toggleSort(key: string) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  const sorted = sortKey
    ? [...data].sort((a, b) => {
        const av = (a as Record<string, unknown>)[sortKey];
        const bv = (b as Record<string, unknown>)[sortKey];
        if (av == null) return 1;
        if (bv == null) return -1;
        const cmp = av < bv ? -1 : av > bv ? 1 : 0;
        return sortDir === "asc" ? cmp : -cmp;
      })
    : data;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-border bg-bg">
            {columns.map((col) => (
              <th
                key={col.key}
                className={[
                  "px-3 py-2 font-mono text-[10px] text-text-tertiary uppercase tracking-widest",
                  col.sortable ? "cursor-pointer hover:text-text-secondary select-none" : "",
                  alignClasses[col.align ?? "left"],
                ].join(" ")}
                onClick={col.sortable ? () => toggleSort(col.key) : undefined}
              >
                {col.label}
                {col.sortable && sortKey === col.key && (
                  <span className="ml-1">{sortDir === "asc" ? "↑" : "↓"}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-3 py-8 text-center text-text-tertiary text-xs">
                {emptyText}
              </td>
            </tr>
          ) : (
            sorted.map((row) => (
              <tr
                key={String((row as Record<string, unknown>)[rowKey])}
                className={[
                  "border-b border-border-soft bg-panel",
                  onRowClick ? "cursor-pointer hover:bg-panel-elev transition-colors" : "",
                ].join(" ")}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => {
                  const isNumeric = !col.render && ["currency", "percent", "number", "integer"].includes(col.format ?? "text");
                  return (
                    <td
                      key={col.key}
                      className={[
                        "px-3 py-2 text-text-primary",
                        alignClasses[col.align ?? "left"],
                        isNumeric ? "font-mono tabular-nums" : "",
                      ].filter(Boolean).join(" ")}
                    >
                      {col.render
                        ? col.render(row[col.key as keyof T] as T[keyof T & string], row)
                        : formatCell((row as Record<string, unknown>)[col.key], col.format ?? "text")}
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
