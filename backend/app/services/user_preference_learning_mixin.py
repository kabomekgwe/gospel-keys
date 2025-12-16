"""User Preference Learning Mixin

Adds adaptive, personalized generation based on user behavior and preferences.

Features:
- User style profiling (harmonic preferences, complexity level, tempo range)
- Adaptive difficulty adjustment
- Personalized recommendations
- Learning from feedback (likes, dislikes, usage patterns)
- Multi-dimensional preference tracking

Tracks:
- Preferred chord types (maj7, m7, dom7, etc.)
- Preferred progressions (ii-V-I, I-IV-V, etc.)
- Tempo preferences
- Complexity preferences
- Genre mixing preferences
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class UserPreferenceLearningMixin:
    """
    Mixin to add user preference learning to any generator.

    Learns from user behavior to provide personalized generation:
    - Adapts to user's skill level
    - Learns preferred chord types and progressions
    - Adjusts complexity based on success rate
    - Provides personalized recommendations

    Usage:
        class MyGenerator(UserPreferenceLearningMixin, BaseGenreGenerator):
            pass

        # Now has:
        adapted_request = generator.adapt_to_user_preferences(request, user_id)
        profile = generator.get_user_profile(user_id)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preference_learning_enabled = True
        self._user_profiles = defaultdict(lambda: self._create_empty_profile())
        self._learning_stats = {
            "profiles_created": 0,
            "adaptations_made": 0,
            "feedback_received": 0
        }

        # Load existing user profiles
        self._load_user_profiles()

    # =====================================================================
    # USER PROFILE MANAGEMENT
    # =====================================================================

    def _create_empty_profile(self) -> Dict[str, Any]:
        """Create empty user profile with default values."""
        return {
            # Basic info
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "total_generations": 0,

            # Harmonic preferences
            "preferred_chord_types": defaultdict(int),  # maj7: 10, m7: 8, etc.
            "preferred_progressions": defaultdict(int),  # ii-V-I: 15, etc.
            "preferred_keys": defaultdict(int),  # C: 12, Gm: 8, etc.

            # Complexity preferences
            "complexity_level": 5,  # 1-10 scale
            "complexity_history": [],  # Track over time
            "success_rate": 1.0,  # % of successful generations

            # Style preferences
            "preferred_tempos": [],  # List of tempos used
            "avg_tempo": 120,
            "preferred_styles": defaultdict(int),  # traditional: 10, modern: 5

            # Behavior patterns
            "generation_times": [],  # When user generates music
            "session_lengths": [],  # How long each session
            "favorite_features": defaultdict(int),  # Which features used most

            # Feedback
            "liked_progressions": [],
            "disliked_progressions": [],
            "feedback_count": 0,

            # Learning metadata
            "learning_rate": 0.1,  # How quickly to adapt
            "confidence": 0.5  # Confidence in profile accuracy
        }

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's complete profile.

        Args:
            user_id: User identifier

        Returns:
            User profile dictionary with all preferences and stats
        """
        profile = self._user_profiles[user_id]

        # Update last active
        profile["last_active"] = datetime.now().isoformat()

        # Compute derived stats
        profile["skill_level"] = self._estimate_skill_level(profile)
        profile["dominant_style"] = self._get_dominant_style(profile)
        profile["favorite_key"] = self._get_favorite_key(profile)

        return dict(profile)  # Return copy

    # =====================================================================
    # ADAPTIVE GENERATION - Personalize Requests
    # =====================================================================

    def adapt_to_user_preferences(
        self,
        request: Any,
        user_id: str,
        adaptation_strength: float = 0.7
    ) -> Any:
        """
        Adapt generation request to user's preferences.

        Modifies request parameters based on learned preferences:
        - Adjusts complexity to user's level
        - Suggests preferred key if none specified
        - Adjusts tempo to user's typical range
        - Incorporates preferred chord types

        Args:
            request: Original generation request
            user_id: User identifier
            adaptation_strength: How much to adapt (0.0-1.0)
                0.0 = no adaptation, 1.0 = full adaptation

        Returns:
            Adapted request with personalized parameters
        """
        try:
            profile = self._user_profiles[user_id]

            # Update profile metadata
            profile["total_generations"] += 1
            profile["last_active"] = datetime.now().isoformat()

            # Adapt key if not specified
            if not request.key or request.key == "auto":
                preferred_key = self._get_favorite_key(profile)
                if preferred_key and adaptation_strength > 0.5:
                    request.key = preferred_key
                    logger.info(f"🎹 Adapted key to user favorite: {preferred_key}")

            # Adapt tempo if not specified
            if not request.tempo or request.tempo == 0:
                if profile["avg_tempo"] > 0:
                    request.tempo = int(profile["avg_tempo"])
                    logger.info(f"🎵 Adapted tempo to user average: {request.tempo} BPM")

            # Adapt complexity (if request has complexity parameter)
            if hasattr(request, "complexity") and adaptation_strength > 0.6:
                target_complexity = profile["complexity_level"]
                # Gradually increase complexity if user is successful
                if profile["success_rate"] > 0.8 and profile["total_generations"] > 10:
                    target_complexity = min(10, target_complexity + 1)
                request.complexity = target_complexity
                logger.info(f"🎯 Adapted complexity to user level: {target_complexity}")

            # Adapt style (if request has application/style parameter)
            if hasattr(request, "application") and not request.application:
                dominant_style = self._get_dominant_style(profile)
                if dominant_style:
                    request.application = dominant_style
                    logger.info(f"🎨 Adapted style to user preference: {dominant_style}")

            self._learning_stats["adaptations_made"] += 1
            return request

        except Exception as e:
            logger.warning(f"⚠️ Preference adaptation failed: {e}, using original request")
            return request

    # =====================================================================
    # LEARNING - Update from User Behavior
    # =====================================================================

    def learn_from_generation(
        self,
        user_id: str,
        request: Any,
        result: Any,
        feedback: Optional[str] = None
    ):
        """
        Learn from user's generation and feedback.

        Updates user profile based on:
        - What was generated (chords, key, tempo, style)
        - Whether generation was successful
        - User feedback (liked, disliked, used)

        Args:
            user_id: User identifier
            request: Original generation request
            result: Generation result
            feedback: Optional feedback ("liked", "disliked", "used", "rejected")
        """
        try:
            profile = self._user_profiles[user_id]

            # Update harmonic preferences
            if hasattr(result, "chords"):
                self._update_chord_preferences(profile, result.chords, feedback)

            if hasattr(result, "progression"):
                progression_str = ",".join(result.progression[:4])  # First 4 chords
                if feedback in ["liked", "used", None]:
                    profile["preferred_progressions"][progression_str] += 1

            # Update key preferences
            if hasattr(request, "key") and request.key:
                if feedback in ["liked", "used", None]:
                    profile["preferred_keys"][request.key] += 1

            # Update tempo preferences
            if hasattr(request, "tempo") and request.tempo:
                profile["preferred_tempos"].append(request.tempo)
                # Keep last 20 tempos
                profile["preferred_tempos"] = profile["preferred_tempos"][-20:]
                profile["avg_tempo"] = sum(profile["preferred_tempos"]) / len(profile["preferred_tempos"])

            # Update style preferences
            if hasattr(request, "application") and request.application:
                if feedback in ["liked", "used", None]:
                    profile["preferred_styles"][request.application] += 1

            # Update complexity history
            if hasattr(request, "complexity"):
                profile["complexity_history"].append(request.complexity)
                profile["complexity_history"] = profile["complexity_history"][-20:]
                # Adjust complexity level based on success
                if feedback in ["liked", "used"]:
                    profile["complexity_level"] = min(10, profile["complexity_level"] + 0.1)
                elif feedback == "disliked":
                    profile["complexity_level"] = max(1, profile["complexity_level"] - 0.2)

            # Update success rate
            if feedback:
                profile["feedback_count"] += 1
                success = feedback in ["liked", "used"]
                # Exponential moving average
                alpha = profile["learning_rate"]
                profile["success_rate"] = (
                    alpha * (1.0 if success else 0.0) +
                    (1 - alpha) * profile["success_rate"]
                )

            # Update feedback tracking
            if feedback == "liked":
                if hasattr(result, "progression"):
                    profile["liked_progressions"].append(result.progression)
                    profile["liked_progressions"] = profile["liked_progressions"][-10:]
            elif feedback == "disliked":
                if hasattr(result, "progression"):
                    profile["disliked_progressions"].append(result.progression)
                    profile["disliked_progressions"] = profile["disliked_progressions"][-10:]

            # Update confidence (more data = higher confidence)
            profile["confidence"] = min(1.0, profile["total_generations"] / 50.0)

            self._learning_stats["feedback_received"] += 1

            # Save periodically
            if profile["total_generations"] % 10 == 0:
                self._save_user_profiles()

            logger.info(f"📚 Learned from {user_id}: feedback={feedback}, success_rate={profile['success_rate']:.2f}")

        except Exception as e:
            logger.warning(f"⚠️ User preference learning failed: {e}")

    def _update_chord_preferences(
        self,
        profile: Dict[str, Any],
        chords: List[str],
        feedback: Optional[str]
    ):
        """Update user's preferred chord types based on what was generated."""
        for chord in chords:
            # Extract chord type (maj7, m7, dom7, etc.)
            chord_type = self._extract_chord_type(chord)
            if feedback in ["liked", "used", None]:
                profile["preferred_chord_types"][chord_type] += 1

    def _extract_chord_type(self, chord: str) -> str:
        """Extract chord type from chord symbol (e.g., Cmaj7 -> maj7)."""
        # Simple extraction (improve with proper chord parser)
        if "maj7" in chord:
            return "maj7"
        elif "m7" in chord:
            return "m7"
        elif "7" in chord:
            return "dom7"
        elif "m" in chord:
            return "minor"
        else:
            return "major"

    # =====================================================================
    # PERSONALIZED RECOMMENDATIONS
    # =====================================================================

    def get_personalized_recommendations(
        self,
        user_id: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized progression recommendations for user.

        Based on user's:
        - Skill level
        - Preferred keys
        - Preferred chord types
        - Recent activity

        Args:
            user_id: User identifier
            count: Number of recommendations

        Returns:
            List of recommendation dictionaries
        """
        profile = self._user_profiles[user_id]
        recommendations = []

        # Get user's favorite key
        favorite_key = self._get_favorite_key(profile)
        if not favorite_key:
            favorite_key = "C"

        # Get user's complexity level
        complexity = profile["complexity_level"]

        # Generate recommendations based on profile
        # 1. Based on liked progressions
        for liked in profile["liked_progressions"][:3]:
            recommendations.append({
                "type": "similar_to_liked",
                "key": favorite_key,
                "progression": liked,
                "reason": "Similar to your liked progressions",
                "confidence": 0.9
            })

        # 2. Based on complexity level
        recommendations.append({
            "type": "skill_appropriate",
            "key": favorite_key,
            "complexity": complexity,
            "reason": f"Matches your skill level ({int(complexity)}/10)",
            "confidence": 0.8
        })

        # 3. Based on preferred style
        dominant_style = self._get_dominant_style(profile)
        if dominant_style:
            recommendations.append({
                "type": "style_match",
                "key": favorite_key,
                "style": dominant_style,
                "reason": f"Your favorite style: {dominant_style}",
                "confidence": 0.85
            })

        # 4. Challenge recommendation (slightly higher complexity)
        if profile["success_rate"] > 0.75 and complexity < 10:
            recommendations.append({
                "type": "challenge",
                "key": favorite_key,
                "complexity": min(10, complexity + 1),
                "reason": "Level up! Try something more advanced",
                "confidence": 0.7
            })

        # 5. Explore new keys
        all_keys = ["C", "D", "E", "F", "G", "A", "B", "Cm", "Dm", "Em", "Fm", "Gm", "Am", "Bm"]
        unused_keys = [k for k in all_keys if k not in profile["preferred_keys"]]
        if unused_keys:
            recommendations.append({
                "type": "explore_key",
                "key": unused_keys[0],
                "reason": f"Try a new key: {unused_keys[0]}",
                "confidence": 0.6
            })

        return recommendations[:count]

    # =====================================================================
    # HELPER METHODS
    # =====================================================================

    def _estimate_skill_level(self, profile: Dict[str, Any]) -> str:
        """Estimate user's skill level from profile."""
        complexity = profile["complexity_level"]
        total_gens = profile["total_generations"]

        if total_gens < 5:
            return "beginner"
        elif complexity < 3:
            return "beginner"
        elif complexity < 6:
            return "intermediate"
        elif complexity < 8:
            return "advanced"
        else:
            return "expert"

    def _get_dominant_style(self, profile: Dict[str, Any]) -> Optional[str]:
        """Get user's most preferred style."""
        styles = profile["preferred_styles"]
        if not styles:
            return None
        return max(styles.items(), key=lambda x: x[1])[0]

    def _get_favorite_key(self, profile: Dict[str, Any]) -> Optional[str]:
        """Get user's most preferred key."""
        keys = profile["preferred_keys"]
        if not keys:
            return None
        return max(keys.items(), key=lambda x: x[1])[0]

    # =====================================================================
    # PERSISTENCE - Save/Load User Profiles
    # =====================================================================

    def _load_user_profiles(self):
        """Load user profiles from disk."""
        try:
            profiles_path = Path("data/user_profiles.json")
            if profiles_path.exists():
                with open(profiles_path, "r") as f:
                    data = json.load(f)
                    self._user_profiles = defaultdict(
                        lambda: self._create_empty_profile(),
                        {k: self._deserialize_profile(v) for k, v in data.items()}
                    )
                    logger.info(f"📚 Loaded {len(self._user_profiles)} user profiles")
        except Exception as e:
            logger.warning(f"⚠️ Could not load user profiles: {e}")

    def _deserialize_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize profile from JSON (convert defaultdicts)."""
        profile = self._create_empty_profile()
        profile.update(data)
        # Convert dicts back to defaultdicts
        profile["preferred_chord_types"] = defaultdict(int, data.get("preferred_chord_types", {}))
        profile["preferred_progressions"] = defaultdict(int, data.get("preferred_progressions", {}))
        profile["preferred_keys"] = defaultdict(int, data.get("preferred_keys", {}))
        profile["preferred_styles"] = defaultdict(int, data.get("preferred_styles", {}))
        profile["favorite_features"] = defaultdict(int, data.get("favorite_features", {}))
        return profile

    def _save_user_profiles(self):
        """Save user profiles to disk."""
        try:
            profiles_path = Path("data/user_profiles.json")
            profiles_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert defaultdicts to regular dicts for JSON serialization
            data = {
                user_id: {
                    **profile,
                    "preferred_chord_types": dict(profile["preferred_chord_types"]),
                    "preferred_progressions": dict(profile["preferred_progressions"]),
                    "preferred_keys": dict(profile["preferred_keys"]),
                    "preferred_styles": dict(profile["preferred_styles"]),
                    "favorite_features": dict(profile["favorite_features"])
                }
                for user_id, profile in self._user_profiles.items()
            }

            with open(profiles_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"💾 Saved {len(self._user_profiles)} user profiles")
        except Exception as e:
            logger.warning(f"⚠️ Could not save user profiles: {e}")

    def get_preference_learning_stats(self) -> Dict[str, Any]:
        """Get preference learning statistics."""
        return {
            "enabled": self._preference_learning_enabled,
            "profiles_created": len(self._user_profiles),
            "adaptations_made": self._learning_stats["adaptations_made"],
            "feedback_received": self._learning_stats["feedback_received"],
            "avg_confidence": (
                sum(p["confidence"] for p in self._user_profiles.values()) / len(self._user_profiles)
                if self._user_profiles else 0.0
            ),
            "total_generations": sum(p["total_generations"] for p in self._user_profiles.values())
        }

    def reset_preference_learning_stats(self):
        """Reset preference learning statistics."""
        self._learning_stats = {
            "profiles_created": 0,
            "adaptations_made": 0,
            "feedback_received": 0
        }
        logger.info("📊 Preference learning statistics reset")
