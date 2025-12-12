/**
 * InteractivePiano Tests
 */
import { describe, it, expect, vi } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { render } from '../../test/utils';
import { InteractivePiano } from './InteractivePiano';

describe('InteractivePiano', () => {
    it('renders correct number of keys', () => {
        // Default: 2 octaves (24 notes) starting from C4
        render(<InteractivePiano />);

        // Count white and black keys
        // Buttons are used for keys
        const keys = screen.getAllByRole('button');
        expect(keys).toHaveLength(24);
    });

    it('highlights specific notes', () => {
        // Middle C (60)
        render(<InteractivePiano highlightedNotes={[60]} />);

        const keys = screen.getAllByRole('button');
        // Find key corresponding to 60 (C4)
        // Note: The implementation renders keys in order. 
        // 2 octaves starting at C4 (60) to B5 (83)
        // 60 is the first key
        const c4Key = keys[0];

        // Check for highlight class (bg-cyan-400 for white keys)
        expect(c4Key).toHaveClass('bg-cyan-400');
    });

    it('identifies root note', () => {
        render(<InteractivePiano rootNote={60} />);

        const keys = screen.getAllByRole('button');
        const c4Key = keys[0];

        // Check for root class (bg-violet-400 for white keys)
        expect(c4Key).toHaveClass('bg-violet-400');
    });

    it('triggers callback on note click', () => {
        const handleNoteClick = vi.fn();
        render(<InteractivePiano onNoteClick={handleNoteClick} />);

        const keys = screen.getAllByRole('button');
        fireEvent.click(keys[0]); // Click C4 (60)

        expect(handleNoteClick).toHaveBeenCalledWith(60);
    });

    it('shows note names by default', () => {
        render(<InteractivePiano />);
        const cNotes = screen.getAllByText('C');
        expect(cNotes.length).toBeGreaterThan(0);
    });

    it('hides note names when requested', () => {
        render(<InteractivePiano showNoteNames={false} />);
        expect(screen.queryByText('C')).not.toBeInTheDocument();
    });
});
