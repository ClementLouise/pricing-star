/** Number/currency/date formatters — all values assumed to be in USD and years CE. */

export function formatCurrency(
  value: number | null | undefined,
  opts: { compact?: boolean; precision?: number } = {},
): string {
  if (value == null) return "—";
  const { compact = true, precision } = opts;
  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (compact) {
    if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(precision ?? 2)}B`;
    if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(precision ?? 1)}M`;
    if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(0)}K`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: precision ?? 0,
  }).format(value);
}

export function formatPercent(value: number | null | undefined, precision = 1): string {
  if (value == null) return "—";
  return `${(value * 100).toFixed(precision)}%`;
}

export function formatNumber(value: number | null | undefined, precision = 0): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: precision,
    minimumFractionDigits: precision,
  }).format(value);
}

export function formatYear(value: number | null | undefined): string {
  if (value == null) return "—";
  return String(value);
}

export function formatDelta(
  delta: number | null | undefined,
  format: "currency" | "percent" | "number" = "currency",
): string {
  if (delta == null) return "";
  const sign = delta > 0 ? "+" : "";
  if (format === "currency") return `${sign}${formatCurrency(delta)}`;
  if (format === "percent") return `${sign}${formatPercent(delta)}`;
  return `${sign}${formatNumber(delta)}`;
}
