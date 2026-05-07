import { useEffect, useRef, useState } from "react";

import type { Column } from "@/components/ui/DataTable";
import { DataTable } from "@/components/ui/DataTable";
import { KPICard } from "@/components/ui/KPICard";
import { Panel } from "@/components/ui/Panel";
import { Slider } from "@/components/ui/Slider";
import { countryFlag, COUNTRY_MAP } from "@/lib/countries";
import { formatCurrency, formatPercent } from "@/lib/formatters";
import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { useDECascade } from "@/hooks/useSimulation";
import type { MarketImpact, Scenario } from "@/types/api";

const DEBOUNCE_MS = 200;

interface MarketRowData extends MarketImpact {
  country_display: string;
}

interface DECascadeTabProps {
  scenario: Scenario;
}

export function DECascadeTab({ scenario }: DECascadeTabProps) {
  const [rebatePct, setRebatePct] = useState(9);
  const deCascade = useDECascade(scenario.id);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounced auto-run on slider change
  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      deCascade.mutate(rebatePct / 100);
    }, DEBOUNCE_MS);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [rebatePct]); // eslint-disable-line react-hooks/exhaustive-deps

  const data = deCascade.data;

  const marketRows: MarketRowData[] = (data?.market_impacts ?? [])
    .filter((m) => m.delta !== 0)
    .sort((a, b) => a.delta - b.delta)
    .map((m) => ({
      ...m,
      country_display: `${countryFlag(m.country)} ${COUNTRY_MAP[m.country]?.name ?? m.country_name}`,
    }));

  const marketColumns: Column<MarketRowData>[] = [
    {
      key: "country_display",
      label: "Market",
    },
    {
      key: "before",
      label: "Price Before",
      align: "right",
      render: (v) => formatCurrency(Number(v), { compact: true }),
    },
    {
      key: "after",
      label: "Price After",
      align: "right",
      render: (v) => formatCurrency(Number(v), { compact: true }),
    },
    {
      key: "delta",
      label: "Delta",
      align: "right",
      render: (v) => (
        <span className={Number(v) < 0 ? "text-danger" : "text-success"}>
          {Number(v) >= 0 ? "+" : ""}
          {formatCurrency(Number(v), { compact: true })}
        </span>
      ),
    },
    {
      key: "delta_pct",
      label: "Δ%",
      align: "right",
      render: (v) => (
        <span className={Number(v) < 0 ? "text-danger" : "text-success"}>
          {Number(v) >= 0 ? "+" : ""}
          {formatPercent(Number(v))}
        </span>
      ),
    },
  ];

  const highRisk = (data?.actually_impacted_count ?? 0) >= 5;
  const anyRisk = (data?.actually_impacted_count ?? 0) > 0;

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="de-cascade" {...TAB_EXPLAINER_CONTENT["de-cascade"]} />
      <h2 className="text-sm font-semibold text-text-primary">DE Cascade Trap Simulator</h2>
      <p className="text-xs text-text-secondary">
        Simulates the impact of disclosing the confidential German net price under the Medical Research Act
        (Medizinforschungsgesetz, March 2026). Adjust the opt-in rebate to see cascade propagation across
        reference markets.
      </p>

      {/* Slider */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-4">
          DE Opt-in Rebate Rate
        </h3>
        <Slider
          min={0}
          max={20}
          step={1}
          value={rebatePct}
          onChange={setRebatePct}
          label="Rebate applied to German list price"
          formatValue={(v) => `${v}%`}
        />
        {deCascade.isPending && (
          <p className="text-xs text-text-tertiary mt-3">Recalculating cascade…</p>
        )}
      </Panel>

      {/* DO NOT OPT-IN banner */}
      {highRisk && data && (
        <div className="flex items-start gap-3 border border-danger/40 bg-danger/10 rounded-md px-4 py-3">
          <span className="text-danger text-lg shrink-0">✕</span>
          <div>
            <p className="text-sm font-semibold text-danger uppercase tracking-wide">
              DO NOT OPT-IN
            </p>
            <p className="text-xs text-text-secondary mt-0.5">
              Disclosing the German confidential price at this rebate level triggers cascade to{" "}
              <strong className="text-text-primary">{data.actually_impacted_count} markets</strong>.
              This represents a high-risk irreversible disclosure. Estimated harm exceeds $1B NPV.
              Verify with legal counsel before any disclosure.
            </p>
          </div>
        </div>
      )}

      {/* Moderate risk warning */}
      {anyRisk && !highRisk && data && (
        <div className="flex items-start gap-3 border border-yellow-500/30 bg-yellow-500/5 rounded-md px-4 py-3">
          <span className="text-yellow-400 shrink-0">⚠</span>
          <p className="text-xs text-text-secondary">
            Opt-in at this level cascades to{" "}
            <strong className="text-text-primary">{data.actually_impacted_count} market{data.actually_impacted_count !== 1 ? "s" : ""}</strong>.
            Monitor cascade propagation carefully.
          </p>
        </div>
      )}

      {/* KPIs */}
      {data && (
        <div className="grid grid-cols-4 gap-3">
          <KPICard
            label="DE Price Before"
            value={data.de_price_before}
            format="currency"
          />
          <KPICard
            label="DE Disclosed Price"
            value={data.de_price_after}
            format="currency"
            status={data.de_price_after < data.de_price_before ? "negative" : undefined}
          />
          <KPICard
            label="DE Delta"
            value={data.de_disclosed_delta}
            format="currency"
            status={data.de_disclosed_delta < 0 ? "negative" : undefined}
          />
          <KPICard
            label="Markets Impacted"
            value={data.actually_impacted_count}
            format="number"
            precision={0}
            sublabel={`of ${data.referencing_markets_count} referencing`}
            status={highRisk ? "negative" : undefined}
          />
        </div>
      )}

      {/* Market impact table */}
      {marketRows.length > 0 && (
        <Panel padding="none">
          <div className="px-3 py-2 border-b border-border">
            <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
              Per-Market Price Impact
            </h3>
          </div>
          <DataTable columns={marketColumns} data={marketRows} rowKey="country" />
        </Panel>
      )}

      {data && marketRows.length === 0 && (
        <Panel>
          <p className="text-sm text-text-secondary text-center py-2">
            No markets impacted at this rebate level — price floor protections hold.
          </p>
        </Panel>
      )}

      {/* Educational note */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-2">
          About the Medizinforschungsgesetz
        </h3>
        <p className="text-xs text-text-secondary leading-relaxed">
          Germany's Medical Research Act (effective March 2026) allows manufacturers to opt into
          disclosing a confidential net price to CMS in exchange for exclusion from Method II
          calculations. Once disclosed, this price propagates through all markets that reference
          Germany in their IRP rules (Austria, Belgium, Netherlands, and ~9 others depending on
          therapy area). The disclosure is <strong className="text-text-primary">permanent and
          irreversible</strong>. This simulator models the worst-case cascade under current reference
          network rules. <strong className="text-text-primary">For strategic use only — not legal
          or regulatory advice.</strong>
        </p>
      </Panel>
    </div>
  );
}
