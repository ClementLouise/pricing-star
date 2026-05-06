import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useApi } from "@/lib/api";
import type { AssetCreate, AssetUpdate } from "@/types/api";

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
  return useMutation({
    mutationFn: (payload: AssetUpdate) => api.assets.update(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assets", id] });
      qc.invalidateQueries({ queryKey: ["assets"] });
    },
  });
}

export function useArchiveAsset() {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.assets.archive(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["assets"] }),
  });
}
