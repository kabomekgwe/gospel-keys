import React from 'react';

/**
 * Container Component - Layout Template
 *
 * Responsive container for page content.
 * Centers content and applies max-width constraints.
 *
 * Sizes:
 * - sm: max-w-screen-sm (640px)
 * - md: max-w-screen-md (768px)
 * - lg: max-w-screen-lg (1024px)
 * - xl: max-w-screen-xl (1280px)
 * - 2xl: max-w-screen-2xl (1536px)
 * - full: w-full (no max-width)
 */

export interface ContainerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
  padding?: boolean; // Apply horizontal padding
  children: React.ReactNode;
  className?: string;
}

const Container: React.FC<ContainerProps> = ({
  size = 'xl',
  padding = true,
  children,
  className = '',
}) => {
  // Max width styles
  const sizeStyles = {
    sm: 'max-w-screen-sm',    // 640px
    md: 'max-w-screen-md',    // 768px
    lg: 'max-w-screen-lg',    // 1024px
    xl: 'max-w-screen-xl',    // 1280px
    '2xl': 'max-w-screen-2xl', // 1536px
    full: 'w-full',
  };

  return (
    <div
      className={`
        mx-auto
        ${sizeStyles[size]}
        ${padding ? 'px-4 sm:px-6 lg:px-8' : ''}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {children}
    </div>
  );
};

export default Container;
