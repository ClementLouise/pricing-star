/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#EFE9DD',
        panel: '#F8F3E6',
        'panel-elev': '#FDF9ED',
        border: '#D5CCB6',
        'border-soft': '#E3DAC4',
        'text-primary': '#161310',
        'text-secondary': '#565045',
        'text-tertiary': '#8C8473',
        gold: {
          900: '#7E5C07',
          500: '#B8860B',
          300: '#D4A574',
          100: '#FFF8E1',
        },
        ink: '#161310',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"SF Mono"', 'monospace'],
        serif: ['"Fraunces"', 'Georgia', 'serif'],
      },
      fontSize: {
        'display-xl': ['96px', { lineHeight: '1', letterSpacing: '-0.03em' }],
        'display-lg': ['72px', { lineHeight: '1.05', letterSpacing: '-0.025em' }],
        'display-md': ['52px', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display-sm': ['40px', { lineHeight: '1.15', letterSpacing: '-0.018em' }],
      },
      letterSpacing: {
        'mono-wide': '0.18em',
        'mono-label': '0.14em',
      },
      maxWidth: {
        'copy': '720px',
        'copy-wide': '920px',
        'container': '1200px',
      },
      spacing: {
        'section': '160px',
        'section-sm': '120px',
        'section-mobile': '80px',
      },
    },
  },
};
