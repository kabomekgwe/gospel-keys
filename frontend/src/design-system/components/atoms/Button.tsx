import React from 'react';
import { tokens } from '../../tokens';

/**
 * Button Component - Atomic Design Pattern
 *
 * A versatile button component with multiple variants, sizes, and states.
 * Follows the design system tokens for consistent styling.
 *
 * Variants:
 * - primary: Main call-to-action (cyan)
 * - secondary: Secondary actions (purple)
 * - success: Positive actions (green)
 * - danger: Destructive actions (red)
 * - ghost: Subtle actions (transparent with border)
 *
 * Sizes:
 * - sm: Small (32px height)
 * - md: Medium (40px height) - default
 * - lg: Large (48px height)
 */

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      loading = false,
      icon,
      iconPosition = 'left',
      disabled,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    // Base styles
    const baseStyles = `
      inline-flex items-center justify-center
      font-medium rounded-DEFAULT
      transition-all duration-base
      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background-dark
      disabled:opacity-50 disabled:cursor-not-allowed
      ${fullWidth ? 'w-full' : ''}
    `;

    // Variant styles
    const variantStyles = {
      primary: `
        bg-primary-cyan-500 text-white
        hover:bg-primary-cyan-600
        focus:ring-primary-cyan-500
        shadow-md hover:shadow-lg
      `,
      secondary: `
        bg-primary-purple-500 text-white
        hover:bg-primary-purple-600
        focus:ring-primary-purple-500
        shadow-md hover:shadow-lg
      `,
      success: `
        bg-status-success-DEFAULT text-white
        hover:bg-status-success-dark
        focus:ring-status-success-DEFAULT
        shadow-md hover:shadow-lg
      `,
      danger: `
        bg-status-error-DEFAULT text-white
        hover:bg-status-error-dark
        focus:ring-status-error-DEFAULT
        shadow-md hover:shadow-lg
      `,
      ghost: `
        bg-transparent text-text-primary border-2 border-border-default
        hover:border-border-hover hover:bg-background-hover
        focus:ring-primary-cyan-500
      `,
    };

    // Size styles
    const sizeStyles = {
      sm: 'h-[32px] px-4 text-sm gap-1.5',
      md: 'h-[40px] px-6 text-base gap-2',
      lg: 'h-[48px] px-8 text-lg gap-2.5',
    };

    // Loading spinner
    const LoadingSpinner = () => (
      <svg
        className="animate-spin -ml-1 mr-2 h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`
          ${baseStyles}
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `.trim().replace(/\s+/g, ' ')}
        {...props}
      >
        {loading && <LoadingSpinner />}
        {!loading && icon && iconPosition === 'left' && (
          <span className="inline-flex">{icon}</span>
        )}
        <span>{children}</span>
        {!loading && icon && iconPosition === 'right' && (
          <span className="inline-flex">{icon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
