from typing import Dict, Any, Optional
from pathlib import Path
import logging

try:
    import essentia.standard as es
    ESSENTIA_AVAILABLE = True
except ImportError:
    ESSENTIA_AVAILABLE = False
    print("Essentia not found. Audio analysis features will be limited.")

logger = logging.getLogger(__name__)

class EssentiaService:
    """
    Service for high-performance audio analysis using Essentia.
    """
    
    def analyze_audio(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract comprehensive audio features: BPM, Key, Loudness, etc.
        """
        if not ESSENTIA_AVAILABLE:
            logger.warning("Essentia not available, skipping detailed analysis")
            return {"error": "Essentia library not installed"}
            
        try:
            # Load audio
            loader = es.MonoLoader(filename=str(file_path))
            audio = loader()
            
            # Rhythm
            rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
            bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)
            
            # Key
            key_extractor = es.KeyExtractor(profileType='edma', tonality='major')
            key, scale, key_strength = key_extractor(audio)
            
            # Loudness
            loudness = es.Loudness()(audio)
            
            return {
                "bpm": float(bpm),
                "bpm_confidence": float(beats_confidence),
                "key": key,
                "scale": scale,
                "key_strength": float(key_strength),
                "loudness": float(loudness),
                "source": "essentia"
            }
            
        except Exception as e:
            logger.error(f"Essentia analysis failed: {e}")
            return {"error": str(e)}

essentia_service = EssentiaService()
