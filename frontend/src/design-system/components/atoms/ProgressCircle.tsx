import React from 'react';

/**
 * ProgressCircle Component - Atomic Design Pattern
 *
 * Circular/radial progress indicator for showing completion status.
 * Perfect for skill levels, exercise completion, or time-based progress.
 *
 * Variants:
 * - primary: Cyan stroke
 * - secondary: Purple stroke
 * - success: Green stroke
 * - warning: Orange stroke
 * - error: Red stroke
 *
 * Sizes:
 * - sm: 48px diameter
 * - md: 64px diameter
 * - lg: 96px diameter
 * - xl: 128px diameter
 */

export interface ProgressCircleProps {
  value: number; // 0-100
  max?: number; // Default 100
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  strokeWidth?: number; // Thickness of the ring (default: 8)
  showLabel?: boolean; // Show percentage in center
  label?: string | React.ReactNode; // Custom content in center
  className?: string;
}

const ProgressCircle: React.FC<ProgressCircleProps> = ({
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  strokeWidth = 8,
  showLabel = true,
  label,
  className = '',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  // Size configurations (diameter in pixels)
  const sizeConfig = {
    sm: { diameter: 48, fontSize: 'text-xs' },
    md: { diameter: 64, fontSize: 'text-sm' },
    lg: { diameter: 96, fontSize: 'text-lg' },
    xl: { diameter: 128, fontSize: 'text-2xl' },
  };

  const { diameter, fontSize } = sizeConfig[size];
  const radius = (diameter - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Variant colors
  const variantColors = {
    primary: '#06b6d4',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
  };

  return (
    <div
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{ width: diameter, height: diameter }}
    >
      <svg
        width={diameter}
        height={diameter}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={diameter / 2}
          cy={diameter / 2}
          r={radius}
          fill="none"
          stroke="#334155"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={diameter / 2}
          cy={diameter / 2}
          r={radius}
          fill="none"
          stroke={variantColors[variant]}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-slow ease-out"
        />
      </svg>
      {/* Center content */}
      <div className={`absolute inset-0 flex items-center justify-center ${fontSize} font-semibold text-text-primary`}>
        {label !== undefined ? (
          label
        ) : showLabel ? (
          <span>{Math.round(percentage)}%</span>
        ) : null}
      </div>
    </div>
  );
};

export default ProgressCircle;
