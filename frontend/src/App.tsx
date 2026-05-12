import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, Route, Routes } from "react-router-dom";

import AuthGuard from "@/components/AuthGuard";
import { ToastProvider } from "@/components/ui/Toast";
import AssetDetailPage from "@/pages/AssetDetailPage";
import AssetListPage from "@/pages/AssetListPage";
import HomePage from "@/pages/HomePage";
import Loading from "@/pages/Loading";
import MyDataPage from "@/pages/MyDataPage";

export default function App() {
  const { isLoading, isAuthenticated } = useAuth0();
  console.log('[App] render — isLoading:', isLoading, 'isAuthenticated:', isAuthenticated);

  if (isLoading) return <Loading />;

  return (
    <ToastProvider>
      <Routes>
        <Route element={<AuthGuard />}>
          <Route path="/home" element={<HomePage />} />
          <Route path="/welcome" element={<Navigate to="/home" replace />} />
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/settings/my-data" element={<MyDataPage />} />
          <Route path="/assets" element={<AssetListPage />} />
          <Route path="/assets/:assetId" element={<AssetDetailPage />} />
          <Route path="/assets/:assetId/scenarios/:scenarioId" element={<AssetDetailPage />} />
        </Route>
      </Routes>
    </ToastProvider>
  );
}
