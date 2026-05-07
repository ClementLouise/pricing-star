import { useState } from "react";
import { useApi } from "@/lib/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { KPICard } from "@/components/ui/KPICard";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { Slider } from "@/components/ui/Slider";
import { useToast } from "@/components/ui/Toast";
import { formatCurrency } from "@/lib/formatters";
import { useUpdateScenario } from "@/hooks/useScenarios";
import { useMonteCarlo, useOptimize, useRunSimulation } from "@/hooks/useSimulation";
import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { useAppStore } from "@/store";
import type { LeversConfig, OptimizerRecommendation, Scenario } from "@/types/api";

const confidencePill: Record<string, "success" | "warning" | "neutral"> = {
  high: "success",
  medium: "warning",
  low: "neutral",
};

function RecommendationCard({
  rec,
  onApply,
  onDismiss,
  applied,
}: {
  rec: OptimizerRecommendation;
  onApply: () => void;
  onDismiss: () => void;
  applied: boolean;
}) {
  return (
    <div className={["border rounded-md p-3 flex flex-col gap-2", applied ? "opacity-50" : "border-border bg-panel"].join(" ")}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="font-mono text-xs text-text-tertiary bg-panel-elev px-1.5 py-0.5 rounded shrink-0">
            {rec.target.toUpperCase()}
          </span>
          <span className="text-sm font-medium text-text-primary">{rec.title}</span>
        </div>
        <Pill variant={confidencePill[rec.confidence] ?? "neutral"}>{rec.confidence}</Pill>
      </div>
      <p className="text-xs text-text-secondary leading-relaxed">{rec.rationale}</p>
      {rec.estimated_impact != null && (
        <p className="text-xs text-text-primary font-medium">
          Estimated impact:{" "}
          <span className={rec.estimated_impact >= 0 ? "text-success" : "text-danger"}>
            {rec.estimated_impact >= 0 ? "+" : ""}
            {formatCurrency(rec.estimated_impact, { compact: true })} NPV
          </span>
        </p>
      )}
      {!applied && (
        <div className="flex items-center gap-2 pt-1">
          <Button size="sm" onClick={onApply}>Apply</Button>
          <Button size="sm" variant="ghost" onClick={onDismiss}>Dismiss</Button>
        </div>
      )}
      {applied && <p className="text-xs text-success">✓ Applied</p>}
    </div>
  );
}

interface OptimizerTabProps {
  scenario: Scenario;
}

export function OptimizerTab({ scenario }: OptimizerTabProps) {
  const optimize = useOptimize(scenario.id);
  const updateScenario = useUpdateScenario(scenario.id);
  const runSim = useRunSimulation(scenario.id);
  const monteCarlo = useMonteCarlo(scenario.id);
  const toast = useToast();
  const api = useApi();
  const simulation = useAppStore((s) => s.latestSimulation);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  const [applied, setApplied] = useState<Set<string>>(new Set());
  const [exportingAudit, setExportingAudit] = useState(false);
  const [mcN, setMcN] = useState(500);
  const [mcSigma, setMcSigma] = useState(5);

  const recommendations = (optimize.data?.recommendations ?? []).filter(
    (r) => !dismissed.has(r.type + r.target),
  );

  async function handleApply(rec: OptimizerRecommendation) {
    if (!rec.action) {
      setApplied((prev) => new Set(prev).add(rec.type + rec.target));
      return;
    }

    const rawLevers = scenario.levers as Partial<LeversConfig> | undefined;
    const levers: LeversConfig = {
      withdrawals: rawLevers?.withdrawals ?? [],
      price_floors: rawLevers?.price_floors ?? {},
      delayed_launches: rawLevers?.delayed_launches ?? {},
      de_opt_in: rawLevers?.de_opt_in ?? false,
      gr_clawback_stress: rawLevers?.gr_clawback_stress ?? false,
    };

    try {
      if (rec.action.startsWith("withdrawal.")) {
        const code = rec.action.split(".")[1];
        levers.withdrawals = [...new Set([...levers.withdrawals, code])];
      } else if (rec.action.startsWith("price_floor.")) {
        const [, countryPct] = rec.action.split(".");
        const [country, pctStr] = countryPct.split("=");
        levers.price_floors = { ...levers.price_floors, [country]: parseFloat(pctStr) };
      } else if (rec.action === "guard.submit_method_ii=false") {
        const existingRegs = scenario.regulations as unknown as Record<string, unknown>;
        const guard = (existingRegs.guard ?? {}) as Record<string, unknown>;
        const updatedRegs = { ...existingRegs, guard: { ...guard, submit_method_ii: false } };
        await updateScenario.mutateAsync({ regulations: updatedRegs as Scenario["regulations"] });
      } else if (rec.action === "de_opt_in=false") {
        levers.de_opt_in = false;
      } else if (rec.action.startsWith("delay.")) {
        const code = rec.action.split(".")[1];
        levers.delayed_launches = { ...levers.delayed_launches, [code]: 2029 };
      }

      await updateScenario.mutateAsync({ levers });
      runSim.mutate();
      setApplied((prev) => new Set(prev).add(rec.type + rec.target));
      toast.success(`Applied: ${rec.title}`);
    } catch {
      toast.error("Failed to apply recommendation");
    }
  }

  async function handleExportAudit() {
    if (!simulation) {
      toast.warning("Run simulation first to export audit data");
      return;
    }
    setExportingAudit(true);
    try {
      const blob = await api.simulations.downloadAuditPack(simulation.simulation_id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit_${simulation.simulation_id.slice(0, 8)}_${new Date().toISOString().slice(0, 10)}.zip`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Audit Pack downloaded");
    } catch {
      toast.error("Failed to download audit pack");
    } finally {
      setExportingAudit(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="optimizer" {...TAB_EXPLAINER_CONTENT.optimizer} />
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">NPV Optimizer</h2>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="secondary" loading={exportingAudit} onClick={handleExportAudit}>
            Export Audit Pack
          </Button>
          <Button
            size="sm"
            loading={optimize.isPending}
            onClick={() =>
              optimize.mutate(undefined, {
                onError: () => toast.error("Optimization failed — run simulation first"),
              })
            }
          >
            Run Optimization
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-3 gap-3">
        <KPICard label="Current NPV" value={simulation?.npv ?? null} format="currency" loading={runSim.isPending} />
        <KPICard label="Method I Anchor" value={simulation?.method_i_value ?? null} format="currency" sublabel={simulation?.method_i_anchor ?? undefined} />
        <KPICard label="Per-Unit Rebate" value={simulation?.per_unit_rebate ?? null} format="currency" status="negative" />
      </div>

      {/* Recommendations */}
      {!optimize.data && !optimize.isPending && (
        <Panel>
          <EmptyState
            title="No analysis yet"
            description="Click Run Optimization to generate strategic recommendations"
            action={
              <Button loading={optimize.isPending} onClick={() => optimize.mutate()}>
                Run Optimization
              </Button>
            }
          />
        </Panel>
      )}

      {optimize.data && recommendations.length === 0 && (
        <Panel>
          <EmptyState title="Scenario appears optimal" description="No high-priority recommendations found for current configuration" />
        </Panel>
      )}

      {recommendations.length > 0 && (
        <div className="flex flex-col gap-3">
          <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
            Strategic Recommendations ({recommendations.length})
          </h3>
          {recommendations.map((rec) => (
            <RecommendationCard
              key={rec.type + rec.target}
              rec={rec}
              applied={applied.has(rec.type + rec.target)}
              onApply={() => handleApply(rec)}
              onDismiss={() => setDismissed((prev) => new Set(prev).add(rec.type + rec.target))}
            />
          ))}
        </div>
      )}

      {/* Monte Carlo G2N confidence intervals */}
      <Panel>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">
            Monte Carlo G2N Sensitivity (F13)
          </h3>
          <Button
            size="sm"
            variant="secondary"
            loading={monteCarlo.isPending}
            onClick={() =>
              monteCarlo.mutate(
                { n: mcN, sigma: mcSigma / 100 },
                { onError: () => toast.error("Monte Carlo failed — run simulation first") },
              )
            }
          >
            Run Monte Carlo
          </Button>
        </div>
        <div className="grid grid-cols-2 gap-6 mb-4">
          <Slider
            min={100}
            max={1000}
            step={100}
            value={mcN}
            onChange={setMcN}
            label="Samples (N)"
            formatValue={(v) => v.toLocaleString()}
          />
          <Slider
            min={1}
            max={20}
            step={1}
            value={mcSigma}
            onChange={setMcSigma}
            label="G2N volatility (σ)"
            formatValue={(v) => `${v}%`}
          />
        </div>

        {monteCarlo.data && (
          <>
            <div className="grid grid-cols-4 gap-3 mb-4">
              <KPICard label="P5 Benchmark" value={monteCarlo.data.p05} format="currency" status="negative" />
              <KPICard label="Median (P50)" value={monteCarlo.data.p50} format="currency" />
              <KPICard label="P95 Benchmark" value={monteCarlo.data.p95} format="currency" status="positive" />
              <KPICard label="P5–P95 Range" value={monteCarlo.data.range} format="currency" sublabel={`n=${monteCarlo.data.samples_n}`} />
            </div>
            <ResponsiveContainer width="100%" height={80}>
              <BarChart
                data={[
                  { label: "P5", value: monteCarlo.data.p05 },
                  { label: "P50", value: monteCarlo.data.p50 },
                  { label: "P95", value: monteCarlo.data.p95 },
                ]}
                margin={{ top: 4, right: 8, left: 8, bottom: 4 }}
              >
                <CartesianGrid vertical={false} stroke="#1e2a3a" />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#6b7280" }} axisLine={false} tickLine={false} />
                <YAxis hide domain={["auto", "auto"]} />
                <Tooltip
                  formatter={(v: unknown) => formatCurrency(Number(v), { compact: true })}
                  contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", fontSize: 12 }}
                />
                <Bar dataKey="value" fill="#2563eb" radius={[3, 3, 0, 0]}>
                  <LabelList
                    dataKey="value"
                    position="top"
                    formatter={(v: unknown) => formatCurrency(Number(v), { compact: true })}
                    style={{ fontSize: 10, fill: "#94a3b8" }}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </>
        )}

        {!monteCarlo.data && !monteCarlo.isPending && (
          <p className="text-xs text-text-tertiary text-center py-2">
            Adjust parameters and click Run Monte Carlo to quantify G2N uncertainty
          </p>
        )}
      </Panel>
    </div>
  );
}
