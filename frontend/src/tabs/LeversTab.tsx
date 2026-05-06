import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { KPICard } from "@/components/ui/KPICard";
import { NumberInput } from "@/components/ui/NumberInput";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { Select } from "@/components/ui/Select";
import { Toggle } from "@/components/ui/Toggle";
import { useToast } from "@/components/ui/Toast";
import { countryFlag, COUNTRY_MAP } from "@/lib/countries";
import { formatCurrency } from "@/lib/formatters";
import { useCountryDataList, useUpdateScenario } from "@/hooks/useScenarios";
import { useRunSimulation } from "@/hooks/useSimulation";
import { useAppStore } from "@/store";
import type { LeversConfig, Scenario } from "@/types/api";

const YEAR_OPTIONS = ["2026", "2027", "2028", "2029", "2030", "2031", "2032", "2033"].map(
  (y) => ({ value: y, label: y }),
);

interface LeversTabProps {
  scenario: Scenario;
}

export function LeversTab({ scenario }: LeversTabProps) {
  const updateScenario = useUpdateScenario(scenario.id);
  const runSim = useRunSimulation(scenario.id);
  const toast = useToast();
  const simulation = useAppStore((s) => s.latestSimulation);
  const { data: countryDataList = [] } = useCountryDataList(scenario.id);

  const rawLevers = scenario.levers as Partial<LeversConfig> | undefined;
  const [levers, setLevers] = useState<LeversConfig>({
    withdrawals: rawLevers?.withdrawals ?? [],
    price_floors: rawLevers?.price_floors ?? {},
    delayed_launches: rawLevers?.delayed_launches ?? {},
    de_opt_in: rawLevers?.de_opt_in ?? false,
    gr_clawback_stress: rawLevers?.gr_clawback_stress ?? false,
  });

  const launched = countryDataList.filter((cd) => cd.launched);

  async function save(updated: LeversConfig) {
    setLevers(updated);
    try {
      await updateScenario.mutateAsync({ levers: updated });
      runSim.mutate(undefined, { onError: () => toast.warning("Levers saved but simulation failed") });
    } catch {
      toast.error("Failed to save levers");
    }
  }

  function toggleWithdrawal(code: string) {
    const ws = levers.withdrawals.includes(code)
      ? levers.withdrawals.filter((c) => c !== code)
      : [...levers.withdrawals, code];
    save({ ...levers, withdrawals: ws });
  }

  function setFloor(code: string, pct: number | null) {
    const floors = { ...levers.price_floors };
    if (pct == null) {
      delete floors[code];
    } else {
      floors[code] = pct;
    }
    save({ ...levers, price_floors: floors });
  }

  function setDelay(code: string, year: number | null) {
    const delays = { ...levers.delayed_launches };
    if (year == null) {
      delete delays[code];
    } else {
      delays[code] = year;
    }
    save({ ...levers, delayed_launches: delays });
  }

  const anchor = simulation?.method_i_anchor;
  const npv = simulation?.npv;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">Strategic Levers</h2>
        <Button
          size="sm"
          variant="secondary"
          loading={runSim.isPending}
          onClick={() => runSim.mutate()}
        >
          Recalculate
        </Button>
      </div>

      {/* Withdrawals */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Withdrawals
        </h3>
        {launched.length === 0 ? (
          <EmptyState title="No launched markets" description="Launch markets in Asset & Markets tab" />
        ) : (
          <div className="flex flex-wrap gap-2">
            {launched.map((cd) => {
              const withdrawn = levers.withdrawals.includes(cd.country_code);
              const isAnchor = anchor === cd.country_code;
              return (
                <button
                  key={cd.country_code}
                  onClick={() => toggleWithdrawal(cd.country_code)}
                  className={[
                    "flex items-center gap-1.5 px-3 py-1.5 rounded border text-sm transition-colors",
                    withdrawn
                      ? "bg-danger/10 border-danger/30 text-danger line-through opacity-60"
                      : "bg-panel-elev border-border text-text-primary hover:border-navy-500",
                  ].join(" ")}
                >
                  {countryFlag(cd.country_code)} {COUNTRY_MAP[cd.country_code]?.name ?? cd.country_code}
                  {isAnchor && <Pill variant="warning">Anchor</Pill>}
                </button>
              );
            })}
          </div>
        )}
      </Panel>

      {/* Price floors */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Price Floors (Ringfencing)
        </h3>
        <div className="space-y-2">
          {launched
            .filter((cd) => !levers.withdrawals.includes(cd.country_code))
            .map((cd) => {
              const floor = levers.price_floors[cd.country_code] ?? null;
              const floorPrice = floor != null && cd.list_price != null ? cd.list_price * floor : null;
              return (
                <div key={cd.country_code} className="flex items-center gap-3">
                  <span className="text-sm text-text-primary w-36 shrink-0">
                    {countryFlag(cd.country_code)} {COUNTRY_MAP[cd.country_code]?.name ?? cd.country_code}
                  </span>
                  <div className="w-28">
                    <NumberInput
                      format="percentage"
                      precision={0}
                      value={floor}
                      placeholder="No floor"
                      onChange={(v) => setFloor(cd.country_code, v)}
                    />
                  </div>
                  <span className="text-xs text-text-tertiary">
                    {floorPrice != null ? `Floor: ${formatCurrency(floorPrice, { compact: true })}` : ""}
                  </span>
                  {floor != null && anchor === cd.country_code && (
                    <Pill variant="success">Anchor protected</Pill>
                  )}
                </div>
              );
            })}
        </div>
      </Panel>

      {/* Delayed launches */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Delayed Launches
        </h3>
        <div className="space-y-2">
          {launched
            .filter((cd) => !levers.withdrawals.includes(cd.country_code))
            .map((cd) => {
              const delay = levers.delayed_launches[cd.country_code] ?? null;
              return (
                <div key={cd.country_code} className="flex items-center gap-3">
                  <span className="text-sm text-text-primary w-36 shrink-0">
                    {countryFlag(cd.country_code)} {COUNTRY_MAP[cd.country_code]?.name ?? cd.country_code}
                  </span>
                  <div className="w-28">
                    <Select
                      options={YEAR_OPTIONS}
                      placeholder="Original"
                      value={delay != null ? String(delay) : ""}
                      onChange={(v) => setDelay(cd.country_code, v ? parseInt(v) : null)}
                    />
                  </div>
                </div>
              );
            })}
        </div>
      </Panel>

      {/* Advanced levers */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Advanced Levers
        </h3>
        <div className="space-y-4">
          <div>
            <Toggle
              label="DE opt-in (Medizinforschungsgesetz)"
              description="Disclose German confidential price, triggering cascade to ~12 reference markets"
              checked={levers.de_opt_in}
              onChange={(v) => save({ ...levers, de_opt_in: v })}
            />
            {levers.de_opt_in && (
              <div className="mt-2 ml-14">
                <Pill variant="warning">Estimated −$2.76B cascade harm — verify with advisors</Pill>
              </div>
            )}
          </div>
          <div>
            <Toggle
              label="GR 55% clawback stress test"
              description="Force Greece G2N to 55% (worst-case regulatory scenario) — stress tests NPV impact"
              checked={levers.gr_clawback_stress}
              onChange={(v) => save({ ...levers, gr_clawback_stress: v })}
            />
            {levers.gr_clawback_stress && (
              <div className="mt-2 ml-14">
                <Pill variant="warning">Stress mode — simulation uses GR G2N = 55%</Pill>
              </div>
            )}
          </div>
          <div>
            <Toggle
              label="BR CMED dormant (Resolution 3/2025)"
              description="Mark Brazil as dormant under CMED 3/2025 — excludes BR from IRP referencing baskets"
              checked={(scenario.cascade_config as Record<string, unknown>)?.br_cmed_dormant === true}
              onChange={(v) =>
                updateScenario.mutate({
                  cascade_config: {
                    ...(scenario.cascade_config as Record<string, unknown> ?? {}),
                    br_cmed_dormant: v,
                  },
                })
              }
            />
          </div>
        </div>
      </Panel>

      {/* Lever impact summary */}
      <Panel>
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">
          Lever Impact Summary
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <KPICard
            label="Current NPV"
            value={npv ?? null}
            format="currency"
            loading={runSim.isPending}
          />
          <div className="text-xs text-text-secondary space-y-1 self-center">
            <div>Withdrawals: {levers.withdrawals.length} market{levers.withdrawals.length !== 1 ? "s" : ""}</div>
            <div>Price floors: {Object.keys(levers.price_floors).length} market{Object.keys(levers.price_floors).length !== 1 ? "s" : ""}</div>
            <div>Delayed launches: {Object.keys(levers.delayed_launches).length}</div>
            <div>DE opt-in: {levers.de_opt_in ? "Active ⚠" : "Off"}</div>
          </div>
        </div>
      </Panel>
    </div>
  );
}
