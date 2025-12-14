/**
 * Theme Hook
 * 
 * Provides dark/light theme toggle functionality with system preference detection.
 * Persists preference to localStorage.
 */
import { useState, useEffect, useCallback } from 'react';

type Theme = 'light' | 'dark' | 'system';

function getSystemTheme(): 'light' | 'dark' {
    if (typeof window === 'undefined') return 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function useTheme() {
    const [theme, setThemeState] = useState<Theme>(() => {
        if (typeof window === 'undefined') return 'system';
        const stored = localStorage.getItem('theme') as Theme;
        return stored || 'system';
    });

    const resolvedTheme = theme === 'system' ? getSystemTheme() : theme;

    // Apply theme to document
    useEffect(() => {
        const root = document.documentElement;

        if (resolvedTheme === 'dark') {
            root.classList.add('dark');
            root.setAttribute('data-theme', 'dark');
        } else {
            root.classList.remove('dark');
            root.setAttribute('data-theme', 'light');
        }
    }, [resolvedTheme]);

    // Listen for system theme changes
    useEffect(() => {
        if (theme !== 'system') return;

        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handler = () => {
            // Force re-render to pick up new system theme
            setThemeState('system');
        };

        mediaQuery.addEventListener('change', handler);
        return () => mediaQuery.removeEventListener('change', handler);
    }, [theme]);

    const setTheme = useCallback((newTheme: Theme) => {
        setThemeState(newTheme);
        localStorage.setItem('theme', newTheme);
    }, []);

    const toggleTheme = useCallback(() => {
        const newTheme = resolvedTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }, [resolvedTheme, setTheme]);

    const cycleTheme = useCallback(() => {
        const themes: Theme[] = ['light', 'dark', 'system'];
        const currentIndex = themes.indexOf(theme);
        const nextTheme = themes[(currentIndex + 1) % themes.length];
        setTheme(nextTheme);
    }, [theme, setTheme]);

    return {
        theme,
        resolvedTheme,
        setTheme,
        toggleTheme,
        cycleTheme,
        isDark: resolvedTheme === 'dark',
        isLight: resolvedTheme === 'light',
    };
}
