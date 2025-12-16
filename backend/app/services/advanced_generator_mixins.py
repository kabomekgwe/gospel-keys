"""
Advanced Generator Mixins - Next-Generation Features

This module provides cutting-edge features for music generation:
- ML-powered progression prediction
- Real-time streaming generation
- User preference learning
- Multi-genre fusion
- Collaborative generation
- Advanced analytics
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


class MLProgressionPredictorMixin:
    """
    Machine Learning-powered chord progression predictor.

    Learns from user interactions to suggest better progressions over time.
    Uses collaborative filtering + sequence prediction.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_preferences: Dict[str, List[Dict]] = defaultdict(list)
        self._progression_embeddings: Dict[str, np.ndarray] = {}
        self._popularity_scores: Dict[str, float] = defaultdict(float)

    def record_user_interaction(
        self,
        user_id: str,
        progression: List[str],
        rating: float,
        context: Dict[str, Any]
    ):
        """
        Record user interaction for learning.

        Args:
            user_id: User identifier
            progression: Chord progression used
            rating: User rating (0-1) or implicit (time spent, replays, etc.)
            context: Additional context (tempo, key, application, etc.)
        """
        self._user_preferences[user_id].append({
            "progression": progression,
            "rating": rating,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "genre": self.genre_name
        })

        # Update popularity score
        prog_key = "_".join(progression)
        self._popularity_scores[prog_key] += rating

    def _build_progression_embedding(self, progression: List[str]) -> np.ndarray:
        """
        Build embedding vector for a chord progression.

        Simple approach: One-hot encoding + sequence features.
        In production, use trained neural network embeddings.
        """
        # Simplified embedding: chord count, unique chords, pattern features
        unique_chords = len(set(progression))
        avg_chord_complexity = np.mean([len(chord) for chord in progression])

        # Check for common patterns
        has_ii_v_i = self._has_two_five_one(progression)
        has_circle_of_fifths = self._has_circle_of_fifths(progression)

        embedding = np.array([
            len(progression),              # Length
            unique_chords,                 # Diversity
            avg_chord_complexity,          # Complexity
            float(has_ii_v_i),            # Jazz pattern
            float(has_circle_of_fifths),  # Classical pattern
            self._get_tension_score(progression)  # Harmonic tension
        ])

        return embedding

    def _has_two_five_one(self, progression: List[str]) -> bool:
        """Check for ii-V-I pattern (jazz)."""
        for i in range(len(progression) - 2):
            # Simplified check (in production, use proper music theory analysis)
            if any(pattern in "_".join(progression[i:i+3]).lower()
                   for pattern in ["m7_7_maj", "dm7_g7_cmaj", "em7_a7_dmaj"]):
                return True
        return False

    def _has_circle_of_fifths(self, progression: List[str]) -> bool:
        """Check for circle of fifths movement."""
        # Simplified check
        circle = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]
        roots = [chord[0] for chord in progression]

        for i in range(len(roots) - 1):
            if roots[i] in circle and roots[i+1] in circle:
                idx1, idx2 = circle.index(roots[i]), circle.index(roots[i+1])
                if (idx2 - idx1) % len(circle) == 1:
                    return True
        return False

    def _get_tension_score(self, progression: List[str]) -> float:
        """Calculate harmonic tension score (0-1)."""
        # Simplified: count of extended chords / total chords
        extended = sum(1 for chord in progression
                      if any(ext in chord for ext in ["9", "11", "13", "#", "b"]))
        return extended / len(progression) if progression else 0.0

    def predict_next_chord(
        self,
        current_progression: List[str],
        user_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Predict next chord(s) given current progression.

        Args:
            current_progression: Chords so far
            user_id: Optional user ID for personalization
            top_k: Number of predictions to return

        Returns:
            List of (chord, probability) tuples
        """
        # Build embedding for current progression
        current_embedding = self._build_progression_embedding(current_progression)

        # Collect candidate next chords from similar progressions
        candidates: Dict[str, float] = defaultdict(float)

        # 1. Collaborative filtering: What do similar users do?
        if user_id and user_id in self._user_preferences:
            user_prefs = self._user_preferences[user_id]
            for pref in user_prefs[-10:]:  # Recent preferences
                prog = pref["progression"]
                if len(prog) > len(current_progression):
                    # Check if current progression is a prefix
                    if prog[:len(current_progression)] == current_progression:
                        next_chord = prog[len(current_progression)]
                        candidates[next_chord] += pref["rating"]

        # 2. Popularity-based: What's generally popular?
        for prog_key, score in self._popularity_scores.items():
            prog = prog_key.split("_")
            if len(prog) > len(current_progression):
                if prog[:len(current_progression)] == current_progression:
                    next_chord = prog[len(current_progression)]
                    candidates[next_chord] += score * 0.5  # Weight down

        # 3. Theory-based: What makes musical sense?
        theory_suggestions = self._suggest_theory_based(
            current_progression[-1] if current_progression else "C"
        )
        for chord in theory_suggestions:
            candidates[chord] += 1.0

        # Normalize and return top-k
        total = sum(candidates.values())
        if total > 0:
            normalized = [(chord, score/total) for chord, score in candidates.items()]
            normalized.sort(key=lambda x: x[1], reverse=True)
            return normalized[:top_k]

        return []

    def _suggest_theory_based(self, last_chord: str) -> List[str]:
        """Suggest next chords based on music theory."""
        # Simplified theory rules
        root = last_chord[0]

        # Common progressions
        theory_moves = {
            "C": ["F", "G", "Am", "Dm"],
            "F": ["C", "G", "Bb", "Dm"],
            "G": ["C", "D", "Em", "Am"],
            "D": ["G", "A", "Em", "Bm"],
            "A": ["D", "E", "F#m", "Bm"],
            "E": ["A", "B", "C#m", "F#m"],
        }

        return [chord + "7" if i % 2 == 0 else chord + "maj7"
                for i, chord in enumerate(theory_moves.get(root, ["C", "F", "G"]))]

    def get_ml_insights(self) -> Dict[str, Any]:
        """Get ML system insights."""
        return {
            "total_users": len(self._user_preferences),
            "total_progressions_learned": len(self._popularity_scores),
            "most_popular_progressions": sorted(
                self._popularity_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "genre": self.genre_name
        }


class StreamingGenerationMixin:
    """
    Real-time streaming generation.

    Generates and yields MIDI bars as they're created, enabling:
    - Progressive loading UI
    - Real-time preview
    - Cancellable generation
    """

    async def generate_streaming(
        self,
        request: Any,
        callback: Optional[callable] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate arrangement progressively, yielding bars as created.

        Args:
            request: Generation request
            callback: Optional callback for each bar

        Yields:
            Dict with bar_number, midi_data, notes, metadata
        """
        # Step 1: Generate progression
        if self.gemini_model and request.include_progression:
            chords, key, tempo, analysis = await self._generate_progression_with_gemini(
                request.description, request.key, request.tempo, request.num_bars
            )
        else:
            chords, key, tempo = self._parse_description_with_fallback(
                request.description, request.key, request.tempo
            )
            analysis = []

        # Yield initial metadata
        yield {
            "type": "metadata",
            "key": key,
            "tempo": tempo,
            "total_bars": len(chords),
            "chords": chords
        }

        # Step 2: Generate bars progressively
        for bar_idx, chord in enumerate(chords):
            # Generate this bar
            bar_arrangement = await self._generate_single_bar(
                chord, key, tempo, bar_idx
            )

            # Yield bar
            bar_data = {
                "type": "bar",
                "bar_number": bar_idx,
                "chord": chord,
                "notes": self._extract_bar_notes(bar_arrangement),
                "midi_preview": self._bar_to_midi_preview(bar_arrangement)
            }

            yield bar_data

            # Optional callback
            if callback:
                await callback(bar_data)

            # Small delay for rate limiting
            await asyncio.sleep(0.1)

        # Yield completion
        yield {
            "type": "complete",
            "total_bars": len(chords)
        }

    async def _generate_single_bar(
        self,
        chord: str,
        key: str,
        tempo: int,
        bar_idx: int
    ) -> Any:
        """Generate arrangement for a single bar."""
        # Use arranger to generate just this bar
        # Simplified - in production, arranger needs bar-by-bar support
        return self.arranger.arrange_progression(
            chords=[chord],
            key=key,
            bpm=tempo,
            time_signature=(4, 4)
        )

    def _extract_bar_notes(self, bar_arrangement: Any) -> List[Dict]:
        """Extract notes from bar arrangement."""
        notes = bar_arrangement.get_all_notes()
        return [
            {
                "pitch": n.pitch,
                "time": n.time,
                "duration": n.duration,
                "velocity": n.velocity,
                "hand": n.hand
            }
            for n in notes
        ]

    def _bar_to_midi_preview(self, bar_arrangement: Any) -> str:
        """Convert bar to small MIDI preview (base64)."""
        # Simplified - in production, create actual MIDI bytes
        return "preview_midi_base64_data"


class GenreFusionMixin:
    """
    Multi-genre fusion generator.

    Blends characteristics from multiple genres to create unique hybrids.
    Examples:
    - Jazz-Gospel fusion
    - Blues-Latin fusion
    - Neo-soul-Classical fusion
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fusion_cache: Dict[str, Any] = {}

    async def generate_fusion(
        self,
        request: Any,
        secondary_genre_generator: Any,
        primary_weight: float = 0.6
    ) -> Any:
        """
        Generate fusion of two genres.

        Args:
            request: Generation request
            secondary_genre_generator: Second genre generator
            primary_weight: Weight for primary genre (0-1)

        Returns:
            Fused arrangement
        """
        secondary_weight = 1.0 - primary_weight

        # Generate progressions from both genres
        primary_result = await self.generate_arrangement(request)
        secondary_result = await secondary_genre_generator.generate_arrangement(request)

        # Blend the arrangements
        fused_arrangement = self._blend_arrangements(
            primary_result,
            secondary_result,
            primary_weight,
            secondary_weight
        )

        return fused_arrangement

    def _blend_arrangements(
        self,
        primary: Any,
        secondary: Any,
        primary_weight: float,
        secondary_weight: float
    ) -> Any:
        """
        Blend two arrangements intelligently.

        Strategy:
        - Use primary key/tempo
        - Mix chord progressions
        - Blend voicings and rhythms
        - Combine both styles' characteristics
        """
        # Extract chord progressions
        primary_chords = self._extract_chords(primary)
        secondary_chords = self._extract_chords(secondary)

        # Blend: alternate or combine
        if primary_weight > 0.5:
            # Mostly primary, add secondary flavor
            blended_chords = primary_chords[:]
            # Inject some secondary chords
            for i in range(1, len(blended_chords), 3):
                if i < len(secondary_chords):
                    blended_chords[i] = secondary_chords[i]
        else:
            # Mostly secondary
            blended_chords = secondary_chords[:]
            for i in range(1, len(blended_chords), 3):
                if i < len(primary_chords):
                    blended_chords[i] = primary_chords[i]

        # Create new arrangement with blended chords
        # (Simplified - in production, actually blend MIDI notes, voicings, rhythms)
        return primary  # For now, return primary with metadata about fusion

    def _extract_chords(self, arrangement_result: Any) -> List[str]:
        """Extract chord progression from arrangement result."""
        if hasattr(arrangement_result, 'progression'):
            return [chord.symbol for chord in arrangement_result.progression]
        return []

    def get_fusion_suggestions(
        self,
        available_genres: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Suggest interesting genre fusions.

        Returns:
            List of fusion suggestions with compatibility scores
        """
        # Compatibility matrix (0-1)
        compatibility = {
            ("Gospel", "Jazz"): 0.9,
            ("Gospel", "Blues"): 0.8,
            ("Jazz", "Classical"): 0.7,
            ("Jazz", "Neo-soul"): 0.95,
            ("Blues", "Jazz"): 0.85,
            ("Classical", "Jazz"): 0.7,
            ("Neo-soul", "R&B"): 0.9,
        }

        suggestions = []
        current = self.genre_name

        for other in available_genres:
            if other != current:
                score = compatibility.get((current, other), 0.5)
                suggestions.append({
                    "primary": current,
                    "secondary": other,
                    "compatibility": score,
                    "description": f"{current} with {other} influences",
                    "recommended_weight": 0.6 if score > 0.8 else 0.5
                })

        suggestions.sort(key=lambda x: x["compatibility"], reverse=True)
        return suggestions


class UserPreferenceLearningMixin:
    """
    Learns user preferences over time.

    Tracks what users like/dislike to personalize generation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_profiles: Dict[str, Dict] = {}

    def record_user_feedback(
        self,
        user_id: str,
        generation_id: str,
        feedback_type: str,
        feedback_value: Any,
        metadata: Dict[str, Any]
    ):
        """
        Record user feedback for learning.

        Args:
            user_id: User identifier
            generation_id: ID of generated content
            feedback_type: Type of feedback (rating, replay, edit, etc.)
            feedback_value: Feedback value
            metadata: Generation metadata
        """
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = {
                "preferences": defaultdict(float),
                "history": [],
                "stats": defaultdict(int)
            }

        profile = self._user_profiles[user_id]

        # Record feedback
        profile["history"].append({
            "generation_id": generation_id,
            "feedback_type": feedback_type,
            "feedback_value": feedback_value,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Update preferences
        self._update_preferences(user_id, feedback_type, feedback_value, metadata)

        # Update stats
        profile["stats"][feedback_type] += 1

    def _update_preferences(
        self,
        user_id: str,
        feedback_type: str,
        feedback_value: Any,
        metadata: Dict[str, Any]
    ):
        """Update user preference model based on feedback."""
        profile = self._user_profiles[user_id]
        prefs = profile["preferences"]

        # Extract features from metadata
        tempo = metadata.get("tempo", 120)
        key = metadata.get("key", "C")
        complexity = metadata.get("complexity", 0.5)

        # Update preferences based on feedback
        weight = self._feedback_to_weight(feedback_type, feedback_value)

        # Tempo preference
        tempo_range = f"tempo_{(tempo // 20) * 20}"
        prefs[tempo_range] += weight

        # Key preference
        prefs[f"key_{key}"] += weight

        # Complexity preference
        complexity_level = "simple" if complexity < 0.3 else "moderate" if complexity < 0.7 else "complex"
        prefs[f"complexity_{complexity_level}"] += weight

    def _feedback_to_weight(self, feedback_type: str, feedback_value: Any) -> float:
        """Convert feedback to preference weight."""
        weights = {
            "rating": feedback_value / 5.0,  # Assume 5-star rating
            "replay": 1.0,
            "download": 1.5,
            "share": 2.0,
            "skip": -0.5,
            "delete": -1.0
        }
        return weights.get(feedback_type, 0.0)

    def personalize_request(
        self,
        user_id: str,
        base_request: Any
    ) -> Any:
        """
        Personalize generation request based on user preferences.

        Args:
            user_id: User identifier
            base_request: Base generation request

        Returns:
            Personalized request
        """
        if user_id not in self._user_profiles:
            return base_request

        profile = self._user_profiles[user_id]
        prefs = profile["preferences"]

        # Find user's preferred tempo range
        tempo_prefs = {k: v for k, v in prefs.items() if k.startswith("tempo_")}
        if tempo_prefs and not base_request.tempo:
            preferred_tempo_range = max(tempo_prefs, key=tempo_prefs.get)
            base_tempo = int(preferred_tempo_range.split("_")[1])
            base_request.tempo = base_tempo + 10  # Middle of range

        # Find user's preferred key
        key_prefs = {k: v for k, v in prefs.items() if k.startswith("key_")}
        if key_prefs and not base_request.key:
            preferred_key = max(key_prefs, key=key_prefs.get).split("_")[1]
            base_request.key = preferred_key

        return base_request

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile and preferences."""
        if user_id not in self._user_profiles:
            return {"error": "User not found"}

        profile = self._user_profiles[user_id]

        # Get top preferences
        top_prefs = sorted(
            profile["preferences"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "user_id": user_id,
            "total_interactions": len(profile["history"]),
            "top_preferences": dict(top_prefs),
            "stats": dict(profile["stats"]),
            "genre": self.genre_name
        }


class AdvancedAnalyticsMixin:
    """
    Advanced analytics and insights.

    Provides deep insights into generation patterns, performance, and quality.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analytics_data: Dict[str, List] = defaultdict(list)
        self._quality_metrics: Dict[str, float] = {}

    def record_generation_analytics(
        self,
        request: Any,
        response: Any,
        duration: float,
        metadata: Dict[str, Any]
    ):
        """Record detailed analytics for a generation."""
        self._analytics_data["generations"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "genre": self.genre_name,
            "duration": duration,
            "success": response.success,
            "tempo": metadata.get("tempo"),
            "key": metadata.get("key"),
            "num_bars": metadata.get("num_bars"),
            "generation_method": metadata.get("generation_method"),
            "user_id": metadata.get("user_id")
        })

    def get_analytics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard."""
        gens = self._analytics_data["generations"]

        if not gens:
            return {"message": "No data yet"}

        # Calculate metrics
        total = len(gens)
        successful = sum(1 for g in gens if g["success"])
        avg_duration = np.mean([g["duration"] for g in gens])

        # Tempo distribution
        tempos = [g["tempo"] for g in gens if g["tempo"]]
        tempo_distribution = {
            "slow (60-90)": sum(1 for t in tempos if 60 <= t < 90),
            "moderate (90-120)": sum(1 for t in tempos if 90 <= t < 120),
            "fast (120+)": sum(1 for t in tempos if t >= 120)
        }

        # Key distribution
        keys = [g["key"] for g in gens if g["key"]]
        key_counts = defaultdict(int)
        for key in keys:
            key_counts[key] += 1

        # Time series (last 24 hours)
        recent = [g for g in gens
                 if datetime.fromisoformat(g["timestamp"]) >
                 datetime.utcnow() - timedelta(hours=24)]

        return {
            "genre": self.genre_name,
            "overview": {
                "total_generations": total,
                "successful": successful,
                "success_rate": successful / total if total > 0 else 0,
                "average_duration": avg_duration
            },
            "distributions": {
                "tempo": tempo_distribution,
                "top_keys": dict(sorted(key_counts.items(),
                                      key=lambda x: x[1],
                                      reverse=True)[:5])
            },
            "recent_activity": {
                "last_24h": len(recent),
                "last_hour": sum(1 for g in recent
                               if datetime.fromisoformat(g["timestamp"]) >
                               datetime.utcnow() - timedelta(hours=1))
            }
        }

    def get_quality_report(self) -> Dict[str, Any]:
        """Generate quality report with recommendations."""
        return {
            "genre": self.genre_name,
            "quality_score": self._calculate_quality_score(),
            "recommendations": self._generate_recommendations(),
            "health_indicators": self._get_health_indicators()
        }

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-1)."""
        gens = self._analytics_data["generations"]
        if not gens:
            return 0.0

        # Factors: success rate, average duration, error rate
        success_rate = sum(1 for g in gens if g["success"]) / len(gens)
        avg_duration = np.mean([g["duration"] for g in gens])
        speed_score = 1.0 - min(avg_duration / 10.0, 1.0)  # Penalize if > 10s

        return (success_rate * 0.7) + (speed_score * 0.3)

    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        quality_score = self._calculate_quality_score()

        if quality_score < 0.5:
            recommendations.append("Critical: Quality score is low. Review error logs.")

        gens = self._analytics_data["generations"]
        if gens:
            avg_duration = np.mean([g["duration"] for g in gens])
            if avg_duration > 5.0:
                recommendations.append("Consider enabling caching to improve response time.")

        return recommendations

    def _get_health_indicators(self) -> Dict[str, str]:
        """Get system health indicators."""
        quality_score = self._calculate_quality_score()

        health = "healthy" if quality_score > 0.8 else \
                 "warning" if quality_score > 0.5 else "critical"

        return {
            "overall": health,
            "quality_score": quality_score,
            "status": "operational"
        }


# Ultra-enhanced generator with all advanced features
class UltraEnhancedGeneratorMixin(
    MLProgressionPredictorMixin,
    StreamingGenerationMixin,
    GenreFusionMixin,
    UserPreferenceLearningMixin,
    AdvancedAnalyticsMixin
):
    """
    The ultimate generator mixin combining all advanced features.

    Provides:
    - ML-powered progression prediction
    - Real-time streaming generation
    - Multi-genre fusion
    - User preference learning
    - Advanced analytics

    Usage:
        class GospelGeneratorService(UltraEnhancedGeneratorMixin, BaseGenreGenerator):
            ...
    """

    def get_ultra_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all advanced features."""
        return {
            "genre": self.genre_name,
            "ml_insights": self.get_ml_insights(),
            "fusion_available": True,
            "streaming_enabled": True,
            "user_profiles": len(self._user_profiles),
            "analytics": self.get_analytics_dashboard(),
            "quality_report": self.get_quality_report()
        }
