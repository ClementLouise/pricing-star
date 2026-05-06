/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand — per PRD §06
        navy: {
          900: '#0F1B2D',
          700: '#1F3251',
          500: '#3D5680',
          300: '#7A8FAB',
          100: '#D9E1ED',
        },
        gold: {
          900: '#8B5E0B',
          500: '#B8860B',
          300: '#D4A574',
          100: '#FFF8E1',
        },
        // Semantic surface
        bg: '#0D1117',
        panel: '#161B22',
        'panel-elev': '#1C2127',
        border: '#21262D',
        // Text
        'text-primary': '#E6EDF3',
        'text-secondary': '#8B949E',
        'text-tertiary': '#6E7681',
        // Functional
        success: '#2E7D32',
        'success-light': '#E8F5E9',
        danger: '#C00000',
        'danger-light': '#FFEBEE',
        warning: '#F59E0B',
        'warning-light': '#FFF8E1',
        info: '#1976D2',
        'info-light': '#E3F2FD',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mono: ['"SF Mono"', '"Monaco"', '"Inconsolata"', '"Fira Code"', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1.2' }],
        sm: ['0.875rem', { lineHeight: '1.4' }],
        base: ['1rem', { lineHeight: '1.6' }],
        lg: ['1.125rem', { lineHeight: '1.4' }],
        xl: ['1.25rem', { lineHeight: '1.4' }],
        '2xl': ['1.5rem', { lineHeight: '1.2' }],
        '3xl': ['1.875rem', { lineHeight: '1.2' }],
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
        sm: '0 1px 2px rgba(0,0,0,0.5)',
        DEFAULT: '0 4px 6px rgba(0,0,0,0.5)',
        lg: '0 10px 15px rgba(0,0,0,0.5)',
        inset: 'inset 0 1px 2px rgba(0,0,0,0.5)',
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
      transitionDuration: {
        fast: '150ms',
        DEFAULT: '250ms',
        slow: '400ms',
      },
    },
  },
  plugins: [],
};
