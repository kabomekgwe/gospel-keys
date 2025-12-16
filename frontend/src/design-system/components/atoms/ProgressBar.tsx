import React from 'react';

/**
 * ProgressBar Component - Atomic Design Pattern
 *
 * Linear progress indicator for showing completion status.
 *
 * Variants:
 * - default: Gray progress
 * - primary: Cyan gradient
 * - secondary: Purple gradient
 * - success: Green progress
 * - warning: Orange/yellow progress
 * - error: Red progress
 *
 * Sizes:
 * - sm: 4px height
 * - md: 8px height
 * - lg: 12px height
 */

export interface ProgressBarProps {
  value: number; // 0-100
  max?: number; // Default 100
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean; // Show percentage label
  label?: string; // Custom label text
  animated?: boolean; // Animated stripes
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  label,
  animated = false,
  className = '',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  // Size styles
  const sizeStyles = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  // Variant styles
  const variantStyles = {
    default: 'bg-text-muted',
    primary: 'bg-gradient-to-r from-primary-cyan-500 to-primary-cyan-600',
    secondary: 'bg-gradient-to-r from-primary-purple-500 to-primary-purple-600',
    success: 'bg-gradient-to-r from-status-success-DEFAULT to-status-success-dark',
    warning: 'bg-gradient-to-r from-status-warning-DEFAULT to-status-warning-dark',
    error: 'bg-gradient-to-r from-status-error-DEFAULT to-status-error-dark',
  };

  // Animated stripes
  const stripesStyle = animated
    ? `
      bg-gradient-to-r from-transparent via-white to-transparent
      bg-[length:200%_100%]
      opacity-20
      animate-[shimmer_2s_linear_infinite]
    `
    : '';

  return (
    <div className={`w-full ${className}`}>
      {(showLabel || label) && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-text-secondary">
            {label || `${Math.round(percentage)}%`}
          </span>
        </div>
      )}
      <div className={`w-full bg-background-card rounded-full overflow-hidden ${sizeStyles[size]}`}>
        <div
          className={`
            ${sizeStyles[size]}
            ${variantStyles[variant]}
            rounded-full
            transition-all duration-slow ease-out
            relative
            overflow-hidden
          `}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        >
          {animated && (
            <div
              className={`absolute inset-0 ${stripesStyle}`}
              style={{
                animation: 'shimmer 2s linear infinite',
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
