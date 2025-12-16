import React from 'react';

/**
 * Badge Component - Atomic Design Pattern
 *
 * Small labels to highlight status, count, or category.
 *
 * Variants:
 * - default: Neutral badge (gray)
 * - primary: Brand primary (cyan)
 * - secondary: Brand secondary (purple)
 * - success: Positive status (green)
 * - warning: Warning status (yellow/orange)
 * - error: Error/danger status (red)
 * - info: Informational (blue)
 *
 * Sizes:
 * - sm: Small (20px height, 12px text)
 * - md: Medium (24px height, 14px text)
 * - lg: Large (28px height, 16px text)
 */

export interface BadgeProps {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  pill?: boolean; // Fully rounded corners
  outlined?: boolean; // Outlined style instead of filled
  icon?: React.ReactNode;
  dot?: boolean; // Show colored dot indicator
  children: React.ReactNode;
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  pill = false,
  outlined = false,
  icon,
  dot = false,
  children,
  className = '',
}) => {
  // Base styles
  const baseStyles = `
    inline-flex items-center justify-center
    font-medium whitespace-nowrap
    ${pill ? 'rounded-full' : 'rounded-DEFAULT'}
    transition-colors duration-fast
  `;

  // Size styles
  const sizeStyles = {
    sm: 'h-5 px-2 text-xs gap-1',
    md: 'h-6 px-2.5 text-sm gap-1.5',
    lg: 'h-7 px-3 text-base gap-2',
  };

  // Variant styles (filled)
  const filledVariantStyles = {
    default: 'bg-background-card text-text-primary border border-border-default',
    primary: 'bg-primary-cyan-500 text-white',
    secondary: 'bg-primary-purple-500 text-white',
    success: 'bg-status-success-DEFAULT text-white',
    warning: 'bg-status-warning-DEFAULT text-white',
    error: 'bg-status-error-DEFAULT text-white',
    info: 'bg-status-info-DEFAULT text-white',
  };

  // Variant styles (outlined)
  const outlinedVariantStyles = {
    default: 'bg-transparent text-text-primary border-2 border-border-default',
    primary: 'bg-transparent text-primary-cyan-500 border-2 border-primary-cyan-500',
    secondary: 'bg-transparent text-primary-purple-500 border-2 border-primary-purple-500',
    success: 'bg-transparent text-status-success-DEFAULT border-2 border-status-success-DEFAULT',
    warning: 'bg-transparent text-status-warning-DEFAULT border-2 border-status-warning-DEFAULT',
    error: 'bg-transparent text-status-error-DEFAULT border-2 border-status-error-DEFAULT',
    info: 'bg-transparent text-status-info-DEFAULT border-2 border-status-info-DEFAULT',
  };

  // Dot colors
  const dotColors = {
    default: 'bg-text-muted',
    primary: 'bg-primary-cyan-500',
    secondary: 'bg-primary-purple-500',
    success: 'bg-status-success-DEFAULT',
    warning: 'bg-status-warning-DEFAULT',
    error: 'bg-status-error-DEFAULT',
    info: 'bg-status-info-DEFAULT',
  };

  const variantStyle = outlined ? outlinedVariantStyles[variant] : filledVariantStyles[variant];

  return (
    <span
      className={`
        ${baseStyles}
        ${sizeStyles[size]}
        ${variantStyle}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {dot && (
        <span className={`w-2 h-2 rounded-full ${dotColors[variant]}`} />
      )}
      {icon && <span className="inline-flex">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};

export default Badge;
