import React from 'react';

/**
 * Card Component - Molecule Design Pattern
 *
 * Flexible container for grouping related content.
 * Used as the foundation for more specific card variants.
 *
 * Features:
 * - Configurable padding
 * - Optional header and footer
 * - Hover effects
 * - Glass morphism variant
 * - Interactive (clickable) variant
 */

export interface CardProps {
  variant?: 'default' | 'glass' | 'bordered' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean; // Hover lift effect
  interactive?: boolean; // Clickable with cursor pointer
  onClick?: () => void;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'md',
  hover = false,
  interactive = false,
  onClick,
  header,
  footer,
  children,
  className = '',
}) => {
  // Padding styles
  const paddingStyles = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  // Variant styles
  const variantStyles = {
    default: `
      bg-background-card
      border border-border-default
    `,
    glass: `
      bg-background-card/70
      backdrop-blur-md
      border border-border-default/50
    `,
    bordered: `
      bg-background-card
      border-2 border-border-default
    `,
    elevated: `
      bg-background-card
      border border-border-default
      shadow-lg
    `,
  };

  // Hover effect
  const hoverStyles = hover
    ? `
      transition-all duration-base
      hover:shadow-xl hover:-translate-y-1
      hover:border-border-hover
    `
    : '';

  // Interactive styles
  const interactiveStyles = interactive || onClick
    ? `
      cursor-pointer
      transition-all duration-base
      hover:shadow-md
      active:scale-[0.98]
    `
    : '';

  const baseStyles = `
    rounded-md
    overflow-hidden
    ${variantStyles[variant]}
    ${hoverStyles}
    ${interactiveStyles}
  `;

  return (
    <div
      className={`${baseStyles} ${className}`.trim().replace(/\s+/g, ' ')}
      onClick={onClick}
      role={interactive || onClick ? 'button' : undefined}
      tabIndex={interactive || onClick ? 0 : undefined}
    >
      {header && (
        <div className={`border-b border-border-default ${paddingStyles[padding]}`}>
          {header}
        </div>
      )}
      <div className={header || footer ? paddingStyles[padding] : paddingStyles[padding]}>
        {children}
      </div>
      {footer && (
        <div className={`border-t border-border-default ${paddingStyles[padding]}`}>
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
