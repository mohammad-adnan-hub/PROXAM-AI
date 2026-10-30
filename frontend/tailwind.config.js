/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Manrope', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        'surface-soft': 'var(--color-surface-soft)',
        border: 'var(--color-border)',
        'border-strong': 'var(--color-border-strong)',
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        mint: 'var(--color-mint)',
        'mint-strong': 'var(--color-mint-strong)',
        lavender: 'var(--color-lavender)',
        peach: 'var(--color-peach)',
        pink: 'var(--color-pink-pastel)',
        'pale-blue': 'var(--color-blue)',
        'soft-yellow': 'var(--color-yellow)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        danger: 'var(--color-danger)',
        info: 'var(--color-info)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-muted': 'var(--color-text-muted)',
      },
      borderRadius: {
        sm: '10px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        pill: '999px',
      },
      boxShadow: {
        card: '0 8px 30px rgba(20, 20, 20, 0.04)',
        'card-md': '0 4px 16px rgba(20, 20, 20, 0.06)',
      },
    },
  },
  plugins: [],
}
