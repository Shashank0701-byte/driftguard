import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'drift-bg':      '#0A0D0F',
        'drift-surface': '#111418',
        'drift-border':  '#1E2329',
        'drift-muted':   '#4B5563',
        'drift-red':     '#EF4444',
        'drift-amber':   '#F59E0B',
        'drift-green':   '#10B981',
        'drift-blue':    '#3B82F6',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
export default config
