"""YouTube video/audio downloader using yt-dlp"""

import asyncio
from pathlib import Path
from typing import Optional
import yt_dlp


class DownloadError(Exception):
    """Download operation failed"""
    pass


async def download_video(url: str, output_path: Path) -> tuple[Path, Optional[str]]:
    """
    Download video/audio from YouTube URL
    
    Args:
        url: YouTube video URL
        output_path: Directory to save the downloaded file
    
    Returns:
        Tuple of (downloaded file path, video title)
    
    Raises:
        DownloadError: If download fails
    """
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',  # Get best audio quality
        'outtmpl': str(output_path / '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }
    
    try:
        # Run yt-dlp in thread pool to avoid blocking
        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = info.get('title', 'Unknown')
                return filename, title
        
        loop = asyncio.get_event_loop()
        filename, title = await loop.run_in_executor(None, _download)
        return Path(filename), title
        
    except Exception as e:
        raise DownloadError(f"Failed to download video: {str(e)}")


def get_video_info(url: str) -> dict:
    """
    Get video information without downloading
    
    Args:
        url: YouTube video URL
    
    Returns:
        Video metadata dict
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)
