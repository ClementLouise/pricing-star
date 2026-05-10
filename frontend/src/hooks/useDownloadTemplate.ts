import { useState } from "react";

import { useToast } from "@/components/ui/Toast";
import { useApi } from "@/lib/api";

export function useDownloadTemplate() {
  const api = useApi();
  const toast = useToast();
  const [downloading, setDownloading] = useState(false);

  async function downloadTemplate(assetName?: string) {
    setDownloading(true);
    try {
      const blob = await api.import.downloadTemplate(assetName);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "pricing-star_import_template.xlsx";
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Téléchargement du modèle échoué");
    } finally {
      setDownloading(false);
    }
  }

  return { downloadTemplate, downloading };
}
