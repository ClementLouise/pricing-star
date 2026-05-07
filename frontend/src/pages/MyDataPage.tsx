import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { useToast } from "@/components/ui/Toast";
import { useApi } from "@/lib/api";

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function MyDataPage() {
  const api = useApi();
  const toast = useToast();
  const navigate = useNavigate();
  const [exportingMyData, setExportingMyData] = useState(false);
  const [exportingTenantPack, setExportingTenantPack] = useState(false);

  async function handleMyDataExport() {
    setExportingMyData(true);
    try {
      const blob = await api.exports.myData();
      triggerDownload(blob, `pricingstar_my-data_${new Date().toISOString().slice(0, 10)}.zip`);
      toast.success("Your data export is ready");
    } catch {
      toast.error("Failed to generate data export");
    } finally {
      setExportingMyData(false);
    }
  }

  async function handleTenantPackExport() {
    setExportingTenantPack(true);
    try {
      const blob = await api.exports.tenantPack();
      triggerDownload(blob, `pricingstar_tenant-pack_${new Date().toISOString().slice(0, 10)}.zip`);
      toast.success("Tenant pack downloaded");
    } catch {
      toast.error("Failed to generate tenant pack — admin role required");
    } finally {
      setExportingTenantPack(false);
    }
  }

  return (
    <AppShell variant="minimal">
      <div className="max-w-2xl mx-auto py-12 px-6">

        <button
          onClick={() => navigate(-1)}
          className="text-xs text-text-tertiary hover:text-text-secondary mb-8 transition-colors"
        >
          ← Retour
        </button>

        <h1 className="text-2xl font-semibold text-text-primary mb-2">Mes données</h1>
        <p className="text-sm text-text-secondary mb-8">
          Conformément au RGPD Article 20, vous pouvez télécharger l'intégralité de vos données
          au format ZIP à tout moment.
        </p>

        <div className="flex flex-col gap-4">

          <Panel>
            <div className="flex items-start justify-between gap-6">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-text-primary mb-1">
                  Export de mes données (RGPD)
                </h3>
                <p className="text-xs text-text-secondary leading-relaxed">
                  Archive ZIP contenant votre profil, les assets, scénarios, simulations et clés API
                  de votre tenant. Les hachages de clés API (secrets) ne sont pas inclus.
                </p>
                <ul className="mt-2 text-xs text-text-tertiary space-y-0.5">
                  <li>profile.json — votre profil utilisateur</li>
                  <li>assets.json — tous les assets</li>
                  <li>scenarios.json — tous les scénarios</li>
                  <li>simulations.json — tous les résultats de simulation</li>
                  <li>audit_log.json — les 500 dernières entrées d'audit</li>
                </ul>
              </div>
              <Button
                variant="secondary"
                size="sm"
                loading={exportingMyData}
                onClick={handleMyDataExport}
                className="shrink-0"
              >
                Télécharger
              </Button>
            </div>
          </Panel>

          <Panel>
            <div className="flex items-start justify-between gap-6">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-text-primary mb-1">
                  Tenant Pack complet
                  <span className="ml-2 text-xs font-normal text-text-tertiary">(admin uniquement)</span>
                </h3>
                <p className="text-xs text-text-secondary leading-relaxed">
                  Même contenu que l'export RGPD, plus la liste de tous les utilisateurs du tenant.
                  Nécessite le rôle administrateur.
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                loading={exportingTenantPack}
                onClick={handleTenantPackExport}
                className="shrink-0"
              >
                Télécharger
              </Button>
            </div>
          </Panel>

          <p className="text-xs text-text-tertiary mt-4 text-center">
            Pour toute question relative à vos données, contactez{" "}
            <span className="text-text-secondary">support@pricingstar.io</span>
          </p>

        </div>
      </div>
    </AppShell>
  );
}
