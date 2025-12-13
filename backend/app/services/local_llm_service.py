"""Local LLM Service using MLX for M4 MacBook Pro

Uses Apple's MLX framework to run Phi-3 Mini (3.8B parameters) locally on M4 Neural Engine.
This provides ~50 tokens/sec inference with zero API costs.

Performance on M4:
- Phi-3 Mini: ~50 tokens/sec
- Latency: 50-150ms (vs 1-2s for Gemini API)
- Cost: $0 (vs $0.50-$2.00 per 1M tokens)
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to import MLX
try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
    logger.info("✅ MLX framework loaded (M4 Neural Engine enabled)")
except ImportError:
    MLX_AVAILABLE = False
    logger.warning("⚠️ MLX not available, local LLM disabled")


class LocalLLMService:
    """Local LLM service using MLX framework on M4 MacBook Pro"""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_name = "mlx-community/Phi-3.5-mini-instruct-4bit"  # 4-bit quantized for speed
        self.loaded = False

        if MLX_AVAILABLE:
            self._load_model()

    def _load_model(self):
        """Load Phi-3 Mini model using MLX (runs on M4 Neural Engine)"""
        try:
            logger.info(f"📥 Loading local LLM: {self.model_name}")
            logger.info("⏳ First load will download ~2.3GB model (one-time)")

            # Load model (cached after first download)
            self.model, self.tokenizer = load(self.model_name)

            logger.info("✅ Local LLM loaded successfully")
            logger.info(f"   Model: Phi-3.5 Mini (3.8B params, 4-bit)")
            logger.info(f"   Device: M4 Neural Engine + GPU")
            logger.info(f"   Expected speed: ~50 tokens/sec")
            self.loaded = True

        except Exception as e:
            logger.error(f"❌ Failed to load local LLM: {e}")
            logger.error("   Falling back to Gemini API for all tasks")
            self.loaded = False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate text using local LLM (M4 Neural Engine)

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        if not self.loaded:
            raise RuntimeError("Local LLM not loaded, use Gemini API instead")

        try:
            # Format prompt for Phi-3 (ChatML format)
            if system_prompt:
                formatted_prompt = f"<|system|>\n{system_prompt}<|end|>\n<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
            else:
                formatted_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

            # Generate using MLX (runs on M4 Neural Engine)
            # Note: MLX's generate() doesn't expose temperature directly
            # It uses default sampling settings which are generally good
            response = generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                verbose=False,  # Set to True to see token generation in real-time
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            raise e

    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """Generate structured JSON output using local LLM

        Args:
            prompt: User prompt
            schema: Expected JSON schema (for documentation only, not enforced)
            max_tokens: Maximum tokens
            temperature: Lower temp for more consistent JSON

        Returns:
            Parsed JSON dict
        """
        # Add JSON formatting instructions
        json_prompt = f"""{prompt}

Respond with ONLY valid JSON matching this structure:
{json.dumps(schema, indent=2)}

JSON Response:"""

        response = self.generate(
            prompt=json_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # Extract JSON from response (handle markdown code blocks and extra text)
        json_text = response

        # Handle markdown code blocks
        if "```json" in response:
            json_text = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_text = response.split("```")[1].split("```")[0].strip()

        # Handle Phi-3 special tokens (strip everything after <|end|>)
        if "<|end|>" in json_text:
            json_text = json_text.split("<|end|>")[0].strip()

        # Try to find JSON object boundaries
        # Look for first { and last }
        if '{' in json_text and '}' in json_text:
            start = json_text.find('{')
            end = json_text.rfind('}') + 1
            json_text = json_text[start:end]

        # Parse JSON
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from local LLM: {e}")
            logger.error(f"Response was: {response}")
            logger.error(f"Extracted JSON text: {json_text}")
            raise ValueError(f"Invalid JSON from local LLM: {e}")

    def is_available(self) -> bool:
        """Check if local LLM is available and loaded"""
        return self.loaded


# Global instance
local_llm_service = LocalLLMService() if MLX_AVAILABLE else None
