import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { DataTable } from "@/components/ui/DataTable";
import type { Column } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { NumberInput } from "@/components/ui/NumberInput";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { SkeletonBlock } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { countryFlag, COUNTRY_MAP } from "@/lib/countries";
import { formatCurrency } from "@/lib/formatters";
import { useCountryDataList, useUpsertCountryData } from "@/hooks/useScenarios";
import { useRunSimulation } from "@/hooks/useSimulation";
import { useAppStore } from "@/store";
import type { CountryData, Scenario } from "@/types/api";

type Preset = "amnog_erosion" | "loe_cliff" | "linear_erosion";

function buildPresetSeries(
  preset: Preset,
  initial: number,
  launchYear: number,
  loeYear: number,
): Record<string, number> {
  const series: Record<string, number> = {};
  const years = Array.from({ length: 15 }, (_, i) => launchYear + i);

  if (preset === "amnog_erosion") {
    years.forEach((y, i) => {
      if (i === 0) series[String(y)] = initial;
      else if (i < 3) series[String(y)] = initial;
      else if (i < 5) series[String(y)] = initial - 0.07;
      else if (i < 6) series[String(y)] = initial - 0.13;
      else series[String(y)] = initial - 0.15;
    });
  } else if (preset === "loe_cliff") {
    const loeIdx = loeYear - launchYear;
    years.forEach((y, i) => {
      if (i < loeIdx - 2) series[String(y)] = initial;
      else if (i === loeIdx - 2) series[String(y)] = initial - 0.05;
      else if (i === loeIdx - 1) series[String(y)] = initial - 0.20;
      else if (i === loeIdx) series[String(y)] = 0.50;
      else if (i === loeIdx + 1) series[String(y)] = 0.30;
      else series[String(y)] = 0.20;
    });
  } else {
    // linear_erosion: initial → (initial - 0.20) over 15 years
    const terminal = initial - 0.20;
    years.forEach((y, i) => {
      series[String(y)] = initial - ((initial - terminal) * i) / 14;
    });
  }
  return series;
}

interface G2NRowProps {
  cd: CountryData;
  launchYear: number;
  loeYear: number;
  scenarioId: string;
}

function G2NRow({ cd, launchYear, loeYear, scenarioId }: G2NRowProps) {
  const upsert = useUpsertCountryData(scenarioId);
  const toast = useToast();
  const [expanded, setExpanded] = useState(false);
  const [confirmRevert, setConfirmRevert] = useState(false);
  const ref = COUNTRY_MAP[cd.country_code];

  const hasTimeSeries = cd.g2n_time_series != null && Object.keys(cd.g2n_time_series).length > 0;
  const staticG2N = cd.g2n_ratio ?? 0.85;
  const years = Array.from({ length: 15 }, (_, i) => launchYear + i);

  async function saveStatic(v: number | null) {
    if (v == null) return;
    try {
      await upsert.mutateAsync({ countryCode: cd.country_code, payload: { g2n_ratio: v } });
    } catch {
      toast.error(`Failed to save ${cd.country_code} G2N`);
    }
  }

  async function saveYearCell(year: number, v: number | null) {
    if (v == null) return;
    const existing = cd.g2n_time_series ?? {};
    const updated = { ...existing, [String(year)]: v };
    try {
      await upsert.mutateAsync({ countryCode: cd.country_code, payload: { g2n_time_series: updated } });
    } catch {
      toast.error(`Failed to save G2N for ${cd.country_code} year ${year}`);
    }
  }

  async function applyPreset(preset: Preset) {
    const series = buildPresetSeries(preset, staticG2N, launchYear, loeYear);
    try {
      await upsert.mutateAsync({ countryCode: cd.country_code, payload: { g2n_time_series: series } });
      toast.success(`Preset applied to ${cd.country_code}`);
    } catch {
      toast.error("Failed to apply preset");
    }
  }

  async function revertToStatic() {
    try {
      await upsert.mutateAsync({ countryCode: cd.country_code, payload: { g2n_time_series: null } });
      setConfirmRevert(false);
      toast.success(`${cd.country_code} reverted to static G2N`);
    } catch {
      toast.error("Failed to revert");
    }
  }

  const netPrice = cd.list_price != null ? cd.list_price * staticG2N : null;
  const isAggressive = staticG2N < 0.65;

  return (
    <>
      <div className={["border-b border-border", expanded ? "bg-panel-elev" : ""].join(" ")}>
        <div className="flex items-center gap-3 px-3 py-2">
          <button
            onClick={() => setExpanded((e) => !e)}
            className="text-text-tertiary hover:text-text-primary w-4 shrink-0"
          >
            {expanded ? "▾" : "▸"}
          </button>
          <span className="text-sm text-text-primary w-36 shrink-0">
            {countryFlag(cd.country_code)} {ref?.name ?? cd.country_code}
          </span>
          <div className="flex items-center gap-2 flex-1">
            {!hasTimeSeries ? (
              <NumberInput
                format="percentage"
                precision={1}
                value={cd.g2n_ratio ?? null}
                onChange={saveStatic}
              />
            ) : (
              <span className="text-sm text-text-secondary">Time-variant ↘</span>
            )}
            {isAggressive && <Pill variant="warning">Aggressive G2N</Pill>}
          </div>
          <span className="text-sm text-text-tertiary tabular-nums w-28 text-right">
            {netPrice != null ? formatCurrency(netPrice, { compact: true }) : "—"}
          </span>
          <button
            onClick={() => (hasTimeSeries ? setConfirmRevert(true) : setExpanded(true))}
            className="text-xs text-navy-300 hover:text-text-primary border border-border px-2 py-1 rounded"
          >
            {hasTimeSeries ? "− Static" : "⊕ TS"}
          </button>
        </div>

        {expanded && (
          <div className="px-4 pb-3 pt-1 border-t border-border/40">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs text-text-tertiary">Apply preset:</span>
              {(["amnog_erosion", "loe_cliff", "linear_erosion"] as Preset[]).map((p) => (
                <button
                  key={p}
                  onClick={() => applyPreset(p)}
                  className="text-xs border border-border px-2 py-0.5 rounded hover:border-navy-500 text-text-secondary hover:text-text-primary"
                >
                  {p === "amnog_erosion" ? "AMNOG erosion" : p === "loe_cliff" ? "LOE cliff" : "Linear erosion"}
                </button>
              ))}
            </div>
            <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${Math.min(years.length, 8)}, 1fr)` }}>
              {years.map((y) => {
                const tsVal = cd.g2n_time_series?.[String(y)];
                return (
                  <div key={y} className="flex flex-col gap-0.5">
                    <span className="text-xs text-text-tertiary text-center">{y}</span>
                    <NumberInput
                      format="percentage"
                      precision={1}
                      value={tsVal ?? staticG2N}
                      onChange={(v) => saveYearCell(y, v)}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <Modal
        open={confirmRevert}
        onClose={() => setConfirmRevert(false)}
        title="Revert to static G2N?"
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmRevert(false)}>Cancel</Button>
            <Button variant="danger" onClick={revertToStatic}>Discard time series</Button>
          </>
        }
      >
        <p className="text-sm text-text-secondary">
          This will delete the time series for <strong className="text-text-primary">{cd.country_code}</strong> and revert to the static G2N value. This cannot be undone.
        </p>
      </Modal>
    </>
  );
}

interface RebatesTabProps {
  scenario: Scenario;
}

export function RebatesTab({ scenario }: RebatesTabProps) {
  const { data: countryDataList = [], isLoading } = useCountryDataList(scenario.id);
  const runSim = useRunSimulation(scenario.id);
  const simulation = useAppStore((s) => s.latestSimulation);
  const asset = useAppStore((s) => s.activeAsset);
  const toast = useToast();

  const launchYear = asset?.launch_year ?? 2027;
  const loeYear = asset?.loe_year ?? 2041;

  const launchedCountries = countryDataList.filter((cd) => cd.launched && !cd.withdrawn);

  interface M2Row { year: number; benchmark: number }
  const m2Rows: M2Row[] = (simulation?.yearly_breakdown ?? []).map((yb) => ({
    year: yb.year,
    benchmark: yb.total_net / (launchedCountries.length || 1),
  }));

  const m2Columns: Column<M2Row>[] = [
    { key: "year", label: "Year", format: "integer" },
    { key: "benchmark", label: "M.II Proxy", format: "currency", align: "right" },
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">Rebates & G2N</h2>
        <Button
          size="sm"
          variant="secondary"
          loading={runSim.isPending}
          onClick={() => runSim.mutate(undefined, { onError: () => toast.error("Simulation failed") })}
        >
          Recalculate
        </Button>
      </div>

      <Panel padding="none">
        <div className="flex items-center justify-between px-3 py-2 border-b border-border">
          <span className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
            Country G2N Overrides
          </span>
          <span className="text-xs text-text-tertiary">{launchedCountries.length} launched</span>
        </div>
        {isLoading ? (
          <div className="p-4"><SkeletonBlock lines={6} /></div>
        ) : launchedCountries.length === 0 ? (
          <EmptyState title="No launched markets" description="Launch at least one market in the Asset & Markets tab" />
        ) : (
          launchedCountries.map((cd) => (
            <G2NRow
              key={cd.country_code}
              cd={cd}
              launchYear={launchYear}
              loeYear={loeYear}
              scenarioId={scenario.id}
            />
          ))
        )}
      </Panel>

      {m2Rows.length > 0 && (
        <Panel>
          <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
            G2N Impact Analysis (Yearly Revenue)
          </h3>
          <DataTable columns={m2Columns} data={m2Rows} rowKey="year" />
        </Panel>
      )}
    </div>
  );
}
