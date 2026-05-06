import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";

import { ApiError, useApi } from "@/lib/api";
import type { CountryData, CountryDataInput, Scenario, ScenarioCreate, ScenarioUpdate } from "@/types/api";

export function useScenarioList(assetId: string) {
  const api = useApi();
  return useQuery({
    queryKey: ["scenarios", assetId],
    queryFn: () => api.scenarios.list(assetId),
    enabled: Boolean(assetId),
  });
}

export function useScenario(id: string) {
  const api = useApi();
  return useQuery({
    queryKey: ["scenario", id],
    queryFn: () => api.scenarios.get(id),
    enabled: Boolean(id),
  });
}

export function useCreateScenario(assetId: string) {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ScenarioCreate) => api.scenarios.create(assetId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["scenarios", assetId] }),
  });
}

export function useUpdateScenario(id: string) {
  const api = useApi();
  const qc = useQueryClient();
  const [conflict, setConflict] = useState<ScenarioUpdate | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: ScenarioUpdate) => {
      // Auto-inject expected_updated_at from TanStack Query cache (EC-UI-02)
      const cached = qc.getQueryData<Scenario>(["scenario", id]);
      return api.scenarios.update(id, {
        ...payload,
        expected_updated_at: payload.expected_updated_at ?? cached?.updated_at ?? null,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["scenario", id] });
      setConflict(null);
    },
    onError: (error: unknown, variables: ScenarioUpdate) => {
      if (error instanceof ApiError && error.status === 409) {
        setConflict(variables);
      }
    },
  });

  const forceOverwrite = useCallback(() => {
    if (conflict) mutation.mutate({ ...conflict, force_override: true });
  }, [conflict, mutation]);

  const reload = useCallback(() => {
    qc.invalidateQueries({ queryKey: ["scenario", id] });
    setConflict(null);
  }, [qc, id]);

  return { ...mutation, conflict, forceOverwrite, reload, dismissConflict: () => setConflict(null) };
}

export function useCountryDataList(scenarioId: string) {
  const api = useApi();
  return useQuery({
    queryKey: ["country-data", scenarioId],
    queryFn: () => api.countryData.list(scenarioId),
    enabled: Boolean(scenarioId),
  });
}

export function useUpsertCountryData(scenarioId: string) {
  const api = useApi();
  const qc = useQueryClient();
  const [conflict, setConflict] = useState<{ countryCode: string; payload: CountryDataInput } | null>(null);

  const mutation = useMutation({
    mutationFn: ({ countryCode, payload }: { countryCode: string; payload: CountryDataInput }) => {
      // Auto-inject expected_updated_at from cache for the specific country (EC-UI-02)
      const cached = qc.getQueryData<CountryData[]>(["country-data", scenarioId]);
      const existing = cached?.find((cd) => cd.country_code === countryCode);
      return api.countryData.upsert(scenarioId, countryCode, {
        ...payload,
        expected_updated_at: payload.expected_updated_at ?? existing?.updated_at ?? null,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["country-data", scenarioId] });
      setConflict(null);
    },
    onError: (
      error: unknown,
      variables: { countryCode: string; payload: CountryDataInput },
    ) => {
      if (error instanceof ApiError && error.status === 409) {
        setConflict(variables);
      }
    },
  });

  const forceOverwrite = useCallback(() => {
    if (conflict) {
      mutation.mutate({
        countryCode: conflict.countryCode,
        payload: { ...conflict.payload, force_override: true },
      });
    }
  }, [conflict, mutation]);

  const reload = useCallback(() => {
    qc.invalidateQueries({ queryKey: ["country-data", scenarioId] });
    setConflict(null);
  }, [qc, scenarioId]);

  return { ...mutation, conflict, forceOverwrite, reload, dismissConflict: () => setConflict(null) };
}

export function useDeleteCountryData(scenarioId: string) {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (countryCode: string) => api.countryData.delete(scenarioId, countryCode),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["scenario", scenarioId] }),
  });
}
