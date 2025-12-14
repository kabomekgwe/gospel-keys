/**
 * PianoRoll Component
 * 
 * Canvas-based piano roll visualization for displaying MIDI notes
 * Features:
 * - Horizontal timeline with notes as colored rectangles
 * - Piano keyboard on the left side
 * - Zoom in/out controls
 * - Playhead position indicator
 * - Note highlighting during playback
 */
import { useRef, useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ZoomIn, ZoomOut, Maximize2, Minimize2 } from 'lucide-react';

export interface Note {
    id: string;
    pitch: number;       // MIDI pitch (0-127)
    start_time: number;   // In seconds
    end_time: number;    // In seconds
    velocity: number;    // 0-127
    hand?: 'left' | 'right';
}

export interface PianoRollProps {
    notes: Note[];
    duration: number;             // Total duration in seconds
    currentTime?: number;         // Current playhead position
    onNoteClick?: (note: Note) => void;
    onSeek?: (time: number) => void;
    isPlaying?: boolean;
    highlightedNotes?: string[];  // IDs of notes to highlight
    chordRegions?: Array<{
        time: number;
        duration: number;
        chord: string;
        romanNumeral?: string;
    }>;
}

// Piano key mappings
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const BLACK_KEYS = [1, 3, 6, 8, 10]; // Indices in NOTE_NAMES

function isBlackKey(pitch: number): boolean {
    return BLACK_KEYS.includes(pitch % 12);
}

function getNoteName(pitch: number): string {
    const octave = Math.floor(pitch / 12) - 1;
    const name = NOTE_NAMES[pitch % 12];
    return `${name}${octave}`;
}

// Color scheme for notes
function getNoteColor(pitch: number, velocity: number, isHighlighted: boolean, hand?: 'left' | 'right'): string {
    if (isHighlighted) {
        return 'rgba(249, 115, 22, 0.95)'; // Orange when highlighted
    }

    // Color by hand if available
    if (hand === 'left') {
        const alpha = 0.6 + (velocity / 127) * 0.4;
        return `rgba(168, 85, 247, ${alpha})`; // Purple for left hand
    }
    if (hand === 'right') {
        const alpha = 0.6 + (velocity / 127) * 0.4;
        return `rgba(6, 182, 212, ${alpha})`; // Cyan for right hand
    }

    // Default: color by pitch register
    const hue = 180 + ((pitch % 24) * 5); // Cyan to purple gradient
    const alpha = 0.6 + (velocity / 127) * 0.4;
    return `hsla(${hue}, 80%, 55%, ${alpha})`;
}

export function PianoRoll({
    notes,
    duration,
    currentTime = 0,
    onSeek,
    isPlaying = false,
    highlightedNotes = [],
    chordRegions = [],
}: PianoRollProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // View state
    const [zoom, setZoom] = useState(1);
    const [scrollX, setScrollX] = useState(0);
    const [isFullscreen, setIsFullscreen] = useState(false);

    // Constants
    const PIANO_WIDTH = 80;
    const NOTE_HEIGHT = 10;
    const MIN_PITCH = 21;  // A0
    const MAX_PITCH = 108; // C8
    const HEADER_HEIGHT = 30;

    // Calculate visible time range
    const pixelsPerSecond = 100 * zoom;
    const totalWidth = duration * pixelsPerSecond;

    // Draw the piano roll
    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        const container = containerRef.current;
        if (!canvas || !container) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set canvas size
        const dpr = window.devicePixelRatio || 1;
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;
        ctx.scale(dpr, dpr);

        const width = rect.width;
        const height = rect.height;
        const rollWidth = width - PIANO_WIDTH;
        const rollHeight = height - HEADER_HEIGHT;

        // Clear canvas
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, width, height);

        // Draw header (timeline)
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(PIANO_WIDTH, 0, rollWidth, HEADER_HEIGHT);

        // Draw time markers
        ctx.fillStyle = '#64748b';
        ctx.font = '11px Inter, sans-serif';
        const startTime = scrollX / pixelsPerSecond;
        const endTime = startTime + rollWidth / pixelsPerSecond;
        const markerInterval = zoom >= 2 ? 0.5 : zoom >= 1 ? 1 : 2;

        for (let t = Math.floor(startTime / markerInterval) * markerInterval; t <= endTime; t += markerInterval) {
            const x = PIANO_WIDTH + (t - startTime) * pixelsPerSecond;
            if (x >= PIANO_WIDTH && x <= width) {
                ctx.fillText(formatTime(t), x + 4, 18);
                ctx.fillStyle = '#334155';
                ctx.fillRect(x, HEADER_HEIGHT, 1, rollHeight);
                ctx.fillStyle = '#64748b';
            }
        }

        // Draw chord regions
        chordRegions.forEach(region => {
            const regionStart = region.time;
            const regionEnd = region.time + region.duration;

            const x1 = PIANO_WIDTH + (regionStart - startTime) * pixelsPerSecond;
            const x2 = PIANO_WIDTH + (regionEnd - startTime) * pixelsPerSecond;

            if (x2 > PIANO_WIDTH && x1 < width) {
                // Background highlight
                ctx.fillStyle = 'rgba(139, 92, 246, 0.1)';
                ctx.fillRect(Math.max(x1, PIANO_WIDTH), HEADER_HEIGHT - 15, Math.min(x2, width) - Math.max(x1, PIANO_WIDTH), 15);

                // Chord label
                ctx.fillStyle = '#a78bfa';
                ctx.font = 'bold 10px Inter, sans-serif';
                if (x1 >= PIANO_WIDTH) {
                    ctx.fillText(region.chord, x1 + 4, HEADER_HEIGHT - 5);
                }
            }
        });

        // Draw piano keyboard
        for (let pitch = MAX_PITCH; pitch >= MIN_PITCH; pitch--) {
            const y = HEADER_HEIGHT + (MAX_PITCH - pitch) * NOTE_HEIGHT;
            const isBlack = isBlackKey(pitch);

            // Key background
            ctx.fillStyle = isBlack ? '#1e293b' : '#334155';
            ctx.fillRect(0, y, PIANO_WIDTH, NOTE_HEIGHT);

            // Key border
            ctx.strokeStyle = '#0f172a';
            ctx.lineWidth = 1;
            ctx.strokeRect(0, y, PIANO_WIDTH, NOTE_HEIGHT);

            // Note name for C notes
            if (pitch % 12 === 0) {
                ctx.fillStyle = '#94a3b8';
                ctx.font = '9px Inter, sans-serif';
                ctx.fillText(getNoteName(pitch), 4, y + 8);
            }
        }

        // Draw horizontal grid lines
        for (let pitch = MAX_PITCH; pitch >= MIN_PITCH; pitch--) {
            const y = HEADER_HEIGHT + (MAX_PITCH - pitch) * NOTE_HEIGHT;
            const isBlack = isBlackKey(pitch);
            ctx.fillStyle = isBlack ? 'rgba(30, 41, 59, 0.8)' : 'rgba(51, 65, 85, 0.5)';
            ctx.fillRect(PIANO_WIDTH, y, rollWidth, NOTE_HEIGHT);

            // Grid line
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(PIANO_WIDTH, y + NOTE_HEIGHT - 1, rollWidth, 1);
        }

        // Draw notes
        notes.forEach(note => {
            if (note.pitch < MIN_PITCH || note.pitch > MAX_PITCH) return;

            const noteStart = note.start_time;
            const noteDuration = note.end_time - note.start_time;

            const x = PIANO_WIDTH + (noteStart - startTime) * pixelsPerSecond;
            const noteWidth = Math.max(noteDuration * pixelsPerSecond, 2);
            const y = HEADER_HEIGHT + (MAX_PITCH - note.pitch) * NOTE_HEIGHT + 1;
            const noteHeight = NOTE_HEIGHT - 2;

            // Skip notes outside visible area
            if (x + noteWidth < PIANO_WIDTH || x > width) return;

            const isHighlighted = highlightedNotes.includes(note.id);
            const color = getNoteColor(note.pitch, note.velocity, isHighlighted, note.hand);

            // Note rectangle with rounded corners
            ctx.fillStyle = color;
            ctx.beginPath();
            const radius = 2;
            const clippedX = Math.max(x, PIANO_WIDTH);
            const clippedWidth = Math.min(x + noteWidth, width) - clippedX;
            ctx.roundRect(clippedX, y, clippedWidth, noteHeight, radius);
            ctx.fill();

            // Note border for highlighted notes
            if (isHighlighted) {
                ctx.strokeStyle = '#f97316';
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // Note name for longer notes
            if (noteWidth > 30) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                ctx.font = '8px Inter, sans-serif';
                ctx.fillText(getNoteName(note.pitch), clippedX + 3, y + noteHeight - 2);
            }
        });

        // Draw playhead
        const playheadX = PIANO_WIDTH + (currentTime - startTime) * pixelsPerSecond;
        if (playheadX >= PIANO_WIDTH && playheadX <= width) {
            // Playhead line
            ctx.strokeStyle = '#f97316';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(playheadX, HEADER_HEIGHT);
            ctx.lineTo(playheadX, height);
            ctx.stroke();

            // Playhead triangle
            ctx.fillStyle = '#f97316';
            ctx.beginPath();
            ctx.moveTo(playheadX - 6, HEADER_HEIGHT);
            ctx.lineTo(playheadX + 6, HEADER_HEIGHT);
            ctx.lineTo(playheadX, HEADER_HEIGHT + 10);
            ctx.closePath();
            ctx.fill();
        }
    }, [notes, duration, currentTime, zoom, scrollX, highlightedNotes, chordRegions, pixelsPerSecond]);

    // Auto-scroll to follow playhead
    useEffect(() => {
        if (isPlaying && canvasRef.current && containerRef.current) {
            const container = containerRef.current;
            const rollWidth = container.getBoundingClientRect().width - PIANO_WIDTH;
            const playheadPos = currentTime * pixelsPerSecond;

            // Keep playhead in the middle 60% of view
            const viewStart = scrollX;
            const leftBound = viewStart + rollWidth * 0.2;
            const rightBound = viewStart + rollWidth * 0.8;

            if (playheadPos < leftBound) {
                setScrollX(Math.max(0, playheadPos - rollWidth * 0.2));
            } else if (playheadPos > rightBound) {
                setScrollX(Math.min(totalWidth - rollWidth, playheadPos - rollWidth * 0.5));
            }
        }
    }, [currentTime, isPlaying, scrollX, pixelsPerSecond, totalWidth]);

    // Redraw on state changes
    useEffect(() => {
        draw();
    }, [draw]);

    // Handle resize
    useEffect(() => {
        const handleResize = () => draw();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [draw]);

    // Handle click/seek
    const handleCanvasClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (!canvas || !onSeek) return;

        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;

        if (x > PIANO_WIDTH) {
            const startTime = scrollX / pixelsPerSecond;
            const time = startTime + (x - PIANO_WIDTH) / pixelsPerSecond;
            onSeek(Math.max(0, Math.min(time, duration)));
        }
    }, [scrollX, pixelsPerSecond, duration, onSeek]);

    // Handle scroll
    const handleWheel = useCallback((e: React.WheelEvent) => {
        e.preventDefault();

        if (e.ctrlKey || e.metaKey) {
            // Zoom
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            setZoom(prev => Math.max(0.25, Math.min(4, prev * delta)));
        } else {
            // Horizontal scroll
            setScrollX(prev => {
                const container = containerRef.current;
                if (!container) return prev;
                const rollWidth = container.getBoundingClientRect().width - PIANO_WIDTH;
                const maxScroll = Math.max(0, totalWidth - rollWidth);
                return Math.max(0, Math.min(maxScroll, prev + e.deltaX + e.deltaY));
            });
        }
    }, [totalWidth]);

    // Toggle fullscreen
    const toggleFullscreen = useCallback(async () => {
        const container = containerRef.current;
        if (!container) return;

        if (!isFullscreen) {
            await container.requestFullscreen?.();
            setIsFullscreen(true);
        } else {
            await document.exitFullscreen?.();
            setIsFullscreen(false);
        }
    }, [isFullscreen]);

    return (
        <motion.div
            ref={containerRef}
            className="relative w-full h-full min-h-[400px] bg-slate-900 rounded-xl overflow-hidden border border-slate-700/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        >
            {/* Canvas */}
            <canvas
                ref={canvasRef}
                className="w-full h-full cursor-crosshair"
                onClick={handleCanvasClick}
                onWheel={handleWheel}
            />

            {/* Controls overlay */}
            <div className="absolute top-4 right-4 flex items-center gap-2">
                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setZoom(prev => Math.min(4, prev * 1.2))}
                    className="p-2 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-700/80 transition-colors"
                    title="Zoom in"
                >
                    <ZoomIn className="w-4 h-4" />
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setZoom(prev => Math.max(0.25, prev / 1.2))}
                    className="p-2 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-700/80 transition-colors"
                    title="Zoom out"
                >
                    <ZoomOut className="w-4 h-4" />
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={toggleFullscreen}
                    className="p-2 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-700/80 transition-colors"
                    title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
                >
                    {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                </motion.button>
            </div>

            {/* Zoom indicator */}
            <div className="absolute bottom-4 right-4 px-3 py-1.5 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700/50 text-xs text-slate-400">
                {Math.round(zoom * 100)}%
            </div>

            {/* Legend */}
            <div className="absolute bottom-4 left-[90px] flex items-center gap-4 px-3 py-1.5 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700/50 text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded bg-cyan-500/80" />
                    Right hand
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded bg-violet-500/80" />
                    Left hand
                </span>
            </div>
        </motion.div>
    );
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}
