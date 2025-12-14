/**
 * MIDI Export Utility
 *
 * Exports lick data to MIDI files using @tonejs/midi
 */

import * as MidiModule from '@tonejs/midi';
// @ts-ignore - CommonJS module compatibility
const Midi = (MidiModule as any).Midi || (MidiModule as any).default?.Midi || MidiModule;

export interface LickMIDIData {
    name: string;
    midi_notes: number[];
    duration_beats: number;
    tempo?: number; // BPM, default 120
}

/**
 * Convert a lick to a MIDI file and trigger download
 */
export function exportLickToMIDI(lick: LickMIDIData): void {
    try {
        // Create a new MIDI file
        const midi = new Midi();

        // Set tempo (default 120 BPM)
        const tempo = lick.tempo || 120;
        midi.header.setTempo(tempo);

        // Add a track
        const track = midi.addTrack();
        track.name = lick.name;

        // Calculate note duration based on total duration and note count
        const totalDurationSeconds = (lick.duration_beats / tempo) * 60; // Convert beats to seconds
        const noteDuration = totalDurationSeconds / lick.midi_notes.length;

        // Add notes to the track
        let currentTime = 0;
        lick.midi_notes.forEach((midiNote) => {
            track.addNote({
                midi: midiNote,
                time: currentTime,
                duration: noteDuration,
                velocity: 0.8, // 80% velocity
            });
            currentTime += noteDuration;
        });

        // Convert to binary array
        const midiArray = midi.toArray();

        // Create blob and download
        const blob = new Blob([midiArray], { type: 'audio/midi' });
        const url = URL.createObjectURL(blob);

        // Create download link and trigger
        const link = document.createElement('a');
        link.href = url;
        link.download = `${sanitizeFileName(lick.name)}.mid`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Cleanup
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting MIDI:', error);
        throw new Error('Failed to export MIDI file');
    }
}

/**
 * Sanitize filename by removing special characters
 */
function sanitizeFileName(name: string): string {
    return name
        .replace(/[^a-z0-9]/gi, '_')
        .replace(/_+/g, '_')
        .toLowerCase();
}

/**
 * Export multiple licks to a single MIDI file
 */
export function exportLicksToMIDI(licks: LickMIDIData[], fileName: string = 'licks'): void {
    try {
        const midi = new Midi();
        const tempo = licks[0]?.tempo || 120;
        midi.header.setTempo(tempo);

        licks.forEach((lick, index) => {
            const track = midi.addTrack();
            track.name = `${index + 1}. ${lick.name}`;

            const totalDurationSeconds = (lick.duration_beats / tempo) * 60;
            const noteDuration = totalDurationSeconds / lick.midi_notes.length;

            let currentTime = 0;
            lick.midi_notes.forEach((midiNote) => {
                track.addNote({
                    midi: midiNote,
                    time: currentTime,
                    duration: noteDuration,
                    velocity: 0.8,
                });
                currentTime += noteDuration;
            });
        });

        const midiArray = midi.toArray();
        const blob = new Blob([midiArray], { type: 'audio/midi' });
        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = `${sanitizeFileName(fileName)}.mid`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting MIDI:', error);
        throw new Error('Failed to export MIDI file');
    }
}
