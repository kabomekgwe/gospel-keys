/**
 * Sheet Music Renderer Hook
 * 
 * Convert MIDI notes to VexFlow notation
 */
import { useRef, useEffect, useCallback } from 'react';
import {
    Renderer,
    Stave,
    StaveNote,
    Voice,
    Formatter,
    Accidental,
} from 'vexflow';
import type { MidiNote } from './useMidiPlayer';

interface UseVexFlowOptions {
    width?: number;
    height?: number;
    showClef?: boolean;
    showTimeSignature?: boolean;
    notesPerMeasure?: number;
}

const NOTE_NAMES = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b'];

function midiToVexFlowKey(midi: number): { key: string; accidental: string | null } {
    const octave = Math.floor(midi / 12) - 1;
    const noteIndex = midi % 12;
    const noteName = NOTE_NAMES[noteIndex];

    // VexFlow uses format like "c/4", "c#/4"
    const hasAccidental = noteName.includes('#');
    const baseNote = noteName.replace('#', '');

    return {
        key: `${baseNote}/${octave}`,
        accidental: hasAccidental ? '#' : null,
    };
}

export function useVexFlow(
    containerRef: React.RefObject<HTMLDivElement>,
    notes: MidiNote[],
    options: UseVexFlowOptions = {}
) {
    const rendererRef = useRef<Renderer | null>(null);
    const {
        width = 800,
        height = 200,
        showClef = true,
        showTimeSignature = true,
        notesPerMeasure = 4,
    } = options;

    const renderNotation = useCallback(() => {
        if (!containerRef.current) return;

        // Clear previous content
        containerRef.current.innerHTML = '';

        // Create renderer
        const renderer = new Renderer(containerRef.current, Renderer.Backends.SVG);
        renderer.resize(width, height);
        rendererRef.current = renderer;

        const context = renderer.getContext();
        context.setFont('Arial', 10);

        if (notes.length === 0) {
            // Draw empty stave
            const stave = new Stave(10, 40, width - 20);
            if (showClef) stave.addClef('treble');
            if (showTimeSignature) stave.addTimeSignature('4/4');
            stave.setContext(context).draw();
            return;
        }

        // Sort notes by start time
        const sortedNotes = [...notes].sort((a, b) => a.startTime - b.startTime);

        // Group notes by time (for chords)
        const noteGroups: MidiNote[][] = [];
        let currentGroup: MidiNote[] = [];
        let lastTime = -1;

        sortedNotes.forEach(note => {
            if (Math.abs(note.startTime - lastTime) < 0.05) {
                // Same time - part of chord
                currentGroup.push(note);
            } else {
                // New beat
                if (currentGroup.length > 0) {
                    noteGroups.push(currentGroup);
                }
                currentGroup = [note];
                lastTime = note.startTime;
            }
        });
        if (currentGroup.length > 0) {
            noteGroups.push(currentGroup);
        }

        // Split into treble and bass
        const trebleNotes = noteGroups.filter(group =>
            group.some(n => n.pitch >= 60) // Middle C and above
        ).slice(0, notesPerMeasure * 2);

        const bassNotes = noteGroups.filter(group =>
            group.some(n => n.pitch < 60)
        ).slice(0, notesPerMeasure * 2);

        // Draw treble stave
        const trebleStave = new Stave(10, 20, width - 20);
        if (showClef) trebleStave.addClef('treble');
        if (showTimeSignature) trebleStave.addTimeSignature('4/4');
        trebleStave.setContext(context).draw();

        // Draw bass stave
        const bassStave = new Stave(10, 100, width - 20);
        if (showClef) bassStave.addClef('bass');
        if (showTimeSignature) bassStave.addTimeSignature('4/4');
        bassStave.setContext(context).draw();

        // Create treble voice
        if (trebleNotes.length > 0) {
            const trebleVexNotes = trebleNotes.map(group => {
                const keys = group
                    .filter(n => n.pitch >= 60)
                    .map(n => midiToVexFlowKey(n.pitch));

                if (keys.length === 0) return null;

                const note = new StaveNote({
                    keys: keys.map(k => k.key),
                    duration: 'q',
                    clef: 'treble',
                });

                // Add accidentals
                keys.forEach((k, i) => {
                    if (k.accidental) {
                        note.addModifier(new Accidental(k.accidental), i);
                    }
                });

                return note;
            }).filter((n): n is StaveNote => n !== null);

            if (trebleVexNotes.length > 0) {
                // Pad with rests if needed
                while (trebleVexNotes.length < notesPerMeasure) {
                    trebleVexNotes.push(new StaveNote({
                        keys: ['b/4'],
                        duration: 'qr',
                    }));
                }

                const trebleVoice = new Voice({ numBeats: notesPerMeasure, beatValue: 4 });
                trebleVoice.addTickables(trebleVexNotes.slice(0, notesPerMeasure));

                new Formatter().joinVoices([trebleVoice]).format([trebleVoice], width - 60);
                trebleVoice.draw(context, trebleStave);
            }
        }

        // Create bass voice
        if (bassNotes.length > 0) {
            const bassVexNotes = bassNotes.map(group => {
                const keys = group
                    .filter(n => n.pitch < 60)
                    .map(n => midiToVexFlowKey(n.pitch));

                if (keys.length === 0) return null;

                const note = new StaveNote({
                    keys: keys.map(k => k.key),
                    duration: 'q',
                    clef: 'bass',
                });

                keys.forEach((k, i) => {
                    if (k.accidental) {
                        note.addModifier(new Accidental(k.accidental), i);
                    }
                });

                return note;
            }).filter((n): n is StaveNote => n !== null);

            if (bassVexNotes.length > 0) {
                while (bassVexNotes.length < notesPerMeasure) {
                    bassVexNotes.push(new StaveNote({
                        keys: ['d/3'],
                        duration: 'qr',
                        clef: 'bass',
                    }));
                }

                const bassVoice = new Voice({ numBeats: notesPerMeasure, beatValue: 4 });
                bassVoice.addTickables(bassVexNotes.slice(0, notesPerMeasure));

                new Formatter().joinVoices([bassVoice]).format([bassVoice], width - 60);
                bassVoice.draw(context, bassStave);
            }
        }
    }, [notes, width, height, showClef, showTimeSignature, notesPerMeasure, containerRef]);

    useEffect(() => {
        renderNotation();
    }, [renderNotation]);

    return {
        render: renderNotation,
    };
}
