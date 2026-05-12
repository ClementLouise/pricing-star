import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://pricingstar.io',
  integrations: [tailwind({ applyBaseStyles: false })],
  output: 'static',
});
