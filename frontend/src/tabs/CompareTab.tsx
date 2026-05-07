import { useState } from "react";

import { Button } from "@/components/ui/Button";
import type { Column } from "@/components/ui/DataTable";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { Select } from "@/components/ui/Select";
import { SkeletonBlock } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { COUNTRY_MAP, countryFlag } from "@/lib/countries";
import { formatCurrency } from "@/lib/formatters";
import { useScenarioList } from "@/hooks/useScenarios";
import { useCompareScenarios } from "@/hooks/useSimulation";
import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { useAppStore } from "@/store";
import type { ScenarioCompareItem, Scenario } from "@/types/api";

interface MetricRowData {
  metric: string;
  [key: string]: string | number | null;
}

interface YearlyRowData {
  year: number;
  [key: string]: string | number | null;
}

interface CountryRowData {
  country_code: string;
  [key: string]: string | number | null;
}

interface CompareTabProps {
  scenario: Scenario;
}

export function CompareTab({ scenario }: CompareTabProps) {
  const asset = useAppStore((s) => s.activeAsset);
  const { data: allScenarios = [] } = useScenarioList(asset?.id ?? "");
  const compare = useCompareScenarios(asset?.id ?? "");
  const toast = useToast();

  const [selectedIds, setSelectedIds] = useState<string[]>([scenario.id]);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [toAdd, setToAdd] = useState("");

  const items: ScenarioCompareItem[] = compare.data?.items ?? [];

  function handleAddScenario() {
    if (!toAdd || selectedIds.includes(toAdd) || selectedIds.length >= 5) return;
    const next = [...selectedIds, toAdd];
    setSelectedIds(next);
    setAddModalOpen(false);
    compare.mutate(next, { onError: () => toast.error("Comparison failed") });
  }

  function runCompare() {
    compare.mutate(selectedIds, { onError: () => toast.error("Comparison failed") });
  }

  const availableToAdd = allScenarios.filter(
    (s: Scenario) => !selectedIds.includes(s.id),
  );

  // Build headline metrics table
  const metricRows: MetricRowData[] = items.length
    ? [
        { metric: "14-Y NPV", ...Object.fromEntries(items.map((i) => [i.scenario_id, i.simulation?.npv ?? null])) },
        { metric: "Peak Revenue", ...Object.fromEntries(items.map((i) => [i.scenario_id, i.simulation?.peak_revenue ?? null])) },
        { metric: "Method I", ...Object.fromEntries(items.map((i) => [i.scenario_id, i.simulation?.method_i_value ?? null])) },
        { metric: "Method I Anchor", ...Object.fromEntries(items.map((i) => [i.scenario_id, i.simulation?.method_i_anchor ?? "—"])) },
        { metric: "Per-Unit Rebate", ...Object.fromEntries(items.map((i) => [i.scenario_id, i.simulation?.per_unit_rebate ?? null])) },
        { metric: "Effective US Net", ...Object.fromEntries(items.map((i) => [i.scenario_id, i.simulation?.effective_us_net ?? null])) },
      ]
    : [];

  const metricColumns: Column<MetricRowData>[] = [
    { key: "metric", label: "Metric" },
    ...items.map((item) => ({
      key: item.scenario_id as keyof MetricRowData & string,
      label: item.scenario_name,
      align: "right" as const,
      render: (v: MetricRowData[keyof MetricRowData & string]) => {
        if (v == null) return "—";
        if (typeof v === "string") return v;
        return formatCurrency(Number(v), { compact: true });
      },
    })),
  ];

  // Build yearly breakdown table (from first scenario as reference)
  const baseYearly = items[0]?.simulation?.yearly_breakdown ?? [];
  const yearlyRows: YearlyRowData[] = baseYearly.map((yb) => {
    const row: YearlyRowData = { year: yb.year };
    items.forEach((item) => {
      const match = item.simulation?.yearly_breakdown.find((r) => r.year === yb.year);
      row[item.scenario_id] = match?.total_net ?? null;
    });
    return row;
  });

  const yearlyColumns: Column<YearlyRowData>[] = [
    { key: "year", label: "Year", format: "integer" },
    ...items.map((item) => ({
      key: item.scenario_id as keyof YearlyRowData & string,
      label: item.scenario_name,
      align: "right" as const,
      format: "currency" as const,
    })),
  ];

  // Build per-country delta table
  const allCountries = [
    ...new Set(items.flatMap((i) => Object.keys(i.simulation?.final_prices ?? {}))),
  ].sort();

  const countryRows: CountryRowData[] = allCountries.map((code) => {
    const row: CountryRowData = { country_code: code };
    items.forEach((item) => {
      row[item.scenario_id] = item.simulation?.final_prices[code] ?? null;
    });
    return row;
  });

  const countryColumns: Column<CountryRowData>[] = [
    {
      key: "country_code",
      label: "Country",
      render: (v) => {
        const code = String(v);
        return `${countryFlag(code)} ${COUNTRY_MAP[code]?.name ?? code}`;
      },
    },
    ...items.map((item) => ({
      key: item.scenario_id as keyof CountryRowData & string,
      label: item.scenario_name,
      align: "right" as const,
      format: "currency" as const,
    })),
  ];

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="compare" {...TAB_EXPLAINER_CONTENT.compare} />
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">Compare Scenarios</h2>
        <div className="flex items-center gap-2">
          {selectedIds.length < 5 && (
            <Button size="sm" variant="secondary" onClick={() => setAddModalOpen(true)}>
              Add scenario
            </Button>
          )}
          <Button size="sm" loading={compare.isPending} onClick={runCompare}>
            Compare
          </Button>
        </div>
      </div>

      {/* Selected scenarios pills */}
      <div className="flex items-center gap-2 flex-wrap">
        {selectedIds.map((id) => {
          const s = allScenarios.find((sc: Scenario) => sc.id === id);
          return (
            <div key={id} className="flex items-center gap-1">
              <Pill variant="neutral">{s?.name ?? id.slice(0, 8)}</Pill>
              {id !== scenario.id && (
                <button
                  onClick={() => setSelectedIds((prev) => prev.filter((x) => x !== id))}
                  className="text-text-tertiary hover:text-text-primary text-xs"
                >
                  ✕
                </button>
              )}
            </div>
          );
        })}
        {selectedIds.length < 2 && (
          <p className="text-xs text-text-tertiary">Add at least 2 scenarios to compare</p>
        )}
      </div>

      {compare.isPending && (
        <Panel><SkeletonBlock lines={6} /></Panel>
      )}

      {items.length >= 2 && !compare.isPending && (
        <>
          {/* Headline metrics */}
          <Panel padding="none">
            <div className="px-3 py-2 border-b border-border">
              <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
                Headline Metrics
              </h3>
            </div>
            <DataTable columns={metricColumns} data={metricRows} rowKey="metric" />
          </Panel>

          {/* Yearly P&L */}
          {yearlyRows.length > 0 && (
            <Panel padding="none">
              <div className="px-3 py-2 border-b border-border">
                <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
                  Yearly Revenue
                </h3>
              </div>
              <DataTable columns={yearlyColumns} data={yearlyRows} rowKey="year" />
            </Panel>
          )}

          {/* Per-country */}
          {countryRows.length > 0 && (
            <Panel padding="none">
              <div className="px-3 py-2 border-b border-border">
                <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
                  Per-Country Final Prices
                </h3>
              </div>
              <DataTable columns={countryColumns} data={countryRows} rowKey="country_code" />
            </Panel>
          )}
        </>
      )}

      {!compare.data && !compare.isPending && (
        <Panel>
          <EmptyState
            title="Select scenarios and click Compare"
            description="Add up to 5 scenarios for side-by-side comparison"
          />
        </Panel>
      )}

      {/* Add scenario modal */}
      <Modal
        open={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        title="Add Scenario to Comparison"
        footer={
          <>
            <Button variant="ghost" onClick={() => setAddModalOpen(false)}>Cancel</Button>
            <Button onClick={handleAddScenario} disabled={!toAdd}>Add</Button>
          </>
        }
      >
        {availableToAdd.length === 0 ? (
          <p className="text-sm text-text-secondary">No other scenarios available for this asset.</p>
        ) : (
          <Select
            label="Scenario"
            options={availableToAdd.map((s: Scenario) => ({ value: s.id, label: s.name }))}
            placeholder="Select a scenario"
            onChange={setToAdd}
            value={toAdd}
          />
        )}
      </Modal>
    </div>
  );
}
