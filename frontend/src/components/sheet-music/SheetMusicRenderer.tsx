/**
 * Sheet Music Renderer Component
 * 
 * Renders MIDI notes as sheet music using VexFlow
 */
import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Music, ZoomIn, ZoomOut, RefreshCw } from 'lucide-react';
import type { MidiNote } from '../../hooks/useMidiPlayer';
import { useVexFlow } from '../../hooks/useVexFlow';

interface SheetMusicRendererProps {
    notes: MidiNote[];
    currentTime?: number;
    height?: number;
    showControls?: boolean;
    tempo?: number;
    keySignature?: string;
    timeSignature?: string;
}

export function SheetMusicRenderer({
    notes,
    currentTime = 0,
    height = 200,
    showControls = true,
    tempo = 120,
    keySignature = 'C',
    timeSignature = '4/4',
}: SheetMusicRendererProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [zoom, setZoom] = useState(1);
    const [containerWidth, setContainerWidth] = useState(800);

    // Handle resize
    useEffect(() => {
        const updateWidth = () => {
            if (containerRef.current?.parentElement) {
                setContainerWidth(containerRef.current.parentElement.clientWidth - 48);
            }
        };

        updateWidth();
        window.addEventListener('resize', updateWidth);
        return () => window.removeEventListener('resize', updateWidth);
    }, []);

    // Get notes visible at current time (show a window of notes)
    // Expanded window for sheet music view
    const visibleNotes = notes.filter(note =>
        note.start_time >= currentTime - 1 &&
        note.start_time <= currentTime + 6
    );

    const { render } = useVexFlow(
        containerRef as React.RefObject<HTMLDivElement>,
        visibleNotes,
        {
            width: containerWidth * zoom,
            height: height * zoom,
            showClef: true,
            showTimeSignature: true,
            tempo,
            keySignature,
            timeSignature,
        }
    );

    return (
        <div className="card p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Music className="w-5 h-5 text-violet-400" />
                    Sheet Music
                </h3>

                {showControls && (
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setZoom(z => Math.max(0.5, z - 0.25))}
                            className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
                            title="Zoom Out"
                        >
                            <ZoomOut className="w-4 h-4" />
                        </button>
                        <span className="text-sm text-slate-400 min-w-[4ch] text-center">
                            {Math.round(zoom * 100)}%
                        </span>
                        <button
                            onClick={() => setZoom(z => Math.min(2, z + 0.25))}
                            className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
                            title="Zoom In"
                        >
                            <ZoomIn className="w-4 h-4" />
                        </button>
                        <button
                            onClick={render}
                            className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
                            title="Refresh"
                        >
                            <RefreshCw className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </div>

            {/* Sheet Music Container */}
            <div
                className="overflow-x-auto bg-white rounded-lg"
                style={{ minHeight: height }}
            >
                {notes.length > 0 ? (
                    <motion.div
                        ref={containerRef}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        style={{
                            width: containerWidth * zoom,
                            height: height * zoom,
                        }}
                    />
                ) : (
                    <div
                        className="flex items-center justify-center text-slate-500"
                        style={{ height }}
                    >
                        <div className="text-center">
                            <Music className="w-12 h-12 mx-auto mb-2 text-slate-400" />
                            <p>No notes to display</p>
                            <p className="text-sm text-slate-400">Add notes to see sheet music</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Legend */}
            <div className="mt-4 flex items-center gap-4 text-xs text-slate-500">
                <span>Treble clef: Right hand notes (≥ C4)</span>
                <span>Bass clef: Left hand notes (&lt; C4)</span>
            </div>
        </div>
    );
}
