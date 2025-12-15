import { VoicingInfo as APIVoicingInfo } from '../../lib/api';
import { VoicingInfo as VoicingAnalysisInfo } from '../../../components/analysis/VoicingVisualizer';

/**
 * Convert API VoicingInfo to VoicingAnalysisInfo for VoicingVisualizer
 */
export function convertToVoicingAnalysisInfo(
    voicing: APIVoicingInfo,
    chordSymbol: string
): VoicingAnalysisInfo {
    // Determine voicing type from name (basic heuristic)
    let voicingType = 'close';
    const nameLower = voicing.name.toLowerCase();
    if (nameLower.includes('drop')) voicingType = nameLower.includes('drop-2') || nameLower.includes('drop 2') ? 'drop_2' : 'drop_3';
    else if (nameLower.includes('open')) voicingType = 'open';
    else if (nameLower.includes('rootless')) voicingType = 'rootless';
    else if (nameLower.includes('shell')) voicingType = 'shell';
    else if (nameLower.includes('spread')) voicingType = 'spread';

    // Calculate intervals between consecutive notes
    const intervals: number[] = [];
    for (let i = 1; i < voicing.midi_notes.length; i++) {
        intervals.push(voicing.midi_notes[i] - voicing.midi_notes[i - 1]);
    }

    // Calculate width
    const widthSemitones = voicing.midi_notes.length > 0
        ? voicing.midi_notes[voicing.midi_notes.length - 1] - voicing.midi_notes[0]
        : 0;

    // Simple complexity score (0-1) based on number of notes and width
    const complexityScore = Math.min(
        1.0,
        (voicing.midi_notes.length / 7 + widthSemitones / 24) / 2
    );

    // Estimate hand span in inches (rough approximation: 1 semitone ≈ 0.65")
    const handSpanInches = widthSemitones * 0.65;

    // Basic chord tone detection (simplified)
    const noteSet = new Set(voicing.midi_notes.map(n => n % 12));
    const rootNote = chordSymbol.match(/^([A-G][#b]?)/)?.[1] || 'C';
    const noteMap: Record<string, number> = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
        'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
    };
    const rootPitchClass = noteMap[rootNote] || 0;

    return {
        chord_symbol: chordSymbol,
        voicing_type: voicingType,
        notes: voicing.midi_notes,
        note_names: voicing.notes,
        intervals,
        width_semitones: widthSemitones,
        inversion: 0, // Would need more analysis to determine
        has_root: noteSet.has(rootPitchClass),
        has_third: noteSet.has((rootPitchClass + 3) % 12) || noteSet.has((rootPitchClass + 4) % 12),
        has_seventh: noteSet.has((rootPitchClass + 10) % 12) || noteSet.has((rootPitchClass + 11) % 12),
        extensions: [],
        complexity_score: complexityScore,
        hand_span_inches: handSpanInches,
    };
}
