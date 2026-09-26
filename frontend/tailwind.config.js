/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
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
          50: '#ffffff', // White background
          100: '#f8fafc', // Very light blue-gray secondary background
          200: '#f1f5f9',
          300: '#e2e8f0',
          400: '#cbd5e1',
        },
        content: {
          200: '#94a3b8', // Neutral gray for inactive elements
          300: '#64748b',
          400: '#475569',
          500: '#334155',
          600: '#1e293b',
          700: '#0f172a', // Dark charcoal text
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
