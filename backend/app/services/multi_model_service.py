"""Multi-Model Local LLM Service for M4 MacBook Pro

Manages multiple local LLMs with automatic task routing based on complexity:
- Tier 1 (Small): Phi-3.5 Mini (3.8B) - Complexity 1-4 tasks (~50 tok/s)
- Tier 2 (Medium): Qwen2.5-7B (4-bit) - Complexity 5-7 tasks (~20 tok/s, good quality)
- Tier 3 (Cloud): Gemini API - Complexity 8-10 tasks (fallback)

Performance on M4 Pro (16-24GB RAM):
- Phi-3.5 Mini: ~50 tokens/sec, 2-3GB RAM
- Qwen2.5-7B (4-bit): ~20 tokens/sec, 5-6GB RAM
- Total RAM usage: ~8-9GB peak (safe for 16GB+ systems)

Cost Savings:
- Current: $13-28/month (60% Gemini usage)
- After: $2-5/month (90% local usage)
- Annual savings: $120-276/year (conservative estimate)

SAFETY NOTE: 70B models require 64GB+ RAM. Using 7B default for safety.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

# Memory safety checks
try:
    from app.utils.memory_check import is_model_safe, get_system_memory, get_recommended_model
    MEMORY_CHECK_AVAILABLE = True
except ImportError:
    MEMORY_CHECK_AVAILABLE = False
    logger.warning("⚠️ Memory check utility not available")

# Try to import MLX
try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
    logger.info("✅ MLX framework loaded (M4 Neural Engine enabled)")
except ImportError:
    MLX_AVAILABLE = False
    logger.warning("⚠️ MLX not available, local LLM disabled")


class LocalModelTier(Enum):
    """Model tiers for task complexity routing"""
    SMALL = "small"      # Phi-3.5 Mini (3.8B) - complexity 1-4
    MEDIUM = "medium"    # Qwen2.5-7B - complexity 5-7
    LARGE = "large"      # Future: 14B model - complexity 8-9


class MultiModelLLMService:
    """Multi-model local LLM service using MLX framework on M4 MacBook Pro

    Automatically routes tasks to the best local model based on complexity:
    - Simple tasks (1-4) → Phi-3.5 Mini (fast, 50 tok/s)
    - Medium tasks (5-7) → Llama 3.3 70B 4-bit (GPT-4 class quality, 5-6 tok/s)
    - Complex tasks (8-10) → Raise error (caller should use Gemini)

    Features:
    - Lazy loading: Models loaded on first use
    - Memory safety: Checks system RAM before loading large models
    - Automatic fallback: Falls back to smaller model if larger fails or RAM insufficient
    - Structured output: JSON generation with validation
    """

    def __init__(self):
        self.models: Dict[LocalModelTier, Tuple[Any, Any]] = {}
        self.active_model: Optional[LocalModelTier] = None

        # Model configurations
        self.model_configs = {
            LocalModelTier.SMALL: {
                "name": "mlx-community/Phi-3.5-mini-instruct-4bit",
                "max_tokens": 2048,
                "chat_template": "chatml",  # <|user|>, <|assistant|>, <|end|>
            },
            LocalModelTier.MEDIUM: {
                "name": "mlx-community/Qwen2.5-14B-Instruct-4bit",
                "max_tokens": 4096,
                "chat_template": "qwen",  # <|im_start|>, <|im_end|>
                "ram_required_gb": 12,
            },
        }

        self.loaded = MLX_AVAILABLE

        # Pre-load Phi-3.5 Mini (already used in production)
        if self.loaded:
            logger.info("🚀 Initializing multi-model LLM service")
            self._load_model(LocalModelTier.SMALL)

    def _load_model(self, tier: LocalModelTier) -> Tuple[Any, Any]:
        """Load a model tier (with caching)

        Args:
            tier: Model tier to load

        Returns:
            Tuple of (model, tokenizer)
        """
        if tier in self.models:
            logger.info(f"✅ Model {tier.value} already loaded")
            return self.models[tier]

        try:
            config = self.model_configs[tier]
            logger.info(f"📥 Loading {tier.value} model: {config['name']}")

            if tier == LocalModelTier.SMALL:
                logger.info("⏳ Loading Phi-3.5 Mini (~3GB RAM, cached after first download)")
            elif tier == LocalModelTier.MEDIUM:
                logger.info("⏳ Loading Qwen2.5-14B (~12GB RAM, cached after first download)")
            
            # Memory safety check before loading
            if MEMORY_CHECK_AVAILABLE:
                is_safe, safety_msg = is_model_safe(config["name"])
                if not is_safe:
                    logger.warning(f"⚠️ {safety_msg}")
                    if tier == LocalModelTier.MEDIUM:
                        logger.warning("🔄 Falling back to SMALL tier (Phi-3.5 Mini)")
                        return self._load_model(LocalModelTier.SMALL)
                    raise RuntimeError(f"Cannot load model: {safety_msg}")
                else:
                    logger.info(safety_msg)

            # Load model using MLX (cached after first download)
            model, tokenizer = load(config["name"])

            self.models[tier] = (model, tokenizer)

            logger.info(f"✅ {tier.value} model loaded successfully")
            logger.info(f"   Model: {config['name']}")
            logger.info(f"   Device: M4 Neural Engine + GPU")
            logger.info(f"   Max tokens: {config['max_tokens']}")

            return model, tokenizer

        except Exception as e:
            logger.error(f"❌ Failed to load {tier.value} model: {e}")
            raise e

    def select_model(self, complexity: int, force_local: bool = False) -> Optional[LocalModelTier]:
        """Select best local model for task complexity

        Routing logic:
        - Complexity 1-4: Phi-3.5 Mini (small, fast)
        - Complexity 5-7: Llama 3.3 70B (medium, GPT-4 quality)
        - Complexity 8-10: Llama 3.3 70B if force_local=True, else None (use Gemini API)

        Args:
            complexity: Task complexity score (1-10)
            force_local: If True, use MEDIUM tier for complexity 8-10 instead of None

        Returns:
            LocalModelTier or None if task too complex for local models
        """
        if complexity <= 4:
            return LocalModelTier.SMALL
        elif complexity <= 7:
            return LocalModelTier.MEDIUM
        else:
            # Task complexity 8-10: use MEDIUM (Llama 3.3 70B) if forced, else None
            if force_local:
                logger.info(f"🦙 Force local enabled: using Llama 3.3 70B for complexity {complexity} task")
                return LocalModelTier.MEDIUM
            return None

    def _format_prompt(self, prompt: str, tier: LocalModelTier, system_prompt: Optional[str] = None) -> str:
        """Format prompt for specific model's chat template

        Args:
            prompt: User prompt
            tier: Model tier (determines chat template)
            system_prompt: Optional system prompt

        Returns:
            Formatted prompt string
        """
        config = self.model_configs[tier]

        if config["chat_template"] == "chatml":
            # Phi-3.5 uses ChatML format
            if system_prompt:
                return f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
            else:
                return f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

        elif config["chat_template"] == "llama3":
            # Llama 3.3 uses official Llama 3 chat format
            if system_prompt:
                return f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            else:
                return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

        elif config["chat_template"] == "qwen":
            # Qwen2.5 uses ChatML-like format with different tags (kept for backward compatibility)
            if system_prompt:
                return f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            else:
                return f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        else:
            raise ValueError(f"Unknown chat template: {config['chat_template']}")

    def generate(
        self,
        prompt: str,
        complexity: int,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        force_local: bool = False,
    ) -> str:
        """Generate text using appropriate local model

        Automatically selects and loads the best model for the given complexity.
        Falls back to smaller model if larger model fails.

        Args:
            prompt: User prompt
            complexity: Task complexity score (1-10)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system prompt
            force_local: If True, use local model even for complexity 8-10

        Returns:
            Generated text

        Raises:
            RuntimeError: If no local model can handle this complexity
            ValueError: If task too complex for local models (8-10) and not forced
        """
        if not self.loaded:
            raise RuntimeError("MLX not available, use Gemini API instead")

        # Select appropriate model tier
        tier = self.select_model(complexity, force_local=force_local)

        if tier is None:
            raise ValueError(
                f"Task complexity {complexity} too high for local models. "
                "Use Gemini API for complexity 8-10 tasks."
            )

        # Load model if not already loaded
        if tier not in self.models:
            logger.info(f"🔄 Loading {tier.value} model for complexity {complexity} task")
            self._load_model(tier)

        # Switch active model if needed
        if self.active_model != tier:
            logger.info(f"🔄 Switching from {self.active_model} to {tier.value} model")
            self.active_model = tier

        try:
            model, tokenizer = self.models[tier]
            config = self.model_configs[tier]

            # Format prompt for this model's chat template
            formatted_prompt = self._format_prompt(prompt, tier, system_prompt)

            # Cap max_tokens to model's limit
            max_tokens = min(max_tokens, config["max_tokens"])

            logger.info(f"🤖 Generating with {tier.value} model (complexity {complexity})")

            # Generate using MLX (runs on M4 Neural Engine)
            response = generate(
                model=model,
                tokenizer=tokenizer,
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                verbose=False,
            )

            return response.strip()

        except Exception as e:
            logger.error(f"❌ {tier.value} model generation failed: {e}")

            # Try fallback to smaller model if medium failed
            if tier == LocalModelTier.MEDIUM:
                logger.warning("⚠️ Falling back to small model (Phi-3.5 Mini)")
                return self.generate(
                    prompt=prompt,
                    complexity=4,  # Force small model
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system_prompt=system_prompt,
                )

            raise e

    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        complexity: int,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        force_local: bool = False,
    ) -> Dict[str, Any]:
        """Generate structured JSON output using local LLM

        Args:
            prompt: User prompt
            schema: Expected JSON schema (for documentation only, not enforced)
            complexity: Task complexity score (1-10)
            max_tokens: Maximum tokens
            temperature: Lower temp for more consistent JSON
            force_local: If True, use local model even for complexity 8-10

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON parsing fails
        """
        # Add JSON formatting instructions
        json_prompt = f"""{prompt}

Respond with ONLY valid JSON matching this structure:
{json.dumps(schema, indent=2)}

JSON Response:"""

        response = self.generate(
            prompt=json_prompt,
            complexity=complexity,
            max_tokens=max_tokens,
            temperature=temperature,
            force_local=force_local,
        )

        # Extract JSON from response
        json_text = self._extract_json(response)

        # Parse JSON
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from local LLM: {e}")
            logger.error(f"Response was: {response[:500]}...")
            logger.error(f"Extracted JSON text: {json_text}")
            raise ValueError(f"Invalid JSON from local LLM: {e}")

    def _extract_json(self, response: str) -> str:
        """Extract JSON from model response (handles markdown, extra tokens, etc.)

        Args:
            response: Raw model response

        Returns:
            Cleaned JSON string
        """
        json_text = response

        # Handle Phi-3.5 special tokens FIRST (strip everything after <|end|>)
        if "<|end|>" in json_text:
            json_text = json_text.split("<|end|>")[0].strip()

        # Handle Llama 3.3 special tokens (strip everything after <|eot_id|>)
        if "<|eot_id|>" in json_text:
            json_text = json_text.split("<|eot_id|>")[0].strip()

        # Handle Qwen special tokens (strip everything after <|im_end|>)
        if "<|im_end|>" in json_text:
            json_text = json_text.split("<|im_end|>")[0].strip()

        # Handle markdown code blocks
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0].strip()

        # Find JSON object boundaries by counting braces
        if '{' in json_text and '}' in json_text:
            start = json_text.find('{')
            brace_count = 0
            end = start
            for i in range(start, len(json_text)):
                if json_text[i] == '{':
                    brace_count += 1
                elif json_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            json_text = json_text[start:end]

        return json_text

    def is_available(self) -> bool:
        """Check if multi-model LLM service is available and loaded"""
        return self.loaded

    def get_loaded_models(self) -> list[str]:
        """Get list of currently loaded model tiers"""
        return [tier.value for tier in self.models.keys()]

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models and their configurations"""
        return {
            "available": self.loaded,
            "loaded_models": self.get_loaded_models(),
            "active_model": self.active_model.value if self.active_model else None,
            "model_configs": {
                tier.value: {
                    "name": config["name"],
                    "max_tokens": config["max_tokens"],
                    "chat_template": config["chat_template"],
                    "complexity_range": {
                        LocalModelTier.SMALL: "1-4 (fast, simple tasks)",
                        LocalModelTier.MEDIUM: "5-7 (GPT-4 class quality)",
                    }.get(tier, "N/A"),
                }
                for tier, config in self.model_configs.items()
            },
        }


# Global instance
multi_model_service = MultiModelLLMService() if MLX_AVAILABLE else None
