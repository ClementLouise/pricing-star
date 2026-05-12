# Pricing Star — Marketing Landing

Site marketing statique Astro pour Pricing Star.

## Stack

- **Framework** : Astro (static output)
- **CSS** : Tailwind CSS avec les design tokens Direction C
- **Fonts** : IBM Plex Sans, IBM Plex Mono, Fraunces (Google Fonts)

## Dev

```bash
cd marketing
npm install
npm run dev       # → http://localhost:4321
```

## Build

```bash
npm run build     # → dist/
npm run preview   # preview du build
```

## Structure

```
src/
├── layouts/Base.astro     # HTML shell, meta, scripts globaux
├── components/            # Une section = un composant
│   ├── Header.astro
│   ├── Hero.astro
│   ├── BoardroomScene.astro
│   ├── Capabilities.astro
│   ├── EngineSection.astro
│   ├── PersonaSection.astro
│   ├── ContactSection.astro
│   ├── Footer.astro
│   └── Eyebrow.astro      # Composant partagé
├── pages/index.astro      # Entry point
├── styles/global.css      # Body bg grid + animations
└── content/copy.ts        # ⚠️ Toutes les copies ici — relire avant go-live
```

## Avant go-live

1. Relire `src/content/copy.ts` — valider les chiffres (47 markets, 200+ IRP rules)
2. Créer l'email `contact@pricingstar.com`
3. Générer `public/og-image.png` (1200×630)
4. Configurer le DNS `pricingstar.com` → Railway

## Railway deploy

- **Root dir** : `marketing`
- **Build command** : `npm run build`
- **Start command** : `npx serve dist` (ou static hosting)
- **Port** : 3000 (pour `npx serve`)
