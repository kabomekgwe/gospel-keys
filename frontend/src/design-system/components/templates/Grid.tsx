import React from 'react';

/**
 * Grid Component - Layout Template
 *
 * CSS Grid-based responsive layout system.
 * Supports auto-responsive columns and custom gap spacing.
 *
 * Columns:
 * - Accepts number (1-12) for fixed columns
 * - 'auto-fit': Automatically fits columns based on minWidth
 * - 'auto-fill': Fills available space with columns
 *
 * Usage Examples:
 * - <Grid cols={3}>...</Grid> - 3 equal columns
 * - <Grid cols="auto-fit" minWidth="300px">...</Grid> - Responsive cards
 */

export interface GridProps {
  cols?: 1 | 2 | 3 | 4 | 5 | 6 | 'auto-fit' | 'auto-fill';
  gap?: 2 | 4 | 6 | 8 | 10 | 12 | 16;
  minWidth?: string; // Minimum column width for auto layouts (e.g., '250px')
  children: React.ReactNode;
  className?: string;
}

const Grid: React.FC<GridProps> = ({
  cols = 3,
  gap = 6,
  minWidth = '250px',
  children,
  className = '',
}) => {
  // Column styles
  const getColsStyle = () => {
    if (cols === 'auto-fit') {
      return `grid-cols-[repeat(auto-fit,minmax(${minWidth},1fr))]`;
    }
    if (cols === 'auto-fill') {
      return `grid-cols-[repeat(auto-fill,minmax(${minWidth},1fr))]`;
    }
    return `grid-cols-1 sm:grid-cols-2 lg:grid-cols-${cols}`;
  };

  const gapClass = `gap-${gap}`;

  return (
    <div
      className={`
        grid
        ${getColsStyle()}
        ${gapClass}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
    >
      {children}
    </div>
  );
};

export default Grid;
