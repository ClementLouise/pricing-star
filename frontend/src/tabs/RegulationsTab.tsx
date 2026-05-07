import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { KPICard } from "@/components/ui/KPICard";
import { NumberInput } from "@/components/ui/NumberInput";
import { Panel } from "@/components/ui/Panel";
import { Select } from "@/components/ui/Select";
import { Toggle } from "@/components/ui/Toggle";
import { useToast } from "@/components/ui/Toast";
import { useUpdateScenario } from "@/hooks/useScenarios";
import { useRunSimulation } from "@/hooks/useSimulation";
import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { useAppStore } from "@/store";
import type { GenerousConfig, GlobeConfig, GuardConfig, RegulationsConfig, Scenario } from "@/types/api";

const YEARS = ["2026", "2027", "2028", "2029", "2030", "2031"].map((y) => ({ value: y, label: y }));

const PHASE_IN_BY_YEAR: Record<string, number> = {
  "2026": 0,
  "2027": -0.075,
  "2028": -0.15,
  "2029": -0.225,
  "2030": -0.30,
  "2031": -0.30,
};

const GLOBE_PHASE_IN_BY_YEAR: Record<string, number> = {
  "2026": 0,
  "2027": -0.0875,
  "2028": -0.175,
  "2029": -0.2625,
  "2030": -0.35,
  "2031": -0.35,
};

type QuickPreset = "pre-mfn" | "generous-only" | "generous-guard" | "full-mfn";

const PRESETS: Record<QuickPreset, RegulationsConfig> = {
  "pre-mfn": {
    generous: { active: false, year: null, medicaid_share: 0.07 },
    guard: { active: false, year: null, submit_method_ii: false, phase_in: null },
    globe: { active: false, year: null, submit_method_ii: false, phase_in: null },
  },
  "generous-only": {
    generous: { active: true, year: 2027, medicaid_share: 0.07 },
    guard: { active: false, year: null, submit_method_ii: false, phase_in: null },
    globe: { active: false, year: null, submit_method_ii: false, phase_in: null },
  },
  "generous-guard": {
    generous: { active: true, year: 2027, medicaid_share: 0.07 },
    guard: { active: true, year: 2028, submit_method_ii: false, phase_in: -0.15 },
    globe: { active: false, year: null, submit_method_ii: false, phase_in: null },
  },
  "full-mfn": {
    generous: { active: true, year: 2027, medicaid_share: 0.07 },
    guard: { active: true, year: 2028, submit_method_ii: false, phase_in: -0.15 },
    globe: { active: true, year: 2029, submit_method_ii: false, phase_in: -0.2625 },
  },
};

const PRESET_OPTIONS = [
  { value: "pre-mfn", label: "Pre-MFN (all off)" },
  { value: "generous-only", label: "Generous only" },
  { value: "generous-guard", label: "Generous + Guard" },
  { value: "full-mfn", label: "Full MFN 2029" },
];

interface GenerousPanelProps {
  config: GenerousConfig;
  onChange: (cfg: GenerousConfig) => void;
}

function GenerousPanel({ config, onChange }: GenerousPanelProps) {
  return (
    <Panel>
      <h3 className="text-xs font-semibold text-navy-300 uppercase tracking-widest mb-3">
        Generous — Medicaid MFN
      </h3>
      <div className="flex flex-col gap-3">
        <Toggle
          label="Active"
          description="Medicaid rebate tied to 2nd-lowest GDP-PPP price in MFN-8 basket"
          checked={config.active}
          onChange={(v) => onChange({ ...config, active: v })}
        />
        {config.active && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <Select
                label="Effective Year"
                options={YEARS}
                value={String(config.year ?? "")}
                onChange={(v) => onChange({ ...config, year: parseInt(v) })}
              />
              <NumberInput
                label="Medicaid Share"
                format="percentage"
                precision={1}
                value={config.medicaid_share}
                onChange={(v) => onChange({ ...config, medicaid_share: v ?? 0.07 })}
                helper="Fraction of US volume that is Medicaid"
              />
            </div>
            <p className="text-xs text-text-tertiary">
              Reference: 2nd-lowest GDP-PPP adjusted price in MFN-8 basket
            </p>
          </>
        )}
      </div>
    </Panel>
  );
}

interface GuardGlobePanelProps {
  label: string;
  subtitle: string;
  config: GuardConfig | GlobeConfig;
  phaseInByYear: Record<string, number>;
  onChange: (cfg: GuardConfig | GlobeConfig) => void;
}

function GuardGlobePanel({ label, subtitle, config, phaseInByYear, onChange }: GuardGlobePanelProps) {
  const phaseIn = config.year ? (phaseInByYear[String(config.year)] ?? null) : null;

  return (
    <Panel>
      <h3 className="text-xs font-semibold text-navy-300 uppercase tracking-widest mb-3">
        {label} — {subtitle}
      </h3>
      <div className="flex flex-col gap-3">
        <Toggle
          label="Active"
          checked={config.active}
          onChange={(v) => onChange({ ...config, active: v })}
        />
        {config.active && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <Select
                label="Effective Year"
                options={YEARS}
                value={String(config.year ?? "")}
                onChange={(v) =>
                  onChange({
                    ...config,
                    year: parseInt(v),
                    phase_in: phaseInByYear[v] ?? null,
                  })
                }
              />
              <div className="flex flex-col gap-1">
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wide">
                  Phase-in
                </span>
                <div className="h-9 flex items-center px-3 rounded border border-border bg-panel-elev text-sm text-text-tertiary tabular-nums">
                  {phaseIn != null ? `${(phaseIn * 100).toFixed(1)}%` : "—"}
                </div>
                <p className="text-xs text-text-tertiary">Derived from year — read only</p>
              </div>
            </div>
            <Toggle
              label="Submit Method II to CMS"
              description="Voluntarily submit volume-weighted average net price. Uses max(M.I, M.II) as benchmark."
              checked={config.submit_method_ii}
              onChange={(v) => onChange({ ...config, submit_method_ii: v })}
            />
          </>
        )}
      </div>
    </Panel>
  );
}

interface RebuttalSummaryProps {
  scenarioId: string;
}

function RebateSummary({ scenarioId }: RebuttalSummaryProps) {
  const simulation = useAppStore((s) => s.latestSimulation);
  const runSim = useRunSimulation(scenarioId);

  return (
    <Panel>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">Rebate Summary</h3>
        <Button size="sm" variant="secondary" loading={runSim.isPending} onClick={() => runSim.mutate()}>
          Recalculate
        </Button>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <KPICard label="Method I Value" value={simulation?.method_i_value ?? null} format="currency" sublabel={simulation?.method_i_anchor ?? undefined} />
        <KPICard label="Method II Value" value={simulation?.method_ii_value ?? null} format="currency" />
        <KPICard label="Per-Unit Rebate" value={simulation?.per_unit_rebate ?? null} format="currency" />
        <KPICard label="Effective US Net" value={simulation?.effective_us_net ?? null} format="currency" />
      </div>
    </Panel>
  );
}

interface RegulationsTabProps {
  scenario: Scenario;
}

export function RegulationsTab({ scenario }: RegulationsTabProps) {
  const updateScenario = useUpdateScenario(scenario.id);
  const toast = useToast();

  const [regs, setRegs] = useState<RegulationsConfig>(
    scenario.regulations ?? {
      generous: { active: false, year: null, medicaid_share: 0.07 },
      guard: { active: false, year: null, submit_method_ii: false, phase_in: null },
      globe: { active: false, year: null, submit_method_ii: false, phase_in: null },
    },
  );

  async function handleSave(newRegs: RegulationsConfig) {
    setRegs(newRegs);
    try {
      await updateScenario.mutateAsync({ regulations: newRegs });
    } catch {
      toast.error("Failed to save regulation settings");
    }
  }

  async function applyPreset(preset: QuickPreset) {
    await handleSave(PRESETS[preset]);
  }

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="regulations" {...TAB_EXPLAINER_CONTENT.regulations} />
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-text-primary">Regulatory Scenario</h2>
        <div className="flex items-center gap-2">
          <Select
            options={PRESET_OPTIONS}
            placeholder="Quick presets"
            onChange={(v) => applyPreset(v as QuickPreset)}
          />
          <Button size="sm" loading={updateScenario.isPending} onClick={() => handleSave(regs)}>
            Save scenario
          </Button>
        </div>
      </div>

      <GenerousPanel
        config={regs.generous}
        onChange={(cfg) => handleSave({ ...regs, generous: cfg })}
      />

      <GuardGlobePanel
        label="Guard"
        subtitle="Medicare Part D MFN"
        config={regs.guard}
        phaseInByYear={PHASE_IN_BY_YEAR}
        onChange={(cfg) => handleSave({ ...regs, guard: cfg as GuardConfig })}
      />

      <GuardGlobePanel
        label="Globe"
        subtitle="Medicare Part B MFN"
        config={regs.globe}
        phaseInByYear={GLOBE_PHASE_IN_BY_YEAR}
        onChange={(cfg) => handleSave({ ...regs, globe: cfg as GlobeConfig })}
      />

      <RebateSummary scenarioId={scenario.id} />
    </div>
  );
}
