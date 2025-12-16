"""AI Prompt Architecture Module

Centralized prompt management with:
- Genre-authentic system prompts
- Complexity-aware templates
- Generation metadata tracking
- Silent fallback with developer logging
"""

from .system_prompts import (
    GENRE_SYSTEM_PROMPTS,
    TASK_SYSTEM_PROMPTS,
    get_system_prompt,
)
from .metadata import GenerationMetadata, GenerationResult
from .builders import PromptBuilder

__all__ = [
    "GENRE_SYSTEM_PROMPTS",
    "TASK_SYSTEM_PROMPTS",
    "get_system_prompt",
    "GenerationMetadata",
    "GenerationResult",
    "PromptBuilder",
]
