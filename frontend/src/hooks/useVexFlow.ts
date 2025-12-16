/**
 * Sheet Music Renderer Hook
 * 
 * Convert MIDI notes to VexFlow notation with accurate rhythm and key signature support
 */
import { useRef, useEffect, useCallback } from 'react';
import {
    Renderer,
    Stave,
    StaveNote,
    Voice,
    Formatter,
    Accidental,
    Beam,
    Dot
} from 'vexflow';
import type { MidiNote } from './useMidiPlayer';

interface UseVexFlowOptions {
    width?: number;
    height?: number;
    showClef?: boolean;
    showTimeSignature?: boolean;
    notesPerMeasure?: number; // fallback if timeSignature not provided
    tempo?: number;
    keySignature?: string;
    timeSignature?: string;
}

// Map MIDI duration (seconds) to VexFlow duration codes
// standard quarters at 120bpm = 0.5s
function quantizeDuration(durationSeconds: number, bpm: number): { duration: string; dots: number } {
    const beatDuration = 60 / bpm; // duration of a quarter note
    const numBeats = durationSeconds / beatDuration;

    // Round to nearest common duration
    // 4 = whole, 2 = half, 1 = quarter, 0.5 = 8th, 0.25 = 16th
    const targetBeats = [4, 3, 2, 1.5, 1, 0.75, 0.5, 0.25];
    const bestBeat = targetBeats.reduce((prev, curr) =>
        Math.abs(curr - numBeats) < Math.abs(prev - numBeats) ? curr : prev
    );

    // Map beats to VexFlow duration
    switch (bestBeat) {
        case 4: return { duration: 'w', dots: 0 };
        case 3: return { duration: 'h', dots: 1 };
        case 2: return { duration: 'h', dots: 0 };
        case 1.5: return { duration: 'q', dots: 1 };
        case 1: return { duration: 'q', dots: 0 };
        case 0.75: return { duration: '8', dots: 1 };
        case 0.5: return { duration: '8', dots: 0 };
        case 0.25: return { duration: '16', dots: 0 };
        default: return { duration: 'q', dots: 0 };
    }
}

// Convert MIDI pitch to VexFlow key string (e.g. "c/4")
// Note: VexFlow handles accidentals automatically if we don't force them, 
// but we need to specify them if they deviate from the key signature.
// For now, we will return the "spelled" version and let VexFlow + KeySignature logic handle it.
const NOTE_NAMES = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b'];

function midiToVexFlowKey(midi: number): { key: string; noteIndex: number } {
    const octave = Math.floor(midi / 12) - 1;
    const noteIndex = midi % 12;
    const noteName = NOTE_NAMES[noteIndex];

    // Simplification: We blindly map to sharps for now. 
    // True key-aware spelling (e.g. Bb vs A#) requires more complex logic or a library like tonal.
    // VexFlow's KeyManager can help if we use it, but for now we retain basic mapping.

    return {
        key: `${noteName}/${octave}`,
        noteIndex
    };
}

function normalizeKeySignature(key: string): string {
    if (!key) return 'C';

    // Handle "Major" (remove it)
    let normalized = key.replace(/\s*major/i, '');

    // Handle "Minor" (replace with 'm')
    normalized = normalized.replace(/\s*minor/i, 'm');

    // Ensure proper casing (first letter uppercase)
    normalized = normalized.charAt(0).toUpperCase() + normalized.slice(1);

    return normalized.trim();
}

export function useVexFlow(
    containerRef: React.RefObject<HTMLDivElement>,
    notes: MidiNote[],
    options: UseVexFlowOptions = {}
) {
    const rendererRef = useRef<InstanceType<typeof Renderer> | null>(null);
    const {
        width = 800,
        height = 200,
        showClef = true,
        showTimeSignature = true,
        tempo = 120, // BPM
        keySignature = 'C',
        timeSignature = '4/4',
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
            if (showTimeSignature) stave.addTimeSignature(timeSignature);
            stave.addKeySignature(keySignature);
            stave.setContext(context).draw();
            return;
        }

        // 1. Group notes by time (chords)
        // Sort notes by start time
        const sortedNotes = [...notes].sort((a, b) => a.start_time - b.start_time);

        // Group by rough timestamp tolerance
        const chords: { time: number; notes: MidiNote[] }[] = [];
        let currentChord: MidiNote[] = [];
        let lastTime = -1;

        sortedNotes.forEach(note => {
            if (lastTime === -1) {
                currentChord.push(note);
                lastTime = note.start_time;
            } else if (Math.abs(note.start_time - lastTime) < 0.05) {
                currentChord.push(note);
            } else {
                if (currentChord.length > 0) {
                    chords.push({ time: lastTime, notes: currentChord });
                }
                currentChord = [note];
                lastTime = note.start_time;
            }
        });
        if (currentChord.length > 0) {
            chords.push({ time: lastTime, notes: currentChord });
        }

        // 2. Separate into Treble vs Bass voices based on 'hand' property
        // We will construct measures. For this simple view, we might just fill one long stave 
        // or a few measures properly. 
        // For the "scrolling window" view, we treat it as one continuous stream, 
        // but VexFlow needs Voice/Formatter to space things out.

        const trebleStaveNotes: InstanceType<typeof StaveNote>[] = [];
        const bassStaveNotes: InstanceType<typeof StaveNote>[] = [];

        // We iterate through chords and assign to staves
        chords.forEach(chord => {
            const trebleNotes = chord.notes.filter(n => n.hand === 'right' || (n.hand === undefined && n.pitch >= 60));
            const bassNotes = chord.notes.filter(n => n.hand === 'left' || (n.hand === undefined && n.pitch < 60));

            // Determine Duration
            // We use the first note's duration as the chord duration
            const firstNote = chord.notes[0];
            const durationSec = firstNote ? (firstNote.end_time - firstNote.start_time) : 0.5;
            const { duration, dots } = quantizeDuration(durationSec, tempo);

            if (trebleNotes.length > 0) {
                const keys = trebleNotes.map(n => midiToVexFlowKey(n.pitch).key);
                const vfNote = new StaveNote({
                    keys,
                    duration,
                    clef: 'treble',
                    autoStem: true,
                });

                if (dots > 0) {
                    for (let j = 0; j < keys.length; j++) {
                        vfNote.addModifier(new Dot(), j);
                    }
                }

                // Add accidentals if needed (naive approach: add for all sharps/flats for now, 
                // typically we'd check against key signature history)
                trebleNotes.forEach((n, i) => {
                    const { noteIndex } = midiToVexFlowKey(n.pitch);
                    // This is still slightly naive; ideally we use KeyManager.
                    // But VexFlow's StaveNote doesn't auto-add accidentals unless we tell it.
                    // We can check if the key signature *doesn't* have this note.
                    // Simplification: Always add '#' if key contains '#'
                    if (NOTE_NAMES[noteIndex].includes('#')) {
                        vfNote.addModifier(new Accidental('#'), i);
                    }
                });

                trebleStaveNotes.push(vfNote);
            } else {
                // Add rest for alignment if bass has note? 
                // For now, the visualizer might just skip silence in one hand to avoid clutter,
                // or we should add a Rest. Let's try adding invisible rests or correct rests later.
                // Ideally we sync voices. Simple approach: Add rest matched to the other hand's duration.
                if (bassNotes.length > 0) {
                    const vfRest = new StaveNote({ keys: ['b/4'], duration: duration + 'r', clef: 'treble' });
                    if (dots > 0) vfRest.addModifier(new Dot(), 0);
                    trebleStaveNotes.push(vfRest);
                }
            }

            if (bassNotes.length > 0) {
                const keys = bassNotes.map(n => midiToVexFlowKey(n.pitch).key);
                const vfNote = new StaveNote({
                    keys,
                    duration,
                    clef: 'bass',
                    autoStem: true,
                });
                if (dots > 0) {
                    for (let j = 0; j < keys.length; j++) {
                        vfNote.addModifier(new Dot(), j);
                    }
                }

                bassNotes.forEach((n, i) => {
                    const { noteIndex } = midiToVexFlowKey(n.pitch);
                    if (NOTE_NAMES[noteIndex].includes('#')) {
                        vfNote.addModifier(new Accidental('#'), i);
                    }
                });

                bassStaveNotes.push(vfNote);
            } else {
                if (trebleNotes.length > 0) {
                    const vfRest = new StaveNote({ keys: ['d/3'], duration: duration + 'r', clef: 'bass' });
                    if (dots > 0) vfRest.addModifier(new Dot(), 0);
                    bassStaveNotes.push(vfRest);
                }
            }
        });

        // Setup Staves
        const validKeySignature = normalizeKeySignature(keySignature);
        const trebleStave = new Stave(10, 20, width - 20);
        if (showClef) trebleStave.addClef('treble');
        if (showTimeSignature) trebleStave.addTimeSignature(timeSignature);
        trebleStave.addKeySignature(validKeySignature);
        trebleStave.setContext(context).draw();

        const bassStave = new Stave(10, 100, width - 20); // Spacing
        if (showClef) bassStave.addClef('bass');
        if (showTimeSignature) bassStave.addTimeSignature(timeSignature);
        bassStave.addKeySignature(validKeySignature);
        bassStave.setContext(context).draw();

        // Format and Draw Voices
        const voices = [];

        if (trebleStaveNotes.length > 0) {
            // We arbitrarily claim '4/4' capacity but turn off strict timing mode 
            // because we are just showing a window of notes, not strictly measure-delimited yet.
            // VexFlow logic: Just format what fits in width.
            const trebleVoice = new Voice({ numBeats: 4, beatValue: 4 });
            trebleVoice.setStrict(false); // Valid for "streaming" or non-measure-bound views
            trebleVoice.addTickables(trebleStaveNotes);
            voices.push(trebleVoice);
        }

        if (bassStaveNotes.length > 0) {
            const bassVoice = new Voice({ numBeats: 4, beatValue: 4 });
            bassVoice.setStrict(false);
            bassVoice.addTickables(bassStaveNotes);
            voices.push(bassVoice);
        }

        if (voices.length > 0) {
            const formatter = new Formatter();
            formatter.joinVoices(voices).format(voices, width - 60);

            if (trebleStaveNotes.length > 0) {
                voices[0].draw(context, trebleStave);
                // Optional: Auto-beam
                const beams = Beam.generateBeams(trebleStaveNotes);
                beams.forEach((b: InstanceType<typeof Beam>) => b.setContext(context).draw());
            }

            if (bassStaveNotes.length > 0) {
                // If we have both, bass is second
                const voiceIndex = trebleStaveNotes.length > 0 ? 1 : 0;
                voices[voiceIndex].draw(context, bassStave);
                const beams = Beam.generateBeams(bassStaveNotes);
                beams.forEach((b: InstanceType<typeof Beam>) => b.setContext(context).draw());
            }
        }

    }, [notes, width, height, showClef, showTimeSignature, tempo, keySignature, timeSignature, containerRef]);

    useEffect(() => {
        renderNotation();
    }, [renderNotation]);

    return {
        render: renderNotation,
    };
}
