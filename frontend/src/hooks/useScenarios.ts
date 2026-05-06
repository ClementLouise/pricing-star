import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useApi } from "@/lib/api";
import type { CountryDataInput, ScenarioCreate, ScenarioUpdate } from "@/types/api";

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
  return useMutation({
    mutationFn: (payload: ScenarioUpdate) => api.scenarios.update(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["scenario", id] }),
  });
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
  return useMutation({
    mutationFn: ({ countryCode, payload }: { countryCode: string; payload: CountryDataInput }) =>
      api.countryData.upsert(scenarioId, countryCode, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["country-data", scenarioId] });
    },
  });
}

export function useDeleteCountryData(scenarioId: string) {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (countryCode: string) => api.countryData.delete(scenarioId, countryCode),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["scenario", scenarioId] }),
  });
}
