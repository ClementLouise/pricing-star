import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { TabExplainer, TAB_EXPLAINER_CONTENT } from "@/components/TabExplainer";
import { Button } from "@/components/ui/Button";
import { Drawer } from "@/components/ui/Drawer";
import { EmptyState } from "@/components/ui/EmptyState";
import { NumberInput } from "@/components/ui/NumberInput";
import { Panel } from "@/components/ui/Panel";
import { Select } from "@/components/ui/Select";
import { SkeletonBlock } from "@/components/ui/Skeleton";
import { Toggle } from "@/components/ui/Toggle";
import { useToast } from "@/components/ui/Toast";
import { countryFlag, COUNTRIES, COUNTRY_MAP, REGIONS } from "@/lib/countries";
import { formatCurrency, formatPercent } from "@/lib/formatters";
import { useCreateScenario, useCountryDataList, useUpsertCountryData } from "@/hooks/useScenarios";
import { useRunSimulation } from "@/hooks/useSimulation";
import { useUpdateAsset } from "@/hooks/useAssets";
import { useAppStore } from "@/store";
import type { Asset, AssetCreate, CountryData, CountryDataInput, Scenario } from "@/types/api";

const THERAPEUTIC_AREAS = [
  "Oncology",
  "Cystic Fibrosis",
  "Cardiovascular",
  "Immunology",
  "Neurology",
  "Rare Disease",
  "Infectious Disease",
  "Metabolic",
  "Other",
].map((v) => ({ value: v, label: v }));

const MODALITIES = [
  "Small molecule",
  "Monoclonal antibody",
  "Biologic",
  "Gene therapy",
  "Cell therapy",
  "Vaccine",
  "Oligonucleotide",
  "Other",
].map((v) => ({ value: v, label: v }));

interface AssetFormProps {
  asset: Asset;
  scenarioId: string;
}

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

function AssetForm({ asset, scenarioId: _scenarioId }: AssetFormProps) {
  const updateAsset = useUpdateAsset(asset.id);
  const toast = useToast();

  const [fields, setFields] = useState<AssetCreate>({
    name: asset.name,
    therapeutic_area: asset.therapeutic_area,
    modality: asset.modality,
    indication: asset.indication,
    us_list_price: asset.us_list_price,
    us_net_share: asset.us_net_share,
    launch_year: asset.launch_year,
    peak_year: asset.peak_year,
    loe_year: asset.loe_year,
    discount_rate: asset.discount_rate,
    cogs_percent: asset.cogs_percent,
    us_patient_population: asset.us_patient_population,
    ex_us_patient_population: asset.ex_us_patient_population,
    peak_capture_rate: asset.peak_capture_rate,
    part_b_share: asset.part_b_share,
    ramp_years: asset.ramp_years,
  });

  const debouncedFields = useDebounce(fields, 500);
  const isFirstRun = useRef(true);

  useEffect(() => {
    if (isFirstRun.current) {
      isFirstRun.current = false;
      return;
    }
    updateAsset
      .mutateAsync(debouncedFields)
      .catch(() => toast.error("Failed to save asset"));
  }, [debouncedFields]); // eslint-disable-line react-hooks/exhaustive-deps

  function set<K extends keyof typeof fields>(key: K, value: (typeof fields)[K]) {
    setFields((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <Panel>
      <h2 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-3">Asset Details</h2>
      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-1">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wide block mb-1">Name</label>
          <input
            value={fields.name}
            onChange={(e) => set("name", e.target.value)}
            className="w-full h-9 rounded border border-border bg-panel-elev text-sm text-text-primary px-3 focus:outline-none focus:border-navy-500 focus:ring-1 focus:ring-navy-500"
          />
        </div>
        <Select
          label="Therapeutic Area"
          options={THERAPEUTIC_AREAS}
          value={fields.therapeutic_area ?? ""}
          onChange={(v) => set("therapeutic_area", v)}
        />
        <Select
          label="Modality"
          options={MODALITIES}
          value={fields.modality ?? ""}
          onChange={(v) => set("modality", v)}
        />
        <div className="col-span-3">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wide block mb-1">Indication</label>
          <input
            value={fields.indication ?? ""}
            onChange={(e) => set("indication", e.target.value)}
            placeholder="e.g. Metastatic NSCLC"
            className="w-full h-9 rounded border border-border bg-panel-elev text-sm text-text-primary px-3 focus:outline-none focus:border-navy-500"
          />
        </div>

        <NumberInput
          label="US List Price ($/yr)"
          format="currency"
          precision={0}
          value={fields.us_list_price}
          onChange={(v) => set("us_list_price", v)}
          helper="Pre-rebate gross WAC"
        />
        <NumberInput
          label="US Net / Gross (G2N)"
          format="percentage"
          precision={1}
          value={fields.us_net_share}
          onChange={(v) => set("us_net_share", v)}
          helper="e.g. 0.50 = 50% net"
        />
        <NumberInput
          label="Discount Rate (WACC)"
          format="percentage"
          precision={1}
          value={fields.discount_rate}
          onChange={(v) => set("discount_rate", v)}
        />

        <NumberInput label="Launch Year" format="integer" precision={0} value={fields.launch_year} onChange={(v) => set("launch_year", v)} />
        <NumberInput label="Peak Year" format="integer" precision={0} value={fields.peak_year} onChange={(v) => set("peak_year", v)} />
        <NumberInput label="LOE Year" format="integer" precision={0} value={fields.loe_year} onChange={(v) => set("loe_year", v)} />

        <NumberInput label="US Patient Pop." format="integer" precision={0} value={fields.us_patient_population} onChange={(v) => set("us_patient_population", v)} />
        <NumberInput label="Ex-US Patient Pop." format="integer" precision={0} value={fields.ex_us_patient_population} onChange={(v) => set("ex_us_patient_population", v)} />
        <NumberInput label="Peak Capture Rate" format="percentage" precision={1} value={fields.peak_capture_rate} onChange={(v) => set("peak_capture_rate", v)} />

        <NumberInput label="COGS %" format="percentage" precision={1} value={fields.cogs_percent} onChange={(v) => set("cogs_percent", v)} />
        <NumberInput label="Part B Share" format="percentage" precision={1} value={fields.part_b_share} onChange={(v) => set("part_b_share", v)} />
        <NumberInput label="Ramp Years" format="integer" precision={0} value={fields.ramp_years} onChange={(v) => set("ramp_years", v)} />
      </div>
    </Panel>
  );
}

interface CountryDrawerProps {
  countryCode: string;
  existingData: CountryData | null;
  scenarioId: string;
  onClose: () => void;
}

function CountryDrawer({ countryCode, existingData, scenarioId, onClose }: CountryDrawerProps) {
  const upsert = useUpsertCountryData(scenarioId);
  const toast = useToast();
  const ref = COUNTRY_MAP[countryCode];

  const [fields, setFields] = useState<CountryDataInput>({
    list_price: existingData?.list_price ?? null,
    net_price: existingData?.net_price ?? null,
    volume: existingData?.volume ?? null,
    launched: existingData?.launched ?? false,
    launch_year: existingData?.launch_year ?? null,
    withdrawn: existingData?.withdrawn ?? false,
    g2n_ratio: existingData?.g2n_ratio ?? null,
  });

  function set<K extends keyof CountryDataInput>(key: K, value: CountryDataInput[K]) {
    setFields((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSave() {
    try {
      await upsert.mutateAsync({ countryCode, payload: fields });
      toast.success(`${ref?.name ?? countryCode} saved`);
      onClose();
    } catch {
      toast.error("Failed to save country data");
    }
  }

  return (
    <Drawer
      open
      onClose={onClose}
      title={`${countryFlag(countryCode)} ${ref?.name ?? countryCode} (${countryCode})`}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button loading={upsert.isPending} onClick={handleSave}>Save</Button>
        </>
      }
    >
      <div className="flex flex-col gap-3">
        <Toggle label="Launched" checked={fields.launched ?? false} onChange={(v) => set("launched", v)} />
        <Toggle label="Withdrawn from market" checked={fields.withdrawn ?? false} onChange={(v) => set("withdrawn", v)} />
        <NumberInput label="List Price ($/yr)" format="currency" precision={0} value={fields.list_price} onChange={(v) => set("list_price", v)} />
        <NumberInput label="Net Price ($/yr)" format="currency" precision={0} value={fields.net_price} onChange={(v) => set("net_price", v)} />
        <NumberInput label="Volume (market share)" format="percentage" precision={2} value={fields.volume} onChange={(v) => set("volume", v)} />
        <NumberInput label="Launch Year" format="integer" precision={0} value={fields.launch_year} onChange={(v) => set("launch_year", v)} />
        <NumberInput label="G2N Ratio" format="percentage" precision={1} value={fields.g2n_ratio} onChange={(v) => set("g2n_ratio", v)} helper="Override default gross-to-net" />
      </div>
    </Drawer>
  );
}

interface CountryCardProps {
  code: string;
  data: CountryData | undefined;
  onClick: () => void;
}

function CountryCard({ code, data, onClick }: CountryCardProps) {
  const ref = COUNTRY_MAP[code];
  const launched = data?.launched ?? false;
  const withdrawn = data?.withdrawn ?? false;

  return (
    <button
      onClick={onClick}
      className={[
        "flex flex-col gap-1 p-2 rounded border text-left transition-colors cursor-pointer",
        withdrawn
          ? "bg-panel border-border opacity-40"
          : launched
          ? "bg-panel-elev border-navy-500/30 hover:border-navy-500"
          : "bg-panel border-border hover:border-border hover:bg-panel-elev",
      ].join(" ")}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-text-primary">
          {countryFlag(code)} {ref?.name ?? code}
        </span>
        {launched && !withdrawn && (
          <span className="w-1.5 h-1.5 rounded-full bg-success" />
        )}
      </div>
      {data ? (
        <div className="text-xs text-text-tertiary space-y-0.5">
          {data.list_price != null && <div>{formatCurrency(data.list_price, { compact: true })}</div>}
          {data.volume != null && <div>{formatPercent(data.volume)} vol</div>}
        </div>
      ) : (
        <div className="text-xs text-text-tertiary">No data</div>
      )}
    </button>
  );
}

interface MarketsGridProps {
  scenarioId: string;
  countryDataList: CountryData[];
}

function MarketsGrid({ scenarioId, countryDataList }: MarketsGridProps) {
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const dataByCode = Object.fromEntries(countryDataList.map((cd) => [cd.country_code, cd]));

  return (
    <>
      {REGIONS.map((region) => {
        const regionCountries = COUNTRIES.filter((c) => c.region === region);
        return (
          <div key={region} className="mb-4">
            <h3 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest mb-2 px-1">
              {region}
            </h3>
            <div className="grid grid-cols-4 gap-2">
              {regionCountries.map((c) => (
                <CountryCard
                  key={c.code}
                  code={c.code}
                  data={dataByCode[c.code]}
                  onClick={() => setSelectedCode(c.code)}
                />
              ))}
            </div>
          </div>
        );
      })}

      {selectedCode && (
        <CountryDrawer
          countryCode={selectedCode}
          existingData={dataByCode[selectedCode] ?? null}
          scenarioId={scenarioId}
          onClose={() => setSelectedCode(null)}
        />
      )}
    </>
  );
}

interface AssetMarketsTabProps {
  asset: Asset;
  scenario: Scenario | null;
}

export function AssetMarketsTab({ asset, scenario }: AssetMarketsTabProps) {
  const setActiveScenario = useAppStore((s) => s.setActiveScenario);
  const createScenario = useCreateScenario(asset.id);
  const toast = useToast();
  const navigate = useNavigate();

  const { data: countryDataList = [], isLoading: cdLoading } = useCountryDataList(scenario?.id ?? "");
  const runSim = useRunSimulation(scenario?.id ?? "");

  async function handleCreateScenario() {
    try {
      const s = await createScenario.mutateAsync({ name: "Baseline", is_baseline: true });
      setActiveScenario(s);
      navigate(`/assets/${asset.id}/scenarios/${s.id}`);
    } catch {
      toast.error("Failed to create scenario");
    }
  }

  if (!scenario) {
    return (
      <div className="flex flex-col gap-4">
        <TabExplainer tabId="asset" {...TAB_EXPLAINER_CONTENT.asset} />
        <AssetForm asset={asset} scenarioId="" />
        <Panel>
          <EmptyState
            title="No scenario yet"
            description="Create a baseline scenario to start entering market data"
            action={
              <Button loading={createScenario.isPending} onClick={handleCreateScenario}>
                Create baseline scenario
              </Button>
            }
          />
        </Panel>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <TabExplainer tabId="asset" {...TAB_EXPLAINER_CONTENT.asset} />
      <AssetForm asset={asset} scenarioId={scenario.id} />

      <Panel>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-text-tertiary uppercase tracking-widest">Markets</h2>
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-tertiary">
              {countryDataList.filter((cd) => cd.launched).length} launched
            </span>
            <Button
              size="sm"
              variant="secondary"
              loading={runSim.isPending}
              onClick={() => runSim.mutate()}
            >
              Run simulation
            </Button>
          </div>
        </div>
        {cdLoading ? (
          <SkeletonBlock lines={4} />
        ) : (
          <MarketsGrid scenarioId={scenario.id} countryDataList={countryDataList} />
        )}
      </Panel>
    </div>
  );
}
