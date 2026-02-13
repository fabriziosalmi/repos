/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
    theme: {
        extend: {
            colors: {
                background: '#020617', // Deeper blue-black
                surface: '#0f172a',    // Deep slate blue
                surfaceHighlight: '#1e293b',
                surfaceAccent: '#334155',
                text: '#f8fafc',
                textMuted: '#94a3b8',
                primary: '#38bdf8',    // Sky blue
                secondary: '#818cf8',  // Indigo
                accent: '#2dd4bf',     // Teal
                glow: 'rgba(56, 189, 248, 0.4)',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Outfit', 'Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            boxShadow: {
                'premium': '0 0 50px -12px rgba(0, 0, 0, 0.5)',
                'glow': '0 0 20px -5px var(--tw-shadow-color)',
            },
            animation: {
                'fade-in': 'fadeIn 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                'slide-up': 'slideUp 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                'float': 'float 6s ease-in-out infinite',
                'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(30px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-20px)' },
                }
            }
        },
    },
    plugins: [],
}

