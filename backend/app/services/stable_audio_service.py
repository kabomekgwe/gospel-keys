from typing import Optional
from pathlib import Path
import logging
import asyncio
import torch
import scipy

try:
    from diffusers import StableAudioPipeline
    STABLE_AUDIO_AVAILABLE = True
except ImportError:
    STABLE_AUDIO_AVAILABLE = False
    print("Stable Audio (diffusers) not installed. Audio generation disabled.")

logger = logging.getLogger(__name__)

class StableAudioService:
    """
    Service for AI-powered audio generation using Stability AI's Stable Audio.
    
    Alternative to AudioCraft that's compatible with Python 3.13.
    Uses Hugging Face Diffusers library.
    """
    
    def __init__(self):
        self.pipeline = None
        self.model_id = "stabilityai/stable-audio-open-1.0"
        
    def _load_model(self):
        """Lazy load the model to save resources until needed."""
        if self.pipeline is None:
            if not STABLE_AUDIO_AVAILABLE:
                raise ImportError("diffusers library not installed")
                
            try:
                logger.info(f"Loading Stable Audio model: {self.model_id}")
                
                # Detect available device
                if torch.cuda.is_available():
                    device = "cuda"
                    dtype = torch.float16
                    logger.info("Using CUDA GPU acceleration")
                elif torch.backends.mps.is_available():
                    device = "mps"
                    dtype = torch.float32  # MPS works better with float32
                    logger.info("Using Apple Silicon (MPS) GPU acceleration")
                else:
                    device = "cpu"
                    dtype = torch.float32
                    logger.info("Using CPU (no GPU detected)")
                
                self.pipeline = StableAudioPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=dtype
                )
                
                # Move to detected device
                self.pipeline = self.pipeline.to(device)
                    
                logger.info(f"Stable Audio model loaded successfully on {device}")
                
            except Exception as e:
                logger.error(f"Failed to load Stable Audio model: {e}")
                raise e

    async def generate_audio(
        self, 
        prompt: str, 
        duration: float = 10.0,
        num_inference_steps: int = 200,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate audio from a text prompt.
        
        Args:
            prompt: Text description of the audio to generate
            duration: Duration in seconds (max 47s for Stable Audio Open)
            num_inference_steps: Quality vs speed tradeoff (100-200 recommended)
            output_path: Where to save the generated audio
            
        Returns:
            Path to the generated audio file
        """
        try:
            # Run model loading and inference in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _generate():
                self._load_model()
                
                # Clamp duration to model limits
                duration_clamped = min(max(duration, 1.0), 47.0)
                
                logger.info(f"Generating audio: '{prompt}' ({duration_clamped}s)")
                
                # Generate audio
                output = self.pipeline(
                    prompt=prompt,
                    audio_end_in_s=duration_clamped,
                    num_inference_steps=num_inference_steps,
                )
                
                # Extract audio array
                audio = output.audios[0]
                sample_rate = 44100  # Stable Audio Open uses 44.1kHz
                
                # Save to file
                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Use scipy to write WAV file
                    scipy.io.wavfile.write(
                        str(output_path),
                        rate=sample_rate,
                        data=audio.T  # Transpose for stereo
                    )
                    
                    logger.info(f"Audio saved to {output_path}")
                    return output_path
                    
                return None

            result_path = await loop.run_in_executor(None, _generate)
            return result_path
            
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            raise e

stable_audio_service = StableAudioService()
