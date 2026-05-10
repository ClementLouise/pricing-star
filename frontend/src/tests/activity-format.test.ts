import { describe, expect, it } from "vitest";

import { formatActivity } from "@/lib/activity-format";
import type { RecentActivityItem } from "@/hooks/useDashboard";

function makeItem(action: string, payload: Record<string, unknown> = {}): RecentActivityItem {
  return { id: "1", user_id: null, action, payload, created_at: new Date().toISOString() };
}

describe("formatActivity", () => {
  const KNOWN_ACTIONS = [
    "asset.created",
    "asset.created_via_import",
    "asset.updated_via_import",
    "asset.updated",
    "asset.archived",
    "scenario.created",
    "scenario.updated",
    "simulation.audit_pack_exported",
    "asset.audit_pack_exported",
    "tenant.audit_pack_exported",
    "tenant.full_export_exported",
    "country_data.updated",
  ];

  it.each(KNOWN_ACTIONS)("returns non-null for known action: %s", (action) => {
    expect(formatActivity(makeItem(action))).not.toBeNull();
  });

  it("returns null for unknown action", () => {
    expect(formatActivity(makeItem("simulation.computed"))).toBeNull();
    expect(formatActivity(makeItem("unknown.event"))).toBeNull();
    expect(formatActivity(makeItem(""))).toBeNull();
  });

  it("falls back to 'Sans nom' when asset_name is missing", () => {
    const result = formatActivity(makeItem("asset.created", {}));
    expect(result?.label).toContain("Sans nom");
  });

  it("falls back to 'Sans nom' when scenario_name is missing", () => {
    const result = formatActivity(makeItem("scenario.created", {}));
    expect(result?.label).toContain("Sans nom");
  });

  it("uses asset_name from payload when provided", () => {
    const result = formatActivity(makeItem("asset.created", { asset_name: "VX-CFTR-NG" }));
    expect(result?.label).toContain("VX-CFTR-NG");
  });

  it("renders scenario_count and country_data_count in detail for import", () => {
    const result = formatActivity(
      makeItem("asset.created_via_import", { asset_name: "Drug X", scenario_count: 3, country_data_count: 42 })
    );
    expect(result?.detail).toContain("3");
    expect(result?.detail).toContain("42");
  });

  it("renders country_code in detail for country_data.updated", () => {
    const result = formatActivity(makeItem("country_data.updated", { country_code: "DE" }));
    expect(result?.detail).toContain("DE");
  });

  it("omits detail when country_code is missing for country_data.updated", () => {
    const result = formatActivity(makeItem("country_data.updated", {}));
    expect(result?.detail).toBeUndefined();
  });
});
