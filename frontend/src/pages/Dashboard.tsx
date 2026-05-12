import { useAuth0 } from "@auth0/auth0-react";

const CLAIMS_NS = "https://pricingstar.io";

export default function Dashboard() {
  const { user, logout } = useAuth0();

  const tenantTier = (user?.[`${CLAIMS_NS}/tenant_tier`] as string) ?? "—";
  const tenantId = (user?.[`${CLAIMS_NS}/tenant_id`] as string) ?? "—";

  return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-6">
      <div className="bg-panel rounded-md border border-border-soft p-8 w-full max-w-md shadow-sm">
        <h1 className="text-2xl font-semibold text-text-primary">
          Hello, {user?.name ?? "there"}
        </h1>
        <div className="mt-4 space-y-2 text-sm text-text-secondary">
          <p>
            <span className="font-medium text-text-primary">Tenant ID:</span> {tenantId}
          </p>
          <p>
            <span className="font-medium text-text-primary">Tier:</span>{" "}
            <span className="capitalize">{tenantTier}</span>
          </p>
        </div>
        <button
          onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          className="mt-6 text-sm text-text-tertiary hover:text-text-secondary underline transition-colors"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
