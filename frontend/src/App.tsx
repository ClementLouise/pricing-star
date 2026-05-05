import { useAuth0 } from "@auth0/auth0-react";
import { Route, Routes } from "react-router-dom";

import AuthGuard from "@/components/AuthGuard";
import Dashboard from "@/pages/Dashboard";
import Loading from "@/pages/Loading";

export default function App() {
  const { isLoading } = useAuth0();

  if (isLoading) return <Loading />;

  return (
    <Routes>
      <Route element={<AuthGuard />}>
        <Route path="/" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}
