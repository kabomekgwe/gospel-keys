import React from 'react';
import { Link } from '@tanstack/react-router';
import { Button } from '../atoms';
import { Container, Stack } from '../templates';

/**
 * Header Component - Main Navigation Organism
 *
 * Top navigation bar with logo, main nav links, and user actions.
 * Sticky positioning with backdrop blur for modern feel.
 */

export interface HeaderProps {
  currentPath?: string;
  user?: {
    name: string;
    avatar?: string;
  };
  onSignOut?: () => void;
  className?: string;
}

const Header: React.FC<HeaderProps> = ({
  currentPath = '/',
  user,
  onSignOut,
  className = '',
}) => {
  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/curriculum', label: 'Curriculum' },
    { path: '/practice', label: 'Practice' },
    { path: '/theory/lab', label: 'Theory Lab' },
    { path: '/ai-studio', label: 'AI Studio' },
  ];

  const isActive = (path: string) => currentPath === path;

  return (
    <header className={`
      sticky top-0 z-fixed
      bg-background-dark/80 backdrop-blur-lg
      border-b border-border-default
      ${className}
    `}>
      <Container>
        <Stack direction="horizontal" spacing={8} align="center" justify="between" className="py-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-cyan-500 to-primary-purple-500 rounded-lg flex items-center justify-center transform transition-transform group-hover:scale-105">
              <span className="text-white text-xl font-bold">GK</span>
            </div>
            <span className="text-text-primary font-bold text-xl hidden sm:block">
              Gospel Keys
            </span>
          </Link>

          {/* Main Navigation */}
          <nav className="hidden md:flex gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`
                  px-4 py-2 rounded-DEFAULT
                  font-medium text-sm
                  transition-all duration-fast
                  ${isActive(link.path)
                    ? 'bg-primary-cyan-500 text-white'
                    : 'text-text-secondary hover:text-text-primary hover:bg-background-card'
                  }
                `}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* User Actions */}
          <Stack direction="horizontal" spacing={4} align="center">
            {user ? (
              <>
                <div className="hidden sm:flex items-center gap-2">
                  {user.avatar ? (
                    <img
                      src={user.avatar}
                      alt={user.name}
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <div className="w-8 h-8 bg-primary-purple-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-semibold">
                        {user.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                  <span className="text-text-primary text-sm font-medium">
                    {user.name}
                  </span>
                </div>
                <Button variant="ghost" size="sm" onClick={onSignOut}>
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
                <Button variant="primary" size="sm">
                  Start Free
                </Button>
              </>
            )}
          </Stack>
        </Stack>
      </Container>
    </header>
  );
};

export default Header;
