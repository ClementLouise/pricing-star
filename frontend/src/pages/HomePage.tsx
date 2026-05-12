import {
  Activity, Archive, BarChart3, ChevronDown, ChevronRight,
  Download, Edit3, GitBranch, Globe, Layers, Plus,
  Shield, Sparkles, Upload,
} from "lucide-react";
import { type ComponentType, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ImportWizard } from "@/components/ImportWizard";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Panel } from "@/components/ui/Panel";
import { Skeleton, SkeletonBlock } from "@/components/ui/Skeleton";
import { useAssetList } from "@/hooks/useAssets";
import { useRecentActivity } from "@/hooks/useDashboard";
import { useDownloadTemplate } from "@/hooks/useDownloadTemplate";
import { useDismissWelcome, useUserMe } from "@/hooks/useUser";
import { formatActivity } from "@/lib/activity-format";
import { formatRelativeTime } from "@/lib/formatters";
import type { Asset } from "@/types/api";

// ─── Icon resolver ────────────────────────────────────────────────────────────

type LucideIcon = ComponentType<{ className?: string }>;
const ICON_MAP: Record<string, LucideIcon> = {
  Plus, Upload, Edit3, Archive, GitBranch, Globe, BarChart3, Download, Activity,
};
function ActivityIcon({ name }: { name: string }) {
  const Icon = ICON_MAP[name] ?? Activity;
  return <Icon className="w-4 h-4 text-text-secondary" />;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const PROBLEMS = [
  {
    title: "Excel ne tient plus.",
    body: "Les régulations CMS empilent du calcul multi-méthodes sur 19 pays OECD ; un spreadsheet casse à la deuxième itération.",
    response: "Moteur de calcul testé contre les fixtures CMS, audit JSON exportable, SOX 404-ready.",
  },
  {
    title: "Le Method I anchor n'est pas évident.",
    body: "Sous la convention CMS multiply (PPP), c'est souvent CH/IE/NO et pas le pays au prix le plus bas. Excel ne le voit pas.",
    response: "Identification automatique de l'anchor avec PPP normalisation et recommandation ringfencing.",
  },
  {
    title: "La cascade IRP est dense.",
    body: "27 marchés référencent l'Allemagne. Un disclosed cut de 9pp coûte typiquement −$2-5B NPV ex-US.",
    response: "Simulateur cascade interactif : quantifie le piège de l'opt-in DE en temps réel.",
  },
];

interface Module {
  icon: LucideIcon;
  name: string;
  description: string;
  detail: string;
}
const MODULES: Module[] = [
  { icon: Globe,      name: "Asset & Markets",   description: "Saisie médicament + prix par pays", detail: "Configurez le médicament (prix US, indications, marchés cibles, G2N). Étape fondatrice de chaque simulation." },
  { icon: Shield,     name: "Regulations",        description: "Activer Generous / Guard / Globe",  detail: "Activez les trois modèles CMS selon votre scénario. Chaque règlement a sa propre méthode de calcul et son calendrier de phase-in." },
  { icon: Layers,     name: "IRP Cascade",        description: "Propagation des prix sur 43 marchés", detail: "Visualisez comment vos prix se propagent via les règles IRP sur les 43 marchés référencés. Chaque modification d'un prix source déclenche une mise à jour en cascade." },
  { icon: BarChart3,  name: "Rebates & G2N",      description: "Rebates confidentiels par pays",   detail: "Saisissez les rebates confidentiels marché par marché et mesurez leur impact sur la NPV. Les ratios G2N déterminent les prix nets qui entrent dans le calcul MFN." },
  { icon: GitBranch,  name: "Strategic Levers",   description: "Withdrawals, floors, opt-in DE",   detail: "Testez des leviers stratégiques : retrait de marchés, floors de prix, délais de lancement, opt-in Allemagne. Chaque levier est quantifié en impact NPV." },
  { icon: Sparkles,   name: "NPV Optimizer",      description: "Recommandations + audit pack",     detail: "Le moteur calcule la NPV 14 ans et génère des recommandations actionnables. L'audit pack JSON est exportable pour les CFO QBR et les revues légales." },
  { icon: Activity,   name: "Compare",            description: "Scénarios côte à côte",            detail: "Comparez 2 à 5 scénarios en parallèle. Vue idéale avant une CFO review pour montrer les trade-offs entre approches réglementaires." },
  { icon: Activity,   name: "Anchor Analysis",    description: "Identification CH/IE/NO",          detail: "Identifie automatiquement l'anchor Method I avec normalisation PPP. Recommandation ringfencing incluse pour sécuriser l'anchor avant submission." },
  { icon: Activity,   name: "DE Trap",            description: "Quantifier l'opt-in DE",           detail: "Quantifie l'impact de l'opt-in allemand sur les 27 marchés qui référencent l'Allemagne. Simulateur interactif du piège confidentiel DE." },
];

// ─── Small shared components ──────────────────────────────────────────────────

function SummaryCell({ label, value, valueClass = "", subtle = false }: {
  label: string; value: string | number; valueClass?: string; subtle?: boolean;
}) {
  return (
    <div className={`bg-bg p-4 ${subtle ? "opacity-70" : ""}`}>
      <p className="font-mono text-xs uppercase tracking-wider text-text-secondary mb-2">{label}</p>
      <p className={`font-mono font-medium text-text-primary tabular-nums ${valueClass || "text-2xl"}`}>
        {value}
      </p>
    </div>
  );
}

function ActionCard({ icon: Icon, title, description, onClick, accent = false }: {
  icon: LucideIcon; title: string; description: string; onClick: () => void; accent?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-left p-4 rounded-lg border transition-colors ${
        accent
          ? "border-gold-500/40 bg-gold-500/5 hover:bg-gold-500/10"
          : "border-border bg-panel hover:bg-panel-elev"
      }`}
    >
      <Icon className={`w-5 h-5 mb-3 ${accent ? "text-gold-500" : "text-text-secondary"}`} />
      <p className="font-sans text-sm font-semibold text-text-primary mb-1">{title}</p>
      <p className="text-xs text-text-secondary">{description}</p>
    </button>
  );
}

// ─── Mode-specific sections ───────────────────────────────────────────────────

function DidacticHero() {
  return (
    <div className="text-center mb-12">
      <p className="font-mono text-xs text-gold-500 tracking-widest uppercase mb-3">Bienvenue</p>
      <h1 className="font-sans text-4xl md:text-5xl font-semibold text-text-primary mb-4 tracking-tight">
        Naviguer MFN. Défendre la NPV.
      </h1>
      <p className="text-base text-text-secondary max-w-2xl mx-auto">
        Le premier outil dédié aux équipes pricing mid-cap pharma pour modéliser et défendre vos prix
        face aux régulations CMS Generous, Guard et Globe.
      </p>
    </div>
  );
}

function DashboardHero({ firstName, assetCount, lastActivityDate }: {
  firstName: string; assetCount: number; lastActivityDate: string | null;
}) {
  return (
    <div className="mb-10">
      <p className="font-mono text-xs text-gold-500 tracking-widest uppercase mb-2">Tableau de bord</p>
      <h1 className="font-sans text-3xl md:text-4xl font-semibold text-text-primary tracking-tight">
        Bonjour {firstName}
      </h1>
      <p className="text-base text-text-secondary mt-2">
        {assetCount} {assetCount === 1 ? "asset" : "assets"} dans votre portfolio.
        {lastActivityDate && ` Dernière activité ${formatRelativeTime(lastActivityDate)}.`}
      </p>
    </div>
  );
}

function PortfolioSummary({ assets }: { assets: Asset[] }) {
  const active = assets.filter(a => !a.archived_at && !a.is_sample).length;
  const sample = assets.filter(a => a.is_sample && !a.archived_at).length;
  const archived = assets.filter(a => a.archived_at !== null).length;
  const lastUpdated = assets
    .filter(a => !a.archived_at)
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0]?.updated_at ?? null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border rounded-lg overflow-hidden mb-10">
      <SummaryCell label="Assets actifs" value={active} />
      <SummaryCell label="Sample" value={sample} subtle />
      <SummaryCell label="Archivés" value={archived} subtle />
      <SummaryCell
        label="Dernière modif"
        value={lastUpdated ? formatRelativeTime(lastUpdated) : "—"}
        valueClass="text-base"
      />
    </div>
  );
}

function QuickActions({ assets, onImport }: { assets: Asset[]; onImport: () => void }) {
  const navigate = useNavigate();
  const { downloadTemplate, downloading } = useDownloadTemplate();
  const lastAsset = assets
    .filter(a => !a.archived_at && !a.is_sample)
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0] ?? null;

  return (
    <div className="mb-10">
      <h3 className="font-sans text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
        Actions rapides
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        <ActionCard icon={Plus} title="Nouvel asset" description="Créer un médicament from scratch" onClick={() => navigate("/assets")} />
        <ActionCard icon={Upload} title="Importer Excel" description="Asset complet depuis un .xlsx" onClick={onImport} />
        <ActionCard
          icon={Download}
          title={downloading ? "Téléchargement…" : "Modèle Excel"}
          description="Template .xlsx pré-rempli"
          onClick={() => downloadTemplate()}
        />
        {lastAsset && (
          <ActionCard
            icon={ChevronRight}
            title={`Reprendre ${lastAsset.name}`}
            description="Dernier asset modifié"
            onClick={() => navigate(`/assets/${lastAsset.id}`)}
            accent
          />
        )}
      </div>
    </div>
  );
}

function ActivityFeed({ items }: { items: ReturnType<typeof useRecentActivity>["data"] }) {
  const navigate = useNavigate();
  if (!items?.length) return null;
  const visible = items.slice(0, 8).map(item => ({ item, fmt: formatActivity(item) })).filter(x => x.fmt !== null);

  return (
    <div className="mb-10">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-sans text-sm font-semibold text-text-secondary uppercase tracking-wider">
          Activité récente
        </h3>
        <span className="font-mono text-xs text-text-tertiary">
          {items.length} {items.length === 1 ? "événement" : "événements"}
        </span>
      </div>
      <Panel padding="none">
        {visible.map(({ item, fmt }, idx) => (
          <div
            key={item.id}
            className={`flex items-start gap-3 p-3 ${idx > 0 ? "border-t border-border" : ""}`}
          >
            <div className="w-8 h-8 rounded bg-panel-elev grid place-items-center shrink-0">
              <ActivityIcon name={fmt!.icon} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-text-primary truncate">{fmt!.label}</p>
              {fmt!.detail && (
                <p className="font-mono text-xs text-text-secondary mt-0.5">{fmt!.detail}</p>
              )}
            </div>
            <p className="font-mono text-xs text-text-tertiary shrink-0 mt-0.5">
              {formatRelativeTime(item.created_at)}
            </p>
          </div>
        ))}
      </Panel>
      <button
        onClick={() => navigate("/settings/my-data")}
        className="mt-2 text-xs text-text-tertiary hover:text-text-secondary transition-colors"
      >
        Voir tout l'historique →
      </button>
    </div>
  );
}

function DidacticOnboarding({ onImport }: { onImport: () => void }) {
  const navigate = useNavigate();
  const { downloadTemplate, downloading } = useDownloadTemplate();
  return (
    <Panel padding="none" className="border-l-4 border-gold-500 mb-10 px-6 py-6">
      <p className="font-mono text-xs text-gold-500 tracking-wider uppercase mb-2">Pour commencer</p>
      <h2 className="font-sans text-2xl font-semibold text-text-primary mb-2">
        Créez votre premier asset
      </h2>
      <p className="text-text-secondary mb-4">
        Décrivez le médicament : prix US, indications, marchés visés. Comptez 5 minutes.
        Vous pourrez ensuite tester autant de scénarios MFN que vous voulez.
      </p>
      <div className="flex flex-wrap gap-3">
        <Button variant="primary" size="md" onClick={() => navigate("/assets")}>
          <Plus className="w-4 h-4" />
          Créer mon premier asset
        </Button>
        <Button variant="secondary" size="md" onClick={onImport}>
          <Upload className="w-4 h-4" />
          Importer depuis Excel
        </Button>
        <Button variant="ghost" size="md" loading={downloading} onClick={() => downloadTemplate()}>
          <Download className="w-4 h-4" />
          Télécharger le modèle Excel
        </Button>
      </div>
    </Panel>
  );
}

function ProblemsSection() {
  return (
    <div className="mb-10">
      <h2 className="font-sans text-xl font-semibold text-text-primary mb-2">Pourquoi cet outil existe</h2>
      <p className="text-text-secondary mb-6">Trois douleurs concrètes qu'Excel ne résout plus en 2026.</p>
      <div className="grid md:grid-cols-3 gap-4">
        {PROBLEMS.map(p => (
          <Panel key={p.title} padding="none" className="border-l-4 border-gold-500 px-4 py-4">
            <h3 className="font-sans text-sm font-semibold text-text-primary mb-2">{p.title}</h3>
            <p className="text-xs text-text-secondary leading-relaxed mb-3">{p.body}</p>
            <p className="font-mono text-[10px] text-gold-500 uppercase tracking-wider mb-1">Notre réponse</p>
            <p className="text-xs text-text-secondary leading-relaxed">{p.response}</p>
          </Panel>
        ))}
      </div>
    </div>
  );
}

function HowItWorksFlow() {
  return (
    <div className="mb-10">
      <h2 className="font-sans text-xl font-semibold text-text-primary mb-2">
        Comment ça marche, en 30 secondes
      </h2>
      <div className="grid md:grid-cols-3 gap-4 mt-4">
        {[
          { step: "ASSET",      desc: "Le médicament (prix, indication, marchés, G2N)", sub: "1 par asset" },
          { step: "SCÉNARIO",   desc: "Une configuration régulatoire + stratégique testée sur cet asset", sub: "N par asset" },
          { step: "SIMULATION", desc: "Le résultat calculé (NPV, Method I/II, cascade, audit JSON)", sub: "N par scénario" },
        ].map(item => (
          <Panel key={item.step} elevated>
            <p className="text-xs text-gold-500 tracking-widest font-semibold mb-2">{item.step}</p>
            <p className="text-sm text-text-primary leading-relaxed mb-2">{item.desc}</p>
            <p className="text-xs text-text-tertiary">{item.sub}</p>
          </Panel>
        ))}
      </div>
      <p className="text-sm text-text-secondary text-center italic mt-6 max-w-2xl mx-auto">
        Vous configurez un asset une seule fois. Vous testez autant de scénarios que vous voulez.
        Chaque scénario produit une simulation traçable.
      </p>
    </div>
  );
}

function ModulesGuide({ variant, hasAssets }: { variant: "full" | "compact"; hasAssets: boolean }) {
  const [expanded, setExpanded] = useState(variant === "full");
  const [activeModule, setActiveModule] = useState<Module | null>(null);
  const navigate = useNavigate();

  return (
    <div className="mb-10">
      <button
        onClick={() => setExpanded(v => !v)}
        className="flex items-center gap-2 w-full text-left mb-4"
      >
        <h3 className="font-sans text-sm font-semibold text-text-secondary uppercase tracking-wider flex-1">
          Les 9 modules de Pricing Star
        </h3>
        <ChevronDown
          className={`w-4 h-4 text-text-tertiary transition-transform ${expanded ? "rotate-180" : ""}`}
        />
      </button>
      {expanded && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {MODULES.map(mod => (
            <button
              key={mod.name}
              onClick={() => setActiveModule(mod)}
              className="text-left p-3 rounded-lg border border-border bg-panel hover:bg-panel-elev transition-colors"
            >
              <mod.icon className="w-4 h-4 text-text-tertiary mb-2" />
              <p className="text-sm font-medium text-text-primary mb-1">{mod.name}</p>
              <p className="text-xs text-text-secondary">{mod.description}</p>
            </button>
          ))}
        </div>
      )}
      {activeModule && (
        <Modal
          open
          onClose={() => setActiveModule(null)}
          title={activeModule.name}
          footer={
            <Button
              variant="primary"
              size="sm"
              onClick={() => { navigate(hasAssets ? "/assets" : "/assets"); setActiveModule(null); }}
            >
              Aller sur mes assets
            </Button>
          }
        >
          <p className="text-sm text-text-secondary leading-relaxed">{activeModule.detail}</p>
        </Modal>
      )}
    </div>
  );
}

// ─── Loading skeleton ─────────────────────────────────────────────────────────

function HomePageSkeleton() {
  return (
    <AppShell variant="minimal">
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="mb-12 flex flex-col items-center gap-3">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-10 w-80" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border rounded-lg overflow-hidden mb-10">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-20" />)}
        </div>
        <SkeletonBlock lines={4} />
      </div>
    </AppShell>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function HomePage() {
  const { data: assetsPage, isLoading: assetsLoading, isError: assetsError } = useAssetList();
  const { data: activity, isLoading: activityLoading } = useRecentActivity(20);
  const { data: me } = useUserMe();
  const { mutateAsync: dismissAsync } = useDismissWelcome();
  console.log('[HomePage] render — assetsLoading:', assetsLoading, 'activityLoading:', activityLoading, 'has_seen_welcome:', me?.has_seen_welcome);
  const [importOpen, setImportOpen] = useState(false);
  const didDismiss = useRef(false);

  // Dismiss first-visit flag once, non-blocking
  useEffect(() => {
    if (me?.has_seen_welcome === false && !didDismiss.current) {
      didDismiss.current = true;
      dismissAsync().catch(() => {});
    }
  }, [me?.has_seen_welcome]); // eslint-disable-line react-hooks/exhaustive-deps

  const isLoading = assetsLoading || activityLoading;
  if (isLoading) return <HomePageSkeleton />;

  const assets = assetsPage?.items ?? [];
  const dashboardMode = !assetsError && (assets.length > 0 || (activity?.length ?? 0) > 0);
  const firstName = me?.name?.split(" ")[0] ?? "à vous";
  const lastActivityDate = activity?.[0]?.created_at ?? null;

  return (
    <AppShell variant="minimal">
      <div className="max-w-6xl mx-auto px-6 py-10">

        {dashboardMode ? (
          <DashboardHero firstName={firstName} assetCount={assets.filter(a => !a.archived_at && !a.is_sample).length} lastActivityDate={lastActivityDate} />
        ) : (
          <DidacticHero />
        )}

        {dashboardMode ? (
          <>
            <PortfolioSummary assets={assets} />
            <QuickActions assets={assets} onImport={() => setImportOpen(true)} />
            <ActivityFeed items={activity} />
            <ModulesGuide variant="compact" hasAssets={assets.length > 0} />
          </>
        ) : (
          <>
            <DidacticOnboarding onImport={() => setImportOpen(true)} />
            <ProblemsSection />
            <HowItWorksFlow />
            <ModulesGuide variant="full" hasAssets={false} />
          </>
        )}

      </div>

      <ImportWizard
        open={importOpen}
        onClose={() => setImportOpen(false)}
        mode="create_new"
      />
    </AppShell>
  );
}
