/**
 * Sidebar Component Tests
 */
import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '../test/utils';
import Sidebar from './Sidebar';

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
    const actual = await vi.importActual('@tanstack/react-router');
    return {
        ...actual,
        Link: ({ to, children, className }: any) => (
            <a href={to} className={className}>{children}</a>
        ),
        useRouterState: () => ({
            location: { pathname: '/' }
        }),
    };
});

describe('Sidebar', () => {
    it('renders the logo', () => {
        render(<Sidebar />);
        expect(screen.getByText('Piano Keys')).toBeInTheDocument();
    });

    it('renders all navigation items', () => {
        render(<Sidebar />);

        expect(screen.getByText('Home')).toBeInTheDocument();
        expect(screen.getByText('Upload')).toBeInTheDocument();
        expect(screen.getByText('Library')).toBeInTheDocument();
        expect(screen.getByText('Discover')).toBeInTheDocument();
        expect(screen.getByText('Practice')).toBeInTheDocument();
        expect(screen.getByText('Theory')).toBeInTheDocument();
        expect(screen.getByText('Jobs')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('renders correct navigation links', () => {
        render(<Sidebar />);

        const links = screen.getAllByRole('link');
        const hrefs = links.map(link => link.getAttribute('href'));

        expect(hrefs).toContain('/');
        expect(hrefs).toContain('/upload');
        expect(hrefs).toContain('/library');
        expect(hrefs).toContain('/discover');
        expect(hrefs).toContain('/practice');
        expect(hrefs).toContain('/theory');
        expect(hrefs).toContain('/jobs');
        expect(hrefs).toContain('/settings');
    });

    it('renders collapse button', () => {
        render(<Sidebar />);
        expect(screen.getByText('Collapse')).toBeInTheDocument();
    });
});
