/**
 * Lick Notation Component
 *
 * Renders a lick as sheet music using VexFlow
 */

import { useEffect, useRef } from 'react';
import { Renderer, Stave, StaveNote, Formatter, Accidental, Voice } from 'vexflow';

interface LickNotationProps {
    midiNotes: number[];
    durationBeats: number;
}

// MIDI note number to VexFlow note name mapping
const midiToVexNote = (midi: number): { note: string; accidental: string | null } => {
    const notes = ['c', 'c', 'd', 'd', 'e', 'f', 'f', 'g', 'g', 'a', 'a', 'b'];
    const accidentals = [null, '#', null, '#', null, null, '#', null, '#', null, '#', null];

    const octave = Math.floor(midi / 12) - 1;
    const noteIndex = midi % 12;

    return {
        note: `${notes[noteIndex]}/${octave}`,
        accidental: accidentals[noteIndex],
    };
};

// Calculate note duration based on beats and note count
const calculateDuration = (totalBeats: number, noteCount: number): string => {
    const beatsPerNote = totalBeats / noteCount;

    if (beatsPerNote >= 4) return 'w'; // whole note
    if (beatsPerNote >= 2) return 'h'; // half note
    if (beatsPerNote >= 1) return 'q'; // quarter note
    if (beatsPerNote >= 0.5) return '8'; // eighth note
    return '16'; // sixteenth note
};

export function LickNotation({ midiNotes, durationBeats }: LickNotationProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!containerRef.current) return;

        // Clear previous render
        containerRef.current.innerHTML = '';

        try {
            // Create renderer
            const renderer = new Renderer(
                containerRef.current,
                Renderer.Backends.SVG
            );

            // Calculate size based on note count
            const width = Math.max(400, midiNotes.length * 40 + 100);
            const height = 150;

            renderer.resize(width, height);
            const context = renderer.getContext();

            // Create stave (staff)
            const stave = new Stave(10, 20, width - 20);
            stave.addClef('treble').setContext(context).draw();

            // Calculate note duration
            const duration = calculateDuration(durationBeats, midiNotes.length);

            // Create notes
            const notes: StaveNote[] = midiNotes.map((midi) => {
                const { note, accidental } = midiToVexNote(midi);

                const staveNote = new StaveNote({
                    keys: [note],
                    duration: duration,
                });

                // Add accidental if needed
                if (accidental) {
                    staveNote.addModifier(new Accidental(accidental), 0);
                }

                return staveNote;
            });

            // Create voice and add notes
            const voice = new Voice({ num_beats: durationBeats, beat_value: 4 });
            voice.addTickables(notes);

            // Format and justify the notes to fit within the stave
            new Formatter().joinVoices([voice]).format([voice], width - 40);

            // Render voice
            voice.draw(context, stave);
        } catch (error) {
            console.error('Error rendering notation:', error);
            // Show error message in the container
            if (containerRef.current) {
                containerRef.current.innerHTML = `
                    <div style="padding: 20px; text-align: center; color: #94a3b8; font-size: 12px;">
                        Unable to render sheet music
                    </div>
                `;
            }
        }
    }, [midiNotes, durationBeats]);

    return (
        <div
            ref={containerRef}
            className="notation-container bg-white rounded-lg p-2 overflow-x-auto"
            style={{ minHeight: '150px' }}
        />
    );
}
