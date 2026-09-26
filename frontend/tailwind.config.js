/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7', // Navigation/selected
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e', // Deep navy for important headings
          950: '#082f49',
        },
        surface: {
          50: 'var(--surface-50)',
          100: 'var(--surface-100)',
          200: 'var(--surface-200)',
          300: 'var(--surface-300)',
          400: 'var(--surface-400)',
        },
        content: {
          200: 'var(--content-200)',
          300: 'var(--content-300)',
          400: 'var(--content-400)',
          500: 'var(--content-500)',
          600: 'var(--content-600)',
          700: 'var(--content-700)',
        },
        critical: {
          500: '#ef4444', // Red for suspicious/critical
          600: '#dc2626',
        },
        warning: {
          500: '#f59e0b', // Amber for warnings
          600: '#d97706',
        },
        verified: {
          500: '#10b981', // Green for verified/normal
          600: '#059669',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      }
    },
  },
  plugins: [],
}
