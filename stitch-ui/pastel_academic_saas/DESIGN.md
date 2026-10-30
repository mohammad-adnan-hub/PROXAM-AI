---
name: Pastel Academic SaaS
colors:
  surface: '#FFFFFF'
  surface-dim: '#dbdad6'
  surface-bright: '#fbf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3ef'
  surface-container: '#efeeea'
  surface-container-high: '#eae8e4'
  surface-container-highest: '#e4e2de'
  on-surface: '#1b1c1a'
  on-surface-variant: '#444748'
  inverse-surface: '#30312e'
  inverse-on-surface: '#f2f0ec'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1c1b1b'
  on-primary-container: '#858383'
  inverse-primary: '#c8c6c5'
  secondary: '#396759'
  on-secondary: '#ffffff'
  secondary-container: '#b9ead8'
  on-secondary-container: '#3e6b5d'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#1a173b'
  on-tertiary-container: '#837faa'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e5e2e1'
  primary-fixed-dim: '#c8c6c5'
  on-primary-fixed: '#1c1b1b'
  on-primary-fixed-variant: '#474646'
  secondary-fixed: '#bceddb'
  secondary-fixed-dim: '#a0d1bf'
  on-secondary-fixed: '#002018'
  on-secondary-fixed-variant: '#204f42'
  tertiary-fixed: '#e4dfff'
  tertiary-fixed-dim: '#c6c2f0'
  on-tertiary-fixed: '#1a173b'
  on-tertiary-fixed-variant: '#454269'
  background: '#fbf9f5'
  on-background: '#1b1c1a'
  surface-variant: '#e4e2de'
  surface-soft: '#F1EEE8'
  text-primary: '#111111'
  text-secondary: '#686868'
  text-muted: '#969696'
  border: '#E8E4DD'
  border-strong: '#D8D2C9'
  primary-hover: '#292929'
  mint: '#B9EAD8'
  mint-strong: '#8FD5BD'
  lavender: '#D5D0FF'
  peach: '#F8D9B5'
  pink: '#F4B9C2'
  blue: '#C8E2F5'
  yellow: '#F4E6A8'
  success: '#9BD9BD'
  warning: '#F3C58E'
  danger: '#E9A4A4'
  info: '#BFDDF2'
typography:
  display-lg:
    fontFamily: Manrope
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Manrope
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Manrope
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  margin: 2rem
  margin-sm: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

# Proxam AI — Design System and UI Guidelines

## 1. Design Overview
Proxam AI is an online examination platform with AI-assisted proctoring for students, teachers, and administrators.
Modern pastel education SaaS theme inspired by warm ivory backgrounds, soft pastel cards, pill buttons, spacious layouts.

## 2. Color System
:root {
  --color-background: #F8F6F2;
  --color-surface: #FFFFFF;
  --color-surface-soft: #F1EEE8;
  --color-text-primary: #111111;
  --color-text-secondary: #686868;
  --color-text-muted: #969696;
  --color-border: #E8E4DD;
  --color-border-strong: #D8D2C9;
  --color-primary: #111111;
  --color-primary-hover: #292929;
  --color-mint: #B9EAD8;
  --color-mint-strong: #8FD5BD;
  --color-lavender: #D5D0FF;
  --color-peach: #F8D9B5;
  --color-pink: #F4B9C2;
  --color-blue: #C8E2F5;
  --color-yellow: #F4E6A8;
  --color-success: #9BD9BD;
  --color-warning: #F3C58E;
  --color-danger: #E9A4A4;
  --color-info: #BFDDF2;
}

## 3. Typography
- Primary font: Inter
- Display font: Manrope
- Test code font: JetBrains Mono

## 4. Border Radius & Shadows
- Inputs: 14px
- Buttons: 999px (pill)
- Cards: 24px
- Main panels: 28px
- Subtle shadow: 0 8px 30px rgba(20, 20, 20, 0.04)
