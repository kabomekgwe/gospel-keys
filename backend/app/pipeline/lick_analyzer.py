"""
Lick Pattern Analyzer - Phase 7 Week 3

Analyzes lick patterns for:
- Motif extraction (finding repeating patterns)
- Style classification (identify jazz, gospel, blues characteristics)
- Similarity search (find similar licks in database)
- N-gram analysis (3-5 note sequences)
- Pattern complexity scoring

Features:
- Extract melodic motifs from licks
- Calculate similarity between licks using multiple metrics
- Classify unknown licks by style
- Find the most similar patterns in database
- Analyze harmonic function and voice leading
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from collections import Counter
import math


@dataclass
class MotifMatch:
    """Extracted motif from a lick"""
    intervals: Tuple[int, ...]
    positions: List[int]  # Where this motif appears
    frequency: int
    length: int


@dataclass
class SimilarityResult:
    """Result of similarity comparison"""
    pattern_name: str
    similarity_score: float  # 0-1 (1 = identical)
    matching_intervals: int
    interval_similarity: float
    rhythm_similarity: float
    contour_similarity: float


class LickAnalyzer:
    """Analyzes lick patterns for characteristics and similarity"""

    def __init__(self):
        """Initialize analyzer"""
        self.lick_database = None

    def _load_database(self):
        """Load database on demand"""
        if not self.lick_database:
            from app.pipeline.lick_database_expanded import lick_database
            self.lick_database = lick_database

    # ========================================================================
    # Motif Extraction
    # ========================================================================

    def extract_motifs(
        self,
        intervals: List[int],
        min_length: int = 3,
        max_length: int = 5
    ) -> List[MotifMatch]:
        """
        Extract repeating motifs from interval sequence

        Args:
            intervals: List of intervals
            min_length: Minimum motif length
            max_length: Maximum motif length

        Returns:
            List of MotifMatch objects sorted by frequency
        """
        motifs: Dict[Tuple[int, ...], List[int]] = {}

        # Find all n-grams of each length
        for length in range(min_length, min(max_length + 1, len(intervals))):
            for i in range(len(intervals) - length + 1):
                motif = tuple(intervals[i:i + length])

                if motif not in motifs:
                    motifs[motif] = []

                motifs[motif].append(i)

        # Convert to MotifMatch objects
        results = [
            MotifMatch(
                intervals=motif,
                positions=positions,
                frequency=len(positions),
                length=len(motif)
            )
            for motif, positions in motifs.items()
            if len(positions) > 1  # Only repeating motifs
        ]

        # Sort by frequency, then length
        results.sort(key=lambda m: (m.frequency, m.length), reverse=True)

        return results

    def get_ngrams(
        self,
        intervals: List[int],
        n: int = 3
    ) -> List[Tuple[int, ...]]:
        """
        Extract n-grams (overlapping subsequences)

        Args:
            intervals: List of intervals
            n: N-gram size

        Returns:
            List of n-grams
        """
        if len(intervals) < n:
            return []

        return [
            tuple(intervals[i:i + n])
            for i in range(len(intervals) - n + 1)
        ]

    # ========================================================================
    # Similarity Metrics
    # ========================================================================

    def calculate_interval_similarity(
        self,
        intervals1: List[int],
        intervals2: List[int]
    ) -> float:
        """
        Calculate similarity based on interval patterns

        Uses Levenshtein distance normalized to 0-1

        Args:
            intervals1: First interval sequence
            intervals2: Second interval sequence

        Returns:
            Similarity score (0-1, 1=identical)
        """
        # Levenshtein distance (edit distance)
        distance = self._levenshtein_distance(intervals1, intervals2)

        # Normalize by max length
        max_len = max(len(intervals1), len(intervals2))

        if max_len == 0:
            return 1.0

        # Convert distance to similarity
        similarity = 1.0 - (distance / max_len)

        return max(0.0, similarity)

    def _levenshtein_distance(
        self,
        seq1: List[int],
        seq2: List[int]
    ) -> int:
        """Calculate Levenshtein edit distance"""
        if len(seq1) < len(seq2):
            return self._levenshtein_distance(seq2, seq1)

        if len(seq2) == 0:
            return len(seq1)

        previous_row = range(len(seq2) + 1)

        for i, c1 in enumerate(seq1):
            current_row = [i + 1]

            for j, c2 in enumerate(seq2):
                # Cost of insertions, deletions, substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)

                current_row.append(min(insertions, deletions, substitutions))

            previous_row = current_row

        return previous_row[-1]

    def calculate_rhythm_similarity(
        self,
        rhythm1: List[float],
        rhythm2: List[float]
    ) -> float:
        """
        Calculate similarity based on rhythmic patterns

        Uses cosine similarity

        Args:
            rhythm1: First rhythm sequence
            rhythm2: Second rhythm sequence

        Returns:
            Similarity score (0-1)
        """
        # Pad to same length
        max_len = max(len(rhythm1), len(rhythm2))
        r1 = list(rhythm1) + [0.0] * (max_len - len(rhythm1))
        r2 = list(rhythm2) + [0.0] * (max_len - len(rhythm2))

        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(r1, r2))
        magnitude1 = math.sqrt(sum(a * a for a in r1))
        magnitude2 = math.sqrt(sum(b * b for b in r2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def calculate_contour_similarity(
        self,
        intervals1: List[int],
        intervals2: List[int]
    ) -> float:
        """
        Calculate similarity based on melodic contour (direction)

        Args:
            intervals1: First interval sequence
            intervals2: Second interval sequence

        Returns:
            Similarity score (0-1)
        """
        # Convert to contour (direction: -1=down, 0=same, 1=up)
        contour1 = self._get_contour(intervals1)
        contour2 = self._get_contour(intervals2)

        # Pad to same length
        max_len = max(len(contour1), len(contour2))
        c1 = contour1 + [0] * (max_len - len(contour1))
        c2 = contour2 + [0] * (max_len - len(contour2))

        # Calculate matching percentage
        matches = sum(1 for a, b in zip(c1, c2) if a == b)

        return matches / max_len if max_len > 0 else 0.0

    def _get_contour(self, intervals: List[int]) -> List[int]:
        """Get melodic contour from intervals"""
        if len(intervals) < 2:
            return []

        contour = []
        for i in range(1, len(intervals)):
            diff = intervals[i] - intervals[i - 1]

            if diff > 0:
                contour.append(1)  # Ascending
            elif diff < 0:
                contour.append(-1)  # Descending
            else:
                contour.append(0)  # Same

        return contour

    def calculate_similarity(
        self,
        intervals1: List[int],
        rhythm1: List[float],
        intervals2: List[int],
        rhythm2: List[float],
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate overall similarity using weighted combination

        Args:
            intervals1: First interval sequence
            rhythm1: First rhythm sequence
            intervals2: Second interval sequence
            rhythm2: Second rhythm sequence
            weights: Optional weight dictionary

        Returns:
            Combined similarity score (0-1)
        """
        if weights is None:
            weights = {
                'intervals': 0.5,
                'rhythm': 0.3,
                'contour': 0.2
            }

        interval_sim = self.calculate_interval_similarity(intervals1, intervals2)
        rhythm_sim = self.calculate_rhythm_similarity(rhythm1, rhythm2)
        contour_sim = self.calculate_contour_similarity(intervals1, intervals2)

        combined = (
            interval_sim * weights['intervals'] +
            rhythm_sim * weights['rhythm'] +
            contour_sim * weights['contour']
        )

        return combined

    # ========================================================================
    # Database Search
    # ========================================================================

    def find_similar_patterns(
        self,
        intervals: List[int],
        rhythm: List[float],
        style: Optional[str] = None,
        top_k: int = 5
    ) -> List[SimilarityResult]:
        """
        Find similar patterns in database

        Args:
            intervals: Query interval sequence
            rhythm: Query rhythm sequence
            style: Optional style filter
            top_k: Number of results to return

        Returns:
            List of SimilarityResult objects sorted by similarity
        """
        self._load_database()

        # Get patterns to search
        if style:
            patterns = self.lick_database.get_by_style(style)
        else:
            patterns = self.lick_database.all_patterns

        results = []

        for pattern in patterns:
            # Calculate similarity metrics
            interval_sim = self.calculate_interval_similarity(
                intervals, list(pattern.intervals)
            )
            rhythm_sim = self.calculate_rhythm_similarity(
                rhythm, list(pattern.rhythm)
            )
            contour_sim = self.calculate_contour_similarity(
                intervals, list(pattern.intervals)
            )

            # Combined similarity
            overall_sim = self.calculate_similarity(
                intervals, rhythm,
                list(pattern.intervals), list(pattern.rhythm)
            )

            # Count matching intervals
            matching = sum(
                1 for a, b in zip(intervals, pattern.intervals) if a == b
            )

            results.append(SimilarityResult(
                pattern_name=pattern.name,
                similarity_score=overall_sim,
                matching_intervals=matching,
                interval_similarity=interval_sim,
                rhythm_similarity=rhythm_sim,
                contour_similarity=contour_sim
            ))

        # Sort by similarity
        results.sort(key=lambda r: r.similarity_score, reverse=True)

        return results[:top_k]

    # ========================================================================
    # Style Classification
    # ========================================================================

    def classify_style(
        self,
        intervals: List[int],
        rhythm: List[float]
    ) -> Dict[str, float]:
        """
        Classify lick style based on similarity to database patterns

        Args:
            intervals: Interval sequence
            rhythm: Rhythm sequence

        Returns:
            Dictionary of style probabilities
        """
        self._load_database()

        # Calculate average similarity to each style
        styles = ['bebop', 'gospel', 'blues', 'neo_soul', 'modern_jazz', 'classical']
        style_scores = {}

        for style in styles:
            patterns = self.lick_database.get_by_style(style)

            if not patterns:
                style_scores[style] = 0.0
                continue

            # Average similarity to all patterns of this style
            similarities = [
                self.calculate_similarity(
                    intervals, rhythm,
                    list(p.intervals), list(p.rhythm)
                )
                for p in patterns
            ]

            style_scores[style] = sum(similarities) / len(similarities)

        # Normalize to probabilities
        total = sum(style_scores.values())

        if total > 0:
            style_scores = {
                style: score / total
                for style, score in style_scores.items()
            }

        return style_scores

    # ========================================================================
    # Complexity Analysis
    # ========================================================================

    def calculate_complexity(
        self,
        intervals: List[int],
        rhythm: List[float]
    ) -> Dict[str, any]:
        """
        Calculate pattern complexity metrics

        Args:
            intervals: Interval sequence
            rhythm: Rhythm sequence

        Returns:
            Dictionary with complexity metrics
        """
        # Interval range (wider = more complex)
        if intervals:
            interval_range = max(intervals) - min(intervals)
        else:
            interval_range = 0

        # Number of unique intervals
        unique_intervals = len(set(intervals))

        # Chromatic density (non-diatonic intervals)
        chromatic_count = sum(
            1 for i in intervals
            if i % 12 in [1, 3, 6, 8, 10]  # Non-diatonic
        )
        chromatic_density = chromatic_count / len(intervals) if intervals else 0

        # Rhythmic complexity (number of different durations)
        unique_rhythms = len(set(rhythm))

        # Directional changes (contour complexity)
        contour = self._get_contour(intervals)
        direction_changes = sum(
            1 for i in range(1, len(contour))
            if contour[i] != contour[i - 1]
        )

        # Combined complexity score (0-10)
        complexity_score = min(10, (
            (interval_range / 12) * 2 +  # Range contribution
            (unique_intervals / 7) * 2 +  # Variety contribution
            chromatic_density * 2 +  # Chromaticism
            (unique_rhythms / 5) * 2 +  # Rhythmic variety
            (direction_changes / len(intervals) if intervals else 0) * 2  # Contour
        ))

        return {
            'complexity_score': complexity_score,
            'interval_range': interval_range,
            'unique_intervals': unique_intervals,
            'chromatic_density': chromatic_density,
            'unique_rhythms': unique_rhythms,
            'direction_changes': direction_changes,
            'total_notes': len(intervals)
        }

    # ========================================================================
    # Characteristic Detection
    # ========================================================================

    def detect_characteristics(
        self,
        intervals: List[int],
        rhythm: List[float]
    ) -> List[str]:
        """
        Detect musical characteristics in a lick

        Args:
            intervals: Interval sequence
            rhythm: Rhythm sequence

        Returns:
            List of characteristic tags
        """
        characteristics = []

        # Chromatic characteristics
        chromatic_count = sum(
            1 for i in range(len(intervals) - 1)
            if abs(intervals[i + 1] - intervals[i]) == 1
        )

        if chromatic_count >= len(intervals) * 0.3:
            characteristics.append("chromatic")

        # Arpeggio detection (mostly thirds and fifths)
        if len(intervals) >= 3:
            thirds_fifths = sum(
                1 for i in range(len(intervals) - 1)
                if abs(intervals[i + 1] - intervals[i]) in [3, 4, 5, 7]
            )

            if thirds_fifths >= len(intervals) * 0.5:
                characteristics.append("arpeggio")

        # Scalar motion (mostly step-wise)
        if len(intervals) >= 3:
            steps = sum(
                1 for i in range(len(intervals) - 1)
                if abs(intervals[i + 1] - intervals[i]) <= 2
            )

            if steps >= len(intervals) * 0.6:
                characteristics.append("scalar")

        # Direction
        contour = self._get_contour(intervals)
        ascending = sum(1 for c in contour if c > 0)
        descending = sum(1 for c in contour if c < 0)

        if ascending > descending * 2:
            characteristics.append("ascending")
        elif descending > ascending * 2:
            characteristics.append("descending")

        # Blue notes (b3, b5, b7)
        blue_notes = [3, 6, 10]
        has_blue_notes = any(
            i % 12 in blue_notes for i in intervals
        )

        if has_blue_notes:
            characteristics.append("blues")

        # Rhythmic characteristics
        if rhythm:
            # Syncopation (notes on off-beats)
            # Simplified: check for non-standard durations
            standard_durations = [0.25, 0.5, 1.0, 2.0, 4.0]
            non_standard = sum(
                1 for r in rhythm
                if not any(abs(r - std) < 0.01 for std in standard_durations)
            )

            if non_standard >= len(rhythm) * 0.3:
                characteristics.append("syncopation")

            # Triplet feel
            triplet_durations = [0.33, 0.34, 0.67, 0.66]
            has_triplets = any(
                any(abs(r - trip) < 0.01 for trip in triplet_durations)
                for r in rhythm
            )

            if has_triplets:
                characteristics.append("triplet")

        return characteristics


# Global analyzer instance
lick_analyzer = LickAnalyzer()


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("LICK ANALYZER TESTS")
    print("=" * 70)

    # Test motif extraction
    test_intervals = [0, 2, 4, 0, 2, 4, 7, 9, 11, 0, 2, 4]
    print("\nTest intervals:", test_intervals)

    motifs = lick_analyzer.extract_motifs(test_intervals, min_length=3, max_length=4)
    print(f"\nExtracted motifs:")
    for motif in motifs[:5]:
        print(f"  {motif.intervals} - appears {motif.frequency} times at positions {motif.positions}")

    # Test similarity
    print("\n" + "=" * 70)
    print("SIMILARITY TESTING")
    print("=" * 70)

    intervals1 = [0, 2, 4, 5, 7, 9, 11, 12]
    rhythm1 = [0.5] * 8

    intervals2 = [0, 2, 4, 5, 7, 9, 10, 12]  # Similar but different
    rhythm2 = [0.5] * 8

    similarity = lick_analyzer.calculate_similarity(
        intervals1, rhythm1, intervals2, rhythm2
    )

    print(f"\nIntervals 1: {intervals1}")
    print(f"Intervals 2: {intervals2}")
    print(f"Similarity: {similarity:.3f}")

    # Test style classification
    print("\n" + "=" * 70)
    print("STYLE CLASSIFICATION")
    print("=" * 70)

    bebop_intervals = [0, 2, 4, 5, 4, 2, 1, 0]  # Bebop-style chromatic
    bebop_rhythm = [0.5] * 8

    style_probs = lick_analyzer.classify_style(bebop_intervals, bebop_rhythm)

    print(f"\nTest lick: {bebop_intervals}")
    print(f"Style probabilities:")
    for style, prob in sorted(style_probs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {style:15} {prob:.3f}")

    # Test complexity
    print("\n" + "=" * 70)
    print("COMPLEXITY ANALYSIS")
    print("=" * 70)

    complexity = lick_analyzer.calculate_complexity(bebop_intervals, bebop_rhythm)

    print(f"\nComplexity metrics:")
    for key, value in complexity.items():
        if isinstance(value, float):
            print(f"  {key:20} {value:.2f}")
        else:
            print(f"  {key:20} {value}")

    # Test characteristic detection
    print("\n" + "=" * 70)
    print("CHARACTERISTIC DETECTION")
    print("=" * 70)

    characteristics = lick_analyzer.detect_characteristics(bebop_intervals, bebop_rhythm)

    print(f"\nDetected characteristics: {', '.join(characteristics)}")

    # Test database search
    print("\n" + "=" * 70)
    print("DATABASE SIMILARITY SEARCH")
    print("=" * 70)

    similar = lick_analyzer.find_similar_patterns(
        intervals=bebop_intervals,
        rhythm=bebop_rhythm,
        style="bebop",
        top_k=5
    )

    print(f"\nTop 5 similar bebop patterns:")
    for i, result in enumerate(similar, 1):
        print(f"{i}. {result.pattern_name}")
        print(f"   Overall: {result.similarity_score:.3f}")
        print(f"   Intervals: {result.interval_similarity:.3f}, Rhythm: {result.rhythm_similarity:.3f}, Contour: {result.contour_similarity:.3f}")
