/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand — legacy dark accents kept for backward compat
        navy: {
          900: '#0F1B2D',
          700: '#1F3251',
          500: '#3D5680',
          300: '#7A8FAB',
          100: '#D9E1ED',
        },
        gold: {
          900: '#7E5C07',      // deep gold for text on light bg
          500: '#B8860B',      // primary accent
          300: '#D4A574',
          100: '#FFF8E1',
        },
        // === SEMANTIC SURFACES (LIGHT WARM BEIGE) ===
        bg: '#EFE9DD',           // warm beige canvas
        panel: '#F8F3E6',        // cards, lighter cream
        'panel-elev': '#FDF9ED', // hover state
        border: '#D5CCB6',       // strong border
        'border-soft': '#E3DAC4',// subtle divider
        // === TEXT (LIGHT) ===
        'text-primary': '#161310',     // near black
        'text-secondary': '#565045',   // warm gray
        'text-tertiary': '#8C8473',    // muted
        // === FUNCTIONAL (adapted for light bg) ===
        success: '#2E7D32',
        'success-light': '#E8F5E9',
        danger: '#B91C1C',
        'danger-light': '#FEF2F2',
        warning: '#B45309',
        'warning-light': '#FEF3C7',
        info: '#1E40AF',
        'info-light': '#EFF6FF',
        // === GRID / TEXTURE ===
        'grid-line': 'rgba(86, 80, 69, 0.06)',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"SF Mono"', '"Monaco"', '"Inconsolata"', 'monospace'],
        serif: ['"Fraunces"', 'Georgia', 'serif'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.2' }],
        sm: ['0.875rem', { lineHeight: '1.4' }],
        base: ['1rem', { lineHeight: '1.6' }],
        lg: ['1.125rem', { lineHeight: '1.4' }],
        xl: ['1.25rem', { lineHeight: '1.4' }],
        '2xl': ['1.5rem', { lineHeight: '1.2' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
        '4xl': ['2.25rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        '5xl': ['3rem', { lineHeight: '1.05', letterSpacing: '-0.025em' }],
        // Numeric display — always pair with font-mono
        'display-num-sm': ['1.5rem', { lineHeight: '1', letterSpacing: '-0.015em' }],
        'display-num-md': ['1.875rem', { lineHeight: '1', letterSpacing: '-0.02em' }],
        'display-num-lg': ['2.5rem', { lineHeight: '1', letterSpacing: '-0.025em' }],
      },
      letterSpacing: {
        tighter: '-0.03em',
        tight: '-0.015em',
        normal: '0',
        wide: '0.04em',
        wider: '0.08em',
        widest: '0.12em',
        editorial: '0.18em',
        'mono-label': '0.14em',
      },
      borderRadius: {
        none: '0',
        sm: '2px',
        DEFAULT: '4px',
        md: '6px',
        lg: '8px',
        full: '9999px',
      },
      boxShadow: {
        sm: '0 1px 3px rgba(22, 19, 16, 0.08)',
        DEFAULT: '0 4px 8px rgba(22, 19, 16, 0.10)',
        lg: '0 10px 20px rgba(22, 19, 16, 0.12)',
        inset: 'inset 0 1px 2px rgba(22, 19, 16, 0.08)',
      },
      spacing: {
        // 8px grid
        '0.5': '4px',
        '1': '8px',
        '1.5': '12px',
        '2': '16px',
        '2.5': '20px',
        '3': '24px',
        '4': '32px',
        '5': '40px',
        '6': '48px',
        '8': '64px',
        '10': '80px',
        '12': '96px',
      },
      backgroundImage: {
        'grid': [
          'linear-gradient(rgba(86, 80, 69, 0.06) 1px, transparent 1px)',
          'linear-gradient(90deg, rgba(86, 80, 69, 0.06) 1px, transparent 1px)',
        ].join(', '),
      },
      backgroundSize: {
        'grid': '48px 48px',
      },
      transitionDuration: {
        fast: '120ms',
        base: '180ms',
        DEFAULT: '250ms',
        slow: '280ms',
      },
      transitionTimingFunction: {
        'out-soft': 'cubic-bezier(0.32, 0.72, 0, 1)',
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.97)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        'slide-in-right': {
          from: { transform: 'translateX(100%)' },
          to: { transform: 'translateX(0)' },
        },
        'slide-in-down': {
          from: { opacity: '0', transform: 'translateY(-6px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 180ms ease-out',
        'scale-in': 'scale-in 200ms cubic-bezier(0.32, 0.72, 0, 1)',
        'slide-in-right': 'slide-in-right 260ms cubic-bezier(0.32, 0.72, 0, 1)',
        'slide-in-down': 'slide-in-down 120ms ease-out',
      },
    },
  },
  plugins: [],
};
