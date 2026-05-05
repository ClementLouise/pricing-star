import { useAuth0 } from "@auth0/auth0-react";

const CLAIMS_NS = "https://pricingstar.io";

export default function Dashboard() {
  const { user, logout } = useAuth0();

  const tenantTier = (user?.[`${CLAIMS_NS}/tenant_tier`] as string) ?? "—";
  const tenantId = (user?.[`${CLAIMS_NS}/tenant_id`] as string) ?? "—";

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center gap-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 w-full max-w-md">
        <h1 className="text-2xl font-semibold text-gray-900">
          Hello, {user?.name ?? "there"} 👋
        </h1>
        <div className="mt-4 space-y-2 text-sm text-gray-600">
          <p>
            <span className="font-medium">Tenant ID:</span> {tenantId}
          </p>
          <p>
            <span className="font-medium">Tier:</span>{" "}
            <span className="capitalize">{tenantTier}</span>
          </p>
        </div>
        <button
          onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          className="mt-6 text-sm text-gray-400 hover:text-gray-600 underline"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
