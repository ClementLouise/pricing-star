import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useApi } from "@/lib/api";
import { useAppStore } from "@/store";

export function useRunSimulation(scenarioId: string) {
  const api = useApi();
  const qc = useQueryClient();
  const setLatestSimulation = useAppStore((s) => s.setLatestSimulation);

  return useMutation({
    mutationFn: () => api.simulations.run(scenarioId),
    onSuccess: (data) => {
      setLatestSimulation(data.results);
      qc.invalidateQueries({ queryKey: ["simulations", scenarioId] });
    },
  });
}

export function useSimulationList(scenarioId: string) {
  const api = useApi();
  return useQuery({
    queryKey: ["simulations", scenarioId],
    queryFn: () => api.simulations.list(scenarioId),
    enabled: Boolean(scenarioId),
  });
}

export function useAnchorAnalysis(scenarioId: string) {
  const api = useApi();
  return useMutation({
    mutationFn: (model: string = "GUARD") => api.simulations.anchorAnalysis(scenarioId, model),
  });
}

export function useDECascade(scenarioId: string) {
  const api = useApi();
  return useMutation({
    mutationFn: (optInRebatePct: number) => api.simulations.deCascade(scenarioId, optInRebatePct),
  });
}

export function useMonteCarlo(scenarioId: string) {
  const api = useApi();
  return useMutation({
    mutationFn: ({ n, sigma, model }: { n: number; sigma: number; model?: string }) =>
      api.simulations.monteCarlo(scenarioId, n, sigma, model),
  });
}

export function useOptimize(scenarioId: string) {
  const api = useApi();
  return useMutation({
    mutationFn: () => api.simulations.optimize(scenarioId),
  });
}

export function useCompareScenarios(assetId: string) {
  const api = useApi();
  return useMutation({
    mutationFn: (scenarioIds: string[]) => api.simulations.compare(assetId, scenarioIds),
  });
}
