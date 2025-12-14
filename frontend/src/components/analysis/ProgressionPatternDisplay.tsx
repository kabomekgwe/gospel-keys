/**
 * Progression Pattern Display Component
 *
 * Displays detected chord progressions with timeline visualization
 * Features:
 * - Timeline view with Recharts (pattern blocks by genre)
 * - List view with pattern cards
 * - Pattern details (name, genre, confidence, description)
 * - Audio playback for patterns (Phase 4)
 * - Genre filtering
 */

import { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Play, List, BarChart3, Info } from 'lucide-react';
import { useChordPlayback } from '../../hooks/useChordPlayback';

export interface ChordEvent {
  time: number;
  duration: number;
  chord: string;
}

export interface ProgressionPattern {
  pattern_name: string;
  genre: string;
  roman_numerals: string[];
  start_index: number;
  end_index: number;
  key: string;
  confidence: number; // 0-1
  description: string;
}

export interface ProgressionPatternDisplayProps {
  /** Detected patterns */
  patterns: ProgressionPattern[];
  /** Total duration for timeline scaling */
  totalDuration: number;
  /** All chords for context */
  chords: ChordEvent[];
  /** Callback when pattern is clicked */
  onPatternClick?: (pattern: ProgressionPattern) => void;
  /** Enable audio playback (default: true) */
  enableAudio?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// Genre colors
const GENRE_COLORS: Record<string, string> = {
  pop: '#3b82f6',       // blue-500
  jazz: '#a855f7',      // purple-500
  blues: '#6366f1',     // indigo-500
  modal: '#14b8a6',     // teal-500
  gospel: '#f59e0b',    // amber-500
  classical: '#ec4899', // pink-500
};

// Genre display names
const GENRE_NAMES: Record<string, string> = {
  pop: 'Pop',
  jazz: 'Jazz',
  blues: 'Blues',
  modal: 'Modal',
  gospel: 'Gospel',
  classical: 'Classical',
};

/**
 * Convert chord symbol to MIDI notes
 * Simple implementation - returns basic triad/seventh chord voicing
 */
function chordToMidiNotes(chordSymbol: string): number[] {
  const noteMap: Record<string, number> = {
    'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
    'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
    'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71,
  };

  // Extract root note
  const rootMatch = chordSymbol.match(/^([A-G][#b]?)/);
  if (!rootMatch) return [60, 64, 67]; // Default to C major

  const root = noteMap[rootMatch[1]];
  const lowerRoot = root - 12; // Bass note one octave below

  // Determine chord quality and build voicing
  const symbol = chordSymbol.toLowerCase();

  if (symbol.includes('maj7') || symbol.includes('M7') || symbol.includes('△7')) {
    // Major 7th: root, 3rd, 5th, 7th
    return [lowerRoot, root, root + 4, root + 7, root + 11];
  } else if (symbol.includes('m7') || symbol.includes('min7') || symbol.includes('-7')) {
    // Minor 7th: root, b3rd, 5th, b7th
    return [lowerRoot, root, root + 3, root + 7, root + 10];
  } else if (symbol.includes('7')) {
    // Dominant 7th: root, 3rd, 5th, b7th
    return [lowerRoot, root, root + 4, root + 7, root + 10];
  } else if (symbol.includes('m') || symbol.includes('min') || symbol.includes('-')) {
    // Minor triad: root, b3rd, 5th
    return [lowerRoot, root, root + 3, root + 7];
  } else if (symbol.includes('dim')) {
    // Diminished: root, b3rd, b5th
    return [lowerRoot, root, root + 3, root + 6];
  } else if (symbol.includes('aug') || symbol.includes('+')) {
    // Augmented: root, 3rd, #5th
    return [lowerRoot, root, root + 4, root + 8];
  } else {
    // Default to major triad: root, 3rd, 5th
    return [lowerRoot, root, root + 4, root + 7];
  }
}

/**
 * Confidence meter (0-100%)
 */
function ConfidenceMeter({ confidence }: { confidence: number }) {
  const percentage = Math.round(confidence * 100);
  const color =
    percentage >= 80 ? 'bg-emerald-500' :
    percentage >= 60 ? 'bg-amber-500' :
    'bg-slate-500';

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-slate-400 w-10 text-right">{percentage}%</span>
    </div>
  );
}

/**
 * Pattern card for list view
 */
function PatternCard({
  pattern,
  chords,
  enableAudio,
  onPlay,
  onClick,
}: {
  pattern: ProgressionPattern;
  chords: ChordEvent[];
  enableAudio: boolean;
  onPlay?: () => void;
  onClick?: () => void;
}) {
  const genreColor = GENRE_COLORS[pattern.genre.toLowerCase()] || GENRE_COLORS.pop;
  const genreName = GENRE_NAMES[pattern.genre.toLowerCase()] || pattern.genre;

  return (
    <div
      className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-base font-semibold text-slate-200 truncate">
              {pattern.pattern_name}
            </h4>
            <span
              className="px-2 py-0.5 rounded text-xs font-medium text-white"
              style={{ backgroundColor: genreColor }}
            >
              {genreName}
            </span>
          </div>

          <div className="text-sm text-slate-400 mb-3">
            {pattern.description}
          </div>

          {/* Pattern details */}
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span>Key: <span className="text-slate-400">{pattern.key}</span></span>
            <span>Chords: <span className="text-slate-400">{pattern.start_index + 1}-{pattern.end_index + 1}</span></span>
            <span>Progression: <span className="text-slate-400">{pattern.roman_numerals.join(' - ')}</span></span>
          </div>

          {/* Confidence */}
          <div className="mt-3">
            <div className="text-xs text-slate-500 mb-1">Confidence</div>
            <ConfidenceMeter confidence={pattern.confidence} />
          </div>
        </div>

        {/* Audio button */}
        {enableAudio && (
          <button
            className="px-3 py-2 bg-cyan-600 hover:bg-cyan-500 rounded-lg flex items-center gap-2 transition-colors flex-shrink-0"
            onClick={(e) => {
              e.stopPropagation();
              onPlay?.();
            }}
          >
            <Play className="w-4 h-4" />
            <span className="text-sm font-medium">Play</span>
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Custom tooltip for timeline
 */
function TimelineTooltip({ active, payload }: any) {
  if (!active || !payload || !payload[0]) return null;

  const pattern: ProgressionPattern = payload[0].payload.pattern;
  const genreColor = GENRE_COLORS[pattern.genre.toLowerCase()] || GENRE_COLORS.pop;

  return (
    <div className="bg-slate-950 border border-slate-700 rounded-lg p-3 shadow-xl max-w-xs">
      <div className="flex items-center gap-2 mb-2">
        <div
          className="w-3 h-3 rounded"
          style={{ backgroundColor: genreColor }}
        />
        <div className="text-sm font-semibold text-slate-200">{pattern.pattern_name}</div>
      </div>
      <div className="text-xs text-slate-400 mb-2">{pattern.description}</div>
      <div className="text-xs text-slate-500">
        <div>Progression: {pattern.roman_numerals.join(' - ')}</div>
        <div>Key: {pattern.key}</div>
        <div>Confidence: {Math.round(pattern.confidence * 100)}%</div>
      </div>
    </div>
  );
}

export function ProgressionPatternDisplay({
  patterns,
  totalDuration,
  chords,
  onPatternClick,
  enableAudio = true,
  className = '',
}: ProgressionPatternDisplayProps) {
  // Audio playback hook
  const { playSequence, isPlaying } = useChordPlayback({
    instrument: 'piano',
    duration: 1.0,
  });

  const [viewMode, setViewMode] = useState<'timeline' | 'list'>('timeline');
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [selectedPattern, setSelectedPattern] = useState<ProgressionPattern | null>(null);

  // Audio playback handler for patterns
  const handlePlayPattern = (pattern: ProgressionPattern) => {
    // Extract chords from the pattern range
    const patternChords = chords.slice(pattern.start_index, pattern.end_index + 1);

    // Convert each chord to MIDI notes
    const chordSequence = patternChords.map(chord => chordToMidiNotes(chord.chord));

    // Play the sequence (1 second per chord)
    playSequence(chordSequence, 1000);
  };

  // Get unique genres
  const uniqueGenres = useMemo(() => {
    return Array.from(new Set(patterns.map(p => p.genre.toLowerCase())));
  }, [patterns]);

  // Filter patterns
  const filteredPatterns = useMemo(() => {
    return selectedGenre
      ? patterns.filter(p => p.genre.toLowerCase() === selectedGenre)
      : patterns;
  }, [patterns, selectedGenre]);

  // Sort patterns by confidence (descending)
  const sortedPatterns = useMemo(() => {
    return [...filteredPatterns].sort((a, b) => b.confidence - a.confidence);
  }, [filteredPatterns]);

  // Prepare timeline data
  const timelineData = useMemo(() => {
    return filteredPatterns.map((pattern, index) => ({
      pattern,
      index,
      start: pattern.start_index,
      end: pattern.end_index,
      duration: pattern.end_index - pattern.start_index + 1,
      genre: pattern.genre.toLowerCase(),
    }));
  }, [filteredPatterns]);

  return (
    <div className={`bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-100">
              Detected Chord Progressions
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              {filteredPatterns.length} pattern{filteredPatterns.length !== 1 ? 's' : ''} found
              {filteredPatterns.length !== patterns.length && ` (${patterns.length} total)`}
            </p>
          </div>

          {/* View toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('timeline')}
              className={`px-3 py-1.5 rounded flex items-center gap-2 text-sm transition-colors ${
                viewMode === 'timeline'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Timeline
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded flex items-center gap-2 text-sm transition-colors ${
                viewMode === 'list'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              <List className="w-4 h-4" />
              List
            </button>
          </div>
        </div>
      </div>

      {/* Genre filter */}
      <div className="px-6 py-3 bg-slate-900/30 border-b border-slate-800">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-slate-400">Genre:</span>
          <button
            onClick={() => setSelectedGenre(null)}
            className={`px-3 py-1 rounded text-xs transition-colors ${
              selectedGenre === null
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            All
          </button>
          {uniqueGenres.map((genre) => {
            const genreName = GENRE_NAMES[genre] || genre;
            const genreColor = GENRE_COLORS[genre] || GENRE_COLORS.pop;
            return (
              <button
                key={genre}
                onClick={() => setSelectedGenre(genre)}
                className={`px-3 py-1 rounded text-xs transition-colors ${
                  selectedGenre === genre
                    ? 'text-white'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                }`}
                style={selectedGenre === genre ? { backgroundColor: genreColor } : undefined}
              >
                {genreName}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      {filteredPatterns.length === 0 ? (
        <div className="px-6 py-12 text-center text-slate-400">
          No patterns match the selected genre.
        </div>
      ) : viewMode === 'timeline' ? (
        /* Timeline View */
        <div className="p-6">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={timelineData}
              layout="vertical"
              margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
            >
              <XAxis
                type="number"
                domain={[0, chords.length]}
                label={{ value: 'Chord Position', position: 'bottom', fill: '#94a3b8' }}
                stroke="#475569"
              />
              <YAxis
                type="category"
                dataKey="pattern.pattern_name"
                stroke="#475569"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
              />
              <RechartsTooltip content={<TimelineTooltip />} />
              <Bar
                dataKey="duration"
                onClick={(data) => {
                  setSelectedPattern(data.pattern);
                  onPatternClick?.(data.pattern);
                }}
                cursor="pointer"
              >
                {timelineData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={GENRE_COLORS[entry.genre] || GENRE_COLORS.pop}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Selected pattern details */}
          {selectedPattern && (
            <div className="mt-6">
              <div className="text-sm text-slate-400 mb-3">Selected Pattern:</div>
              <PatternCard
                pattern={selectedPattern}
                chords={chords}
                enableAudio={enableAudio}
                onPlay={() => handlePlayPattern(selectedPattern)}
                onClick={() => onPatternClick?.(selectedPattern)}
              />
            </div>
          )}
        </div>
      ) : (
        /* List View */
        <div className="p-6 space-y-3">
          {sortedPatterns.map((pattern, index) => (
            <PatternCard
              key={index}
              pattern={pattern}
              chords={chords}
              enableAudio={enableAudio}
              onPlay={() => handlePlayPattern(pattern)}
              onClick={() => {
                setSelectedPattern(pattern);
                onPatternClick?.(pattern);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
