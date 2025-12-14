#!/usr/bin/env python3
"""
Gospel MIDI Quality Validator

Validates that MIDIs meet gospel piano standards:
- Extended harmony (9ths, 11ths, 13ths)
- Proper voice leading
- Gospel rhythm patterns
- Playability (hand span, difficulty)
- Duration and structure

Usage:
    # Validate all MIDIs in directory
    python scripts/validate_gospel_midis.py --input data/gospel_dataset/validated

    # Validate single file
    python scripts/validate_gospel_midis.py --file gospel_0001.mid

    # Strict validation (for training data)
    python scripts/validate_gospel_midis.py --strict
"""

import argparse
from pathlib import Path
import pretty_midi
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import json


@dataclass
class ValidationResult:
    """MIDI validation result."""
    filename: str
    passed: bool
    score: float  # 0-100
    issues: List[str]
    warnings: List[str]
    metrics: Dict[str, float]


class GospelMIDIValidator:
    """Validate gospel piano MIDI files."""

    def __init__(self, strict: bool = False):
        self.strict = strict

        # Validation thresholds
        self.min_duration = 30  # seconds
        self.max_duration = 300  # 5 minutes
        self.min_notes = 50
        self.min_pitch_range = 24  # 2 octaves
        self.max_hand_span = 12  # Maximum playable span (semitones)

    def validate_file(self, midi_path: Path) -> ValidationResult:
        """Validate a single MIDI file."""
        issues = []
        warnings = []
        metrics = {}

        try:
            midi = pretty_midi.PrettyMIDI(str(midi_path))

            # 1. Duration check
            duration = midi.get_end_time()
            metrics["duration"] = duration

            if duration < self.min_duration:
                issues.append(f"Too short: {duration:.1f}s (min: {self.min_duration}s)")
            elif duration > self.max_duration:
                warnings.append(f"Very long: {duration:.1f}s (may need splitting)")

            # 2. Note count check
            total_notes = sum(len(inst.notes) for inst in midi.instruments)
            metrics["total_notes"] = total_notes

            if total_notes < self.min_notes:
                issues.append(f"Too few notes: {total_notes} (min: {self.min_notes})")

            # 3. Pitch range check (gospel uses wide range)
            all_pitches = [note.pitch for inst in midi.instruments for note in inst.notes]
            if all_pitches:
                pitch_range = max(all_pitches) - min(all_pitches)
                metrics["pitch_range"] = pitch_range

                if pitch_range < self.min_pitch_range:
                    issues.append(f"Limited range: {pitch_range} semitones (min: {self.min_pitch_range})")

            # 4. Gospel harmony check (extended chords)
            has_extended_harmony = self._check_extended_harmony(midi)
            metrics["extended_harmony"] = 1.0 if has_extended_harmony else 0.0

            if not has_extended_harmony and self.strict:
                warnings.append("No obvious extended harmony (9ths, 11ths, 13ths) detected")

            # 5. Rhythm check (gospel feel)
            has_gospel_rhythm = self._check_gospel_rhythm(midi)
            metrics["gospel_rhythm"] = 1.0 if has_gospel_rhythm else 0.0

            if not has_gospel_rhythm:
                warnings.append("Rhythm doesn't match typical gospel patterns")

            # 6. Playability check
            playability_issues = self._check_playability(midi)
            metrics["playability_score"] = 1.0 - (len(playability_issues) / 10)

            if playability_issues:
                for issue in playability_issues[:3]:  # Show first 3
                    warnings.append(f"Playability: {issue}")

            # 7. Voice leading smoothness
            voice_leading_score = self._check_voice_leading(midi)
            metrics["voice_leading"] = voice_leading_score

            if voice_leading_score < 0.6 and self.strict:
                warnings.append(f"Voice leading could be smoother (score: {voice_leading_score:.2f})")

            # Calculate overall score
            score = self._calculate_score(metrics, issues, warnings)

            # Determine pass/fail
            passed = len(issues) == 0 and (not self.strict or len(warnings) <= 2)

            return ValidationResult(
                filename=midi_path.name,
                passed=passed,
                score=score,
                issues=issues,
                warnings=warnings,
                metrics=metrics
            )

        except Exception as e:
            return ValidationResult(
                filename=midi_path.name,
                passed=False,
                score=0.0,
                issues=[f"Failed to load: {str(e)}"],
                warnings=[],
                metrics={}
            )

    def _check_extended_harmony(self, midi: pretty_midi.PrettyMIDI) -> bool:
        """Check for extended jazz harmony (9ths, 11ths, 13ths)."""
        # Look for chord intervals beyond octave
        # Simplified check: look for notes with intervals of 14+ semitones
        for inst in midi.instruments:
            notes_by_time = {}

            for note in inst.notes:
                time_bucket = int(note.start * 4)  # Quarter note buckets
                if time_bucket not in notes_by_time:
                    notes_by_time[time_bucket] = []
                notes_by_time[time_bucket].append(note.pitch)

            # Check for extended intervals in simultaneous notes
            for pitches in notes_by_time.values():
                if len(pitches) >= 3:
                    pitches_sorted = sorted(pitches)
                    for i in range(len(pitches_sorted) - 1):
                        interval = pitches_sorted[-1] - pitches_sorted[0]
                        if interval >= 14:  # 9th or higher
                            return True

        return False

    def _check_gospel_rhythm(self, midi: pretty_midi.PrettyMIDI) -> bool:
        """Check for gospel rhythm patterns (syncopation, backbeat)."""
        # Look for off-beat notes (syncopation)
        total_notes = 0
        offbeat_notes = 0

        for inst in midi.instruments:
            for note in inst.notes:
                total_notes += 1
                # Check if note starts on offbeat (not on quarter note)
                beat_position = (note.start * 2) % 1  # Half-beat resolution
                if 0.2 < beat_position < 0.8:  # Offbeat
                    offbeat_notes += 1

        if total_notes == 0:
            return False

        offbeat_ratio = offbeat_notes / total_notes
        # Gospel typically has 20-50% offbeat notes
        return 0.15 < offbeat_ratio < 0.6

    def _check_playability(self, midi: pretty_midi.PrettyMIDI) -> List[str]:
        """Check if arrangement is playable by human."""
        issues = []

        for inst in midi.instruments:
            # Group notes by time
            notes_by_time = {}
            for note in inst.notes:
                time_bucket = int(note.start * 16)  # 16th note resolution
                if time_bucket not in notes_by_time:
                    notes_by_time[time_bucket] = []
                notes_by_time[time_bucket].append(note.pitch)

            # Check hand spans
            for pitches in notes_by_time.values():
                if len(pitches) > 1:
                    span = max(pitches) - min(pitches)
                    if span > self.max_hand_span:
                        issues.append(f"Hand span too wide: {span} semitones")

                if len(pitches) > 6:
                    issues.append(f"Too many simultaneous notes: {len(pitches)}")

        return issues

    def _check_voice_leading(self, midi: pretty_midi.PrettyMIDI) -> float:
        """Check voice leading smoothness (0-1 score)."""
        # Measure average interval between consecutive chords
        # Smaller intervals = smoother voice leading

        total_movement = 0
        chord_count = 0

        for inst in midi.instruments:
            # Group notes into chords
            chords = []
            current_chord = []
            last_time = 0

            sorted_notes = sorted(inst.notes, key=lambda n: n.start)

            for note in sorted_notes:
                if note.start - last_time > 0.5:  # New chord
                    if current_chord:
                        chords.append(current_chord)
                    current_chord = [note.pitch]
                else:
                    current_chord.append(note.pitch)
                last_time = note.start

            if current_chord:
                chords.append(current_chord)

            # Calculate movement between chords
            for i in range(len(chords) - 1):
                chord1 = sorted(chords[i])
                chord2 = sorted(chords[i + 1])

                # Calculate minimum total movement
                if chord1 and chord2:
                    movement = sum(abs(c2 - c1) for c1, c2 in zip(chord1, chord2))
                    total_movement += movement
                    chord_count += 1

        if chord_count == 0:
            return 0.5

        avg_movement = total_movement / chord_count
        # Good voice leading: avg movement < 5 semitones per voice
        # Scale to 0-1 (5 semitones = 1.0, 20+ = 0.0)
        score = max(0, 1.0 - (avg_movement - 5) / 15)
        return score

    def _calculate_score(
        self,
        metrics: Dict[str, float],
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate overall quality score (0-100)."""
        score = 100.0

        # Deduct for issues
        score -= len(issues) * 20

        # Deduct for warnings
        score -= len(warnings) * 5

        # Bonus for good metrics
        if metrics.get("extended_harmony", 0) > 0:
            score += 10

        if metrics.get("gospel_rhythm", 0) > 0:
            score += 10

        if metrics.get("voice_leading", 0) > 0.7:
            score += 10

        return max(0, min(100, score))

    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        """Validate all MIDI files in directory."""
        results = []

        midi_files = list(directory.glob("*.mid"))
        print(f"🔍 Validating {len(midi_files)} MIDI files...\n")

        for midi_file in midi_files:
            result = self.validate_file(midi_file)
            results.append(result)

            # Print result
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.filename} - Score: {result.score:.0f}/100")

            if result.issues:
                for issue in result.issues:
                    print(f"   ❌ {issue}")

            if result.warnings and self.strict:
                for warning in result.warnings[:2]:  # Show first 2 warnings
                    print(f"   ⚠️  {warning}")

        return results

    def generate_report(self, results: List[ValidationResult], output_file: Path):
        """Generate validation report."""
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        avg_score = sum(r.score for r in results) / len(results) if results else 0

        report = f"""# Gospel MIDI Validation Report

**Total Files**: {len(results)}
**Passed**: {len(passed)} ({len(passed)/len(results)*100:.1f}%)
**Failed**: {len(failed)} ({len(failed)/len(results)*100:.1f}%)
**Average Score**: {avg_score:.1f}/100

## Failed Files

"""

        for result in failed:
            report += f"### {result.filename} (Score: {result.score:.0f})\n\n"
            for issue in result.issues:
                report += f"- ❌ {issue}\n"
            for warning in result.warnings:
                report += f"- ⚠️ {warning}\n"
            report += "\n"

        output_file.write_text(report)
        print(f"\n📄 Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Validate gospel MIDI files")
    parser.add_argument("--input", type=Path, default=Path("data/gospel_dataset/validated"))
    parser.add_argument("--file", type=Path, help="Validate single file")
    parser.add_argument("--strict", action="store_true", help="Strict validation mode")
    parser.add_argument("--report", type=Path, help="Generate report file")

    args = parser.parse_args()

    validator = GospelMIDIValidator(strict=args.strict)

    if args.file:
        # Validate single file
        result = validator.validate_file(args.file)
        print(f"\n{'✅ PASSED' if result.passed else '❌ FAILED'}")
        print(f"Score: {result.score:.0f}/100")
        print(f"\nMetrics:")
        for key, value in result.metrics.items():
            print(f"  {key}: {value:.2f}")

    else:
        # Validate directory
        results = validator.validate_directory(args.input)

        # Summary
        passed = sum(1 for r in results if r.passed)
        print(f"\n📊 Summary:")
        print(f"   Passed: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
        print(f"   Avg Score: {sum(r.score for r in results)/len(results):.1f}/100")

        # Generate report if requested
        if args.report:
            validator.generate_report(results, args.report)


if __name__ == "__main__":
    main()
