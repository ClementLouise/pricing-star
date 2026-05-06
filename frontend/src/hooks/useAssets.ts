import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useState } from "react";

import { ApiError, useApi } from "@/lib/api";
import type { Asset, AssetCreate, AssetUpdate } from "@/types/api";

export function useAssetList() {
  const api = useApi();
  return useQuery({
    queryKey: ["assets"],
    queryFn: () => api.assets.list(),
  });
}

export function useAsset(id: string) {
  const api = useApi();
  return useQuery({
    queryKey: ["assets", id],
    queryFn: () => api.assets.get(id),
    enabled: Boolean(id),
  });
}

export function useCreateAsset() {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: AssetCreate) => api.assets.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assets"] }),
  });
}

export function useUpdateAsset(id: string) {
  const api = useApi();
  const qc = useQueryClient();
  const [conflict, setConflict] = useState<AssetUpdate | null>(null);

  const mutation = useMutation({
    mutationFn: (payload: AssetUpdate) => {
      // Auto-inject expected_updated_at from TanStack Query cache (EC-UI-02)
      const cached = qc.getQueryData<Asset>(["assets", id]);
      return api.assets.update(id, {
        ...payload,
        expected_updated_at: payload.expected_updated_at ?? cached?.updated_at ?? null,
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assets", id] });
      qc.invalidateQueries({ queryKey: ["assets"] });
      setConflict(null);
    },
    onError: (error: unknown, variables: AssetUpdate) => {
      if (error instanceof ApiError && error.status === 409) {
        setConflict(variables);
      }
    },
  });

  const forceOverwrite = useCallback(() => {
    if (conflict) mutation.mutate({ ...conflict, force_override: true });
  }, [conflict, mutation]);

  const reload = useCallback(() => {
    qc.invalidateQueries({ queryKey: ["assets", id] });
    qc.invalidateQueries({ queryKey: ["assets"] });
    setConflict(null);
  }, [qc, id]);

  return { ...mutation, conflict, forceOverwrite, reload, dismissConflict: () => setConflict(null) };
}

export function useArchiveAsset() {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.assets.archive(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assets"] }),
  });
}
