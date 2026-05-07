import { useAuth0 } from "@auth0/auth0-react";
import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";

import { KPICard } from "@/components/ui/KPICard";
import { Pill } from "@/components/ui/Pill";
import { useAppStore } from "@/store";

const CLAIMS_NS = "https://pricingstar.io";

const TABS = [
  { id: "asset", label: "Asset & Markets" },
  { id: "regulations", label: "Regulations" },
  { id: "cascade", label: "IRP Cascade" },
  { id: "rebates", label: "Rebates & G2N" },
  { id: "levers", label: "Strategic Levers" },
  { id: "optimizer", label: "NPV Optimizer" },
  { id: "compare", label: "Compare" },
  { id: "anchor", label: "Anchor Analysis" },
  { id: "de-cascade", label: "DE Trap" },
] as const;

interface AppShellProps {
  children: ReactNode;
  variant?: "default" | "minimal";
}

function UserMenu() {
  const { user, logout } = useAuth0();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [open]);

  const label = user?.name ?? user?.email ?? "Account";

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1 text-xs text-text-secondary hover:text-text-primary transition-colors"
      >
        {label}
        <ChevronDown size={12} className="text-text-tertiary" />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-52 bg-panel border border-border rounded-md shadow-md z-50 overflow-hidden">
          <button
            onClick={() => { navigate("/welcome"); setOpen(false); }}
            className="w-full text-left px-4 py-2.5 text-xs text-text-secondary hover:text-text-primary hover:bg-panel-elev transition-colors"
          >
            Revoir l'introduction
          </button>
          <button
            onClick={() => { navigate("/settings/my-data"); setOpen(false); }}
            className="w-full text-left px-4 py-2.5 text-xs text-text-secondary hover:text-text-primary hover:bg-panel-elev transition-colors"
          >
            Mes données
          </button>
          <div className="border-t border-border" />
          <button
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            className="w-full text-left px-4 py-2.5 text-xs text-text-tertiary hover:text-text-primary hover:bg-panel-elev transition-colors"
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}

function TenantChip() {
  const { user } = useAuth0();
  const tenantId = (user?.[`${CLAIMS_NS}/tenant_id`] as string | undefined) ?? "";
  const tier = (user?.[`${CLAIMS_NS}/tenant_tier`] as string | undefined) ?? "";
  if (!tenantId) return null;
  const initials = tenantId.replace(/[^a-zA-Z0-9]/g, "").slice(0, 2).toUpperCase();
  const variant = tier === "trial" ? "warning" : tier === "production" ? "success" : "neutral";
  return (
    <div className="flex items-center gap-1.5 border-l border-border pl-3">
      <span className="font-mono text-xs font-medium text-text-secondary">{initials}</span>
      {tier && <Pill variant={variant}>{tier}</Pill>}
    </div>
  );
}

function Header() {
  return (
    <header className="flex items-center justify-between px-4 h-12 bg-panel border-b border-border shrink-0">
      <div className="flex items-center gap-3">
        <Link to="/assets" className="flex items-center gap-0.5 text-sm font-semibold text-text-primary tracking-tight">
          PRICING<span className="text-gold-500">STAR</span>
          <span className="text-gold-500 text-[8px] leading-none ml-0.5">●</span>
        </Link>
        <TenantChip />
      </div>
      <UserMenu />
    </header>
  );
}

function KPIBar() {
  const latestSimulation = useAppStore((s) => s.latestSimulation);
  const activeAsset = useAppStore((s) => s.activeAsset);

  if (!activeAsset) return null;

  return (
    <div className="flex items-stretch gap-0 border-b border-border bg-panel shrink-0">
      <div className="px-4 py-2 border-r border-border min-w-48">
        <p className="text-xs text-text-tertiary uppercase tracking-widest">Asset</p>
        <p className="text-sm font-medium text-text-primary truncate">{activeAsset.name}</p>
        {activeAsset.indication && (
          <p className="text-xs text-text-secondary truncate">{activeAsset.indication}</p>
        )}
      </div>
      <div className="flex items-stretch flex-1">
        <div className="border-r border-border">
          <KPICard label="14-Y NPV" value={latestSimulation?.npv ?? null} format="currency" />
        </div>
        <div className="border-r border-border">
          <KPICard label="Peak Revenue" value={latestSimulation?.peak_revenue ?? null} format="currency" />
        </div>
        <div className="border-r border-border">
          <KPICard
            label="Method I Anchor"
            value={latestSimulation?.method_i_value ?? null}
            format="currency"
            sublabel={latestSimulation?.method_i_anchor ?? undefined}
          />
        </div>
        <div>
          <KPICard
            label="US Net Price"
            value={
              activeAsset.us_list_price != null && activeAsset.us_net_share != null
                ? activeAsset.us_list_price * activeAsset.us_net_share
                : null
            }
            format="currency"
            precision={0}
          />
        </div>
      </div>
    </div>
  );
}

function TabNav() {
  const activeTab = useAppStore((s) => s.activeTab);
  const setActiveTab = useAppStore((s) => s.setActiveTab);
  const activeScenario = useAppStore((s) => s.activeScenario);

  return (
    <nav className="flex border-b border-border bg-panel shrink-0 px-4" aria-label="Tabs">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          disabled={!activeScenario && tab.id !== "asset"}
          className={[
            "px-3 py-2 text-xs border-b-2 transition-colors duration-fast",
            activeTab === tab.id
              ? "border-gold-500 text-text-primary font-medium"
              : "border-transparent text-text-secondary hover:text-text-primary",
            !activeScenario && tab.id !== "asset" ? "opacity-40 cursor-not-allowed" : "cursor-pointer",
          ].join(" ")}
        >
          {tab.label}
        </button>
      ))}
      {activeScenario && (
        <span className="ml-auto self-center text-xs text-text-tertiary">
          Scenario: <span className="text-text-secondary">{activeScenario.name}</span>
        </span>
      )}
    </nav>
  );
}

export function AppShell({ children, variant = "default" }: AppShellProps) {
  return (
    <div className="flex flex-col h-screen bg-bg text-text-primary overflow-hidden">
      <Header />
      {variant === "default" && <KPIBar />}
      {variant === "default" && <TabNav />}
      <main className="flex-1 overflow-y-auto p-4">{children}</main>
    </div>
  );
}
