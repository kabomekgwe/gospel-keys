"""Piano isolation using Demucs source separation"""

import asyncio
from pathlib import Path
import subprocess
import shutil


class SourceSeparationError(Exception):
    """Source separation failed"""
    pass


async def isolate_piano(audio_path: Path, output_dir: Path) -> Path:
    """
    Isolate piano from audio mix using Demucs
    
    Args:
        audio_path: Input audio file (must be WAV)
        output_dir: Directory to save separated stems
    
    Returns:
        Path to isolated piano audio (from 'other' stem)
    
    Raises:
        SourceSeparationError: If separation fails
    """
    # Check if demucs is available
    if not shutil.which("demucs"):
        raise SourceSeparationError(
            "Demucs not found. Install with: pip install demucs"
        )
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Run demucs command
        # Demucs creates: htdemucs/{track_name}/{bass,drums,other,vocals}.wav
        # Piano is typically in the 'other' stem
        def _separate():
            cmd = [
                "demucs",
                "--two-stems=other",  # Only separate 'other' stem (piano/instruments)
                "-o", str(output_dir),
                "-n", "htdemucs",  # Use htdemucs model (best quality)
                str(audio_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _separate)
        
        # Find the output file
        # Demucs outputs to: output_dir/htdemucs/track_name/other.wav
        track_name = audio_path.stem
        separated_file = output_dir / "htdemucs" / track_name / "other.wav"
        
        if not separated_file.exists():
            raise SourceSeparationError(
                f"Expected output file not found: {separated_file}"
            )
        
        return separated_file
        
    except subprocess.CalledProcessError as e:
        raise SourceSeparationError(
            f"Demucs separation failed: {e.stderr}"
        )
    except Exception as e:
        raise SourceSeparationError(f"Source separation failed: {str(e)}")
