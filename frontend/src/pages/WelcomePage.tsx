import { useNavigate } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { useDismissWelcome } from "@/hooks/useUser";

const STEPS = [
  {
    n: 1,
    label: "Asset & Markets",
    desc: "Saisir le médicament et les prix par pays",
  },
  {
    n: 2,
    label: "Regulations",
    desc: "Activer Generous, Guard, Globe selon votre scénario",
  },
  {
    n: 3,
    label: "IRP Cascade",
    desc: "Voir les prix se propager sur 43 marchés",
  },
  {
    n: 4,
    label: "Rebates & G2N",
    desc: "Affiner les rebates confidentiels",
  },
  {
    n: 5,
    label: "NPV Optimizer",
    desc: "Lire la NPV, voir les recommandations, exporter l'audit",
  },
  {
    n: 6,
    label: "Compare",
    desc: "Mettre 2 à 5 scénarios côte à côte avant CFO QBR",
  },
];

const PROBLEMS = [
  {
    title: "Excel ne tient plus.",
    body: "Les régulations CMS empilent du calcul multi-méthodes sur 19 pays OECD ; un spreadsheet casse à la deuxième itération.",
    response:
      "Moteur de calcul testé contre les fixtures CMS, audit JSON exportable, SOX 404-ready.",
  },
  {
    title: "Le Method I anchor n'est pas évident.",
    body: "Sous la convention CMS multiply (PPP), c'est souvent CH/IE/NO et pas le pays au prix le plus bas. Excel ne le voit pas.",
    response:
      "Identification automatique de l'anchor avec PPP normalisation et recommandation ringfencing.",
  },
  {
    title: "La cascade IRP est dense.",
    body: "27 marchés référencent l'Allemagne. Un disclosed cut de 9pp coûte typiquement −$2-5B NPV ex-US.",
    response:
      "Simulateur cascade interactif : quantifie le piège de l'opt-in DE en temps réel.",
  },
];

export default function WelcomePage() {
  const navigate = useNavigate();
  const dismiss = useDismissWelcome();

  async function handleContinue() {
    try {
      await dismiss.mutateAsync();
    } catch {
      // Non-blocking — navigate regardless
    }
    navigate("/assets");
  }

  return (
    <AppShell variant="minimal">
      <div className="max-w-4xl mx-auto py-12 px-6">

        {/* Section 1 — Hero */}
        <div className="text-center mb-12">
          <p className="text-xs text-gold-500 tracking-widest font-semibold mb-3">
            BIENVENUE SUR PRICING STAR
          </p>
          <h1 className="text-4xl md:text-5xl font-semibold text-text-primary mb-4">
            Naviguer MFN. Défendre la NPV.
          </h1>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Le premier outil dédié aux équipes pricing mid-cap pharma pour modéliser et défendre
            vos prix face aux régulations Generous, Guard et Globe.
          </p>
        </div>

        {/* Section 2 — Pourquoi cet outil existe */}
        <div className="grid md:grid-cols-3 gap-4 mb-12">
          {PROBLEMS.map((p) => (
            <Panel key={p.title} className="border-l-4 border-gold-500">
              <h3 className="text-sm font-semibold text-text-primary mb-2">{p.title}</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-3">{p.body}</p>
              <p className="text-xs font-medium text-text-primary uppercase tracking-wider mb-1">
                Notre réponse
              </p>
              <p className="text-xs text-text-secondary leading-relaxed">{p.response}</p>
            </Panel>
          ))}
        </div>

        {/* Section 3 — Comment ça marche */}
        <div className="mb-12">
          <p className="text-xs text-gold-500 tracking-widest font-semibold mb-6 text-center">
            COMMENT ÇA MARCHE, EN 30 SECONDES
          </p>
          <div className="grid md:grid-cols-3 gap-4">
            {[
              {
                step: "ASSET",
                desc: "Le médicament (prix, indication, marchés, G2N)",
                sub: "1 par asset",
              },
              {
                step: "SCÉNARIO",
                desc: "Une configuration régulatoire + stratégique testée sur cet asset",
                sub: "N par asset",
              },
              {
                step: "SIMULATION",
                desc: "Le résultat calculé (NPV, Method I/II, cascade, audit JSON)",
                sub: "N par scénario",
              },
            ].map((item) => (
              <Panel key={item.step} elevated>
                <p className="text-xs text-gold-500 tracking-widest font-semibold mb-2">
                  {item.step}
                </p>
                <p className="text-sm text-text-primary leading-relaxed mb-2">{item.desc}</p>
                <p className="text-xs text-text-tertiary">{item.sub}</p>
              </Panel>
            ))}
          </div>
          <p className="text-sm text-text-primary font-medium text-center mt-6">
            "Vous configurez un asset une seule fois. Vous testez autant de scénarios que vous
            voulez. Chaque scénario produit une simulation traçable."
          </p>
        </div>

        {/* Section 4 — Parcours type */}
        <div className="mb-12">
          <p className="text-xs text-gold-500 tracking-widest font-semibold mb-4 text-center">
            LE PARCOURS TYPE POUR VOTRE PREMIÈRE SIMULATION
          </p>
          <div className="flex flex-col gap-2">
            {STEPS.map((s) => (
              <button
                key={s.n}
                onClick={handleContinue}
                className="flex items-center gap-4 px-4 py-3 rounded-md border border-border bg-panel hover:bg-panel-elev transition-colors text-left"
              >
                <span className="w-7 h-7 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-500 text-xs font-semibold flex items-center justify-center shrink-0">
                  {s.n}
                </span>
                <span>
                  <span className="text-sm font-medium text-text-primary">{s.label}</span>
                  <span className="text-xs text-text-secondary ml-2">— {s.desc}</span>
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Section 5 — CTA */}
        <div className="flex flex-col items-center gap-3 mt-12">
          <Button variant="primary" size="lg" loading={dismiss.isPending} onClick={handleContinue}>
            Continuer vers mes assets →
          </Button>
          <p className="text-xs text-text-tertiary italic">
            Vous pourrez revenir à cette page à tout moment via le menu utilisateur.
          </p>
        </div>

      </div>
    </AppShell>
  );
}
