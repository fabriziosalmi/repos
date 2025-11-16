/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-bg': '#0a0a1a',
        'cyber-text': '#00ffcc',
        'cyber-primary': '#00ffff',
      },
      boxShadow: {
        'cyber-glow': '0 0 10px rgba(0, 255, 255, 0.5)',
      }
    },
    fontFamily: {
      'mono': ['Fira Code', 'Courier', 'monospace'],
    }
  },
  plugins: [],
}