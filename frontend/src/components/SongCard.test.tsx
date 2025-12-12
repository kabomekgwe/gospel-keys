/**
 * SongCard Component Tests
 */
import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '../test/utils';
import { SongCard } from './SongCard';
import type { Song } from '../lib/api';

// Mock TanStack Router
vi.mock('@tanstack/react-router', async () => {
    const actual = await vi.importActual('@tanstack/react-router');
    return {
        ...actual,
        Link: ({ to, children, className }: any) => (
            <a href={to} className={className}>{children}</a>
        ),
    };
});

const mockSong: Song = {
    id: 'test-song-1',
    title: 'Test Song',
    artist: 'Test Artist',
    duration: 180,
    key_signature: 'C major',
    tempo: 120,
    difficulty: 'intermediate',
    favorite: false,
    created_at: '2024-01-01T00:00:00Z',
    time_signature: '4/4',
    note_count: 100,
    chord_count: 20,
    last_accessed_at: '2024-01-01T00:00:00Z',
};

describe('SongCard', () => {
    it('renders song title', () => {
        render(<SongCard song={mockSong} viewMode="grid" />);
        expect(screen.getByText('Test Song')).toBeInTheDocument();
    });

    it('renders artist name', () => {
        render(<SongCard song={mockSong} viewMode="grid" />);
        expect(screen.getByText('Test Artist')).toBeInTheDocument();
    });

    it('renders duration in formatted time', () => {
        render(<SongCard song={mockSong} viewMode="grid" />);
        // 180 seconds = 3:00
        expect(screen.getByText('3:00')).toBeInTheDocument();
    });

    it('renders difficulty badge', () => {
        render(<SongCard song={mockSong} viewMode="grid" />);
        expect(screen.getByText('intermediate')).toBeInTheDocument();
    });

    it('links to song detail page', () => {
        render(<SongCard song={mockSong} viewMode="grid" />);
        const link = screen.getByRole('link');
        expect(link).toHaveAttribute('href', '/library/test-song-1');
    });

    it('renders in list view mode', () => {
        render(<SongCard song={mockSong} viewMode="list" />);
        expect(screen.getByText('Test Song')).toBeInTheDocument();
        expect(screen.getByText('Test Artist')).toBeInTheDocument();
    });

    it('handles missing artist gracefully', () => {
        const songWithoutArtist = { ...mockSong, artist: undefined };
        render(<SongCard song={songWithoutArtist} viewMode="grid" />);
        expect(screen.getByText('Test Song')).toBeInTheDocument();
    });

    it('handles missing duration gracefully', () => {
        const songWithoutDuration = { ...mockSong, duration: 0 };
        render(<SongCard song={songWithoutDuration} viewMode="grid" />);
        expect(screen.getByText('Test Song')).toBeInTheDocument();
    });
});
