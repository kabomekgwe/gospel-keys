"""
Gospel AI Module - MLX-powered music generation

Integrates MLX transformer with existing rule-based GospelArranger
for hybrid AI + theory-driven gospel piano generation.
"""

from .mlx_music_generator import MLXGospelGenerator, MLXMusicTransformer

__all__ = ["MLXGospelGenerator", "MLXMusicTransformer"]
