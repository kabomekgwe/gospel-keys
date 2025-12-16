import type { Config } from 'tailwindcss';
import { tokens } from './src/design-system/tokens';

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Colors from design tokens
      colors: {
        primary: {
          cyan: tokens.colors.primary.cyan,
          purple: tokens.colors.primary.purple,
        },
        background: tokens.colors.background,
        text: tokens.colors.text,
        status: tokens.colors.status,
        genre: tokens.colors.genre,
        difficulty: tokens.colors.difficulty,
        border: tokens.colors.border,
      },

      // Typography
      fontFamily: tokens.typography.fontFamily,
      fontSize: tokens.typography.fontSize,
      fontWeight: tokens.typography.fontWeight,
      lineHeight: tokens.typography.lineHeight,
      letterSpacing: tokens.typography.letterSpacing,

      // Spacing
      spacing: tokens.spacing,

      // Border radius
      borderRadius: tokens.borderRadius,

      // Shadows
      boxShadow: {
        ...tokens.shadows,
        glow: {
          cyan: tokens.shadows.glow.cyan,
          purple: tokens.shadows.glow.purple,
          green: tokens.shadows.glow.green,
        },
      },

      // Z-index
      zIndex: tokens.zIndex,

      // Animations
      transitionDuration: tokens.animation.duration,
      transitionTimingFunction: tokens.animation.easing,
      keyframes: tokens.animation.keyframes,
      animation: {
        'fade-in': 'fadeIn 200ms ease-out',
        'slide-up': 'slideUp 200ms ease-out',
        'slide-down': 'slideDown 200ms ease-out',
        'scale-in': 'scaleIn 200ms ease-out',
      },

      // Breakpoints (screens)
      screens: tokens.breakpoints,
    },
  },
  plugins: [],
};

export default config;
