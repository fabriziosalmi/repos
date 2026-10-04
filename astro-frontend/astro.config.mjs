import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Tailwind 3 e' agganciato via postcss.config.mjs, non piu' con
  // @astrojs/tailwind: quell'integrazione si ferma ad Astro 5 (peer
  // "astro: ^3||^4||^5") e Astro 7 e' obbligatorio per GHSA-26w7-cxv4-gfx2.
  // Cosi' i nomi delle classi restano identici: nessuna migrazione a Tailwind 4.
  integrations: [
    // privacy-policy.html is copied verbatim from public/: Astro never routes it,
    // so the sitemap would not know it exists.
    sitemap({ customPages: ['https://fabriziosalmi.github.io/repos/privacy-policy.html'] }),
  ],
  site: 'https://fabriziosalmi.github.io',
  base: '/repos/',
});
