import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwindcss';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  integrations: [tailwind(), react()],
  site: 'https://fabriziosalmi.github.io',
  base: '/repos',
});
