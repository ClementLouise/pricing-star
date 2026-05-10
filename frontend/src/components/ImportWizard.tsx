import { AlertTriangle, CheckCircle, Download, Upload, XCircle } from "lucide-react";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { useApi } from "@/lib/api";
import type { ImportDryRunResult, ImportExecuteResult, ImportValidationError } from "@/types/api";

export interface ImportWizardProps {
  open: boolean;
  onClose: () => void;
  /** create_new = new asset; update_existing = overwrite an existing asset */
  mode: "create_new" | "update_existing";
  targetAssetId?: string;
  targetAssetName?: string;
}

type Step = "upload" | "review" | "done";

function ErrorGroup({ errors }: { errors: ImportValidationError[] }) {
  const bySheet = errors.reduce<Record<string, ImportValidationError[]>>((acc, e) => {
    (acc[e.sheet] ??= []).push(e);
    return acc;
  }, {});
  return (
    <div className="flex flex-col gap-2">
      {Object.entries(bySheet).map(([sheet, errs]) => (
        <div key={sheet}>
          <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1">
            {sheet}
          </p>
          {errs.map((e, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-danger py-1">
              <XCircle size={12} className="mt-0.5 shrink-0" />
              <span>{e.message}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function WarningList({ warnings }: { warnings: ImportValidationError[] }) {
  if (!warnings.length) return null;
  return (
    <div className="mt-3 rounded border border-yellow-700/40 bg-yellow-900/20 p-3 flex flex-col gap-1">
      {warnings.map((w, i) => (
        <div key={i} className="flex items-start gap-2 text-xs text-yellow-400">
          <AlertTriangle size={12} className="mt-0.5 shrink-0" />
          <span>{w.message}</span>
        </div>
      ))}
    </div>
  );
}

export function ImportWizard({
  open,
  onClose,
  mode,
  targetAssetId,
  targetAssetName,
}: ImportWizardProps) {
  const api = useApi();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [step, setStep] = useState<Step>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [validating, setValidating] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [downloadingTemplate, setDownloadingTemplate] = useState(false);
  const [dryRun, setDryRun] = useState<ImportDryRunResult | null>(null);
  const [result, setResult] = useState<ImportExecuteResult | null>(null);
  const [executeError, setExecuteError] = useState<string | null>(null);

  function reset() {
    setStep("upload");
    setFile(null);
    setDryRun(null);
    setResult(null);
    setExecuteError(null);
    setValidating(false);
    setExecuting(false);
  }

  function handleClose() {
    reset();
    onClose();
  }

  async function handleDownloadTemplate() {
    setDownloadingTemplate(true);
    try {
      const blob = await api.import.downloadTemplate(targetAssetName);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `pricing-star_import_template.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setDownloadingTemplate(false);
    }
  }

  async function handleValidate() {
    if (!file) return;
    setValidating(true);
    try {
      const res = await api.import.dryRun(file, mode, targetAssetId);
      setDryRun(res);
    } catch (err) {
      setDryRun({
        valid: false,
        mode,
        errors: [{
          sheet: "(fichier)", row: null, column: null,
          code: "API_ERROR", message: String(err), raw_value: null,
        }],
        warnings: [],
        summary: { scenario_count: 0, country_data_count: 0, scenario_names: [] },
      });
    } finally {
      setValidating(false);
      setStep("review");
    }
  }

  async function handleExecute() {
    if (!file || !dryRun?.valid) return;
    setExecuting(true);
    setExecuteError(null);
    try {
      const res = await api.import.execute(file, mode, targetAssetId);
      setResult(res);
      setStep("done");
    } catch (err) {
      setExecuteError(String(err));
    } finally {
      setExecuting(false);
    }
  }

  // ── Titles ─────────────────────────────────────────────────────────────────
  const title =
    step === "done" ? "Import réussi" :
    mode === "update_existing" ? `Mettre à jour${targetAssetName ? ` — ${targetAssetName}` : ""}` :
    "Importer depuis Excel";

  // ── Step: Upload ───────────────────────────────────────────────────────────
  const uploadStep = (
    <>
      <div className="flex flex-col gap-3">
        {mode === "update_existing" && targetAssetName && (
          <div className="rounded border border-border bg-panel-elev px-3 py-2 text-xs text-text-secondary">
            Mise à jour de l'asset : <span className="text-text-primary font-medium">{targetAssetName}</span>
          </div>
        )}

        {/* Template download panel */}
        <div className="flex items-center justify-between rounded border border-border bg-panel-elev px-4 py-3">
          <div>
            <p className="text-sm font-medium text-text-primary">Modèle Excel</p>
            <p className="text-xs text-text-secondary mt-0.5">Téléchargez le template et remplissez-le avant d'importer</p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            loading={downloadingTemplate}
            onClick={handleDownloadTemplate}
          >
            <Download size={14} />
            Télécharger
          </Button>
        </div>

        {/* File drop zone */}
        <div
          className="rounded border-2 border-dashed border-border hover:border-navy-500 transition-colors cursor-pointer flex flex-col items-center justify-center gap-2 py-8 px-4 text-center"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f) setFile(f);
          }}
        >
          <Upload size={24} className="text-text-tertiary" />
          {file ? (
            <p className="text-sm text-text-primary font-medium">{file.name}</p>
          ) : (
            <>
              <p className="text-sm text-text-secondary">Déposez un fichier XLSX ici</p>
              <p className="text-xs text-text-tertiary">ou cliquez pour sélectionner</p>
            </>
          )}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) setFile(f); }}
        />

      </div>

      {/* Footer */}
      <div className="flex justify-end gap-2 pt-4 border-t border-border mt-4">
        <Button variant="ghost" onClick={handleClose}>Annuler</Button>
        <Button
          disabled={!file}
          loading={validating}
          onClick={handleValidate}
        >
          Valider
        </Button>
      </div>
    </>
  );

  // ── Step: Review ───────────────────────────────────────────────────────────
  const reviewStep = dryRun && (
    <>
      <div className="flex flex-col gap-3 max-h-72 overflow-y-auto pr-1">
        {dryRun.valid ? (
          <div className="rounded border border-green-700/40 bg-green-900/20 p-3">
            <div className="flex items-center gap-2 text-green-400 text-sm font-medium mb-2">
              <CheckCircle size={14} />
              Fichier valide — prêt à importer
            </div>
            <ul className="text-xs text-text-secondary space-y-1">
              <li>{dryRun.summary.scenario_count} scénario{dryRun.summary.scenario_count !== 1 ? "s" : ""}</li>
              <li>{dryRun.summary.country_data_count} ligne{dryRun.summary.country_data_count !== 1 ? "s" : ""} de données pays</li>
            </ul>
          </div>
        ) : (
          <div className="rounded border border-danger/40 bg-red-900/10 p-3">
            <div className="flex items-center gap-2 text-danger text-sm font-medium mb-2">
              <XCircle size={14} />
              {dryRun.errors.length} erreur{dryRun.errors.length !== 1 ? "s" : ""} de validation
            </div>
            <ErrorGroup errors={dryRun.errors} />
          </div>
        )}
        <WarningList warnings={dryRun.warnings} />
        {executeError && (
          <p className="text-xs text-danger">{executeError}</p>
        )}
      </div>

      {/* Footer */}
      <div className="flex justify-end gap-2 pt-4 border-t border-border mt-4">
        <Button variant="ghost" onClick={() => { setStep("upload"); setExecuteError(null); }}>
          Modifier le fichier
        </Button>
        <Button
          disabled={!dryRun.valid}
          loading={executing}
          onClick={handleExecute}
        >
          {mode === "update_existing" ? "Mettre à jour" : "Importer"}
        </Button>
      </div>
    </>
  );

  // ── Step: Done ─────────────────────────────────────────────────────────────
  const doneStep = result && (
    <>
      <div className="flex flex-col items-center gap-4 py-4">
        <CheckCircle size={40} className="text-green-400" />
        <div className="text-center">
          <p className="text-sm text-text-primary font-medium">
            {mode === "update_existing" ? "Asset mis à jour avec succès" : "Asset créé avec succès"}
          </p>
          <p className="text-xs text-text-secondary mt-1">
            {result.scenario_ids.length} scénario{result.scenario_ids.length !== 1 ? "s" : ""} importé{result.scenario_ids.length !== 1 ? "s" : ""},&nbsp;
            {result.country_data_count} données pays
          </p>
        </div>
        <WarningList warnings={result.warnings} />
      </div>

      {/* Footer */}
      <div className="flex justify-end gap-2 pt-4 border-t border-border mt-4">
        <Button variant="ghost" onClick={handleClose}>Fermer</Button>
        <Button onClick={() => { handleClose(); navigate(`/assets/${result.asset_id}`); }}>
          Voir l'asset
        </Button>
      </div>
    </>
  );

  return (
    <Modal open={open} onClose={handleClose} title={title} size="md">
      {step === "upload" && uploadStep}
      {step === "review" && reviewStep}
      {step === "done" && doneStep}
    </Modal>
  );
}
