/**
 * Gospel Keys Design System Tokens
 *
 * Foundation of the design system - all visual design constants.
 * Used throughout the application for consistent styling.
 */

// ============================================================================
// COLORS
// ============================================================================

export const colors = {
  // Primary Brand Colors
  primary: {
    cyan: {
      50: '#ecfeff',
      100: '#cffafe',
      200: '#a5f3fc',
      300: '#67e8f9',
      400: '#22d3ee',
      500: '#06b6d4', // Main
      600: '#0891b2',
      700: '#0e7490',
      800: '#155e75',
      900: '#164e63',
    },
    purple: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#8b5cf6', // Main
      600: '#7c3aed',
      700: '#6d28d9',
      800: '#5b21b6',
      900: '#4c1d95',
    },
  },

  // Background Colors
  background: {
    dark: '#0f172a',      // Main dark background
    card: '#1e293b',      // Card/elevated surfaces
    hover: '#334155',     // Hover states
    input: '#1e293b',     // Input backgrounds
    overlay: 'rgba(15, 23, 42, 0.9)', // Modal overlays
  },

  // Text Colors
  text: {
    primary: '#f8fafc',   // Main text
    secondary: '#cbd5e1', // Secondary text
    muted: '#94a3b8',     // Muted/disabled text
    inverse: '#0f172a',   // Text on light backgrounds
  },

  // Status Colors
  status: {
    success: {
      light: '#22c55e',
      DEFAULT: '#10b981',
      dark: '#059669',
    },
    warning: {
      light: '#fbbf24',
      DEFAULT: '#f59e0b',
      dark: '#d97706',
    },
    error: {
      light: '#f87171',
      DEFAULT: '#ef4444',
      dark: '#dc2626',
    },
    info: {
      light: '#38bdf8',
      DEFAULT: '#0ea5e9',
      dark: '#0284c7',
    },
  },

  // Genre-Specific Colors
  genre: {
    gospel: {
      primary: '#8b5cf6',
      gradient: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)',
    },
    jazz: {
      primary: '#f59e0b',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #eab308 100%)',
    },
    blues: {
      primary: '#3b82f6',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
    },
    neosoul: {
      primary: '#ec4899',
      gradient: 'linear-gradient(135deg, #ec4899 0%, #f97316 100%)',
    },
    classical: {
      primary: '#6366f1',
      gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    },
  },

  // Difficulty Colors
  difficulty: {
    beginner: '#22c55e',
    intermediate: '#f59e0b',
    advanced: '#ef4444',
  },

  // Border Colors
  border: {
    default: '#334155',
    hover: '#475569',
    focus: '#06b6d4',
  },
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  // Font Families
  fontFamily: {
    sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
    mono: ['Fira Code', 'Monaco', 'Courier New', 'monospace'],
  },

  // Font Sizes
  fontSize: {
    '6xl': '4rem',      // 64px - Hero headings
    '5xl': '3rem',      // 48px - Page titles
    '4xl': '2.25rem',   // 36px - Section headings
    '3xl': '1.875rem',  // 30px - Card titles
    '2xl': '1.5rem',    // 24px - Subsection headings
    xl: '1.25rem',      // 20px - Large body
    lg: '1.125rem',     // 18px - Body large
    base: '1rem',       // 16px - Body text
    sm: '0.875rem',     // 14px - Small text
    xs: '0.75rem',      // 12px - Extra small
  },

  // Font Weights
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  // Line Heights
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },

  // Letter Spacing
  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
  },
} as const;

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
  32: '8rem',     // 128px
} as const;

// ============================================================================
// BORDER RADIUS
// ============================================================================

export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px - Small elements
  DEFAULT: '0.5rem', // 8px - Default (buttons, inputs)
  md: '0.75rem',    // 12px - Cards
  lg: '1rem',       // 16px - Large cards
  xl: '1.5rem',     // 24px - Modals
  '2xl': '2rem',    // 32px - Extra large
  full: '9999px',   // Fully rounded (pills, avatars)
} as const;

// ============================================================================
// SHADOWS
// ============================================================================

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  DEFAULT: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  md: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  '2xl': '0 35px 60px -15px rgba(0, 0, 0, 0.3)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  none: 'none',

  // Colored shadows for genre-specific elements
  glow: {
    cyan: '0 0 20px rgba(6, 182, 212, 0.5)',
    purple: '0 0 20px rgba(139, 92, 246, 0.5)',
    green: '0 0 20px rgba(16, 185, 129, 0.5)',
  },
} as const;

// ============================================================================
// ANIMATION
// ============================================================================

export const animation = {
  // Durations
  duration: {
    instant: '0ms',
    fast: '150ms',
    base: '200ms',
    slow: '300ms',
    slower: '500ms',
  },

  // Easing Functions
  easing: {
    linear: 'linear',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  // Common animations
  keyframes: {
    fadeIn: {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    slideUp: {
      from: { transform: 'translateY(10px)', opacity: 0 },
      to: { transform: 'translateY(0)', opacity: 1 },
    },
    slideDown: {
      from: { transform: 'translateY(-10px)', opacity: 0 },
      to: { transform: 'translateY(0)', opacity: 1 },
    },
    scaleIn: {
      from: { transform: 'scale(0.95)', opacity: 0 },
      to: { transform: 'scale(1)', opacity: 1 },
    },
  },
} as const;

// ============================================================================
// Z-INDEX
// ============================================================================

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1100,
  fixed: 1200,
  modalBackdrop: 1300,
  modal: 1400,
  popover: 1500,
  tooltip: 1600,
} as const;

// ============================================================================
// BREAKPOINTS
// ============================================================================

export const breakpoints = {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large desktop
} as const;

// ============================================================================
// COMPONENT-SPECIFIC TOKENS
// ============================================================================

export const components = {
  button: {
    height: {
      sm: '2rem',      // 32px
      md: '2.5rem',    // 40px
      lg: '3rem',      // 48px
    },
    padding: {
      sm: '0.5rem 1rem',    // 8px 16px
      md: '0.75rem 1.5rem', // 12px 24px
      lg: '1rem 2rem',      // 16px 32px
    },
  },

  input: {
    height: {
      sm: '2rem',      // 32px
      md: '2.5rem',    // 40px
      lg: '3rem',      // 48px
    },
  },

  card: {
    padding: {
      sm: '1rem',      // 16px
      md: '1.5rem',    // 24px
      lg: '2rem',      // 32px
    },
  },

  progress: {
    height: {
      sm: '0.25rem',   // 4px
      md: '0.5rem',    // 8px
      lg: '0.75rem',   // 12px
    },
  },
} as const;

// ============================================================================
// EXPORTS
// ============================================================================

export const tokens = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animation,
  zIndex,
  breakpoints,
  components,
} as const;

export default tokens;
