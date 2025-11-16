import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import csp from 'vite-plugin-csp'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    csp({
      policy: {
        'default-src': ['self'],
        'script-src': ['self'],
        'style-src': ['self', 'unsafe-inline'],
        'img-src': ['self', 'data:', 'https:'],
        'connect-src': ['self'],
        'font-src': ['self', 'data:', 'https://fonts.gstatic.com'],
        'object-src': ['none'],
        'base-uri': ['self'],
        'form-action': ['self'],
        'frame-ancestors': ['none'],
        'upgrade-insecure-requests': true
      }
    })
  ],
  base: '',
})
