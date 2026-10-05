// Tailwind 3 via PostCSS. Prima lo agganciava @astrojs/tailwind, che non
// supporta Astro 7 (peer "astro: ^3.0.0||^4.0.0||^5.0.0"). Le direttive
// @tailwind stanno gia' in src/styles/global.css, importato da Layout.astro.
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
