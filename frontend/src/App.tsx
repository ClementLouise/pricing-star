import { useAuth0 } from "@auth0/auth0-react";
import { Route, Routes } from "react-router-dom";

import AuthGuard from "@/components/AuthGuard";
import { ToastProvider } from "@/components/ui/Toast";
import AssetDetailPage from "@/pages/AssetDetailPage";
import AssetListPage from "@/pages/AssetListPage";
import Loading from "@/pages/Loading";
import WelcomePage from "@/pages/WelcomePage";

export default function App() {
  const { isLoading } = useAuth0();

  if (isLoading) return <Loading />;

  return (
    <ToastProvider>
      <Routes>
        <Route element={<AuthGuard />}>
          <Route path="/welcome" element={<WelcomePage />} />
          <Route path="/" element={<AssetListPage />} />
          <Route path="/assets" element={<AssetListPage />} />
          <Route path="/assets/:assetId" element={<AssetDetailPage />} />
          <Route path="/assets/:assetId/scenarios/:scenarioId" element={<AssetDetailPage />} />
        </Route>
      </Routes>
    </ToastProvider>
  );
}
