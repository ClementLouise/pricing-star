import { useState } from "react";
import { ChevronDown, ChevronUp, Info } from "lucide-react";

interface TabExplainerProps {
  tabId: string;
  whatItDoes: string;
  whenToUse: string;
  watchOutFor?: string;
}

function useExplainerState(tabId: string): [boolean, () => void] {
  const storageKey = `pricingstar.explainer.${tabId}`;
  const discoveredKey = "pricingstar.explainer.discovered";

  const [expanded, setExpanded] = useState<boolean>(() => {
    const stored = localStorage.getItem(storageKey);
    if (stored !== null) return stored === "expanded";
    // Auto-expand until the user has first interacted with any explainer
    return localStorage.getItem(discoveredKey) !== "true";
  });

  function toggle() {
    setExpanded((prev) => {
      const next = !prev;
      localStorage.setItem(storageKey, next ? "expanded" : "collapsed");
      if (localStorage.getItem(discoveredKey) !== "true") {
        localStorage.setItem(discoveredKey, "true");
      }
      return next;
    });
  }

  return [expanded, toggle];
}

export function TabExplainer({ tabId, whatItDoes, whenToUse, watchOutFor }: TabExplainerProps) {
  const [expanded, toggle] = useExplainerState(tabId);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggle();
    }
  }

  return (
    <div className="border border-border rounded-md overflow-hidden bg-panel">
      <div
        role="button"
        aria-expanded={expanded}
        tabIndex={0}
        onClick={toggle}
        onKeyDown={handleKeyDown}
        className="flex items-center justify-between px-4 h-9 cursor-pointer hover:bg-panel-elev transition-colors duration-fast focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-gold-500"
      >
        <div className="flex items-center gap-2">
          <Info size={14} className="text-gold-500 shrink-0" />
          <span className="text-xs text-text-secondary">À quoi sert cet onglet ?</span>
        </div>
        <span className="flex items-center gap-1 text-xs text-gold-500 hover:text-gold-300">
          {expanded ? "Masquer" : "Voir l'explication"}
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </span>
      </div>

      <div
        className={[
          "overflow-hidden transition-[max-height] duration-[250ms] ease-out motion-reduce:transition-none",
          expanded ? "max-h-[300px]" : "max-h-0",
        ].join(" ")}
      >
        <div className="flex border-t border-border">
          <div className="flex-1 px-4 py-3 border-r border-border">
            <p className="text-xs text-gold-500 tracking-wider uppercase mb-1">À QUOI ÇA SERT</p>
            <p className="text-sm text-text-primary leading-relaxed">{whatItDoes}</p>
          </div>
          <div className={`flex-1 px-4 py-3${watchOutFor ? " border-r border-border" : ""}`}>
            <p className="text-xs text-gold-500 tracking-wider uppercase mb-1">QUAND L'UTILISER</p>
            <p className="text-sm text-text-primary leading-relaxed">{whenToUse}</p>
          </div>
          {watchOutFor && (
            <div className="flex-1 px-4 py-3">
              <p className="text-xs text-gold-500 tracking-wider uppercase mb-1">ATTENTION</p>
              <p className="text-sm text-text-primary leading-relaxed">{watchOutFor}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export const TAB_EXPLAINER_CONTENT: Record<
  string,
  Pick<TabExplainerProps, "whatItDoes" | "whenToUse" | "watchOutFor">
> = {
  asset: {
    whatItDoes:
      "C'est le point de départ. Vous y décrivez votre médicament (prix US, G2N, années clés) et vous configurez les prix et volumes pour les marchés où il sera lancé.",
    whenToUse: "Toujours en premier. Tous les autres onglets dépendent des données saisies ici.",
    watchOutFor:
      "Sans au moins 5 pays OECD-19 lancés, les onglets MFN et Cascade ne pourront rien calculer.",
  },
  regulations: {
    whatItDoes:
      "Vous activez ou désactivez les trois régulations CMS — Generous (Medicaid), Guard (Part D), Globe (Part B) — et choisissez l'année de phase-in pour chacune. C'est ce qui définit le scénario que vous testez.",
    whenToUse:
      "Après avoir saisi les prix par pays. Créez plusieurs scénarios pour comparer (ex : « Pre-MFN » vs « Full MFN 2029 »).",
    watchOutFor:
      "Soumettre Method II est rarement avantageux : le benchmark CMS est max(Method I, Method II), donc submitter pousse mécaniquement vers le haut.",
  },
  cascade: {
    whatItDoes:
      "Vous visualisez comment les prix se propagent sur 43 marchés. Quand un pays référence l'Allemagne et que le prix allemand bouge, ça cascade — parfois sur 27 marchés simultanément. Cet onglet montre la propagation itération par itération jusqu'à convergence.",
    whenToUse:
      "Après avoir activé les régulations. Permet de comprendre l'effet domino avant d'arriver sur la NPV finale.",
    watchOutFor:
      "Si « Cascade did not converge », augmentez max iterations à 10. Au-delà de 15, c'est probablement une règle IRP circulaire à signaler au support.",
  },
  rebates: {
    whatItDoes:
      "Vous saisissez les rebates confidentiels par pays sous forme de Gross-to-Net ratio. Soit une valeur statique, soit une trajectoire année par année — utile pour modéliser AMNOG en Allemagne, le LOE cliff, ou les renégociations multi-annuelles.",
    whenToUse:
      "Quand vos hypothèses de rebate diffèrent des défauts pays. Indispensable si vous voulez un Method II précis.",
    watchOutFor:
      "G2N hors plage [launch_year, loe_year+5] est ignoré : le système retombe sur la valeur statique. Vérifiez les bornes de votre time-series.",
  },
  levers: {
    whatItDoes:
      "Vous appliquez des actions de mitigation : retirer un pays, fixer un plancher de prix pour protéger un anchor, repousser un lancement, ou activer l'opt-in confidentiel allemand. Chaque levier affiche son impact NPV individuel et combiné.",
    whenToUse:
      "Une fois la NPV de base calculée, pour explorer comment la défendre. À utiliser en boucle avec l'onglet NPV Optimizer.",
    watchOutFor:
      "Combiner withdraw + price floor sur le même pays crée un conflit. Le système l'affiche, mais c'est à vous de trancher.",
  },
  optimizer: {
    whatItDoes:
      "Le moteur génère 3 à 7 recommandations stratégiques classées par impact NPV (ex : « ne pas opt-in en Allemagne », « set price floor en CH »). C'est aussi d'ici que vous exportez l'audit JSON SOX-defensible pour votre CFO et le board.",
    whenToUse:
      "Avant chaque décision majeure de pricing. Et systématiquement avant un comité ou une présentation au board.",
    watchOutFor:
      "Les recommandations dépendent du dernier scénario simulé. Cliquez « Run Optimization » à chaque modification importante.",
  },
  compare: {
    whatItDoes:
      "Vous mettez 2 à 5 scénarios côte à côte avec deltas color-codés sur la NPV, le peak revenue, le Method I, le rebate par dose et le P&L annuel. Export PDF formaté pour board ou XLSX brut pour l'équipe finance.",
    whenToUse:
      "Avant tout CFO QBR. Le format type : « Pre-MFN baseline » vs « Full MFN » vs « Mitigated » pour montrer la valeur de votre stratégie.",
    watchOutFor:
      "Compare bloque les comparaisons inter-asset : tous les scénarios doivent appartenir au même asset. C'est volontaire (apples-to-apples).",
  },
  anchor: {
    whatItDoes:
      "Identifie automatiquement le pays qui ancre Method I (typiquement CH/IE/NO sous la convention CMS multiply), même quand ce n'est pas intuitif. Génère une recommandation ringfencing selon la fragilité de l'anchor.",
    whenToUse:
      "Pour comprendre pourquoi votre Method I tombe à un certain niveau, et où concentrer votre effort de price discipline.",
    watchOutFor:
      "Un anchor « fragile » (gap < 5% au #2) peut shifter à la moindre pression sur l'anchor. Surveillez les négociations dans ces pays.",
  },
  "de-cascade": {
    whatItDoes:
      "Quantifie l'impact du Medical Research Act allemand (mars 2026) : un opt-in confidentiel offre ~9pp de prix disclosed plus bas, mais cascade sur 27 marchés référençant l'Allemagne. Le simulateur chiffre l'impact NPV en temps réel.",
    whenToUse: "Si l'Allemagne est lancée et que vous envisagez l'opt-in. À regarder AVANT de prendre la décision.",
    watchOutFor:
      "Pour la plupart des assets mid-cap avec footprint ex-US, l'opt-in coûte plus qu'il ne rapporte (~−$2-5B NPV typique). C'est le piège classique.",
  },
};
