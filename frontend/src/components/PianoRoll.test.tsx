/**
 * PianoRoll Tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent } from '@testing-library/react';
import { render } from '../test/utils';
import { PianoRoll, type Note } from './PianoRoll';

// Mock canvas context
const mockContext = {
    fillRect: vi.fn(),
    strokeRect: vi.fn(),
    scale: vi.fn(),
    fillText: vi.fn(),
    beginPath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    closePath: vi.fn(),
    roundRect: vi.fn(),
} as unknown as CanvasRenderingContext2D;

describe('PianoRoll', () => {
    beforeEach(() => {
        vi.clearAllMocks();

        // Mock getContext
        HTMLCanvasElement.prototype.getContext = vi.fn(() => mockContext) as any;

        // Mock getBoundingClientRect
        Element.prototype.getBoundingClientRect = vi.fn(() => ({
            width: 800,
            height: 600,
            top: 0,
            left: 0,
            bottom: 600,
            right: 800,
            x: 0,
            y: 0,
            toJSON: () => { }
        }));
    });

    const mockNotes: Note[] = [
        { id: '1', pitch: 60, startTime: 0, duration: 1, velocity: 100 },
        { id: '2', pitch: 64, startTime: 1, duration: 1, velocity: 90 }, // E4
        { id: '3', pitch: 67, startTime: 2, duration: 2, velocity: 80 }, // G4
    ];

    it('renders without crashing', () => {
        const { container } = render(
            <PianoRoll
                notes={mockNotes}
                duration={10}
            />
        );
        expect(container.querySelector('canvas')).toBeInTheDocument();
    });

    it('draws notes on canvas', () => {
        render(<PianoRoll notes={mockNotes} duration={10} />);

        // Draw is called in useEffect, so we expect fillRect calls
        // Initial clear + piano keys + grid lines + notes
        expect(mockContext.fillRect).toHaveBeenCalled();
        expect(mockContext.roundRect).toHaveBeenCalledTimes(mockNotes.length);
    });

    it('handles interactions (zoom)', () => {
        const { getByTitle } = render(<PianoRoll notes={mockNotes} duration={10} />);

        const zoomInBtn = getByTitle('Zoom in');
        fireEvent.click(zoomInBtn);

        // Triggering re-render/re-draw
        expect(mockContext.fillRect).toHaveBeenCalled();
    });

    it('displays zoom level', () => {
        const { getByText } = render(<PianoRoll notes={mockNotes} duration={10} />);
        expect(getByText('100%')).toBeInTheDocument();
    });

    it('draws playhead when playing', () => {
        render(
            <PianoRoll
                notes={mockNotes}
                duration={10}
                isPlaying={true}
                currentTime={5}
            />
        );

        // Should draw playhead line and triangle
        // We look for orange color usage
        expect(mockContext.strokeStyle).toBe('#f97316'); // Playhead color
        // Ideally we inspect call arguments, but checking calls exists is good baseline
        expect(mockContext.stroke).toHaveBeenCalled();
    });
});
