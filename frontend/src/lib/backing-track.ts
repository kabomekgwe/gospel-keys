/**
 * Backing Track Generation for Jazz Licks
 * Generates style-appropriate chord accompaniment patterns
 */

export interface BackingTrackNote {
  midi: number;
  time: number; // in beats
  duration: number; // in beats
}

export interface BackingTrackPattern {
  notes: BackingTrackNote[];
  totalBeats: number;
}

/**
 * Style-specific rhythm patterns (in beats)
 * Each number represents when a chord hit occurs
 */
const RHYTHM_PATTERNS: Record<string, number[]> = {
  bebop: [0, 2], // Beats 1 and 3 (swing feel)
  blues: [0, 1, 2, 3], // All four beats (blues shuffle)
  modern: [0, 1.5, 3], // Syncopated pattern
  gospel: [0, 1.5, 2, 3.5], // Gospel groove with anticipations
  swing: [0, 2], // Beats 1 and 3 (classic swing)
  bossa: [0, 1, 2.5, 3], // Bossa nova pattern
};

/**
 * Parse chord symbol to extract root and quality
 */
function parseChord(chordSymbol: string): { root: string; quality: string } {
  // Remove whitespace
  const clean = chordSymbol.trim();

  // Extract root note (handles sharps/flats)
  const rootMatch = clean.match(/^([A-G][#b]?)/);
  if (!rootMatch) {
    throw new Error(`Invalid chord symbol: ${chordSymbol}`);
  }

  const root = rootMatch[1];
  const quality = clean.substring(root.length);

  return { root, quality };
}

/**
 * Convert note name to MIDI number
 */
function noteToMidi(noteName: string, octave: number = 3): number {
  const noteMap: Record<string, number> = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11,
  };

  const pitch = noteMap[noteName];
  if (pitch === undefined) {
    throw new Error(`Invalid note name: ${noteName}`);
  }

  return 12 * (octave + 1) + pitch;
}

/**
 * Get chord intervals based on quality
 */
function getChordIntervals(quality: string): number[] {
  // Simplified voicing: root, third, seventh (shell voicing)
  const qualityLower = quality.toLowerCase();

  if (qualityLower.includes('maj7') || qualityLower === 'maj' || qualityLower === 'Δ') {
    return [0, 4, 11]; // Root, major 3rd, major 7th
  } else if (qualityLower.includes('m7') || qualityLower.includes('min7')) {
    return [0, 3, 10]; // Root, minor 3rd, minor 7th
  } else if (qualityLower.includes('7')) {
    return [0, 4, 10]; // Root, major 3rd, minor 7th (dominant)
  } else if (qualityLower.includes('m') || qualityLower.includes('min')) {
    return [0, 3, 7]; // Root, minor 3rd, perfect 5th
  } else if (qualityLower.includes('dim')) {
    return [0, 3, 6]; // Root, minor 3rd, diminished 5th
  } else if (qualityLower.includes('aug')) {
    return [0, 4, 8]; // Root, major 3rd, augmented 5th
  } else {
    // Default to major triad
    return [0, 4, 7]; // Root, major 3rd, perfect 5th
  }
}

/**
 * Generate chord voicing MIDI notes
 */
function getChordVoicing(chordSymbol: string, octave: number = 3): number[] {
  const { root, quality } = parseChord(chordSymbol);
  const rootMidi = noteToMidi(root, octave);
  const intervals = getChordIntervals(quality);

  return intervals.map(interval => rootMidi + interval);
}

/**
 * Generate backing track for a chord or progression
 * @param context - Single chord symbol or space-separated progression
 * @param style - Jazz style (bebop, blues, modern, gospel, swing, bossa)
 * @param lengthBars - Number of bars to generate
 * @returns Backing track pattern with MIDI notes and timing
 */
export function generateBackingTrack(
  context: string,
  style: string,
  lengthBars: number = 2
): BackingTrackPattern {
  const chords = context.split(/\s+/).filter(c => c.length > 0);
  const rhythmPattern = RHYTHM_PATTERNS[style] || RHYTHM_PATTERNS.swing;
  const beatsPerBar = 4;
  const totalBeats = lengthBars * beatsPerBar;

  const notes: BackingTrackNote[] = [];

  if (chords.length === 1) {
    // Single chord - repeat pattern throughout
    const chordVoicing = getChordVoicing(chords[0]);

    for (let bar = 0; bar < lengthBars; bar++) {
      for (const beat of rhythmPattern) {
        const time = bar * beatsPerBar + beat;

        // Add each note of the chord voicing
        for (const midi of chordVoicing) {
          notes.push({
            midi,
            time,
            duration: 0.5, // Short stab
          });
        }
      }
    }
  } else {
    // Chord progression - distribute chords evenly across bars
    const beatsPerChord = totalBeats / chords.length;

    chords.forEach((chord, chordIndex) => {
      const chordVoicing = getChordVoicing(chord);
      const chordStartTime = chordIndex * beatsPerChord;
      const chordEndTime = chordStartTime + beatsPerChord;

      // Apply rhythm pattern within each chord's duration
      for (const beat of rhythmPattern) {
        const time = chordStartTime + (beat % beatsPerChord);

        // Only add if within chord duration
        if (time < chordEndTime) {
          for (const midi of chordVoicing) {
            notes.push({
              midi,
              time,
              duration: 0.5,
            });
          }
        }
      }
    });
  }

  // Sort by time
  notes.sort((a, b) => a.time - b.time);

  return {
    notes,
    totalBeats,
  };
}
