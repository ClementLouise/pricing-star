import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { Outlet } from "react-router-dom";

export default function AuthGuard() {
  const { isAuthenticated, loginWithRedirect } = useAuth0();

  useEffect(() => {
    if (!isAuthenticated) {
      loginWithRedirect();
    }
  }, [isAuthenticated, loginWithRedirect]);

  if (!isAuthenticated) return null;

  return <Outlet />;
}
