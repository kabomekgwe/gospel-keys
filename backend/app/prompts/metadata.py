"""Generation Metadata Tracking

Tracks AI generation results for developer visibility without exposing
failures to end users (silent fallback approach).
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelSource(str, Enum):
    """Source of generated content"""
    PHI_3_5_MINI = "phi-3.5-mini"           # Local, fast (complexity 1-4)
    LLAMA_3_3_70B = "llama-3.3-70b"         # Local, quality (complexity 5-7)
    GEMINI_FLASH = "gemini-1.5-flash"       # Cloud, fast (complexity 1-4)
    GEMINI_PRO = "gemini-1.5-pro"           # Cloud, quality (complexity 5-10)
    TEMPLATE_FALLBACK = "template"          # Rule-based fallback
    UNKNOWN = "unknown"


class GenerationMetadata(BaseModel):
    """Metadata about AI generation for monitoring/debugging

    This is logged for developer visibility but NOT shown to end users.
    """
    model_used: ModelSource
    fallback_count: int = Field(
        default=0,
        description="Number of fallbacks before success (0 = primary worked)"
    )
    generation_time_ms: float = Field(
        description="Total generation time in milliseconds"
    )
    token_count: Optional[int] = Field(
        default=None,
        description="Approximate token count (input + output)"
    )
    quality_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in output quality (1.0 = highest, AI-generated)"
    )
    complexity: int = Field(
        ge=1,
        le=10,
        description="Task complexity level (1-10)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_chain: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Chain of errors during fallback attempts"
    )
    prompt_length: int = Field(
        default=0,
        description="Length of input prompt in characters"
    )

    class Config:
        use_enum_values = True


class GenerationResult(BaseModel):
    """Complete generation result with content and metadata"""
    content: Dict[str, Any] = Field(
        description="Generated content (user-facing)"
    )
    metadata: GenerationMetadata = Field(
        description="Generation metadata (developer-facing)"
    )

    def to_user_response(self) -> Dict[str, Any]:
        """Return ONLY content (hide metadata from users)

        This is what students see - no mention of failures or fallbacks.
        """
        return self.content

    def to_admin_response(self) -> Dict[str, Any]:
        """Return content WITH metadata (for admin/developer monitoring)

        This is what you see in logs/dashboards - full transparency.
        """
        return {
            "content": self.content,
            "meta": {
                "model": self.metadata.model_used,
                "fallbacks": self.metadata.fallback_count,
                "quality_confidence": self.metadata.quality_confidence,
                "generation_time_ms": self.metadata.generation_time_ms,
                "complexity": self.metadata.complexity,
                "timestamp": self.metadata.timestamp.isoformat(),
                "token_count": self.metadata.token_count,
                "error_chain": self.metadata.error_chain,
            }
        }

    def has_fallback(self) -> bool:
        """Check if this result used fallback"""
        return self.metadata.fallback_count > 0

    def is_template_based(self) -> bool:
        """Check if this result used template fallback"""
        return self.metadata.model_used == ModelSource.TEMPLATE_FALLBACK

    def get_quality_tier(self) -> str:
        """Get quality tier for monitoring

        Returns:
            "excellent" (AI, no fallback)
            "good" (AI, after fallback)
            "acceptable" (template)
        """
        if self.is_template_based():
            return "acceptable"
        elif self.metadata.fallback_count == 0:
            return "excellent"
        else:
            return "good"


class FallbackMetrics(BaseModel):
    """Aggregated fallback metrics for monitoring dashboard"""
    total_requests: int
    fallback_count: int
    fallback_rate: float = Field(
        description="Percentage of requests that fell back (0.0-1.0)"
    )
    by_task_type: Dict[str, float] = Field(
        default_factory=dict,
        description="Fallback rate by task type"
    )
    by_complexity: Dict[str, float] = Field(
        default_factory=dict,
        description="Fallback rate by complexity level"
    )
    by_genre: Dict[str, float] = Field(
        default_factory=dict,
        description="Fallback rate by genre"
    )
    avg_generation_time_ms: float
    recent_failures: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent failure details for debugging"
    )
