import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  integrations: [
    tailwind(),
    // privacy-policy.html is copied verbatim from public/: Astro never routes it,
    // so the sitemap would not know it exists.
    sitemap({ customPages: ['https://fabriziosalmi.github.io/repos/privacy-policy.html'] }),
  ],
  site: 'https://fabriziosalmi.github.io',
  base: '/repos/',
});
