import { useQuery } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";

export interface RecentActivityItem {
  id: string;
  user_id: string | null;
  action: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export function useRecentActivity(limit = 20) {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  return useQuery({
    queryKey: ["dashboard", "recent-activity", limit],
    enabled: isAuthenticated,
    queryFn: async (): Promise<RecentActivityItem[]> => {
      const token = await getAccessTokenSilently();
      const res = await fetch(`/api/dashboard/recent-activity?limit=${limit}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to load activity");
      const json = (await res.json()) as { items: RecentActivityItem[] };
      return json.items;
    },
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  });
}
