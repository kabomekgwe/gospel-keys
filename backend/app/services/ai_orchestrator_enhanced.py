"""Enhanced AI Model Orchestrator with Fallback Tracking

Extends the base orchestrator with:
- Generation metadata tracking
- Silent fallback with developer logging
- Comprehensive error chain tracking
- Admin health metrics
"""

import json
import time
import logging
from typing import Any, Dict, Optional, Union

from app.services.ai_orchestrator import (
    AIOrchestrator as BaseOrchestrator,
    TaskType,
    GeminiModel,
    LOCAL_LLM_ENABLED,
    multi_model_service
)
from app.prompts.metadata import (
    GenerationMetadata,
    GenerationResult,
    ModelSource,
    FallbackMetrics
)

logger = logging.getLogger(__name__)

# In-memory metrics tracking (replace with Redis in production)
_fallback_metrics: Dict[str, int] = {
    "total_requests": 0,
    "fallback_count": 0,
    "template_count": 0,
}
_recent_failures: list = []
MAX_RECENT_FAILURES = 50


class EnhancedAIOrchestrator(BaseOrchestrator):
    """AI Orchestrator with enhanced fallback tracking and metadata

    Key features:
    - Silent fallback: Users see seamless experience
    - Developer logging: Full visibility into failures
    - Metadata tracking: Monitor model performance
    - Health metrics: Dashboard for monitoring
    """

    def _get_model_name(self, complexity: int) -> ModelSource:
        """Determine which model will be used based on complexity

        Args:
            complexity: Task complexity (1-10)

        Returns:
            ModelSource enum value
        """
        if LOCAL_LLM_ENABLED and (
            complexity <= self.COMPLEXITY_MEDIUM or settings.force_local_llm
        ):
            if complexity <= self.COMPLEXITY_SMALL:
                return ModelSource.PHI_3_5_MINI
            else:
                return ModelSource.LLAMA_3_3_70B
        else:
            # Gemini cloud fallback
            gemini_model = self.select_gemini_model(complexity)
            if gemini_model == GeminiModel.FLASH:
                return ModelSource.GEMINI_FLASH
            else:
                return ModelSource.GEMINI_PRO

    def _track_fallback_metric(
        self,
        task_type: TaskType,
        complexity: int,
        genre: Optional[str] = None
    ) -> None:
        """Track fallback metrics for monitoring

        Args:
            task_type: Type of task that failed
            complexity: Task complexity level
            genre: Musical genre (optional)
        """
        _fallback_metrics["fallback_count"] += 1

        # Track by task type
        task_key = f"task_{task_type.value}"
        _fallback_metrics[task_key] = _fallback_metrics.get(task_key, 0) + 1

        # Track by complexity
        complexity_key = f"complexity_{complexity}"
        _fallback_metrics[complexity_key] = _fallback_metrics.get(complexity_key, 0) + 1

        # Track by genre if provided
        if genre:
            genre_key = f"genre_{genre.lower()}"
            _fallback_metrics[genre_key] = _fallback_metrics.get(genre_key, 0) + 1

    def _log_recent_failure(
        self,
        task_type: TaskType,
        complexity: int,
        error_chain: list,
        genre: Optional[str] = None
    ) -> None:
        """Log recent failure for debugging

        Args:
            task_type: Type of task that failed
            complexity: Task complexity level
            error_chain: Chain of errors during fallback
            genre: Musical genre (optional)
        """
        failure_record = {
            "timestamp": time.time(),
            "task_type": task_type.value,
            "complexity": complexity,
            "genre": genre,
            "error_chain": error_chain
        }

        _recent_failures.append(failure_record)

        # Keep only recent failures
        if len(_recent_failures) > MAX_RECENT_FAILURES:
            _recent_failures.pop(0)

    async def generate_with_metadata(
        self,
        prompt: str,
        task_type: TaskType,
        complexity: Optional[int] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        cache_ttl_hours: int = 24,
        genre: Optional[str] = None,
        return_metadata: bool = False
    ) -> Union[Dict[str, Any], GenerationResult]:
        """Generate with complete metadata tracking

        This is the enhanced version that tracks everything for monitoring
        while maintaining seamless user experience.

        Args:
            prompt: Input prompt
            task_type: Type of task
            complexity: Task complexity (1-10, auto-detected if None)
            generation_config: Model-specific config
            cache_ttl_hours: Cache TTL
            genre: Musical genre for context
            return_metadata: If True, return GenerationResult with metadata
                           If False, return only content (user-facing)

        Returns:
            Content dict (if return_metadata=False) or
            GenerationResult with metadata (if return_metadata=True)
        """
        # Track request
        _fallback_metrics["total_requests"] += 1

        # Auto-detect complexity if not provided
        if complexity is None:
            complexity = self.TASK_COMPLEXITY.get(task_type, 5)

        # Default generation config
        if generation_config is None:
            generation_config = {
                "temperature": 0.7,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json",
            }

        start_time = time.time()
        error_chain = []
        fallback_count = 0

        # Determine primary model
        expected_model = self._get_model_name(complexity)

        # Check if we should use local LLM
        use_local = LOCAL_LLM_ENABLED and (
            complexity <= self.COMPLEXITY_MEDIUM or settings.force_local_llm
        )

        # === ATTEMPT 1: Primary Model (Local LLM or Gemini) ===
        if use_local:
            try:
                logger.info(
                    f"🤖 Using local multi-model LLM for {task_type.value}",
                    extra={
                        "complexity": complexity,
                        "genre": genre,
                        "expected_model": expected_model.value
                    }
                )

                result = multi_model_service.generate_structured(
                    prompt=prompt,
                    schema={},
                    complexity=complexity,
                    max_tokens=generation_config.get("max_output_tokens", 1024),
                    temperature=generation_config.get("temperature", 0.7),
                )

                generation_time_ms = (time.time() - start_time) * 1000

                # SUCCESS: Create metadata
                metadata = GenerationMetadata(
                    model_used=expected_model,
                    fallback_count=0,
                    generation_time_ms=generation_time_ms,
                    token_count=len(prompt) // 4 + len(str(result)) // 4,
                    quality_confidence=0.95,  # High confidence for primary model
                    complexity=complexity,
                    error_chain=[],
                    prompt_length=len(prompt)
                )

                logger.info(
                    f"✅ {task_type.value} generated successfully with {expected_model.value}",
                    extra={
                        "generation_time_ms": generation_time_ms,
                        "complexity": complexity,
                        "genre": genre
                    }
                )

                generation_result = GenerationResult(content=result, metadata=metadata)
                return generation_result if return_metadata else generation_result.to_user_response()

            except Exception as e:
                fallback_count += 1
                error_chain.append({
                    "model": expected_model.value,
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })

                logger.warning(
                    f"⚠️ Primary model failed for {task_type.value}",
                    extra={
                        "model": expected_model.value,
                        "error": str(e),
                        "complexity": complexity,
                        "genre": genre,
                        "prompt_length": len(prompt)
                    }
                )

        # === ATTEMPT 2: Gemini Fallback (if local failed) ===
        if fallback_count > 0 or not use_local:
            try:
                selected_model = self.select_gemini_model(complexity)

                if not self.gemini_models:
                    raise ValueError("No Gemini models available")

                if selected_model not in self.gemini_models:
                    if GeminiModel.FLASH in self.gemini_models:
                        selected_model = GeminiModel.FLASH
                    else:
                        raise ValueError("No fallback model available")

                model = self.gemini_models[selected_model]
                response = await model.generate_content_async(
                    prompt,
                    generation_config=generation_config
                )

                result = json.loads(response.text)
                generation_time_ms = (time.time() - start_time) * 1000

                # Map Gemini model to ModelSource
                if selected_model == GeminiModel.FLASH:
                    model_source = ModelSource.GEMINI_FLASH
                else:
                    model_source = ModelSource.GEMINI_PRO

                # SUCCESS: Create metadata
                metadata = GenerationMetadata(
                    model_used=model_source,
                    fallback_count=fallback_count,
                    generation_time_ms=generation_time_ms,
                    token_count=len(prompt) // 4 + len(str(result)) // 4,
                    quality_confidence=0.90 if fallback_count == 0 else 0.85,
                    complexity=complexity,
                    error_chain=error_chain,
                    prompt_length=len(prompt)
                )

                if fallback_count > 0:
                    logger.info(
                        f"✅ {task_type.value} succeeded with Gemini fallback",
                        extra={
                            "model": model_source.value,
                            "fallback_count": fallback_count,
                            "generation_time_ms": generation_time_ms
                        }
                    )
                    self._track_fallback_metric(task_type, complexity, genre)

                generation_result = GenerationResult(content=result, metadata=metadata)
                return generation_result if return_metadata else generation_result.to_user_response()

            except Exception as e:
                fallback_count += 1
                error_chain.append({
                    "model": "gemini",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })

                logger.error(
                    f"🚨 Gemini fallback failed for {task_type.value}",
                    extra={
                        "error": str(e),
                        "complexity": complexity,
                        "genre": genre,
                        "error_chain": error_chain
                    }
                )

        # === ATTEMPT 3: Template Fallback (guaranteed success) ===
        logger.error(
            f"🚨 ALL MODELS FAILED - Using template fallback for {task_type.value}",
            extra={
                "complexity": complexity,
                "genre": genre,
                "error_chain": error_chain,
                "fallback_count": fallback_count
            }
        )

        # Generate template-based fallback
        result = self._generate_template_fallback_enhanced(task_type, complexity, genre)
        generation_time_ms = (time.time() - start_time) * 1000

        # Track template usage
        _fallback_metrics["template_count"] += 1
        self._track_fallback_metric(task_type, complexity, genre)
        self._log_recent_failure(task_type, complexity, error_chain, genre)

        # Create metadata
        metadata = GenerationMetadata(
            model_used=ModelSource.TEMPLATE_FALLBACK,
            fallback_count=fallback_count,
            generation_time_ms=generation_time_ms,
            token_count=len(prompt) // 4 + len(str(result)) // 4,
            quality_confidence=0.70,  # Templates are acceptable but not personalized
            complexity=complexity,
            error_chain=error_chain,
            prompt_length=len(prompt)
        )

        generation_result = GenerationResult(content=result, metadata=metadata)

        # User sees seamless result, developer sees full context
        return generation_result if return_metadata else generation_result.to_user_response()

    def _generate_template_fallback_enhanced(
        self,
        task_type: TaskType,
        complexity: int,
        genre: Optional[str] = None
    ) -> Dict[str, Any]:
        """Enhanced template fallback with genre awareness

        Args:
            task_type: Type of task
            complexity: Task complexity
            genre: Musical genre

        Returns:
            Template-based content
        """
        # Delegate to base class template generation
        if task_type == TaskType.CURRICULUM_PLANNING:
            return self._generate_fallback_curriculum({}, 12)
        elif task_type in [TaskType.EXERCISE_GENERATION, TaskType.PROGRESSION_GENERATION]:
            return self._generate_fallback_exercise("progression", {"key": "C"})
        else:
            # Generic fallback
            return {
                "status": "template_generated",
                "message": f"Content generated from template for {task_type.value}",
                "genre": genre or "general",
                "complexity": complexity
            }

    def get_health_metrics(self) -> FallbackMetrics:
        """Get AI health metrics for monitoring dashboard

        Returns:
            FallbackMetrics with aggregated statistics
        """
        total = _fallback_metrics["total_requests"]
        fallbacks = _fallback_metrics["fallback_count"]
        templates = _fallback_metrics["template_count"]

        fallback_rate = fallbacks / total if total > 0 else 0.0

        # Aggregate by task type
        by_task_type = {}
        for key, value in _fallback_metrics.items():
            if key.startswith("task_"):
                task_name = key.replace("task_", "")
                task_total = value
                by_task_type[task_name] = value / total if total > 0 else 0.0

        # Aggregate by complexity
        by_complexity = {}
        for key, value in _fallback_metrics.items():
            if key.startswith("complexity_"):
                complexity_level = key.replace("complexity_", "")
                by_complexity[complexity_level] = value / total if total > 0 else 0.0

        # Aggregate by genre
        by_genre = {}
        for key, value in _fallback_metrics.items():
            if key.startswith("genre_"):
                genre_name = key.replace("genre_", "")
                by_genre[genre_name] = value / total if total > 0 else 0.0

        # Calculate average generation time (mock data - would need actual tracking)
        avg_generation_time_ms = 2000.0  # Placeholder

        return FallbackMetrics(
            total_requests=total,
            fallback_count=fallbacks,
            fallback_rate=fallback_rate,
            by_task_type=by_task_type,
            by_complexity=by_complexity,
            by_genre=by_genre,
            avg_generation_time_ms=avg_generation_time_ms,
            recent_failures=_recent_failures[-10:]  # Last 10 failures
        )


# Global enhanced orchestrator instance
enhanced_ai_orchestrator = EnhancedAIOrchestrator()
