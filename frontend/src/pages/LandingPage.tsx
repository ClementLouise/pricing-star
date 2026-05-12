import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { Navigate } from "react-router-dom";

// ─── Copy ────────────────────────────────────────────────────────────────────

const copy = {
  hero: {
    eyebrow: "— Global Pricing Intelligence",
    titleLine1: "Where pharma pricing",
    titleLine2: "meets the world.",
    subtext:
      "Pricing Star is the modeling layer for global launch sequencing — built for Heads of Pricing & Market Access who refuse to let regulatory cascades dictate their NPV.",
    caption: "▸ MFN. IRP. Reference pricing. Across 47 markets. In real time.",
  },
  boardroom: {
    eyebrow: "— Chapter One",
    title: ["It is Tuesday morning.", "The Pricing Committee meets in 4 hours."],
    body: [
      "Your asset gets FDA approval in Q4. The launch sequencing memo is due Thursday. You have 47 countries to model, 12 reference pricing cascades to anticipate, and the latest MFN executive order looming over the US benchmark.",
      "Your team is running scenarios in Excel — three tabs deep, formulas inherited from a consultant who left in 2023.",
      "This is the moment Pricing Star was built for.",
    ],
  },
  capabilities: {
    eyebrow: "— What it does",
    title: "Three capabilities.",
    titleItalic: "One source of truth.",
    cards: [
      {
        num: "01",
        title: "IRP Cascade Modeling",
        body: "Model how a price decision in one market cascades through 200+ reference pricing dependencies across the world. Before you commit, see the second-order effects three steps ahead.",
        tag: "47 markets",
      },
      {
        num: "02",
        title: "MFN Simulation",
        body: "Quantify the impact of US Most-Favored-Nation pricing scenarios on your global revenue. Stress-test executive orders, congressional drafts, and ex-US reference baskets in minutes.",
        tag: "US · Europe · Asia",
      },
      {
        num: "03",
        title: "Launch Sequencing",
        body: "Determine the optimal order in which to launch — and the prices to hold — to maximize NPV across the global rollout. Move beyond spreadsheet heuristics.",
        tag: "NPV-optimized",
      },
    ],
  },
  engine: {
    eyebrow: "— Under the hood",
    title: ["A deterministic", "cascade engine."],
    body: "Pricing Star is built on a calculation engine that resolves 200+ regulatory interdependencies in under 800ms. Every scenario is deterministic, every result reproducible, every cascade auditable down to the source country.",
    stats: [
      { value: "200+", label: "IRP rules" },
      { value: "47", label: "markets in roadmap" },
      { value: "< 800ms", label: "full cascade resolution" },
    ],
  },
  persona: {
    eyebrow: "— Who it's built for",
    quote:
      "Built for Heads of Pricing & Market Access at mid-cap pharma companies launching globally — where every percentage point of price differential moves NPV by nine figures.",
    attribution: "— Pricing Star Design Principle, 2026",
  },
  contact: {
    eyebrow: "— Get in touch",
    title: "Currently working with select teams,",
    titleItalic: "ahead of public launch.",
    body: "We work directly with a small number of pricing teams to refine the product against real launch scenarios. If your pipeline includes a global launch in the next 18 months, we'd be glad to talk.",
    email: "contact@pricingstar.com",
  },
  footer: {
    text: "Pricing Star · 2026 · contact@pricingstar.com",
  },
};

// ─── Scroll-reveal hook ───────────────────────────────────────────────────────

function useScrollReveal() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -60px 0px" }
    );
    document.querySelectorAll(".reveal-item").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);
}

// ─── Header scroll effect ─────────────────────────────────────────────────────

function useHeaderScroll() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return scrolled;
}

// ─── Eyebrow ──────────────────────────────────────────────────────────────────

function Eyebrow({ text, centered }: { text: string; centered?: boolean }) {
  return (
    <p
      className={`font-mono text-[11px] uppercase tracking-mono-label text-text-tertiary mb-6 ${
        centered ? "text-center" : ""
      }`}
    >
      {text}
    </p>
  );
}

// ─── LandingPage ─────────────────────────────────────────────────────────────

export default function LandingPage() {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0();
  useScrollReveal();
  const headerScrolled = useHeaderScroll();

  if (!isLoading && isAuthenticated) return <Navigate to="/home" replace />;

  return (
    <div className="min-h-screen bg-bg font-sans text-text-primary">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 border-b transition-all duration-300 ${
          headerScrolled
            ? "bg-bg/92 backdrop-blur-md border-border-soft"
            : "bg-transparent border-transparent"
        }`}
      >
        <div className="max-w-[1200px] mx-auto px-8 h-14 flex items-center justify-between">
          <span className="font-mono text-[13px] uppercase tracking-[0.1em] text-text-primary font-medium">
            PRICING <span className="text-gold-500">★</span> STAR
          </span>
          <button
            onClick={() => loginWithRedirect()}
            className="font-mono text-[11px] uppercase tracking-mono-label text-text-secondary hover:text-text-primary transition-colors duration-200 cursor-pointer"
          >
            Log in →
          </button>
        </div>
      </header>

      {/* ── Hero ───────────────────────────────────────────────────────────── */}
      <section className="min-h-screen flex items-center justify-center pt-14">
        <div className="max-w-[1200px] mx-auto px-8 py-32">
          <div className="max-w-[920px]">
            <div className="hero-reveal">
              <Eyebrow text={copy.hero.eyebrow} />
            </div>
            <h1 className="font-serif font-light text-[64px] md:text-[80px] text-text-primary mb-8 leading-[1.05] tracking-[-0.025em] hero-reveal hero-d1">
              {copy.hero.titleLine1}
              <br />
              <em>{copy.hero.titleLine2}</em>
            </h1>
            <p className="text-xl md:text-[21px] text-text-secondary leading-relaxed max-w-[620px] mb-10 hero-reveal hero-d2">
              {copy.hero.subtext}
            </p>
            <p className="font-mono text-[11px] text-text-tertiary tracking-mono-label hero-reveal hero-d3">
              {copy.hero.caption}
            </p>
          </div>
        </div>
      </section>

      {/* ── Boardroom Scene ────────────────────────────────────────────────── */}
      <section className="bg-panel py-[120px] md:py-[160px]">
        <div className="max-w-[1200px] mx-auto px-8">
          <div className="max-w-[720px] reveal-item">
            <Eyebrow text={copy.boardroom.eyebrow} />
            <h2 className="font-serif font-light italic text-[40px] md:text-[52px] text-text-primary mb-12 leading-tight tracking-[-0.02em]">
              {copy.boardroom.title[0]}
              <br />
              {copy.boardroom.title[1]}
            </h2>
            <div className="space-y-6">
              {copy.boardroom.body.map((para, i) => (
                <p
                  key={i}
                  className={`font-serif text-[19px] md:text-[21px] leading-relaxed reveal-item reveal-delay-${Math.min(i + 1, 4)} ${
                    i === copy.boardroom.body.length - 1
                      ? "text-text-primary font-medium"
                      : "text-text-secondary"
                  }`}
                >
                  {para}
                </p>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Capabilities ───────────────────────────────────────────────────── */}
      <section className="bg-bg py-[120px] md:py-[160px]">
        <div className="max-w-[1200px] mx-auto px-8">
          <div className="mb-16 reveal-item">
            <Eyebrow text={copy.capabilities.eyebrow} />
            <h2 className="font-serif font-light text-[40px] md:text-[52px] text-text-primary leading-tight tracking-[-0.02em]">
              {copy.capabilities.title}
              <br />
              <em>{copy.capabilities.titleItalic}</em>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {copy.capabilities.cards.map((card, i) => (
              <div
                key={i}
                className={`bg-panel border border-border-soft rounded-lg p-9 flex flex-col hover:-translate-y-0.5 hover:shadow-lg transition-all duration-300 reveal-item reveal-delay-${i + 1}`}
              >
                <span className="font-mono text-[13px] text-gold-500 font-medium mb-6">
                  {card.num}
                </span>
                <h3 className="font-serif font-light italic text-[26px] md:text-[28px] text-text-primary leading-tight mb-5">
                  {card.title}
                </h3>
                <p className="text-[15px] text-text-secondary leading-relaxed flex-1 mb-8">
                  {card.body}
                </p>
                <span className="font-mono text-[10px] uppercase tracking-mono-label text-text-tertiary">
                  {card.tag}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Engine ─────────────────────────────────────────────────────────── */}
      <section className="bg-panel py-[120px] md:py-[160px]">
        <div className="max-w-[1200px] mx-auto px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-16 items-start">
            <div className="reveal-item">
              <Eyebrow text={copy.engine.eyebrow} />
              <h2 className="font-serif font-light italic text-[32px] md:text-[36px] text-text-primary leading-tight">
                {copy.engine.title[0]}
                <br />
                {copy.engine.title[1]}
              </h2>
            </div>
            <div className="md:col-span-2 reveal-item reveal-delay-1">
              <p className="text-[16px] text-text-secondary leading-[1.55] mb-12 max-w-[720px]">
                {copy.engine.body}
              </p>
              <div className="grid grid-cols-3 gap-8 border-t border-border-soft pt-8">
                {copy.engine.stats.map((stat, i) => (
                  <div key={i} className={`reveal-item reveal-delay-${i + 1}`}>
                    <p className="font-mono text-[28px] font-medium text-text-primary tabular-nums mb-1">
                      {stat.value}
                    </p>
                    <p className="font-mono text-[10px] uppercase tracking-mono-label text-text-tertiary">
                      {stat.label}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Persona ────────────────────────────────────────────────────────── */}
      <section className="bg-bg py-[120px] md:py-[160px]">
        <div className="max-w-[1200px] mx-auto px-8 flex flex-col items-center text-center">
          <div className="reveal-item">
            <Eyebrow text={copy.persona.eyebrow} centered />
          </div>
          <blockquote className="max-w-[800px] reveal-item reveal-delay-1">
            <p className="font-serif font-light italic text-[32px] md:text-[36px] text-text-primary leading-[1.3]">
              "{copy.persona.quote}"
            </p>
            <footer className="mt-8">
              <cite className="font-mono text-[11px] uppercase tracking-mono-label text-text-tertiary not-italic">
                {copy.persona.attribution}
              </cite>
            </footer>
          </blockquote>
        </div>
      </section>

      {/* ── Contact ────────────────────────────────────────────────────────── */}
      <section id="contact" className="bg-panel py-[120px] md:py-[160px]">
        <div className="max-w-[1200px] mx-auto px-8">
          <div className="max-w-[720px] mx-auto reveal-item">
            <Eyebrow text={copy.contact.eyebrow} />
            <h2 className="font-serif font-light text-[40px] md:text-[44px] text-text-primary leading-tight mb-10">
              {copy.contact.title}
              <br />
              <em>{copy.contact.titleItalic}</em>
            </h2>
            <p className="text-[17px] text-text-secondary leading-relaxed max-w-[580px] mb-12 reveal-item reveal-delay-1">
              {copy.contact.body}
            </p>
            <a
              href={`mailto:${copy.contact.email}`}
              className="font-mono text-[15px] text-text-secondary hover:text-text-primary transition-colors duration-200 border-b border-border-soft hover:border-text-primary pb-0.5 reveal-item reveal-delay-2"
            >
              {copy.contact.email} &nbsp;→
            </a>
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer className="bg-bg border-t border-border-soft py-8">
        <div className="max-w-[1200px] mx-auto px-8">
          <p className="font-mono text-[11px] text-text-tertiary">
            {copy.footer.text}
          </p>
        </div>
      </footer>

    </div>
  );
}

// ─── Hero CSS animations ──────────────────────────────────────────────────────
// Injected once via a style tag — scoped to .hero-reveal to avoid
// conflicting with the IntersectionObserver-based .reveal-item system.
const heroStyle = `
  .hero-reveal {
    opacity: 0;
    transform: translateY(20px);
    animation: hero-up 0.7s ease-out forwards;
  }
  .hero-d1 { animation-delay: 0.15s; }
  .hero-d2 { animation-delay: 0.30s; }
  .hero-d3 { animation-delay: 0.45s; }
  @keyframes hero-up {
    to { opacity: 1; transform: translateY(0); }
  }
  @media (prefers-reduced-motion: reduce) {
    .hero-reveal { animation: none; opacity: 1; transform: none; }
  }
`;

// Append style once
if (typeof document !== "undefined" && !document.getElementById("hero-style")) {
  const tag = document.createElement("style");
  tag.id = "hero-style";
  tag.textContent = heroStyle;
  document.head.appendChild(tag);
}
