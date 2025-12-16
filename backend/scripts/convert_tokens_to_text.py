"""
Convert MidiTok REMI Tokens to Text Token Format

Converts training data from Phase 1 (integer tokens) to Phase 2 (text tokens)
for fine-tuning Qwen 2.5-14B with human-readable music tokens.

Input:  train.jsonl with {"prompt": "...", "tokens": [1, 234, 567]}
Output: mlx_train.jsonl with {"text": "Human: ...\n\nAssistant: SONG_START NOTE_ON_60 ..."}

Usage:
    python scripts/convert_tokens_to_text.py \
        --input data/training/train.jsonl \
        --output data/training/mlx_train.jsonl \
        --format mlx
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from tqdm import tqdm

from app.services.text_token_service import text_token_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenConverter:
    """Convert REMI tokens to text tokens for MLX fine-tuning"""

    def __init__(self, output_format: str = "mlx"):
        self.text_service = text_token_service
        self.output_format = output_format  # "mlx", "alpaca", "chatml"

    def convert_sample(self, sample: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert single training sample from REMI to text tokens.

        Args:
            sample: {"prompt": "...", "tokens": [1, 234, 567], "metadata": {...}}

        Returns:
            {"text": "formatted training example"}
        """
        prompt = sample.get("prompt", "Generate music")
        remi_tokens = sample.get("tokens", [])

        # Convert REMI → Text tokens
        text_tokens = self.text_service.remi_to_text_tokens(remi_tokens)

        # Join into string
        text_token_string = self.text_service.tokens_to_string(text_tokens)

        # Format for fine-tuning
        if self.output_format == "mlx":
            # MLX format (Qwen chat template)
            formatted_text = f"""<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant
{text_token_string}<|im_end|>"""

        elif self.output_format == "alpaca":
            # Alpaca format
            formatted_text = f"""### Instruction:
{prompt}

### Response:
{text_token_string}"""

        elif self.output_format == "chatml":
            # ChatML format
            formatted_text = f"""<|user|>
{prompt}<|end|>
<|assistant|>
{text_token_string}<|end|>"""

        else:
            # Simple format
            formatted_text = f"Q: {prompt}\n\nA: {text_token_string}"

        return {"text": formatted_text}

    def convert_dataset(
        self,
        input_path: Path,
        output_path: Path,
        max_samples: int = None
    ):
        """
        Convert entire dataset from REMI to text tokens.

        Args:
            input_path: Input JSONL file (REMI tokens)
            output_path: Output JSONL file (text tokens)
            max_samples: Maximum samples to convert (None = all)
        """
        logger.info(f"📊 Converting dataset: {input_path}")
        logger.info(f"   Output: {output_path}")
        logger.info(f"   Format: {self.output_format}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Count total samples
        total_samples = sum(1 for _ in open(input_path))
        if max_samples:
            total_samples = min(total_samples, max_samples)

        logger.info(f"   Processing {total_samples} samples...")

        # Convert samples
        converted_count = 0
        error_count = 0

        with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
            for i, line in enumerate(tqdm(infile, total=total_samples, desc="Converting")):
                if max_samples and i >= max_samples:
                    break

                try:
                    # Parse input sample
                    sample = json.loads(line)

                    # Convert to text tokens
                    converted_sample = self.convert_sample(sample)

                    # Write to output
                    outfile.write(json.dumps(converted_sample) + '\n')
                    converted_count += 1

                except Exception as e:
                    logger.error(f"Error converting sample {i}: {e}")
                    error_count += 1
                    continue

        logger.info(f"✅ Conversion complete!")
        logger.info(f"   Converted: {converted_count} samples")
        logger.info(f"   Errors: {error_count} samples")
        logger.info(f"   Output: {output_path}")

        return converted_count, error_count

    def validate_conversion(self, input_path: Path, output_path: Path, num_samples: int = 10):
        """
        Validate that conversion preserves token information.

        Args:
            input_path: Original REMI token file
            output_path: Converted text token file
            num_samples: Number of samples to validate
        """
        logger.info(f"🔍 Validating conversion (checking {num_samples} samples)...")

        success_count = 0
        fail_count = 0

        with open(input_path, 'r') as infile, open(output_path, 'r') as outfile:
            for i in range(num_samples):
                try:
                    # Read original and converted
                    original_line = infile.readline()
                    converted_line = outfile.readline()

                    if not original_line or not converted_line:
                        break

                    original = json.loads(original_line)
                    converted = json.loads(converted_line)

                    # Extract tokens from converted text
                    text = converted.get("text", "")

                    # Find assistant response (after "assistant" marker)
                    if "<|im_start|>assistant" in text:
                        text_tokens_str = text.split("<|im_start|>assistant\n")[1].split("<|im_end|>")[0]
                    else:
                        text_tokens_str = text.split("A: ")[1] if "A: " in text else text

                    text_tokens = self.text_service.string_to_tokens(text_tokens_str.strip())

                    # Convert back to REMI
                    reconstructed_remi = self.text_service.text_to_remi_tokens(text_tokens)
                    original_remi = original.get("tokens", [])

                    # Compare
                    if reconstructed_remi == original_remi:
                        success_count += 1
                    else:
                        fail_count += 1
                        logger.warning(f"Sample {i}: Token mismatch!")
                        logger.warning(f"  Original length: {len(original_remi)}")
                        logger.warning(f"  Reconstructed length: {len(reconstructed_remi)}")

                except Exception as e:
                    logger.error(f"Validation error at sample {i}: {e}")
                    fail_count += 1

        logger.info(f"✅ Validation complete!")
        logger.info(f"   Successful: {success_count}/{num_samples}")
        logger.info(f"   Failed: {fail_count}/{num_samples}")

        return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(description="Convert REMI tokens to text tokens")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input JSONL file with REMI tokens"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output JSONL file with text tokens"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="mlx",
        choices=["mlx", "alpaca", "chatml", "simple"],
        help="Output format for fine-tuning"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum samples to convert (None = all)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate conversion after completion"
    )
    parser.add_argument(
        "--validate-samples",
        type=int,
        default=10,
        help="Number of samples to validate"
    )

    args = parser.parse_args()

    logger.info("🎵 MidiTok REMI → Text Token Converter")
    logger.info("="*60)

    # Create converter
    converter = TokenConverter(output_format=args.format)

    # Convert dataset
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        logger.error(f"❌ Input file not found: {input_path}")
        return

    converted, errors = converter.convert_dataset(
        input_path=input_path,
        output_path=output_path,
        max_samples=args.max_samples
    )

    # Validate if requested
    if args.validate and converted > 0:
        converter.validate_conversion(
            input_path=input_path,
            output_path=output_path,
            num_samples=min(args.validate_samples, converted)
        )

    logger.info("🎉 Done!")


if __name__ == "__main__":
    main()
