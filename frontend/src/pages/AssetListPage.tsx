import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Panel } from "@/components/ui/Panel";
import { Pill } from "@/components/ui/Pill";
import { SkeletonBlock } from "@/components/ui/Skeleton";
import { useToast } from "@/components/ui/Toast";
import { ImportWizard } from "@/components/ImportWizard";
import { formatCurrency, formatYear } from "@/lib/formatters";
import { useApi } from "@/lib/api";
import { useAssetList, useCreateAsset } from "@/hooks/useAssets";
import type { Asset } from "@/types/api";

function AssetRow({ asset }: { asset: Asset }) {
  const navigate = useNavigate();
  return (
    <div
      className="flex items-center gap-4 px-4 py-3 border-b border-border last:border-b-0 hover:bg-panel-elev cursor-pointer transition-colors"
      onClick={() => navigate(`/assets/${asset.id}`)}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary truncate">{asset.name}</p>
        {asset.indication && (
          <p className="text-xs text-text-secondary truncate">{asset.indication}</p>
        )}
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <div className="w-28 flex justify-end">
          {asset.therapeutic_area && (
            <Pill variant="neutral">{asset.therapeutic_area}</Pill>
          )}
        </div>
        <div className="text-right w-28">
          <p className="font-mono text-sm text-text-primary tabular-nums">
            {asset.us_list_price != null ? formatCurrency(asset.us_list_price, { compact: true }) : "—"}
          </p>
        </div>
        <div className="text-right w-20">
          <p className="font-mono text-sm text-text-primary tabular-nums">{formatYear(asset.launch_year)}</p>
        </div>
        <div className="text-right w-20">
          <p className="font-mono text-sm text-text-primary tabular-nums">{formatYear(asset.loe_year)}</p>
        </div>
      </div>
    </div>
  );
}

function TableHeader() {
  return (
    <div className="flex items-center gap-4 px-4 py-2 border-b border-border bg-panel-elev/60">
      <div className="flex-1 min-w-0">
        <p className="font-mono text-[10px] uppercase tracking-widest text-text-tertiary">Asset</p>
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <div className="w-28 text-right">
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-tertiary">Area</p>
        </div>
        <div className="w-28 text-right">
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-tertiary">US List</p>
        </div>
        <div className="w-20 text-right">
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-tertiary">Launch</p>
        </div>
        <div className="w-20 text-right">
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-tertiary">LOE</p>
        </div>
      </div>
    </div>
  );
}

function CreateAssetModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const createAsset = useCreateAsset();
  const toast = useToast();
  const navigate = useNavigate();
  const [name, setName] = useState("");

  async function handleCreate() {
    if (!name.trim()) return;
    try {
      const asset = await createAsset.mutateAsync({ name: name.trim() });
      toast.success(`Asset "${asset.name}" created`);
      onClose();
      navigate(`/assets/${asset.id}`);
    } catch {
      toast.error("Failed to create asset");
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="New Asset"
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button loading={createAsset.isPending} onClick={handleCreate} disabled={!name.trim()}>
            Create
          </Button>
        </>
      }
    >
      <Input
        label="Asset name"
        placeholder="e.g. VX-CFTR-NG"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        helper="You can fill in all other details after creation"
        autoFocus
      />
    </Modal>
  );
}

export default function AssetListPage() {
  const { data, isLoading } = useAssetList();
  const [creating, setCreating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const api = useApi();
  const toast = useToast();

  const assets = data?.items ?? [];

  async function handleExport() {
    setExporting(true);
    try {
      const blob = await api.exports.tenantPack();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `pricingstar_export_${new Date().toISOString().slice(0, 10)}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Export failed");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <header className="flex items-center justify-between px-6 h-12 bg-panel border-b border-border">
        <span className="flex items-center gap-0.5 text-sm font-semibold text-text-primary tracking-tight">
          PRICING<span className="text-gold-500">STAR</span>
          <span className="text-gold-500 text-[8px] leading-none ml-0.5">●</span>
        </span>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-6">
          <p className="font-mono text-xs uppercase tracking-widest text-text-tertiary mb-1">Portfolio</p>
          <div className="flex items-end justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-text-primary">Assets</h1>
              {!isLoading && (
                <p className="text-sm text-text-secondary mt-0.5">
                  {assets.length === 0
                    ? "No assets yet"
                    : `${assets.length} asset${assets.length === 1 ? "" : "s"}`}
                </p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" loading={exporting} onClick={handleExport}>
                Export
              </Button>
              <Button variant="secondary" size="sm" onClick={() => setImporting(true)}>
                Import from Excel
              </Button>
              <Button size="sm" onClick={() => setCreating(true)}>
                New asset
              </Button>
            </div>
          </div>
        </div>

        <Panel padding="none">
          {isLoading ? (
            <div className="p-4">
              <SkeletonBlock lines={5} />
            </div>
          ) : assets.length === 0 ? (
            <EmptyState
              title="No assets yet"
              description="Create your first asset or import from Excel to start modeling pricing scenarios"
              action={
                <div className="flex items-center gap-2">
                  <Button variant="secondary" size="sm" onClick={() => setImporting(true)}>
                    Import from Excel
                  </Button>
                  <Button size="sm" onClick={() => setCreating(true)}>
                    Create asset
                  </Button>
                </div>
              }
            />
          ) : (
            <>
              <TableHeader />
              {assets.map((a) => <AssetRow key={a.id} asset={a} />)}
            </>
          )}
        </Panel>
      </main>

      <CreateAssetModal open={creating} onClose={() => setCreating(false)} />
      <ImportWizard
        open={importing}
        onClose={() => setImporting(false)}
        mode="create_new"
      />
    </div>
  );
}
