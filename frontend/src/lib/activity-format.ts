import type { RecentActivityItem } from "@/hooks/useDashboard";

interface FormattedActivity {
  icon: string;
  label: string;
  detail?: string;
}

const s = (v: unknown): string | undefined => (typeof v === "string" ? v : undefined);
const n = (v: unknown): number | undefined => (typeof v === "number" ? v : undefined);

/**
 * Map an audit log action + payload to a human French sentence.
 * Returns null for unknown actions — caller should skip those entries.
 */
export function formatActivity(item: RecentActivityItem): FormattedActivity | null {
  const p = item.payload;
  switch (item.action) {
    case "asset.created":
      return {
        icon: "Plus",
        label: `Asset « ${s(p.asset_name) ?? "Sans nom"} » créé`,
      };
    case "asset.created_via_import":
      return {
        icon: "Upload",
        label: `Asset « ${s(p.asset_name) ?? "Sans nom"} » importé depuis Excel`,
        detail: `${n(p.scenario_count) ?? 0} scénarios, ${n(p.country_data_count) ?? 0} lignes pays`,
      };
    case "asset.updated_via_import":
      return {
        icon: "Upload",
        label: `Asset « ${s(p.asset_name) ?? "Sans nom"} » mis à jour depuis Excel`,
      };
    case "asset.updated":
      return {
        icon: "Edit3",
        label: `Asset « ${s(p.asset_name) ?? "Sans nom"} » modifié`,
      };
    case "asset.archived":
      return { icon: "Archive", label: "Asset archivé" };
    case "scenario.created":
      return {
        icon: "GitBranch",
        label: `Nouveau scénario « ${s(p.scenario_name) ?? "Sans nom"} »`,
      };
    case "scenario.updated":
      return {
        icon: "Edit3",
        label: `Scénario « ${s(p.scenario_name) ?? "Sans nom"} » modifié`,
      };
    case "simulation.audit_pack_exported":
      return {
        icon: "Download",
        label: "Audit Pack simulation téléchargé",
      };
    case "asset.audit_pack_exported": {
      const sizeKb = ((n(p.size_bytes) ?? 0) / 1024).toFixed(0);
      return {
        icon: "Download",
        label: "Audit Pack asset téléchargé",
        detail: `${n(p.scenario_count) ?? 0} scénarios, ${sizeKb} KB`,
      };
    }
    case "tenant.audit_pack_exported":
    case "tenant.full_export_exported":
      return {
        icon: "Download",
        label: "Export tenant complet téléchargé",
      };
    case "country_data.updated":
      return {
        icon: "Globe",
        label: "Prix pays mis à jour",
        detail: s(p.country_code) ? `Marché ${s(p.country_code)}` : undefined,
      };
    default:
      return null;
  }
}
