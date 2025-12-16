import React from 'react';

/**
 * Stack Component - Layout Template
 *
 * Flexbox-based vertical or horizontal stacking layout.
 * Automatically applies consistent spacing between children.
 *
 * Direction:
 * - vertical: Stack items vertically (default)
 * - horizontal: Stack items horizontally
 *
 * Spacing: Uses design system spacing tokens (2, 4, 6, 8, etc.)
 * Alignment: start, center, end, stretch
 * Justification: start, center, end, between, around, evenly
 */

export interface StackProps {
  direction?: 'vertical' | 'horizontal';
  spacing?: 2 | 4 | 6 | 8 | 10 | 12 | 16;
  align?: 'start' | 'center' | 'end' | 'stretch';
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';
  wrap?: boolean;
  children: React.ReactNode;
  className?: string;
}

const Stack: React.FC<StackProps> = ({
  direction = 'vertical',
  spacing = 4,
  align = 'stretch',
  justify = 'start',
  wrap = false,
  children,
  className = '',
}) => {
  // Direction styles
  const directionStyles = {
    vertical: 'flex-col',
    horizontal: 'flex-row',
  };

  // Spacing styles (gap utility)
  const spacingClass = `gap-${spacing}`;

  // Alignment styles
  const alignStyles = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
  };

  // Justification styles
  const justifyStyles = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between',
    around: 'justify-around',
    evenly: 'justify-evenly',
  };

  return (
    <div
      className={`
        flex
        ${directionStyles[direction]}
        ${spacingClass}
        ${alignStyles[align]}
        ${justifyStyles[justify]}
        ${wrap ? 'flex-wrap' : ''}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {children}
    </div>
  );
};

export default Stack;
