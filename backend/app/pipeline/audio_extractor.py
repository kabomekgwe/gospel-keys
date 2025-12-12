"""Audio extraction and conversion using ffmpeg"""

import asyncio
from pathlib import Path
import ffmpeg


class AudioExtractionError(Exception):
    """Audio extraction failed"""
    pass


async def extract_audio(
    input_path: Path,
    output_path: Path,
    sample_rate: int = 44100,
    channels: int = 1
) -> Path:
    """
    Extract and convert audio to standard format
    
    Args:
        input_path: Input audio/video file
        output_path: Output audio file path (should be .wav)
        sample_rate: Target sample rate in Hz (default: 44100)
        channels: Number of channels, 1=mono, 2=stereo (default: 1)
    
    Returns:
        Path to output audio file
    
    Raises:
        AudioExtractionError: If extraction fails
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run ffmpeg in thread pool
        def _extract():
            (
                ffmpeg
                .input(str(input_path))
                .output(
                    str(output_path),
                    acodec='pcm_s16le',  # PCM 16-bit
                    ar=sample_rate,
                    ac=channels,
                    vn=None,  # No video
                )
                .overwrite_output()
                .run(quiet=True, capture_stderr=True)
            )
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _extract)
        
        return output_path
        
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        raise AudioExtractionError(f"FFmpeg extraction failed: {error_message}")
    except Exception as e:
        raise AudioExtractionError(f"Audio extraction failed: {str(e)}")


async def get_audio_info(input_path: Path) -> dict:
    """
    Get audio file information
    
    Args:
        input_path: Path to audio/video file
    
    Returns:
        Audio metadata dict
    """
    try:
        def _probe():
            return ffmpeg.probe(str(input_path))
        
        loop = asyncio.get_event_loop()
        probe_data = await loop.run_in_executor(None, _probe)
        
        # Extract audio stream info
        audio_streams = [
            stream for stream in probe_data['streams']
            if stream['codec_type'] == 'audio'
        ]
        
        if not audio_streams:
            raise AudioExtractionError("No audio stream found")
        
        audio_stream = audio_streams[0]
        
        return {
            'duration': float(probe_data['format'].get('duration', 0)),
            'sample_rate': int(audio_stream.get('sample_rate', 0)),
            'channels': int(audio_stream.get('channels', 0)),
            'codec': audio_stream.get('codec_name', 'unknown'),
        }
        
    except Exception as e:
        raise AudioExtractionError(f"Failed to get audio info: {str(e)}")
