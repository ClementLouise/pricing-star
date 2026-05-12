import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button } from "@/components/ui/Button";
import type { Column } from "@/components/ui/DataTable";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { KPICard } from "@/components/ui/KPICard";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { useToast } from "@/components/ui/Toast";
import { countryFlag, COUNTRY_MAP } from "@/lib/countries";
import { formatCurrency, formatPercent } from "@/lib/formatters";
import { useAnchorAnalysis } from "@/hooks/useSimulation";
import type { AnchorCountry, Scenario } from "@/types/api";

type Model = "GUARD" | "GLOBE" | "GENEROUS";

const MODEL_TABS: { id: Model; label: string }[] = [
  { id: "GUARD", label: "Guard (Part D)" },
  { id: "GLOBE", label: "Globe (Part B)" },
  { id: "GENEROUS", label: "Generous (Medicaid)" },
];

const ringfenceVariant: Record<string, "success" | "warning" | "neutral"> = {
  firm: "success",
  moderate: "warning",
  fragile: "neutral",
};

function ringfenceLevel(gapPct: number): string {
  if (gapPct > 0.15) return "firm";
  if (gapPct >= 0.05) return "moderate";
  return "fragile";
}

interface AnchorRowData {
  country: string;
  country_name: string;
  nominal: number;
  ppp: number;
  adjusted: number;
  is_anchor: boolean;
}

interface AnchorAnalysisTabProps {
  scenario: Scenario;
}

export function AnchorAnalysisTab({ scenario }: AnchorAnalysisTabProps) {
  const [model, setModel] = useState<Model>("GUARD");
  const anchorAnalysis = useAnchorAnalysis(scenario.id);
  const toast = useToast();

  const data = anchorAnalysis.data;

  function runAnalysis(m: Model) {
    setModel(m);
    anchorAnalysis.mutate(m, {
      onError: () => toast.error("Anchor analysis failed — run simulation first"),
    });
  }

  const anchorCode = data?.anchor.country ?? null;

  const rankingRows: AnchorRowData[] = (data?.all_ranked ?? []).map((c: AnchorCountry) => ({
    ...c,
    is_anchor: c.country === anchorCode,
  }));

  const rankingColumns: Column<AnchorRowData>[] = [
    {
      key: "country",
      label: "Market",
      render: (v, row) => {
        const code = String(v);
        return (
          <span className="flex items-center gap-2">
            {countryFlag(code)} {COUNTRY_MAP[code]?.name ?? row.country_name}
            {row.is_anchor && <Pill variant="warning">ANCHOR</Pill>}
          </span>
        );
      },
    },
    {
      key: "nominal",
      label: "Nominal Price",
      align: "right",
      render: (v) => formatCurrency(Number(v), { compact: true }),
    },
    {
      key: "ppp",
      label: "PPP Factor",
      align: "right",
      render: (v) => Number(v).toFixed(3),
    },
    {
      key: "adjusted",
      label: "PPP-Adjusted",
      align: "right",
      render: (v) => formatCurrency(Number(v), { compact: true }),
    },
  ];

  const rfLevel = data ? ringfenceLevel(data.anchor_gap_pct) : null;

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="anchor" {...TAB_EXPLAINER_CONTENT.anchor} />
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">MFN Anchor Analysis</h2>
        <div className="flex items-center gap-1 bg-panel-elev border border-border rounded p-0.5">
          {MODEL_TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => runAnalysis(t.id)}
              className={[
                "px-3 py-1 text-xs rounded transition-colors",
                model === t.id && data
                  ? "bg-navy-600 text-text-primary font-medium"
                  : "text-text-secondary hover:text-text-primary",
              ].join(" ")}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {!data && !anchorAnalysis.isPending && (
        <Panel>
          <EmptyState
            title="No anchor analysis yet"
            description="Run simulation first, then click a model basket above to analyze the anchor"
            action={
              <Button loading={anchorAnalysis.isPending} onClick={() => runAnalysis(model)}>
                Analyze {model}
              </Button>
            }
          />
        </Panel>
      )}

      {anchorAnalysis.isPending && (
        <Panel>
          <div className="flex items-center justify-center py-8 text-sm text-text-secondary">
            Computing anchor analysis…
          </div>
        </Panel>
      )}

      {data && !anchorAnalysis.isPending && (
        <>
          {/* Non-obvious anchor warning */}
          {data.is_non_obvious_anchor && data.nominal_lowest && (
            <div className="flex items-start gap-3 border border-yellow-500/30 bg-yellow-500/5 rounded-md px-4 py-3">
              <span className="text-yellow-400 text-base shrink-0">⚠</span>
              <div>
                <p className="text-sm font-medium text-yellow-300">Non-obvious anchor detected</p>
                <p className="text-xs text-text-secondary mt-0.5">
                  Nominal lowest price is{" "}
                  <strong className="text-text-primary">
                    {countryFlag(data.nominal_lowest.country)}{" "}
                    {COUNTRY_MAP[data.nominal_lowest.country]?.name ?? data.nominal_lowest.country}
                  </strong>{" "}
                  ({formatCurrency(data.nominal_lowest.nominal, { compact: true })}), but the PPP-adjusted
                  anchor is{" "}
                  <strong className="text-text-primary">
                    {countryFlag(data.anchor.country)}{" "}
                    {COUNTRY_MAP[data.anchor.country]?.name ?? data.anchor.country}
                  </strong>
                  . Ringfencing the nominal country alone is insufficient.
                </p>
              </div>
            </div>
          )}

          {/* Hero KPIs */}
          <div className="grid grid-cols-4 gap-3">
            <KPICard
              label="Anchor Market"
              value={null}
              format="currency"
              sublabel={
                `${countryFlag(data.anchor.country)} ${COUNTRY_MAP[data.anchor.country]?.name ?? data.anchor.country}`
              }
            />
            <KPICard
              label="PPP-Adjusted Price"
              value={data.anchor.adjusted}
              format="currency"
            />
            <KPICard
              label={`${model} Benchmark`}
              value={data.benchmark}
              format="currency"
              sublabel="Method I × 1.02"
            />
            <KPICard
              label="Gap to #2"
              value={null}
              format="currency"
              sublabel={
                data.second
                  ? `${formatPercent(data.anchor_gap_pct)} · ${formatCurrency(data.anchor_gap, { compact: true })}`
                  : "Only 1 market"
              }
            />
          </div>

          {/* Ringfencing recommendation */}
          <Panel>
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
                    Ringfencing Recommendation
                  </h3>
                  {rfLevel && (
                    <Pill variant={ringfenceVariant[rfLevel] ?? "neutral"}>
                      {rfLevel.toUpperCase()}
                    </Pill>
                  )}
                </div>
                <p className="text-sm text-text-primary leading-relaxed">
                  {data.ringfence_recommendation}
                </p>
              </div>
              <div className="text-right shrink-0">
                <p className="text-xs text-text-tertiary">Anchor gap</p>
                <p className="text-lg font-mono font-semibold text-text-primary">
                  {formatPercent(data.anchor_gap_pct)}
                </p>
                <p className="text-xs text-text-tertiary">
                  {rfLevel === "fragile" ? "< 5% — very fragile" :
                   rfLevel === "moderate" ? "5–15% — moderate" :
                   "> 15% — firm"}
                </p>
              </div>
            </div>
          </Panel>

          {/* PPP-adjusted ranking chart */}
          {rankingRows.length > 0 && (
            <Panel>
              <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
                PPP-Adjusted Price Ranking
              </h3>
              <ResponsiveContainer width="100%" height={Math.max(120, rankingRows.length * 22)}>
                <BarChart
                  layout="vertical"
                  data={rankingRows.map((r) => ({
                    label: countryFlag(r.country) + " " + (COUNTRY_MAP[r.country]?.name ?? r.country),
                    value: r.adjusted,
                    isAnchor: r.is_anchor,
                  }))}
                  margin={{ top: 2, right: 64, left: 8, bottom: 2 }}
                >
                  <CartesianGrid horizontal={false} stroke="#D5CCB6" />
                  <XAxis
                    type="number"
                    tickFormatter={(v: number) => formatCurrency(v, { compact: true })}
                    tick={{ fontSize: 10, fill: "#565045" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    width={110}
                    tick={{ fontSize: 11, fill: "#565045" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    formatter={(v: unknown) => [formatCurrency(Number(v), { compact: true }), "PPP-Adjusted"]}
                    contentStyle={{ background: "#F8F3E6", border: "1px solid #D5CCB6", fontSize: 12, color: "#161310" }}
                  />
                  <Bar dataKey="value" radius={[0, 3, 3, 0]}>
                    {rankingRows.map((entry) => (
                      <Cell
                        key={entry.country}
                        fill={entry.is_anchor ? "#B8860B" : "#1E40AF"}
                        opacity={entry.is_anchor ? 1 : 0.75}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Panel>
          )}

          {/* OECD-19 ranking table */}
          {rankingRows.length > 0 && (
            <Panel padding="none">
              <div className="px-3 py-2 border-b border-border flex items-center justify-between">
                <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
                  PPP-Adjusted Ranking ({model})
                </h3>
                <span className="text-xs text-text-tertiary">{rankingRows.length} markets</span>
              </div>
              <DataTable
                columns={rankingColumns}
                data={rankingRows}
                rowKey="country"
              />
            </Panel>
          )}

          {/* Methodology note */}
          <Panel>
            <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-2">
              Methodology
            </h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Method I benchmark = lowest PPP-adjusted ex-US price × 1.02. PPP adjuster = US GDP per capita /
              country GDP per capita (PPP), lower-bounded at 1.000. Anchor country is the market with the
              lowest PPP-adjusted price in the {model} basket.{" "}
              <strong className="text-text-primary">For strategic use only — not legal or regulatory advice.</strong>
            </p>
          </Panel>
        </>
      )}
    </div>
  );
}
