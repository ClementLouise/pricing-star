import { useState } from "react";
import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { Skeleton } from "@/components/ui/Skeleton";
import { AppShell } from "@/components/layout/AppShell";
import { ImportWizard } from "@/components/ImportWizard";
import { useToast } from "@/components/ui/Toast";
import { useApi } from "@/lib/api";
import { useAsset } from "@/hooks/useAssets";
import { useScenarioList, useCreateScenario } from "@/hooks/useScenarios";
import { useAppStore } from "@/store";
import { AnchorAnalysisTab } from "@/tabs/AnchorAnalysisTab";
import { AssetMarketsTab } from "@/tabs/AssetMarketsTab";
import { CascadeTab } from "@/tabs/CascadeTab";
import { CompareTab } from "@/tabs/CompareTab";
import { DECascadeTab } from "@/tabs/DECascadeTab";
import { LeversTab } from "@/tabs/LeversTab";
import { OptimizerTab } from "@/tabs/OptimizerTab";
import { RebatesTab } from "@/tabs/RebatesTab";
import { RegulationsTab } from "@/tabs/RegulationsTab";
import type { Scenario } from "@/types/api";

export default function AssetDetailPage() {
  const { assetId, scenarioId: routeScenarioId } = useParams<{
    assetId: string;
    scenarioId?: string;
  }>();
  const navigate = useNavigate();
  const toast = useToast();

  const { data: asset, isLoading: assetLoading } = useAsset(assetId ?? "");
  const { data: scenarios = [], isLoading: scenariosLoading } = useScenarioList(assetId ?? "");

  const setActiveAsset = useAppStore((s) => s.setActiveAsset);
  const setActiveScenario = useAppStore((s) => s.setActiveScenario);
  const activeScenario = useAppStore((s) => s.activeScenario);
  const activeTab = useAppStore((s) => s.activeTab);

  const api = useApi();
  const [scenarioPickerOpen, setScenarioPickerOpen] = useState(false);
  const [newScenarioName, setNewScenarioName] = useState("");
  const [downloadingPack, setDownloadingPack] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const createScenario = useCreateScenario(assetId ?? "");

  // Sync asset to store
  useEffect(() => {
    if (asset) setActiveAsset(asset);
  }, [asset, setActiveAsset]);

  // Resolve active scenario from route param or first scenario
  useEffect(() => {
    if (scenarios.length === 0) return;
    const target = routeScenarioId
      ? scenarios.find((s) => s.id === routeScenarioId)
      : scenarios[0];
    if (target) setActiveScenario(target);
  }, [scenarios, routeScenarioId, setActiveScenario]);

  async function handleDownloadAssetPack() {
    if (!assetId) return;
    setDownloadingPack(true);
    try {
      const blob = await api.auditPack.downloadForAsset(assetId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `pricingstar_${(asset?.name ?? assetId).replace(/ /g, "_")}_${new Date().toISOString().slice(0, 10)}.zip`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Asset Audit Pack downloaded");
    } catch {
      toast.error("No simulations found — run at least one simulation first");
    } finally {
      setDownloadingPack(false);
    }
  }

  async function handleCreateScenario() {
    if (!newScenarioName.trim()) return;
    try {
      const s = await createScenario.mutateAsync({ name: newScenarioName.trim() });
      setActiveScenario(s);
      setScenarioPickerOpen(false);
      navigate(`/assets/${assetId}/scenarios/${s.id}`);
    } catch {
      toast.error("Failed to create scenario");
    }
  }

  if (assetLoading || scenariosLoading) {
    return (
      <div className="min-h-screen bg-bg p-6">
        <Skeleton className="h-8 w-64 mb-4" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <EmptyState
          title="Asset not found"
          action={<Button onClick={() => navigate("/assets")}>Back to assets</Button>}
        />
      </div>
    );
  }

  const scenarioOptions = scenarios.map((s: Scenario) => ({ value: s.id, label: s.name }));

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-4">
        <nav className="text-xs text-text-tertiary flex items-center gap-2">
          <button onClick={() => navigate("/assets")} className="hover:text-text-secondary transition-colors">
            Assets
          </button>
          <span>/</span>
          <span className="text-text-primary">{asset.name}</span>
          {activeScenario && (
            <>
              <span>/</span>
              <button
                onClick={() => setScenarioPickerOpen(true)}
                className="text-text-secondary hover:text-text-primary transition-colors"
              >
                {activeScenario.name}
              </button>
            </>
          )}
        </nav>
        <div className="flex items-center gap-2">
          {scenarioOptions.length > 0 && (
            <Select
              options={scenarioOptions}
              value={activeScenario?.id ?? ""}
              onChange={(id) => {
                const s = scenarios.find((sc: Scenario) => sc.id === id);
                if (s) {
                  setActiveScenario(s);
                  navigate(`/assets/${assetId}/scenarios/${id}`);
                }
              }}
            />
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setImportOpen(true)}
          >
            Update from Excel
          </Button>
          <Button
            size="sm"
            variant="ghost"
            loading={downloadingPack}
            onClick={handleDownloadAssetPack}
          >
            Download Asset Pack
          </Button>
          <Button size="sm" variant="secondary" onClick={() => setScenarioPickerOpen(true)}>
            New scenario
          </Button>
        </div>
      </div>

      {activeTab === "asset" && (
        <AssetMarketsTab asset={asset} scenario={activeScenario} />
      )}
      {activeScenario ? (
        <>
          {activeTab === "regulations" && <RegulationsTab scenario={activeScenario} />}
          {activeTab === "cascade" && <CascadeTab scenario={activeScenario} />}
          {activeTab === "rebates" && <RebatesTab scenario={activeScenario} />}
          {activeTab === "levers" && <LeversTab scenario={activeScenario} />}
          {activeTab === "optimizer" && <OptimizerTab scenario={activeScenario} />}
          {activeTab === "compare" && <CompareTab scenario={activeScenario} />}
          {activeTab === "anchor" && <AnchorAnalysisTab scenario={activeScenario} />}
          {activeTab === "de-cascade" && <DECascadeTab scenario={activeScenario} />}
        </>
      ) : (
        activeTab !== "asset" && (
          <EmptyState
            title="Select a scenario first"
            description="Navigate to the Asset & Markets tab to create or select a scenario"
          />
        )
      )}

      <ImportWizard
        open={importOpen}
        onClose={() => setImportOpen(false)}
        mode="update_existing"
        targetAssetId={assetId}
        targetAssetName={asset.name}
      />

      {/* New scenario modal */}
      <Modal
        open={scenarioPickerOpen}
        onClose={() => setScenarioPickerOpen(false)}
        title="New Scenario"
        footer={
          <>
            <Button variant="ghost" onClick={() => setScenarioPickerOpen(false)}>Cancel</Button>
            <Button
              loading={createScenario.isPending}
              onClick={handleCreateScenario}
              disabled={!newScenarioName.trim()}
            >
              Create
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-3">
          <label className="text-xs font-medium text-text-secondary uppercase tracking-wide">Name</label>
          <input
            autoFocus
            value={newScenarioName}
            onChange={(e) => setNewScenarioName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreateScenario()}
            placeholder="e.g. Full MFN 2029"
            className="w-full h-9 rounded border border-border bg-panel-elev text-sm text-text-primary px-3 focus:outline-none focus:border-navy-500"
          />
        </div>
      </Modal>
    </AppShell>
  );
}
