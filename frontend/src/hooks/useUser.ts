import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth0 } from "@auth0/auth0-react";

interface UserMe {
  id: string;
  name: string;
  role: string;
  has_seen_welcome: boolean;
}

async function fetchMe(token: string): Promise<UserMe> {
  const res = await fetch("/api/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch user");
  return res.json();
}

async function patchMe(token: string, payload: Partial<UserMe>): Promise<UserMe> {
  const res = await fetch("/api/users/me", {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update user");
  return res.json();
}

export function useUserMe() {
  const { getAccessTokenSilently } = useAuth0();
  return useQuery<UserMe>({
    queryKey: ["userMe"],
    queryFn: async () => {
      const token = await getAccessTokenSilently();
      return fetchMe(token);
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useDismissWelcome() {
  const { getAccessTokenSilently } = useAuth0();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const token = await getAccessTokenSilently();
      return patchMe(token, { has_seen_welcome: true });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["userMe"] });
    },
  });
}
