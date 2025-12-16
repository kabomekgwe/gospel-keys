"""
Advanced mixins for generator enhancement.

Provides optional features that can be mixed into BaseGenreGenerator:
- Caching for Gemini responses
- Logging and metrics
- Rate limiting
- A/B testing hooks
"""

import logging
import hashlib
import time
from typing import Optional, Dict, Any
from functools import wraps
from datetime import datetime, timedelta


# Configure logger
logger = logging.getLogger(__name__)


class CachingMixin:
    """
    Adds caching capability to generators.

    Caches Gemini API responses to reduce API calls and costs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache: Dict[str, tuple] = {}  # key -> (response, timestamp)
        self._cache_ttl_seconds = 3600  # 1 hour default

    def _cache_key(self, description: str, key: Optional[str], tempo: Optional[int], num_bars: int) -> str:
        """Generate cache key from request parameters."""
        data = f"{self.genre_name}|{description}|{key}|{tempo}|{num_bars}"
        return hashlib.md5(data.encode()).hexdigest()

    def _get_cached_progression(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int],
        num_bars: int
    ) -> Optional[tuple]:
        """Get cached progression if available and not expired."""
        cache_key = self._cache_key(description, key, tempo, num_bars)

        if cache_key in self._cache:
            response, timestamp = self._cache[cache_key]

            # Check if cache is still valid
            if time.time() - timestamp < self._cache_ttl_seconds:
                logger.info(f"Cache hit for {self.genre_name} progression")
                return response
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
                logger.debug(f"Cache expired for {cache_key}")

        return None

    def _set_cached_progression(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int],
        num_bars: int,
        response: tuple
    ):
        """Store progression in cache."""
        cache_key = self._cache_key(description, key, tempo, num_bars)
        self._cache[cache_key] = (response, time.time())
        logger.debug(f"Cached {self.genre_name} progression: {cache_key}")

    def clear_cache(self):
        """Clear all cached progressions."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {count} cached progressions")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_items": len(self._cache),
            "ttl_seconds": self._cache_ttl_seconds,
            "genre": self.genre_name
        }


class LoggingMixin:
    """
    Adds comprehensive logging and metrics to generators.

    Logs all generation requests, timing, and outcomes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generation_count = 0
        self._total_generation_time = 0.0
        self._error_count = 0
        self._gemini_call_count = 0

    def _log_generation_start(self, request: Any):
        """Log generation request start."""
        logger.info(f"{self.genre_name} generation started", extra={
            "genre": self.genre_name,
            "description": request.description[:100],
            "key": request.key,
            "tempo": request.tempo,
            "num_bars": request.num_bars,
            "timestamp": datetime.utcnow().isoformat()
        })

    def _log_generation_complete(self, duration_seconds: float, success: bool):
        """Log generation completion."""
        self._generation_count += 1
        self._total_generation_time += duration_seconds

        if success:
            logger.info(f"{self.genre_name} generation completed", extra={
                "genre": self.genre_name,
                "duration_seconds": duration_seconds,
                "success": True
            })
        else:
            self._error_count += 1
            logger.error(f"{self.genre_name} generation failed", extra={
                "genre": self.genre_name,
                "duration_seconds": duration_seconds,
                "success": False,
                "error_count": self._error_count
            })

    def _log_gemini_call(self, description: str):
        """Log Gemini API call."""
        self._gemini_call_count += 1
        logger.debug(f"Gemini API call #{self._gemini_call_count}", extra={
            "genre": self.genre_name,
            "description": description[:50],
            "call_number": self._gemini_call_count
        })

    def get_metrics(self) -> Dict[str, Any]:
        """Get generator metrics."""
        avg_time = (
            self._total_generation_time / self._generation_count
            if self._generation_count > 0
            else 0.0
        )

        return {
            "genre": self.genre_name,
            "total_generations": self._generation_count,
            "total_generation_time": self._total_generation_time,
            "average_generation_time": avg_time,
            "error_count": self._error_count,
            "gemini_calls": self._gemini_call_count,
            "error_rate": (
                self._error_count / self._generation_count
                if self._generation_count > 0
                else 0.0
            )
        }

    def reset_metrics(self):
        """Reset all metrics counters."""
        self._generation_count = 0
        self._total_generation_time = 0.0
        self._error_count = 0
        self._gemini_call_count = 0
        logger.info(f"Reset metrics for {self.genre_name}")


class RateLimitingMixin:
    """
    Adds rate limiting to generators.

    Prevents excessive API calls to Gemini.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._call_timestamps = []
        self._max_calls_per_minute = 60
        self._max_calls_per_hour = 1000

    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded."""
        now = time.time()

        # Remove old timestamps (older than 1 hour)
        self._call_timestamps = [
            ts for ts in self._call_timestamps
            if now - ts < 3600
        ]

        # Check per-minute limit
        recent_calls = [
            ts for ts in self._call_timestamps
            if now - ts < 60
        ]

        if len(recent_calls) >= self._max_calls_per_minute:
            logger.warning(f"Rate limit exceeded (per-minute) for {self.genre_name}")
            return False

        # Check per-hour limit
        if len(self._call_timestamps) >= self._max_calls_per_hour:
            logger.warning(f"Rate limit exceeded (per-hour) for {self.genre_name}")
            return False

        return True

    def _record_api_call(self):
        """Record an API call for rate limiting."""
        self._call_timestamps.append(time.time())

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        now = time.time()

        recent_minute = [
            ts for ts in self._call_timestamps
            if now - ts < 60
        ]

        recent_hour = [
            ts for ts in self._call_timestamps
            if now - ts < 3600
        ]

        return {
            "genre": self.genre_name,
            "calls_last_minute": len(recent_minute),
            "calls_last_hour": len(recent_hour),
            "max_per_minute": self._max_calls_per_minute,
            "max_per_hour": self._max_calls_per_hour,
            "remaining_minute": self._max_calls_per_minute - len(recent_minute),
            "remaining_hour": self._max_calls_per_hour - len(recent_hour)
        }


class ABTestingMixin:
    """
    Adds A/B testing capability to generators.

    Allows testing different generation strategies.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ab_variant: Optional[str] = None
        self._ab_test_active = False

    def set_ab_variant(self, variant: str):
        """Set A/B test variant (e.g., 'control', 'variant_a')."""
        self._ab_variant = variant
        self._ab_test_active = True
        logger.info(f"A/B test variant set to '{variant}' for {self.genre_name}")

    def disable_ab_test(self):
        """Disable A/B testing."""
        self._ab_test_active = False
        self._ab_variant = None
        logger.info(f"A/B testing disabled for {self.genre_name}")

    def _get_ab_variant_params(self) -> Dict[str, Any]:
        """Get parameters based on A/B variant."""
        if not self._ab_test_active or self._ab_variant is None:
            return {}

        # Example: Different temperature settings for variants
        variants = {
            "control": {"temperature": 0.7},
            "variant_a": {"temperature": 0.9},
            "variant_b": {"temperature": 0.5}
        }

        return variants.get(self._ab_variant, {})

    def get_ab_status(self) -> Dict[str, Any]:
        """Get A/B testing status."""
        return {
            "genre": self.genre_name,
            "ab_test_active": self._ab_test_active,
            "variant": self._ab_variant
        }


# Combined mixin for full-featured generator
class EnhancedGeneratorMixin(CachingMixin, LoggingMixin, RateLimitingMixin, ABTestingMixin):
    """
    Combines all enhancement mixins.

    Provides caching, logging, metrics, rate limiting, and A/B testing.

    Usage:
        class GospelGeneratorService(EnhancedGeneratorMixin, BaseGenreGenerator):
            ...
    """

    def get_full_status(self) -> Dict[str, Any]:
        """Get comprehensive status including all mixin features."""
        return {
            "genre": self.genre_name,
            "cache": self.get_cache_stats(),
            "metrics": self.get_metrics(),
            "rate_limit": self.get_rate_limit_status(),
            "ab_testing": self.get_ab_status()
        }
