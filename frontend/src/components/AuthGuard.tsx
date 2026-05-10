import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useUserMe } from "@/hooks/useUser";

export default function AuthGuard() {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();
  const location = useLocation();
  const { data: userMe, isLoading: userLoading } = useUserMe();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect();
    }
  }, [isAuthenticated, isLoading, loginWithRedirect]);

  if (isLoading || !isAuthenticated) return null;

  // Wait for user data before deciding on redirect
  if (userLoading) return null;

  if (userMe && !userMe.has_seen_welcome && location.pathname !== "/home") {
    return <Navigate to="/home" replace />;
  }

  return <Outlet />;
}
