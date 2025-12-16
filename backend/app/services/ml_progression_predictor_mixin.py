"""ML Progression Predictor Mixin

Adds collaborative filtering and ML-powered chord progression prediction to any generator.

Features:
- Collaborative filtering based on user behavior
- Genre-aware progression prediction
- Contextual chord suggestions
- Learning from successful generations
- Popularity-based recommendations

Algorithm:
- User-Item Matrix: Users x Chord Progressions
- Similarity: Cosine similarity between users
- Prediction: Weighted average of similar users' preferences
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MLProgressionPredictorMixin:
    """
    Mixin to add ML-powered chord progression prediction to any generator.

    Uses collaborative filtering to predict chord progressions based on:
    - User behavior (what progressions users like)
    - Genre characteristics
    - Progression popularity
    - Contextual similarity

    Usage:
        class MyGenerator(MLProgressionPredictorMixin, BaseGenreGenerator):
            pass

        # Now has:
        predicted_chords = generator.predict_next_chord(current_progression, context)
        suggestions = generator.get_progression_suggestions(key, style)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ml_predictor_enabled = True
        self._progression_cache = {}
        self._user_preferences = defaultdict(lambda: defaultdict(int))
        self._progression_popularity = defaultdict(int)
        self._ml_stats = {
            "predictions_made": 0,
            "cache_hits": 0,
            "learning_updates": 0
        }

        # Load existing ML data if available
        self._load_ml_data()

    # =====================================================================
    # CHORD PROGRESSION PREDICTION - Collaborative Filtering
    # =====================================================================

    def predict_next_chord(
        self,
        current_progression: List[str],
        context: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """
        Predict next chord(s) in progression using ML.

        Uses collaborative filtering based on:
        - Previous chord context (last 2-3 chords)
        - Genre patterns
        - User preferences
        - Popularity data

        Args:
            current_progression: List of chord symbols already in progression
            context: Dict with 'key', 'genre', 'user_id', 'style', etc.

        Returns:
            List of (chord, confidence) tuples, sorted by confidence
            Example: [("Cmaj7", 0.85), ("Am7", 0.72), ("Dm7", 0.65)]
        """
        try:
            # Extract context
            key = context.get("key", "C")
            user_id = context.get("user_id", "default")
            style = context.get("style", "standard")

            # Get last 2-3 chords for context window
            context_window = current_progression[-3:] if len(current_progression) >= 3 else current_progression

            # Check cache
            cache_key = f"{self.genre_name}:{key}:{','.join(context_window)}:{style}"
            if cache_key in self._progression_cache:
                self._ml_stats["cache_hits"] += 1
                return self._progression_cache[cache_key]

            # Predict using multiple strategies
            predictions = self._collaborative_filtering_predict(context_window, key, user_id)
            genre_predictions = self._genre_pattern_predict(context_window, key, style)
            popularity_predictions = self._popularity_predict(context_window, key)

            # Combine predictions (ensemble)
            combined = self._combine_predictions(
                predictions,
                genre_predictions,
                popularity_predictions,
                weights=[0.4, 0.4, 0.2]  # CF, Genre, Popularity
            )

            # Cache result
            self._progression_cache[cache_key] = combined
            self._ml_stats["predictions_made"] += 1

            logger.info(f"🤖 ML predicted {len(combined)} next chords for {context_window}")
            return combined

        except Exception as e:
            logger.warning(f"⚠️ ML prediction failed: {e}, using fallback")
            return self._fallback_predict(current_progression, key)

    def _collaborative_filtering_predict(
        self,
        context_window: List[str],
        key: str,
        user_id: str
    ) -> List[Tuple[str, float]]:
        """
        Collaborative filtering: predict based on similar users' preferences.

        Algorithm:
        1. Find users with similar progression preferences
        2. Get their next chord choices after context_window
        3. Weight by user similarity
        4. Return top candidates
        """
        # Get user's previous progressions
        user_prefs = self._user_preferences.get(user_id, {})

        # Find similar users (simplified - in production, use proper similarity metrics)
        similar_users = self._find_similar_users(user_id, user_prefs)

        # Aggregate next chord choices from similar users
        next_chord_scores = defaultdict(float)
        for similar_user_id, similarity in similar_users:
            similar_prefs = self._user_preferences.get(similar_user_id, {})
            for progression, count in similar_prefs.items():
                prog_chords = progression.split(",")
                # Check if context matches
                if self._context_matches(context_window, prog_chords):
                    # Get next chord
                    context_len = len(context_window)
                    if len(prog_chords) > context_len:
                        next_chord = prog_chords[context_len]
                        next_chord_scores[next_chord] += similarity * count

        # Normalize scores to probabilities
        if not next_chord_scores:
            return []

        total = sum(next_chord_scores.values())
        predictions = [
            (chord, score / total)
            for chord, score in next_chord_scores.items()
        ]

        # Sort by confidence
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:5]  # Top 5 predictions

    def _genre_pattern_predict(
        self,
        context_window: List[str],
        key: str,
        style: str
    ) -> List[Tuple[str, float]]:
        """
        Genre-specific pattern prediction.

        Uses known genre patterns (ii-V-I for jazz, I-IV-V for blues, etc.)
        """
        # Get genre-specific patterns
        patterns = self._get_genre_patterns(key, style)

        predictions = []
        for pattern in patterns:
            pattern_chords = pattern["chords"]
            confidence = pattern.get("confidence", 0.5)

            # Check if context matches pattern
            if self._context_matches(context_window, pattern_chords):
                context_len = len(context_window)
                if len(pattern_chords) > context_len:
                    next_chord = pattern_chords[context_len]
                    predictions.append((next_chord, confidence))

        return predictions

    def _popularity_predict(
        self,
        context_window: List[str],
        key: str
    ) -> List[Tuple[str, float]]:
        """
        Popularity-based prediction: most commonly used next chords.
        """
        # Get popularity data for progressions starting with context
        context_str = ",".join(context_window)

        next_chord_counts = defaultdict(int)
        for progression, count in self._progression_popularity.items():
            if progression.startswith(context_str):
                prog_chords = progression.split(",")
                if len(prog_chords) > len(context_window):
                    next_chord = prog_chords[len(context_window)]
                    next_chord_counts[next_chord] += count

        # Normalize
        if not next_chord_counts:
            return []

        total = sum(next_chord_counts.values())
        predictions = [
            (chord, count / total)
            for chord, count in next_chord_counts.items()
        ]

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:5]

    def _combine_predictions(
        self,
        *prediction_lists: List[Tuple[str, float]],
        weights: List[float] = None
    ) -> List[Tuple[str, float]]:
        """
        Ensemble: combine predictions from multiple strategies.

        Args:
            prediction_lists: Multiple lists of (chord, confidence) tuples
            weights: Weight for each prediction list

        Returns:
            Combined predictions sorted by weighted confidence
        """
        if weights is None:
            weights = [1.0 / len(prediction_lists)] * len(prediction_lists)

        combined_scores = defaultdict(float)

        for pred_list, weight in zip(prediction_lists, weights):
            for chord, confidence in pred_list:
                combined_scores[chord] += confidence * weight

        # Sort by combined score
        predictions = [
            (chord, score)
            for chord, score in combined_scores.items()
        ]
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions[:5]  # Top 5

    # =====================================================================
    # PROGRESSION SUGGESTIONS - Context-Aware
    # =====================================================================

    def get_progression_suggestions(
        self,
        key: str,
        style: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get full progression suggestions for given key and style.

        Args:
            key: Musical key (e.g., "C", "Am")
            style: Style descriptor (e.g., "traditional", "modern", "jazz")
            context: Optional context (user_id, complexity, etc.)

        Returns:
            List of progression suggestions with metadata
            Example:
            [
                {
                    "progression": ["Cmaj7", "Am7", "Dm7", "G7"],
                    "name": "Jazz ii-V-I",
                    "confidence": 0.85,
                    "popularity": 127,
                    "genre": "Jazz"
                }
            ]
        """
        context = context or {}
        user_id = context.get("user_id", "default")

        suggestions = []

        # Get genre-specific patterns
        patterns = self._get_genre_patterns(key, style)
        for pattern in patterns:
            suggestions.append({
                "progression": pattern["chords"],
                "name": pattern["name"],
                "confidence": pattern.get("confidence", 0.7),
                "popularity": self._get_progression_popularity(pattern["chords"]),
                "genre": self.genre_name,
                "source": "genre_pattern"
            })

        # Get user-preferred progressions
        user_prefs = self._user_preferences.get(user_id, {})
        for progression, count in sorted(user_prefs.items(), key=lambda x: x[1], reverse=True)[:3]:
            chords = progression.split(",")
            suggestions.append({
                "progression": chords,
                "name": "Your favorite",
                "confidence": 0.9,
                "popularity": count,
                "genre": self.genre_name,
                "source": "user_preference"
            })

        # Sort by confidence * popularity
        suggestions.sort(key=lambda x: x["confidence"] * (x["popularity"] + 1), reverse=True)

        return suggestions[:10]  # Top 10 suggestions

    # =====================================================================
    # LEARNING - Update from User Behavior
    # =====================================================================

    def learn_from_generation(
        self,
        user_id: str,
        progression: List[str],
        feedback: Optional[str] = None
    ):
        """
        Learn from successful generation.

        Updates:
        - User preference matrix
        - Progression popularity
        - Genre patterns (if highly rated)

        Args:
            user_id: User identifier
            progression: Generated chord progression
            feedback: Optional feedback ("liked", "used", "rejected")
        """
        try:
            progression_str = ",".join(progression)

            # Update user preferences
            if feedback in ["liked", "used", None]:  # Positive feedback
                self._user_preferences[user_id][progression_str] += 1
                self._progression_popularity[progression_str] += 1
                self._ml_stats["learning_updates"] += 1

                logger.info(f"📚 ML learned from {user_id}: {progression_str[:50]}...")

            # Save periodically
            if self._ml_stats["learning_updates"] % 10 == 0:
                self._save_ml_data()

        except Exception as e:
            logger.warning(f"⚠️ ML learning failed: {e}")

    # =====================================================================
    # HELPER METHODS
    # =====================================================================

    def _context_matches(self, context: List[str], pattern: List[str]) -> bool:
        """Check if context matches start of pattern."""
        if len(context) > len(pattern):
            return False
        return pattern[:len(context)] == context

    def _find_similar_users(
        self,
        user_id: str,
        user_prefs: Dict[str, int],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find top-k similar users using cosine similarity.

        Args:
            user_id: Target user
            user_prefs: Target user's preferences
            top_k: Number of similar users to return

        Returns:
            List of (similar_user_id, similarity_score) tuples
        """
        similarities = []

        for other_user_id, other_prefs in self._user_preferences.items():
            if other_user_id == user_id:
                continue

            # Compute cosine similarity
            similarity = self._cosine_similarity(user_prefs, other_prefs)
            similarities.append((other_user_id, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, prefs1: Dict[str, int], prefs2: Dict[str, int]) -> float:
        """Compute cosine similarity between two preference dictionaries."""
        # Get common keys
        common_keys = set(prefs1.keys()) & set(prefs2.keys())
        if not common_keys:
            return 0.0

        # Compute dot product and magnitudes
        dot_product = sum(prefs1[k] * prefs2[k] for k in common_keys)
        mag1 = sum(v ** 2 for v in prefs1.values()) ** 0.5
        mag2 = sum(v ** 2 for v in prefs2.values()) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def _get_genre_patterns(self, key: str, style: str) -> List[Dict[str, Any]]:
        """
        Get genre-specific chord progression patterns.

        This is genre-specific and should be overridden or configured per genre.
        """
        # Default patterns (override in subclass)
        return [
            {
                "name": "Basic Progression",
                "chords": [f"{key}", "F", "G", f"{key}"],
                "confidence": 0.7
            }
        ]

    def _get_progression_popularity(self, progression: List[str]) -> int:
        """Get popularity count for a progression."""
        progression_str = ",".join(progression)
        return self._progression_popularity.get(progression_str, 0)

    def _fallback_predict(
        self,
        current_progression: List[str],
        key: str
    ) -> List[Tuple[str, float]]:
        """Fallback prediction when ML fails."""
        # Simple rule-based fallback
        common_chords = [f"{key}", "F", "G", "Am", "Dm", "Em"]
        return [(chord, 0.5) for chord in common_chords[:3]]

    # =====================================================================
    # PERSISTENCE - Save/Load ML Data
    # =====================================================================

    def _load_ml_data(self):
        """Load ML data from disk."""
        try:
            ml_data_path = Path("data/ml_progression_data.json")
            if ml_data_path.exists():
                with open(ml_data_path, "r") as f:
                    data = json.load(f)
                    self._user_preferences = defaultdict(
                        lambda: defaultdict(int),
                        {k: defaultdict(int, v) for k, v in data.get("user_preferences", {}).items()}
                    )
                    self._progression_popularity = defaultdict(int, data.get("progression_popularity", {}))
                    logger.info(f"📚 Loaded ML data: {len(self._user_preferences)} users")
        except Exception as e:
            logger.warning(f"⚠️ Could not load ML data: {e}")

    def _save_ml_data(self):
        """Save ML data to disk."""
        try:
            ml_data_path = Path("data/ml_progression_data.json")
            ml_data_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "user_preferences": {k: dict(v) for k, v in self._user_preferences.items()},
                "progression_popularity": dict(self._progression_popularity),
                "updated_at": datetime.now().isoformat()
            }

            with open(ml_data_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"💾 Saved ML data: {len(self._user_preferences)} users")
        except Exception as e:
            logger.warning(f"⚠️ Could not save ML data: {e}")

    def get_ml_predictor_stats(self) -> Dict[str, Any]:
        """Get ML predictor statistics."""
        return {
            "enabled": self._ml_predictor_enabled,
            "predictions_made": self._ml_stats["predictions_made"],
            "cache_hits": self._ml_stats["cache_hits"],
            "learning_updates": self._ml_stats["learning_updates"],
            "users_tracked": len(self._user_preferences),
            "progressions_tracked": len(self._progression_popularity),
            "cache_size": len(self._progression_cache)
        }

    def reset_ml_predictor_stats(self):
        """Reset ML predictor statistics."""
        self._ml_stats = {
            "predictions_made": 0,
            "cache_hits": 0,
            "learning_updates": 0
        }
        logger.info("📊 ML predictor statistics reset")
