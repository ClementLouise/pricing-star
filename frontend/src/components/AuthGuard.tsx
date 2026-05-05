import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { Outlet } from "react-router-dom";

export default function AuthGuard() {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect();
    }
  }, [isAuthenticated, isLoading, loginWithRedirect]);

  if (isLoading || !isAuthenticated) return null;

  return <Outlet />;
}
