/**
 * SheetMusicRenderer Tests
 */
import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { render } from '../../test/utils';
import { SheetMusicRenderer } from './SheetMusicRenderer';

// Mock useVexFlow hook
vi.mock('../../hooks/useVexFlow', () => ({
    useVexFlow: () => ({
        render: vi.fn(),
    }),
}));

describe('SheetMusicRenderer', () => {
    it('renders controls by default', () => {
        render(<SheetMusicRenderer notes={[]} />);

        expect(screen.getByTitle('Zoom In')).toBeInTheDocument();
        expect(screen.getByTitle('Zoom Out')).toBeInTheDocument();
        expect(screen.getByTitle('Refresh')).toBeInTheDocument();
    });

    it('hides controls when specified', () => {
        render(<SheetMusicRenderer notes={[]} showControls={false} />);

        expect(screen.queryByTitle('Zoom In')).not.toBeInTheDocument();
    });

    it('shows empty state when no notes provided', () => {
        render(<SheetMusicRenderer notes={[]} />);

        expect(screen.getByText('No notes to display')).toBeInTheDocument();
    });

    it('renders rendering container when notes exist', () => {
        const mockNotes: any[] = [
            { id: '1', pitch: 60, start_time: 0, end_time: 1, velocity: 100 }
        ];

        render(<SheetMusicRenderer notes={mockNotes} />);

        expect(screen.queryByText('No notes to display')).not.toBeInTheDocument();
        // Container should be present (though content is handled by VexFlow which is mocked)
    });

    it('shows legend', () => {
        render(<SheetMusicRenderer notes={[]} />);
        expect(screen.getByText(/Treble clef:/)).toBeInTheDocument();
    });
});
