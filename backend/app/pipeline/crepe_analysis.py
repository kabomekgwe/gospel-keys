"""Crepe-based pitch analysis"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import librosa
import soundfile as sf

# Optional import - crepe requires TensorFlow which doesn't support Python 3.13 yet
try:
    import crepe
    CREPE_AVAILABLE = True
except ImportError:
    CREPE_AVAILABLE = False
    print("Warning: crepe not available. Advanced pitch analysis will be disabled.")


async def extract_pitch_contour(
    audio_path: Path,
    sample_rate: int = 16000,
    model_capacity: str = "full",
    viterbi: bool = True
) -> Dict:
    """
    Extract detailed pitch contour using CREPE (preferred) or librosa.pyin (fallback)
    
    Args:
        audio_path: Path to audio file
        sample_rate: Sampling rate (16kHz recommended for CREPE, 22kHz for pyin)
        model_capacity: "tiny", "small", "medium", "large", "full" (CREPE only)
        viterbi: Use viterbi smoothing algorithm
    
    Returns:
        Dict with time, frequency, confidence/voicing, and notes
    """
    if CREPE_AVAILABLE:
        return await _extract_pitch_crepe(audio_path, sample_rate, model_capacity, viterbi)
    else:
        return await _extract_pitch_pyin(audio_path, sample_rate)


async def _extract_pitch_crepe(
    audio_path: Path,
    sample_rate: int,
    model_capacity: str,
    viterbi: bool
) -> Dict:
    """Extract pitch using CREPE neural network"""
    # Load audio
    audio, sr = librosa.load(str(audio_path), sr=sample_rate, mono=True)
    
    # Run CREPE
    time, frequency, confidence, activation = crepe.predict(
        audio,
        sr,
        model_capacity=model_capacity,
        viterbi=viterbi,
        step_size=10  # 10ms hop
    )
    
    # Convert frequencies to note names
    notes = [_frequency_to_note(f) if c > 0.5 else None 
             for f, c in zip(frequency, confidence)]
    
    return {
        "time": time.tolist(),
        "frequency": frequency.tolist(),
        "confidence": confidence.tolist(),
        "notes": notes,
        "sampling_rate": sample_rate
    }


async def _extract_pitch_pyin(
    audio_path: Path,
    sample_rate: int = 22050
) -> Dict:
    """
    Extract pitch using librosa.pyin (traditional DSP approach)
    
    This is a fallback when CREPE is not available.
    Works well for monophonic audio (voice, single instruments).
    """
    # Load audio
    y, sr = librosa.load(str(audio_path), sr=sample_rate, mono=True)
    
    # Extract F0 with pyin
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sr,
        frame_length=2048
    )
    
    # Time stamps
    times = librosa.times_like(f0, sr=sr)
    
    # Convert to note names (same format as CREPE)
    notes = []
    for freq, voiced in zip(f0, voiced_flag):
        if voiced and not np.isnan(freq):
            notes.append(_frequency_to_note(freq))
        else:
            notes.append(None)
    
    return {
        "time": times.tolist(),
        "frequency": f0.tolist(),
        "confidence": voiced_probs.tolist(),  # Use voicing probability as confidence
        "notes": notes,
        "sampling_rate": sample_rate
    }


def detect_blue_notes(pitch_data: Dict, genre_key: str = "blues") -> List[Dict]:
    """
    Detect blue notes (bent/microtonal notes) in blues/jazz
    
    Blue notes are typically:
    - Flattened 3rd
    - Flattened 5th  
    - Flattened 7th
    
    Args:
        pitch_data: Output from extract_pitch_contour
        genre_key: Musical key context
    
    Returns:
        List of detected blue note events
    """
    blue_notes = []
    frequencies = np.array(pitch_data["frequency"])
    confidences = np.array(pitch_data["confidence"])
    times = np.array(pitch_data["time"])
    
    # Find regions with high confidence
    confident_regions = confidences > 0.7
    
    # Detect microtonal deviations
    for i in range(1, len(frequencies) - 1):
        if not confident_regions[i]:
            continue
        
        freq = frequencies[i]
        # Check if frequency falls between standard semitones
        midi_note = librosa.hz_to_midi(freq)
        deviation = midi_note - round(midi_note)
        
        # Blue note if 20-40 cents flat
        if -0.4 < deviation < -0.2:
            blue_notes.append({
                "time": float(times[i]),
                "frequency": float(freq),
                "midi_note": float(midi_note),
                "cents_deviation": float(deviation * 100),
                "type": "blue_note",
                "confidence": float(confidences[i])
            })
    
    return blue_notes


def detect_vibrato(pitch_data: Dict, min_rate: float = 4.0, max_rate: float = 8.0) -> List[Dict]:
    """
    Detect vibrato (periodic pitch oscillation)
    
    Args:
        pitch_data: Output from extract_pitch_contour
        min_rate: Minimum vibrato rate in Hz
        max_rate: Maximum vibrato rate in Hz
    
    Returns:
        List of vibrato regions
    """
    vibrato_regions = []
    frequencies = np.array(pitch_data["frequency"])
    times = np.array(pitch_data["time"])
    confidences = np.array(pitch_data["confidence"])
    
    # Use sliding window to detect oscillations
    window_size = 50  # ~500ms at 10ms hop
    
    for i in range(0, len(frequencies) - window_size, 10):
        window_freqs = frequencies[i:i+window_size]
        window_conf = confidences[i:i+window_size]
        
        if np.mean(window_conf) < 0.6:
            continue
        
        # Calculate oscillation rate via autocorrelation
        # Simplified approach - check for periodic variation
        freq_std = np.std(window_freqs)
        
        if freq_std > 5:  # Significant variation
            vibrato_regions.append({
                "start_time": float(times[i]),
                "end_time": float(times[i + window_size - 1]),
                "center_frequency": float(np.mean(window_freqs)),
                "extent_hz": float(freq_std * 2),
                "rate_estimate": 5.0,  # Placeholder - needs FFT analysis
                "type": "vibrato"
            })
    
    return vibrato_regions


def analyze_pitch_bends(pitch_data: Dict) -> Dict:
    """
    Analyze pitch bends and slides
    
    Returns statistics on:
    - Number of bends
    - Average bend extent
    - Bend directions
    """
    frequencies = np.array(pitch_data["frequency"])
    times = np.array(pitch_data["time"])
    confidences = np.array(pitch_data["confidence"])
    
    # Calculate pitch deltas
    pitch_deltas = np.diff(librosa.hz_to_midi(frequencies))
    
    # Find significant bends (>50 cents in <100ms)
    bends = []
    for i in range(len(pitch_deltas)):
        if abs(pitch_deltas[i]) > 0.5 and confidences[i] > 0.7:
            bends.append({
                "time": float(times[i]),
                "extent_semitones": float(pitch_deltas[i]),
                "direction": "up" if pitch_deltas[i] > 0 else "down"
            })
    
    return {
        "total_bends": len(bends),
        "average_extent": float(np.mean([abs(b["extent_semitones"]) for b in bends])) if bends else 0.0,
        "bends": bends[:100]  # Limit response size
    }


def _frequency_to_note(frequency: float) -> Optional[str]:
    """Convert frequency to note name"""
    if frequency == 0 or np.isnan(frequency):
        return None
    
    try:
        midi_note = librosa.hz_to_midi(frequency)
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = int(midi_note / 12) - 1
        note_index = int(round(midi_note)) % 12
        return f"{note_names[note_index]}{octave}"
    except:
        return None
