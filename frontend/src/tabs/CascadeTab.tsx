import { useEffect } from "react";

import { Button } from "@/components/ui/Button";
import type { Column } from "@/components/ui/DataTable";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { Skeleton } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { COUNTRY_MAP } from "@/lib/countries";
import { formatCurrency } from "@/lib/formatters";
import { useRunSimulation } from "@/hooks/useSimulation";
import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { useAppStore } from "@/store";
import type { Scenario } from "@/types/api";

interface CascadeTabProps {
  scenario: Scenario;
}

interface PriceRow {
  country_code: string;
  country_name: string;
  final_price: number;
}

interface YearlyRow {
  year: number;
  us_revenue: number;
  ex_us_revenue: number;
  total_net: number;
  discounted: number;
}

const priceColumns: Column<PriceRow>[] = [
  {
    key: "country_code",
    label: "Country",
    render: (v) => {
      const code = String(v);
      const name = COUNTRY_MAP[code]?.name ?? code;
      return (
        <span className="font-mono text-text-primary">
          {code} <span className="text-text-tertiary font-sans">{name}</span>
        </span>
      );
    },
  },
  { key: "final_price", label: "Final Price ($/yr)", format: "currency", align: "right", sortable: true },
];

const yearlyColumns: Column<YearlyRow>[] = [
  { key: "year", label: "Year", format: "integer", sortable: true },
  { key: "us_revenue", label: "US Revenue", format: "currency", align: "right" },
  { key: "ex_us_revenue", label: "Ex-US Revenue", format: "currency", align: "right" },
  { key: "total_net", label: "Total Net", format: "currency", align: "right" },
  { key: "discounted", label: "Discounted", format: "currency", align: "right" },
];

export function CascadeTab({ scenario }: CascadeTabProps) {
  const simulation = useAppStore((s) => s.latestSimulation);
  const runSim = useRunSimulation(scenario.id);
  const toast = useToast();

  useEffect(() => {
    if (!simulation) {
      runSim.mutate(undefined, {
        onError: () => toast.error("Cascade failed — ensure at least 1 market is launched"),
      });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const priceRows: PriceRow[] = simulation
    ? Object.entries(simulation.final_prices).map(([code, price]) => ({
        country_code: code,
        country_name: COUNTRY_MAP[code]?.name ?? code,
        final_price: price,
      }))
    : [];

  const yearlyRows: YearlyRow[] = simulation?.yearly_breakdown ?? [];

  const isLoading = runSim.isPending && !simulation;

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="cascade" {...TAB_EXPLAINER_CONTENT.cascade} />
      {/* Controls */}
      <Panel>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-text-primary">IRP Cascade</h2>
            {simulation && (
              <Pill variant={simulation.cascade_converged ? "success" : "warning"}>
                {simulation.cascade_converged
                  ? `Converged in ${simulation.cascade_iterations ?? "?"} iterations`
                  : "Did not converge"}
              </Pill>
            )}
          </div>
          <Button
            size="sm"
            variant="secondary"
            loading={runSim.isPending}
            onClick={() =>
              runSim.mutate(undefined, {
                onError: () => toast.error("Cascade failed"),
              })
            }
          >
            Run again
          </Button>
        </div>

        {simulation && (
          <div className="mt-3 grid grid-cols-3 gap-4 text-xs text-text-secondary">
            <div>
              <span className="text-text-tertiary">Markets with prices:</span>{" "}
              <span className="text-text-primary">{Object.keys(simulation.final_prices).length}</span>
            </div>
            <div>
              <span className="text-text-tertiary">Method I anchor:</span>{" "}
              <span className="text-text-primary">
                {simulation.method_i_anchor ?? "—"}{" "}
                {simulation.method_i_value != null && (
                  <span>({formatCurrency(simulation.method_i_value, { compact: true })})</span>
                )}
              </span>
            </div>
            <div>
              <span className="text-text-tertiary">NPV (14-year):</span>{" "}
              <span className="text-text-primary font-semibold">
                {simulation.npv != null ? formatCurrency(simulation.npv, { compact: true }) : "—"}
              </span>
            </div>
          </div>
        )}
      </Panel>

      {/* Final prices table */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Market Prices (Post-Cascade)
        </h3>
        {isLoading ? (
          <Skeleton className="h-48 w-full" />
        ) : priceRows.length === 0 ? (
          <EmptyState
            title="No cascade results"
            description="Run the simulation to see per-market final prices"
          />
        ) : (
          <DataTable columns={priceColumns} data={priceRows} rowKey="country_code" />
        )}
      </Panel>

      {/* Yearly NPV breakdown */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Yearly Revenue Breakdown
        </h3>
        {isLoading ? (
          <Skeleton className="h-48 w-full" />
        ) : yearlyRows.length === 0 ? (
          <EmptyState title="No yearly data" description="Run simulation first" />
        ) : (
          <DataTable columns={yearlyColumns} data={yearlyRows as unknown as YearlyRow[]} rowKey="year" />
        )}
      </Panel>

      {/* Convergence warning */}
      {simulation && !simulation.cascade_converged && (
        <Panel>
          <p className="text-sm text-warning">
            Cascade did not fully converge. Consider adjusting price floors or withdrawal strategy.
            Max iterations: {simulation.cascade_iterations ?? "unknown"}.
          </p>
        </Panel>
      )}
    </div>
  );
}
