import { useAuth0 } from "@auth0/auth0-react";
import { useCallback } from "react";

import type {
  AnchorAnalysis,
  Asset,
  AssetCreate,
  AssetDuplicate,
  AssetUpdate,
  CountryData,
  CountryDataInput,
  DECascadeResult,
  MonteCarloResult,
  OptimizerResult,
  Page,
  Scenario,
  ScenarioCompareResult,
  ScenarioCreate,
  ScenarioDuplicate,
  ScenarioUpdate,
  SimulateResponse,
  SimulationResult,
} from "@/types/api";

const BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function call<T>(
  getToken: () => Promise<string>,
  path: string,
  init?: RequestInit,
): Promise<T> {
  const token = await getToken();
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null) as { detail?: string } | null;
    throw new ApiError(res.status, body?.detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

async function download(
  getToken: () => Promise<string>,
  path: string,
): Promise<Blob> {
  const token = await getToken();
  const res = await fetch(`${BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null) as { detail?: string } | null;
    throw new ApiError(res.status, body?.detail ?? res.statusText);
  }
  return res.blob();
}

export function useApi() {
  const { getAccessTokenSilently } = useAuth0();
  const tok = useCallback(() => getAccessTokenSilently(), [getAccessTokenSilently]);

  return {
    assets: {
      list: (cursor?: string) =>
        call<Page<Asset>>(tok, `/assets${cursor ? `?cursor=${cursor}` : ""}`),
      get: (id: string) => call<Asset>(tok, `/assets/${id}`),
      create: (payload: AssetCreate) =>
        call<Asset>(tok, "/assets", { method: "POST", body: JSON.stringify(payload) }),
      update: (id: string, payload: AssetUpdate) =>
        call<Asset>(tok, `/assets/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
      archive: (id: string) => call<void>(tok, `/assets/${id}`, { method: "DELETE" }),
      duplicate: (id: string, payload: AssetDuplicate) =>
        call<Asset>(tok, `/assets/${id}/duplicate`, {
          method: "POST",
          body: JSON.stringify(payload),
        }),
    },

    scenarios: {
      list: (assetId: string) =>
        call<Scenario[]>(tok, `/assets/${assetId}/scenarios`),
      get: (id: string) => call<Scenario>(tok, `/scenarios/${id}`),
      create: (assetId: string, payload: ScenarioCreate) =>
        call<Scenario>(tok, `/assets/${assetId}/scenarios`, {
          method: "POST",
          body: JSON.stringify(payload),
        }),
      update: (id: string, payload: ScenarioUpdate) =>
        call<Scenario>(tok, `/scenarios/${id}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        }),
      archive: (id: string) => call<void>(tok, `/scenarios/${id}`, { method: "DELETE" }),
      duplicate: (id: string, payload: ScenarioDuplicate) =>
        call<Scenario>(tok, `/scenarios/${id}/duplicate`, {
          method: "POST",
          body: JSON.stringify(payload),
        }),
    },

    countryData: {
      list: (scenarioId: string) =>
        call<CountryData[]>(tok, `/scenarios/${scenarioId}/country-data`),
      upsert: (scenarioId: string, countryCode: string, payload: CountryDataInput) =>
        call<CountryData>(tok, `/scenarios/${scenarioId}/country-data/${countryCode}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        }),
      delete: (scenarioId: string, countryCode: string) =>
        call<void>(tok, `/scenarios/${scenarioId}/country-data/${countryCode}`, {
          method: "DELETE",
        }),
    },

    simulations: {
      run: (scenarioId: string) =>
        call<SimulateResponse>(tok, `/scenarios/${scenarioId}/simulate`, { method: "POST" }),
      list: (scenarioId: string) =>
        call<SimulationResult[]>(tok, `/scenarios/${scenarioId}/simulations`),
      get: (id: string) => call<SimulationResult>(tok, `/simulations/${id}`),
      anchorAnalysis: (scenarioId: string, model = "GUARD") =>
        call<AnchorAnalysis>(tok, `/scenarios/${scenarioId}/anchor-analysis?model=${model}`, { method: "POST" }),
      deCascade: (scenarioId: string, optInRebatePct: number) =>
        call<DECascadeResult>(tok, `/scenarios/${scenarioId}/de-cascade`, {
          method: "POST",
          body: JSON.stringify({ opt_in_rebate_pct: optInRebatePct }),
        }),
      monteCarlo: (scenarioId: string, n: number, sigma: number, model = "GUARD") =>
        call<MonteCarloResult>(tok, `/scenarios/${scenarioId}/monte-carlo`, {
          method: "POST",
          body: JSON.stringify({ n, sigma, model }),
        }),
      optimize: (scenarioId: string) =>
        call<OptimizerResult>(tok, `/scenarios/${scenarioId}/optimize`, { method: "POST" }),
      compare: (assetId: string, scenarioIds: string[]) =>
        call<ScenarioCompareResult>(tok, `/assets/${assetId}/compare`, {
          method: "POST",
          body: JSON.stringify({ scenario_ids: scenarioIds }),
        }),
      downloadAuditPack: (simulationId: string) =>
        download(tok, `/simulations/${simulationId}/audit-pack`),
    },

    auditPack: {
      downloadForAsset: (assetId: string) =>
        download(tok, `/assets/${assetId}/audit-pack`),
    },

    exports: {
      myData: () => download(tok, `/export/my-data`),
      tenantPack: () => download(tok, `/export/tenant-pack`),
    },
  };
}
