"""Music Theory Service using music21"""

import music21
from pathlib import Path
from typing import Optional, Dict, Any

class MusicTheoryService:
    """Service for advanced music theory analysis"""

    def analyze_score(self, midi_file_path: Path) -> Dict[str, Any]:
        """
        Analyze a MIDI file to extract key, time signature, and other metadata.
        
        Args:
            midi_file_path: Path to the MIDI file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Parse MIDI file
            score = music21.converter.parse(str(midi_file_path))
            
            # Analyze Key
            key = score.analyze('key')
            key_name = f"{key.tonic.name} {key.mode}"
            
            # Analyze Time Signature
            # distinct time signatures found
            time_signatures = []
            parts = score.parts
            if parts:
                # Check first part (piano usually)
                part = parts[0]
                for ts in part.recurse().getElementsByClass(music21.meter.TimeSignature):
                    if ts.ratioString not in time_signatures:
                        time_signatures.append(ts.ratioString)
            
            primary_time_signature = time_signatures[0] if time_signatures else "4/4"
            
            # Future: Measure analysis, quantization, etc.
            
            return {
                "key": key_name,
                "confidence": key.correlationCoefficient,
                "time_signature": primary_time_signature,
                "time_signatures": time_signatures
            }
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            return {
                "key": "C Major", # Fallback
                "confidence": 0.0,
                "time_signature": "4/4",
                "error": str(e)
            }

# Global instance
music_theory_service = MusicTheoryService()
