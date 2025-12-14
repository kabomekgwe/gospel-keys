/**
 * Reharmonization Panel Component
 *
 * Displays reharmonization suggestions with filters and audio comparison
 * Features:
 * - Virtualized suggestion list (react-window)
 * - Filters (jazz level, type, voice leading quality)
 * - Audio comparison buttons (Phase 4)
 * - Mini piano keyboard previews
 * - Voicing metadata
 */

import { useState, useMemo } from 'react';
// TODO: Fix react-window CommonJS import issue with Vite
// Temporarily disabled virtualization for testing
// import * as ReactWindow from 'react-window';
import { ArrowRight, Play, Volume2, Info } from 'lucide-react';
import { MiniPiano } from '../Piano';
import { useChordPlayback } from '../../hooks/useChordPlayback';

export interface ReharmonizationSuggestion {
  original_chord: string;
  suggested_chord: string;
  reharmonization_type: string;
  explanation: string;
  jazz_level: number; // 1-5
  voice_leading_quality: string; // smooth, moderate, dramatic
  // Optional voicing data for piano preview
  voicing?: {
    notes: number[]; // MIDI note numbers
  };
}

export interface ReharmonizationPanelProps {
  /** Original chord being reharmonized */
  originalChord: string;
  /** List of reharmonization suggestions */
  suggestions: ReharmonizationSuggestion[];
  /** Callback when a suggestion is selected */
  onSuggestionSelect?: (suggestion: ReharmonizationSuggestion) => void;
  /** Maximum visible items before virtualizing (default: 5) */
  maxVisible?: number;
  /** Enable audio playback (default: true) */
  enableAudio?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// Reharmonization type display names
const REHARMONIZATION_TYPE_NAMES: Record<string, string> = {
  tritone_substitution: 'Tritone Sub',
  diatonic_substitution: 'Diatonic Sub',
  passing_chord: 'Passing Chord',
  approach_chord: 'Approach Chord',
  backdoor: 'Backdoor',
  modal_interchange: 'Modal Interchange',
  upper_structure: 'Upper Structure',
  diminished_passing: 'Diminished',
};

/**
 * Get color for jazz level (1-5)
 */
function getJazzLevelColor(level: number): string {
  if (level <= 1) return 'bg-emerald-900/50 border-emerald-700 text-emerald-400';
  if (level === 2) return 'bg-cyan-900/50 border-cyan-700 text-cyan-400';
  if (level === 3) return 'bg-amber-900/50 border-amber-700 text-amber-400';
  if (level === 4) return 'bg-orange-900/50 border-orange-700 text-orange-400';
  return 'bg-rose-900/50 border-rose-700 text-rose-400';
}

/**
 * Get color for voice leading quality
 */
function getVoiceLeadingColor(quality: string): string {
  if (quality === 'smooth') return 'text-emerald-400';
  if (quality === 'moderate') return 'text-amber-400';
  return 'text-rose-400';
}

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
 * Individual suggestion card
 */
function SuggestionCard({
  suggestion,
  originalChord,
  enableAudio,
  onSelect,
  onPlayOriginal,
  onPlaySuggestion,
  onCompare,
  style,
}: {
  suggestion: ReharmonizationSuggestion;
  originalChord: string;
  enableAudio: boolean;
  onSelect?: (suggestion: ReharmonizationSuggestion) => void;
  onPlayOriginal?: () => void;
  onPlaySuggestion?: () => void;
  onCompare?: () => void;
  style?: React.CSSProperties;
}) {
  const [showTooltip, setShowTooltip] = useState(false);

  const typeName = REHARMONIZATION_TYPE_NAMES[suggestion.reharmonization_type] || suggestion.reharmonization_type;
  const jazzLevelColor = getJazzLevelColor(suggestion.jazz_level);
  const voiceLeadingColor = getVoiceLeadingColor(suggestion.voice_leading_quality);

  return (
    <div
      style={style}
      className="px-4"
    >
      <div className="bg-slate-900/50 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors">
        <div className="flex items-start gap-4">
          {/* Chord transition */}
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="text-lg font-semibold text-slate-200">{originalChord}</div>
            <ArrowRight className="w-5 h-5 text-slate-500 flex-shrink-0" />
            <div className="text-lg font-semibold text-cyan-400">{suggestion.suggested_chord}</div>
          </div>

          {/* Badges */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Jazz Level */}
            <span className={`px-2 py-1 rounded border text-xs font-medium ${jazzLevelColor}`}>
              Lv {suggestion.jazz_level}
            </span>

            {/* Voice Leading */}
            <span className={`text-xs font-medium capitalize ${voiceLeadingColor}`}>
              {suggestion.voice_leading_quality}
            </span>

            {/* Explanation tooltip */}
            <div className="relative">
              <button
                className="p-1 hover:bg-slate-800 rounded transition-colors"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              >
                <Info className="w-4 h-4 text-slate-400" />
              </button>
              {showTooltip && (
                <div className="absolute right-0 top-full mt-2 w-64 bg-slate-950 border border-slate-700 rounded-lg p-3 shadow-xl z-10">
                  <div className="text-xs text-slate-300">{suggestion.explanation}</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Type badge */}
        <div className="mt-3">
          <span className="px-2 py-1 bg-slate-800 border border-slate-700 rounded text-xs text-slate-400">
            {typeName}
          </span>
        </div>

        {/* Mini piano preview (if voicing data available) */}
        {suggestion.voicing && suggestion.voicing.notes.length > 0 && (
          <div className="mt-3">
            <MiniPiano
              activeNotes={suggestion.voicing.notes}
              minPitch={Math.min(...suggestion.voicing.notes)}
              maxPitch={Math.max(...suggestion.voicing.notes)}
            />
          </div>
        )}

        {/* Audio controls */}
        {enableAudio && (
          <div className="mt-3 flex items-center gap-2">
            <button
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded flex items-center gap-1.5 text-xs transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                onPlayOriginal?.();
              }}
            >
              <Play className="w-3 h-3" />
              Original
            </button>
            <button
              className="px-3 py-1.5 bg-cyan-900/50 hover:bg-cyan-900/70 border border-cyan-800 rounded flex items-center gap-1.5 text-xs text-cyan-400 transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                onPlaySuggestion?.();
                onSelect?.(suggestion);
              }}
            >
              <Play className="w-3 h-3" />
              Try This
            </button>
            <button
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded flex items-center gap-1.5 text-xs transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                onCompare?.();
              }}
            >
              <Volume2 className="w-3 h-3" />
              Compare
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export function ReharmonizationPanel({
  originalChord,
  suggestions,
  onSuggestionSelect,
  maxVisible = 5,
  enableAudio = true,
  className = '',
}: ReharmonizationPanelProps) {
  // Audio playback hook
  const { playChord, playSequence } = useChordPlayback({
    instrument: 'piano',
    duration: 1.5,
  });

  // Filter state
  const [selectedJazzLevel, setSelectedJazzLevel] = useState<number | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedVoiceLeading, setSelectedVoiceLeading] = useState<string | null>(null);

  // Audio playback handlers
  const handlePlayOriginal = (chordSymbol: string) => {
    const notes = chordToMidiNotes(chordSymbol);
    playChord(notes);
  };

  const handlePlaySuggestion = (suggestion: ReharmonizationSuggestion) => {
    // Use voicing notes if available, otherwise convert chord symbol
    const notes = suggestion.voicing?.notes || chordToMidiNotes(suggestion.suggested_chord);
    playChord(notes);
  };

  const handleCompare = (originalChord: string, suggestion: ReharmonizationSuggestion) => {
    const originalNotes = chordToMidiNotes(originalChord);
    const suggestedNotes = suggestion.voicing?.notes || chordToMidiNotes(suggestion.suggested_chord);
    // Play original, then suggested (1.5s delay between)
    playSequence([originalNotes, suggestedNotes], 1500);
  };

  // Get unique values for filters
  const uniqueTypes = useMemo(() => {
    return Array.from(new Set(suggestions.map(s => s.reharmonization_type)));
  }, [suggestions]);

  const uniqueVoiceLeading = useMemo(() => {
    return Array.from(new Set(suggestions.map(s => s.voice_leading_quality)));
  }, [suggestions]);

  // Apply filters
  const filteredSuggestions = useMemo(() => {
    return suggestions.filter(s => {
      if (selectedJazzLevel !== null && s.jazz_level !== selectedJazzLevel) return false;
      if (selectedType !== null && s.reharmonization_type !== selectedType) return false;
      if (selectedVoiceLeading !== null && s.voice_leading_quality !== selectedVoiceLeading) return false;
      return true;
    });
  }, [suggestions, selectedJazzLevel, selectedType, selectedVoiceLeading]);

  // Virtualization temporarily disabled due to CommonJS import issues
  // TODO: Re-enable with proper ESM-compatible virtualization library
  const useVirtualization = false;

  return (
    <div className={`bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 bg-slate-900/80 border-b border-slate-800">
        <h3 className="text-lg font-semibold text-slate-100">
          Reharmonization Ideas for {originalChord}
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          {filteredSuggestions.length} suggestion{filteredSuggestions.length !== 1 ? 's' : ''}
          {filteredSuggestions.length !== suggestions.length && ` (${suggestions.length} total)`}
        </p>
      </div>

      {/* Filters */}
      <div className="px-6 py-4 bg-slate-900/30 border-b border-slate-800">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-sm text-slate-400">Filters:</span>

          {/* Jazz Level Filter */}
          <select
            value={selectedJazzLevel ?? ''}
            onChange={(e) => setSelectedJazzLevel(e.target.value ? Number(e.target.value) : null)}
            className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value="">All Levels</option>
            <option value="1">Level 1 (Beginner)</option>
            <option value="2">Level 2</option>
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5 (Advanced)</option>
          </select>

          {/* Type Filter */}
          <select
            value={selectedType ?? ''}
            onChange={(e) => setSelectedType(e.target.value || null)}
            className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value="">All Types</option>
            {uniqueTypes.map((type) => (
              <option key={type} value={type}>
                {REHARMONIZATION_TYPE_NAMES[type] || type}
              </option>
            ))}
          </select>

          {/* Voice Leading Filter */}
          <select
            value={selectedVoiceLeading ?? ''}
            onChange={(e) => setSelectedVoiceLeading(e.target.value || null)}
            className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            <option value="">All Voice Leading</option>
            {uniqueVoiceLeading.map((quality) => (
              <option key={quality} value={quality}>
                {quality.charAt(0).toUpperCase() + quality.slice(1)}
              </option>
            ))}
          </select>

          {/* Clear filters */}
          {(selectedJazzLevel !== null || selectedType !== null || selectedVoiceLeading !== null) && (
            <button
              onClick={() => {
                setSelectedJazzLevel(null);
                setSelectedType(null);
                setSelectedVoiceLeading(null);
              }}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded text-xs text-slate-400 transition-colors"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Suggestions List */}
      {filteredSuggestions.length === 0 ? (
        <div className="px-6 py-12 text-center text-slate-400">
          No suggestions match the selected filters.
        </div>
      ) : (
        /* Regular list (virtualization temporarily disabled) */
        <div className="py-4">
          {filteredSuggestions.map((suggestion, index) => (
            <div key={index} className="mb-2 last:mb-0">
              <SuggestionCard
                suggestion={suggestion}
                originalChord={originalChord}
                enableAudio={enableAudio}
                onSelect={onSuggestionSelect}
                onPlayOriginal={() => handlePlayOriginal(originalChord)}
                onPlaySuggestion={() => handlePlaySuggestion(suggestion)}
                onCompare={() => handleCompare(originalChord, suggestion)}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
