/**
 * Voicing Visualizer Component
 *
 * Displays how a chord is voiced on piano with detailed metadata
 * Features:
 * - Color-coded piano keyboard (root, 3rd, 5th, 7th, extensions)
 * - Voicing metadata (type, complexity, hand span, inversion)
 * - Audio playback integration (Phase 4)
 * - Responsive modes (full vs compact)
 */

import { useMemo } from 'react';
import { PianoKeyboard } from '../music';
import { Play, Music2 } from 'lucide-react';
import { useChordPlayback } from '../../hooks/useChordPlayback';

export interface VoicingInfo {
  chord_symbol: string;
  voicing_type: string;
  notes: number[];          // MIDI note numbers
  note_names: string[];     // e.g., ["C3", "E3", "G3", "B3"]
  intervals: number[];      // Intervals between consecutive notes
  width_semitones: number;
  inversion: number;
  has_root: boolean;
  has_third: boolean;
  has_seventh: boolean;
  extensions: string[];     // e.g., ["9", "11", "13"]
  complexity_score: number; // 0-1
  hand_span_inches: number;
}

export interface VoicingVisualizerProps {
  /** Chord symbol (e.g., "Cmaj7") */
  chord: string;
  /** Voicing analysis data */
  voicing: VoicingInfo;
  /** Callback when a note is played (Phase 4) */
  onNotePlay?: (midiNote: number) => void;
  /** Show detailed metadata panel */
  showDetails?: boolean;
  /** Compact mode for Generator/Practice */
  compact?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// Color mapping for chord tones
const CHORD_TONE_COLORS = {
  root: 'cyan',
  third: 'emerald',
  fifth: 'slate',
  seventh: 'violet',
  extension: 'amber',
} as const;

// Voicing type display names
const VOICING_TYPE_NAMES: Record<string, string> = {
  close: 'Close',
  open: 'Open',
  drop_2: 'Drop-2',
  drop_3: 'Drop-3',
  drop_2_4: 'Drop-2-4',
  rootless: 'Rootless',
  shell: 'Shell',
  spread: 'Spread',
  quartal: 'Quartal',
  cluster: 'Cluster',
};

/**
 * Get color for a note based on its chord tone function
 */
function getNoteColor(
  pitch: number,
  rootPitch: number,
  voicing: VoicingInfo
): string | undefined {
  const pitchClass = pitch % 12;
  const rootClass = rootPitch % 12;
  const interval = (pitchClass - rootClass + 12) % 12;

  // Root
  if (interval === 0) return CHORD_TONE_COLORS.root;

  // 3rd (minor or major)
  if (interval === 3 || interval === 4) return CHORD_TONE_COLORS.third;

  // 5th
  if (interval === 7) return CHORD_TONE_COLORS.fifth;

  // 7th (minor or major)
  if (interval === 10 || interval === 11) return CHORD_TONE_COLORS.seventh;

  // Extensions (9, 11, 13, altered)
  if ([1, 2, 5, 6, 9].includes(interval)) return CHORD_TONE_COLORS.extension;

  return undefined;
}

/**
 * Get root pitch from chord symbol
 */
function getRootPitch(chordSymbol: string): number {
  const noteMap: Record<string, number> = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
  };

  // Extract root note (first 1-2 characters)
  const root = chordSymbol.match(/^([A-G][#b]?)/)?.[1];
  return root ? noteMap[root] + 60 : 60; // Default to C4
}

/**
 * Render complexity stars (1-5)
 */
function ComplexityStars({ score }: { score: number }) {
  const stars = Math.round(score * 5);
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <span
          key={i}
          className={`text-sm ${
            i < stars ? 'text-amber-400' : 'text-slate-700'
          }`}
        >
          ★
        </span>
      ))}
    </div>
  );
}

/**
 * Render hand span indicator with color coding
 */
function HandSpanIndicator({ span }: { span: number }) {
  const color =
    span < 9 ? 'text-emerald-500' :
    span < 12 ? 'text-amber-500' :
    'text-rose-500';

  return (
    <span className={`font-semibold ${color}`}>
      {span.toFixed(1)}"
    </span>
  );
}

export function VoicingVisualizer({
  chord,
  voicing,
  onNotePlay,
  showDetails = true,
  compact = false,
  className = '',
}: VoicingVisualizerProps) {
  // Audio playback hook
  const { playChord, playArpeggio, isPlaying } = useChordPlayback({
    instrument: 'piano',
    duration: 1.0,
  });

  // Calculate note colors based on chord tones
  const noteColors = useMemo(() => {
    const colors = new Map<number, string>();
    const rootPitch = getRootPitch(voicing.chord_symbol);

    voicing.notes.forEach((pitch) => {
      const color = getNoteColor(pitch, rootPitch, voicing);
      if (color) colors.set(pitch, color);
    });

    return colors;
  }, [voicing]);

  // Calculate piano range (show a bit more context around the voicing)
  const minPitch = Math.max(21, Math.min(...voicing.notes) - 6);
  const maxPitch = Math.min(108, Math.max(...voicing.notes) + 6);

  // Voicing type display name
  const voicingTypeName = VOICING_TYPE_NAMES[voicing.voicing_type] || voicing.voicing_type;

  // Inversion display
  const inversionText =
    voicing.inversion === 0 ? 'Root' :
    voicing.inversion === 1 ? '1st' :
    voicing.inversion === 2 ? '2nd' :
    `${voicing.inversion}th`;

  if (compact) {
    // Compact mode for Generator/Practice
    return (
      <div className={`flex items-center gap-4 p-3 bg-slate-900/50 rounded-lg border border-slate-800 ${className}`}>
        <div className="flex-shrink-0">
          <PianoKeyboard
            minPitch={minPitch}
            maxPitch={maxPitch}
            activeNotes={voicing.notes}
            noteColors={noteColors}
            onNotePlay={onNotePlay}
            showLabels={false}
            keySize={24}
          />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-slate-200">{chord}</span>
            <span className="text-xs px-2 py-0.5 bg-slate-800 rounded text-slate-400">
              {voicingTypeName}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span>Notes: {voicing.note_names.join(', ')}</span>
            {voicing.extensions.length > 0 && (
              <span className="text-amber-500">+{voicing.extensions.join(', ')}</span>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Full mode for Analysis tab
  return (
    <div className={`bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-100">{chord}</h3>
            <p className="text-sm text-slate-400 mt-1">
              {voicingTypeName} Voicing
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 disabled:cursor-not-allowed rounded-lg flex items-center gap-2 transition-colors"
              onClick={() => playChord(voicing.notes)}
              disabled={isPlaying}
            >
              <Play className="w-4 h-4" />
              <span className="text-sm font-medium">{isPlaying ? 'Playing...' : 'Play'}</span>
            </button>
            <button
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:cursor-not-allowed rounded-lg flex items-center gap-2 transition-colors"
              onClick={() => playArpeggio(voicing.notes, 150)}
              disabled={isPlaying}
            >
              <Music2 className="w-4 h-4" />
              <span className="text-sm font-medium">Arpeggio</span>
            </button>
          </div>
        </div>
      </div>

      {/* Piano Keyboard */}
      <div className="px-6 py-6 bg-slate-900/30">
        <PianoKeyboard
          minPitch={minPitch}
          maxPitch={maxPitch}
          activeNotes={voicing.notes}
          noteColors={noteColors}
          onNotePlay={onNotePlay}
          showLabels={true}
          keySize={40}
          className="mx-auto"
        />
        {/* Note labels */}
        <div className="mt-4 flex justify-center gap-2 flex-wrap">
          {voicing.note_names.map((note, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-slate-800 rounded-full text-sm font-medium text-slate-300"
            >
              {note}
            </span>
          ))}
        </div>
      </div>

      {/* Metadata Panel */}
      {showDetails && (
        <div className="px-6 py-4 bg-slate-900/80 border-t border-slate-800">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Voicing Type */}
            <div>
              <div className="text-xs text-slate-500 mb-1">Type</div>
              <div className="text-sm font-medium text-slate-200">{voicingTypeName}</div>
            </div>

            {/* Complexity */}
            <div>
              <div className="text-xs text-slate-500 mb-1">Complexity</div>
              <ComplexityStars score={voicing.complexity_score} />
            </div>

            {/* Hand Span */}
            <div>
              <div className="text-xs text-slate-500 mb-1">Hand Span</div>
              <HandSpanIndicator span={voicing.hand_span_inches} />
            </div>

            {/* Inversion */}
            <div>
              <div className="text-xs text-slate-500 mb-1">Inversion</div>
              <div className="text-sm font-medium text-slate-200">{inversionText}</div>
            </div>
          </div>

          {/* Chord Tones */}
          <div className="mt-4 pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-500 mb-2">Chord Tones</div>
            <div className="flex items-center gap-3 flex-wrap">
              {voicing.has_root && (
                <span className="px-2 py-1 bg-cyan-950/50 border border-cyan-800 rounded text-xs text-cyan-400">
                  Root
                </span>
              )}
              {voicing.has_third && (
                <span className="px-2 py-1 bg-emerald-950/50 border border-emerald-800 rounded text-xs text-emerald-400">
                  3rd
                </span>
              )}
              {voicing.has_seventh && (
                <span className="px-2 py-1 bg-violet-950/50 border border-violet-800 rounded text-xs text-violet-400">
                  7th
                </span>
              )}
              {voicing.extensions.length > 0 && (
                <span className="px-2 py-1 bg-amber-950/50 border border-amber-800 rounded text-xs text-amber-400">
                  {voicing.extensions.join(', ')}
                </span>
              )}
            </div>
          </div>

          {/* Intervals */}
          <div className="mt-4 pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-500 mb-2">Intervals</div>
            <div className="text-sm text-slate-400">
              {voicing.intervals.join(' - ')} semitones
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
