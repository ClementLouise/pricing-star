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
  size?: "sm" | "md";
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
  size = "md",
}: KPICardProps) {
  const deltaSign = delta != null && delta > 0 ? "▲" : "▼";
  const valueClass = size === "sm"
    ? "font-mono font-medium text-display-num-sm text-text-primary tabular-nums"
    : "font-mono font-medium text-display-num-md text-text-primary tabular-nums";

  return (
    <div className="relative flex flex-col gap-1 px-4 py-3 bg-panel border border-border-soft rounded-md overflow-hidden">
      {/* Gold accent bar — 2px top, 24px wide */}
      <div className="absolute top-0 left-4 w-6 h-0.5 bg-gold-500" />
      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-text-tertiary mt-1">{label}</p>
      {loading ? (
        <div className="h-8 w-24 animate-pulse bg-border-soft rounded" />
      ) : (
        <p className={valueClass}>{render(value, format, precision)}</p>
      )}
      {delta != null && !loading && (
        <p className={["font-mono text-xs tabular-nums", statusColors[status]].join(" ")}>
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
