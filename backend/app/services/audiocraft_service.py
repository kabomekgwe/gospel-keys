from typing import Optional, Dict, Any
from pathlib import Path
import logging
import asyncio

logger = logging.getLogger(__name__)

class AudioCraftService:
    """
    Service for generative audio using Meta's AudioCraft (MusicGen).
    """
    
    def __init__(self):
        self.model = None
        self._model_name = 'small' # Default to small for lighter resource usage
        
    def _load_model(self):
        """Lazy load the model to save resources until needed."""
        if self.model is None:
            try:
                from audiocraft.models import MusicGen
                logger.info(f"Loading MusicGen model: {self._model_name}")
                self.model = MusicGen.get_pretrained(f'facebook/musicgen-{self._model_name}')
                self.model.set_generation_params(duration=10) # Default 10s
            except ImportError:
                logger.error("AudioCraft not installed.")
                raise ImportError("AudioCraft library is not available.")
            except Exception as e:
                logger.error(f"Failed to load MusicGen: {e}")
                raise e

    async def generate_music(self, prompt: str, duration: int = 15, output_path: Path = None) -> Path:
        """
        Generate music from a text prompt.
        """
        try:
            # Run model loading and inference in a thread/executor to avoid blocking async loop
            loop = asyncio.get_event_loop()
            
            def _generate():
                self._load_model()
                self.model.set_generation_params(duration=duration)
                wav = self.model.generate([prompt])
                
                # Save to file
                from audiocraft.data.audio import audio_write
                if output_path:
                    # AudioCraft adds extension automatically, strip it if present?
                    # audio_write expects path without extension
                    stem_path = str(output_path.with_suffix(''))
                    audio_write(stem_path, wav[0].cpu(), self.model.sample_rate, strategy="loudness", loudness_compressor=True)
                    return output_path
                return None

            result_path = await loop.run_in_executor(None, _generate)
            return result_path
            
        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            raise e

audiocraft_service = AudioCraftService()
