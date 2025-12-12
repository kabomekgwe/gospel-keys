"""Audio effects for practice mode using librosa"""

import asyncio
from pathlib import Path
from typing import Optional
import librosa
import soundfile as sf
import numpy as np


class AudioEffectsError(Exception):
    """Audio effects processing failed"""
    pass


async def time_stretch_audio(
    input_path: Path,
    output_path: Path,
    rate: float,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None
) -> Path:
    """
    Time-stretch audio without pitch change using librosa
    
    Args:
        input_path: Input audio file
        output_path: Output stretched audio path  
        rate: Time stretch rate (0.5 = half speed, 2.0 = double speed)
        start_time: Extract from this time (seconds)
        end_time: Extract until this time (seconds)
    
    Returns:
        Path to stretched audio file
    
    Raises:
        AudioEffectsError: If processing fails
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _stretch():
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            
            # Extract section if specified
            if start_time is not None or end_time is not None:
                start_sample = int(start_time * sr) if start_time else 0
                end_sample = int(end_time * sr) if end_time else len(y)
                y = y[start_sample:end_sample]
            
            # Time-stretch using phase vocoder
            # rate parameter: >1 speeds up, <1 slows down
            y_stretched = librosa.effects.time_stretch(y, rate=rate)
            
            # Save stretched audio
            sf.write(str(output_path), y_stretched, sr)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _stretch)
        
        return output_path
        
    except Exception as e:
        raise AudioEffectsError(f"Time stretching failed: {str(e)}")


async def extract_audio_section(
    input_path: Path,
    output_path: Path,
    start_time: float,
    end_time: float
) -> Path:
    """
    Extract a section of audio without any processing
    
    Args:
        input_path: Input audio file
        output_path: Output audio file
        start_time: Start time in seconds
        end_time: End time in seconds
    
    Returns:
        Path to extracted audio
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _extract():
            # Load audio
            y, sr = librosa.load(str(input_path), sr=None, mono=True)
            
            # Extract section
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            y_section = y[start_sample:end_sample]
            
            # Save
            sf.write(str(output_path), y_section, sr)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _extract)
        
        return output_path
        
    except Exception as e:
        raise AudioEffectsError(f"Audio extraction failed: {str(e)}")
