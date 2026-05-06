import { formatCurrency, formatDelta, formatNumber, formatPercent } from "@/lib/formatters";

type KPIFormat = "currency" | "percent" | "number";

interface KPICardProps {
  label: string;
  value: number | null | undefined;
  format?: KPIFormat;
  precision?: number;
  delta?: number | null;
  deltaFormat?: KPIFormat;
  status?: "positive" | "negative" | "neutral";
  sublabel?: string;
  loading?: boolean;
}

function render(value: number | null | undefined, format: KPIFormat, precision?: number): string {
  if (value == null) return "—";
  if (format === "currency") return formatCurrency(value, { compact: true, precision });
  if (format === "percent") return formatPercent(value, precision);
  return formatNumber(value, precision);
}

const statusColors: Record<NonNullable<KPICardProps["status"]>, string> = {
  positive: "text-success",
  negative: "text-danger",
  neutral: "text-text-secondary",
};

export function KPICard({
  label,
  value,
  format = "currency",
  precision,
  delta,
  deltaFormat = "currency",
  status = "neutral",
  sublabel,
  loading = false,
}: KPICardProps) {
  const deltaSign = delta != null && delta > 0 ? "↑" : "↓";

  return (
    <div className="flex flex-col gap-1 p-3 rounded-md bg-panel border border-border">
      <p className="text-xs font-medium text-text-tertiary uppercase tracking-widest">{label}</p>
      {loading ? (
        <div className="h-8 w-24 animate-pulse bg-panel-elev rounded" />
      ) : (
        <p className="text-2xl font-semibold text-text-primary tabular-nums">{render(value, format, precision)}</p>
      )}
      {delta != null && !loading && (
        <p className={["text-xs tabular-nums", statusColors[status]].join(" ")}>
          {deltaSign} {formatDelta(Math.abs(delta), deltaFormat)}{" "}
          {value != null && delta !== 0 && (
            <span className="text-text-tertiary">({formatPercent(Math.abs(delta / (value - delta)))})</span>
          )}
        </p>
      )}
      {sublabel && <p className="text-xs text-text-tertiary">{sublabel}</p>}
    </div>
  );
}
