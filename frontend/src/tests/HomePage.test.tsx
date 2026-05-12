import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

import { useAssetList } from "@/hooks/useAssets";
import { useRecentActivity } from "@/hooks/useDashboard";
import { useDismissWelcome, useUserMe } from "@/hooks/useUser";
import { useNavigate } from "react-router-dom";

// ── Module mocks (hoisted by Vitest) ──────────────────────────────────────────

vi.mock("@/components/layout/AppShell", () => ({
  AppShell: ({ children }: { children: unknown }) => <>{children as React.ReactNode}</>,
}));
vi.mock("@/components/ImportWizard", () => ({
  ImportWizard: () => null,
}));
vi.mock("@/components/ui/Modal", () => ({
  Modal: ({ open, children, title }: { open: boolean; children: unknown; title: string }) =>
    open ? <div role="dialog" aria-label={title}>{children as React.ReactNode}</div> : null,
}));
vi.mock("react-router-dom", () => ({ useNavigate: vi.fn() }));
vi.mock("@auth0/auth0-react", () => ({
  useAuth0: () => ({ isAuthenticated: true, getAccessTokenSilently: vi.fn() }),
}));
vi.mock("@/hooks/useAssets", () => ({ useAssetList: vi.fn() }));
vi.mock("@/hooks/useDashboard", () => ({ useRecentActivity: vi.fn() }));
vi.mock("@/hooks/useUser", () => ({
  useUserMe: vi.fn(),
  useDismissWelcome: vi.fn(),
}));
vi.mock("@/hooks/useDownloadTemplate", () => ({
  useDownloadTemplate: () => ({ downloadTemplate: vi.fn(), downloading: false }),
}));

// ── Helpers ───────────────────────────────────────────────────────────────────

import type { Asset } from "@/types/api";

function makeAsset(overrides: Partial<Asset> = {}): Asset {
  return {
    id: "asset-1",
    tenant_id: "t1",
    name: "VX-CFTR-NG",
    therapeutic_area: null,
    modality: null,
    indication: "CF",
    us_list_price: 300000,
    us_net_share: 0.5,
    launch_year: 2027,
    peak_year: 2030,
    loe_year: 2038,
    cogs_percent: 0.05,
    discount_rate: 0.1,
    us_patient_population: null,
    ex_us_patient_population: null,
    peak_capture_rate: 0.8,
    part_b_share: 0.5,
    ramp_years: 3,
    is_sample: false,
    sample_origin: null,
    created_at: "2026-05-01T10:00:00Z",
    updated_at: "2026-05-09T14:00:00Z",
    archived_at: null,
    ...overrides,
  };
}

const EMPTY_PAGE = { items: [], next_cursor: null };

// ── Setup ─────────────────────────────────────────────────────────────────────

let mockNavigate: Mock;
let mockDismiss: Mock;

beforeEach(async () => {
  mockNavigate = vi.fn();
  mockDismiss = vi.fn().mockResolvedValue({});

  (useNavigate as Mock).mockReturnValue(mockNavigate);
  (useAssetList as Mock).mockReturnValue({ data: EMPTY_PAGE, isLoading: false, isError: false });
  (useRecentActivity as Mock).mockReturnValue({ data: [], isLoading: false });
  (useUserMe as Mock).mockReturnValue({ data: { id: "u1", name: "Sarah Chen", role: "admin", has_seen_welcome: true } });
  (useDismissWelcome as Mock).mockReturnValue({ mutateAsync: mockDismiss });

});

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("HomePage", () => {
  async function renderPage() {
    const { default: HomePage } = await import("@/pages/HomePage");
    return render(<HomePage />);
  }

  it("renders didactic mode when no assets and no activity", async () => {
    await renderPage();
    expect(screen.getByText(/Naviguer MFN. Défendre la NPV./)).toBeInTheDocument();
    expect(screen.getByText(/Pour commencer/i)).toBeInTheDocument();
    expect(screen.queryByText(/Tableau de bord/i)).toBeNull();
  });

  it("renders dashboard mode when assets are present", async () => {
    (useAssetList as Mock).mockReturnValue({
      data: { items: [makeAsset()], next_cursor: null },
      isLoading: false,
      isError: false,
    });
    await renderPage();
    expect(screen.getByText(/Tableau de bord/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Bonjour Sarah/i })).toBeInTheDocument();
    expect(screen.queryByText(/Naviguer MFN/)).toBeNull();
  });

  it("renders dashboard mode when activity is present but no assets", async () => {
    (useRecentActivity as Mock).mockReturnValue({
      data: [{ id: "e1", user_id: null, action: "asset.created", payload: { asset_name: "Drug X" }, created_at: "2026-05-09T14:00:00Z" }],
      isLoading: false,
    });
    await renderPage();
    expect(screen.getByText(/Tableau de bord/i)).toBeInTheDocument();
  });

  it("calls mutateAsync once on mount when has_seen_welcome is false", async () => {
    (useUserMe as Mock).mockReturnValue({
      data: { id: "u1", name: "New User", role: "admin", has_seen_welcome: false },
    });
    await renderPage();
    await waitFor(() => expect(mockDismiss).toHaveBeenCalledOnce());
  });

  it("does not call mutateAsync when has_seen_welcome is true", async () => {
    (useUserMe as Mock).mockReturnValue({
      data: { id: "u1", name: "Sarah", role: "admin", has_seen_welcome: true },
    });
    await renderPage();
    await waitFor(() => {}, { timeout: 100 });
    expect(mockDismiss).not.toHaveBeenCalled();
  });

  it("quick action 'Nouvel asset' navigates to /assets", async () => {
    (useAssetList as Mock).mockReturnValue({
      data: { items: [makeAsset()], next_cursor: null },
      isLoading: false,
      isError: false,
    });
    await renderPage();
    fireEvent.click(screen.getByRole("button", { name: /Nouvel asset/i }));
    expect(mockNavigate).toHaveBeenCalledWith("/assets");
  });

  it("renders activity items in the order returned (newest first from API)", async () => {
    (useAssetList as Mock).mockReturnValue({
      data: { items: [makeAsset()], next_cursor: null },
      isLoading: false,
      isError: false,
    });
    (useRecentActivity as Mock).mockReturnValue({
      data: [
        { id: "e1", user_id: null, action: "asset.created", payload: { asset_name: "First Drug" }, created_at: "2026-05-09T15:00:00Z" },
        { id: "e2", user_id: null, action: "scenario.created", payload: { scenario_name: "Base Case" }, created_at: "2026-05-09T14:00:00Z" },
      ],
      isLoading: false,
    });
    await renderPage();
    // First drug should appear before base case (already sorted by API)
    const labels = screen.getAllByText(/Asset|scénario/i).map(el => el.textContent ?? "");
    const firstIdx = labels.findIndex(l => l.includes("First Drug"));
    const secondIdx = labels.findIndex(l => l.includes("Base Case"));
    expect(firstIdx).toBeLessThan(secondIdx);
  });

  it("filters out unknown action types silently — no crash", async () => {
    (useAssetList as Mock).mockReturnValue({
      data: { items: [makeAsset()], next_cursor: null },
      isLoading: false,
      isError: false,
    });
    (useRecentActivity as Mock).mockReturnValue({
      data: [
        { id: "e1", user_id: null, action: "totally.unknown", payload: {}, created_at: "2026-05-09T15:00:00Z" },
      ],
      isLoading: false,
    });
    // Should render without throwing
    expect(() => renderPage()).not.toThrow();
    await renderPage();
    // The feed header shows but no items rendered (unknown action filtered)
    expect(screen.queryByText(/totally\.unknown/)).toBeNull();
  });
});
