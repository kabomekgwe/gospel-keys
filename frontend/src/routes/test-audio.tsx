/**
 * Audio Integration Test Page
 *
 * Tests all three components with audio playback:
 * - VoicingVisualizer
 * - ReharmonizationPanel
 * - ProgressionPatternDisplay
 */

import { createFileRoute } from '@tanstack/react-router';
import { VoicingVisualizer, type VoicingInfo } from '../components/analysis/VoicingVisualizer';
import { ReharmonizationPanel, type ReharmonizationSuggestion } from '../components/analysis/ReharmonizationPanel';
import { ProgressionPatternDisplay, type ProgressionPattern, type ChordEvent } from '../components/analysis/ProgressionPatternDisplay';

export const Route = createFileRoute('/test-audio')({
  component: TestAudioPage,
});

function TestAudioPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Page Header */}
        <div>
          <h1 className="text-4xl font-bold text-cyan-400 mb-2">
            🎵 Audio Integration Test
          </h1>
          <p className="text-slate-400">
            Testing Tone.js audio playback for all components
          </p>
        </div>

        {/* Test 1: VoicingVisualizer */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-slate-200">
            1. VoicingVisualizer Component
          </h2>
          <p className="text-sm text-slate-400">
            Test chord playback and arpeggio mode
          </p>
          <VoicingVisualizer
            chord="Cmaj7"
            voicing={mockVoicing}
            showDetails={true}
            compact={false}
          />
        </section>

        {/* Test 2: ReharmonizationPanel */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-slate-200">
            2. ReharmonizationPanel Component
          </h2>
          <p className="text-sm text-slate-400">
            Test original, suggestion, and comparison playback
          </p>
          <ReharmonizationPanel
            originalChord="Cmaj7"
            suggestions={mockSuggestions}
            enableAudio={true}
          />
        </section>

        {/* Test 3: ProgressionPatternDisplay */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-slate-200">
            3. ProgressionPatternDisplay Component
          </h2>
          <p className="text-sm text-slate-400">
            Test progression sequence playback
          </p>
          <ProgressionPatternDisplay
            patterns={mockPatterns}
            totalDuration={8.0}
            chords={mockChords}
            enableAudio={true}
          />
        </section>

        {/* Instructions */}
        <section className="bg-slate-900/50 border border-slate-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-cyan-400 mb-3">
            Testing Instructions
          </h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li className="flex items-start gap-2">
              <span className="text-cyan-500">1.</span>
              <span><strong>VoicingVisualizer:</strong> Click "Play" to hear Cmaj7 chord. Click "Arpeggio" to hear notes sequentially.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-500">2.</span>
              <span><strong>ReharmonizationPanel:</strong> Click "Original" to hear Cmaj7. Click "Try This" to hear suggestion. Click "Compare" to hear both.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-500">3.</span>
              <span><strong>ProgressionPatternDisplay:</strong> Click "Play" on any pattern card to hear the chord progression.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-cyan-500">4.</span>
              <span>Check browser console for any Tone.js errors.</span>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}

// Mock data for testing

const mockVoicing: VoicingInfo = {
  chord_symbol: 'Cmaj7',
  voicing_type: 'drop_2',
  notes: [48, 60, 64, 71, 67], // C3, C4, E4, B4, G4
  note_names: ['C3', 'C4', 'E4', 'B4', 'G4'],
  intervals: [12, 4, 7, -4],
  width_semitones: 19,
  inversion: 0,
  has_root: true,
  has_third: true,
  has_seventh: true,
  extensions: [],
  complexity_score: 0.6,
  hand_span_inches: 9.5,
};

const mockSuggestions: ReharmonizationSuggestion[] = [
  {
    original_chord: 'Cmaj7',
    suggested_chord: 'Em7',
    reharmonization_type: 'diatonic_substitution',
    explanation: 'Diatonic substitute - Em7 shares the tonic function with Cmaj7 in C major.',
    jazz_level: 1,
    voice_leading_quality: 'smooth',
    voicing: {
      notes: [52, 64, 67, 71, 74], // E3, E4, G4, B4, D5
    },
  },
  {
    original_chord: 'Cmaj7',
    suggested_chord: 'Am7',
    reharmonization_type: 'diatonic_substitution',
    explanation: 'Relative minor substitute - Am7 is the vi chord in C major.',
    jazz_level: 1,
    voice_leading_quality: 'smooth',
    voicing: {
      notes: [57, 64, 67, 69, 72], // A3, E4, G4, A4, C5
    },
  },
  {
    original_chord: 'Cmaj7',
    suggested_chord: 'Cmaj9',
    reharmonization_type: 'upper_structure',
    explanation: 'Extended voicing - adds the 9th (D) for richer color.',
    jazz_level: 2,
    voice_leading_quality: 'moderate',
    voicing: {
      notes: [48, 60, 64, 67, 71, 74], // C3, C4, E4, G4, B4, D5
    },
  },
  {
    original_chord: 'Cmaj7',
    suggested_chord: 'F#m7b5',
    reharmonization_type: 'tritone_substitution',
    explanation: 'Tritone substitution - creates tension and interest.',
    jazz_level: 4,
    voice_leading_quality: 'dramatic',
  },
];

const mockChords: ChordEvent[] = [
  { time: 0.0, duration: 2.0, chord: 'Dm7' },
  { time: 2.0, duration: 2.0, chord: 'G7' },
  { time: 4.0, duration: 2.0, chord: 'Cmaj7' },
  { time: 6.0, duration: 2.0, chord: 'Cmaj7' },
];

const mockPatterns: ProgressionPattern[] = [
  {
    pattern_name: 'ii-V-I in C Major',
    genre: 'jazz',
    roman_numerals: ['ii', 'V', 'I'],
    start_index: 0,
    end_index: 2,
    key: 'C major',
    confidence: 0.95,
    description: 'The most common jazz progression. Creates strong resolution to the tonic.',
  },
  {
    pattern_name: 'I-V-vi-IV',
    genre: 'pop',
    roman_numerals: ['I', 'V', 'vi', 'IV'],
    start_index: 0,
    end_index: 2,
    key: 'C major',
    confidence: 0.75,
    description: 'Popular progression used in countless pop songs.',
  },
];
