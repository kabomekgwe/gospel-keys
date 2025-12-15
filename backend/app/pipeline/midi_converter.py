"""MIDI conversion pipeline using GPU-accelerated pitch detection"""
import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch

# GPU utilities
from app.core.gpu import get_device, is_gpu_available, warmup_device

logger = logging.getLogger(__name__)

# Optional import - torchcrepe for GPU-accelerated pitch detection
try:
    import torchcrepe
    TORCHCREPE_AVAILABLE = True
except ImportError as e:
    TORCHCREPE_AVAILABLE = False
    logger.warning(f"torchcrepe not available: {e}. GPU transcription disabled.")
except Exception as e:
    TORCHCREPE_AVAILABLE = False
    logger.warning(f"Error importing torchcrepe: {e}. GPU transcription disabled.")

# Optional import - basic-pitch requires TensorFlow which doesn't support Python 3.13 yet
try:
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH
    BASIC_PITCH_AVAILABLE = True
except ImportError:
    BASIC_PITCH_AVAILABLE = False
    logger.info("basic-pitch not available (TensorFlow incompatible). Using alternatives.")

import pretty_midi

from app.schemas.transcription import NoteEvent


class TranscriptionError(Exception):
    """MIDI transcription failed"""
    pass


async def transcribe_audio(
    audio_path: Path,
    midi_output_path: Path,
    onset_threshold: float = 0.5,
    frame_threshold: float = 0.3,
    use_gpu: bool = True,
) -> tuple[list[NoteEvent], Path, Optional[float]]:
    """
    Transcribe audio to MIDI using GPU-accelerated methods when available.
    
    Priority: torchcrepe (GPU) > basic-pitch (TensorFlow) > librosa (CPU)
    
    Args:
        audio_path: Input audio file (WAV)
        midi_output_path: Output MIDI file path
        onset_threshold: Note onset threshold (0-1)
        frame_threshold: Note frame threshold (0-1)
        use_gpu: Whether to prefer GPU-accelerated transcription
    
    Returns:
        Tuple of (note events list, MIDI file path, estimated tempo)
    
    Raises:
        TranscriptionError: If transcription fails
    """
    start_time = time.time()
    
    # GPU-accelerated path (torchcrepe)
    if use_gpu and TORCHCREPE_AVAILABLE and is_gpu_available():
        logger.info(f"Using torchcrepe (GPU: {get_device().type}) for transcription")
        try:
            result = await _transcribe_with_torchcrepe(
                audio_path, midi_output_path, onset_threshold
            )
            elapsed = time.time() - start_time
            logger.info(f"GPU transcription completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            logger.warning(f"GPU transcription failed, falling back: {e}")
    
    # TensorFlow path (basic-pitch)
    if BASIC_PITCH_AVAILABLE:
        logger.info("Using basic-pitch (TensorFlow) for transcription")
        return await _transcribe_with_basic_pitch(
            audio_path, midi_output_path, onset_threshold, frame_threshold
        )
    
    # CPU fallback (librosa)
    logger.info("Using librosa (CPU) for transcription")
    result = await _transcribe_with_librosa(audio_path, midi_output_path)
    elapsed = time.time() - start_time
    logger.info(f"CPU transcription completed in {elapsed:.2f}s")
    return result


async def _transcribe_with_torchcrepe(
    audio_path: Path,
    midi_output_path: Path,
    onset_threshold: float = 0.5,
) -> tuple[list[NoteEvent], Path, Optional[float]]:
    """
    GPU-accelerated transcription using torchcrepe.
    
    Torchcrepe provides neural network-based pitch detection that runs
    efficiently on Apple Silicon MPS and NVIDIA CUDA GPUs.
    """
    import torchaudio
    
    try:
        midi_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _transcribe():
            device = get_device()
            warmup_device(device)
            
            # Load audio
            audio, sr = torchaudio.load(str(audio_path))
            
            # Convert to mono if stereo
            if audio.shape[0] > 1:
                audio = audio.mean(dim=0, keepdim=True)
            
            # Resample to 16kHz (torchcrepe requirement)
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(sr, 16000)
                audio = resampler(audio)
                sr = 16000
            
            # Move to GPU
            audio = audio.to(device)
            
            # Run pitch detection
            # Returns: time, frequency, confidence, activation
            pitch, periodicity = torchcrepe.predict(
                audio,
                sr,
                hop_length=160,  # 10ms hop
                fmin=50,
                fmax=2000,
                model='full',
                decoder=torchcrepe.decode.weighted_argmax,
                device=device,
                return_periodicity=True,
                batch_size=1024,
            )
            
            # Apply confidence threshold
            pitch = torchcrepe.filter.median(pitch, 3)
            pitch = torchcrepe.threshold.At(onset_threshold)(pitch, periodicity)
            
            # Move back to CPU for MIDI generation
            pitch = pitch.cpu().numpy().flatten()
            periodicity = periodicity.cpu().numpy().flatten()
            
            # Convert pitch track to note events
            notes = _pitch_to_notes(pitch, periodicity, sr, hop_length=160)
            
            # Create MIDI file
            midi = pretty_midi.PrettyMIDI()
            piano = pretty_midi.Instrument(program=0)
            
            for note_data in notes:
                note = pretty_midi.Note(
                    velocity=int(note_data['velocity']),
                    pitch=note_data['pitch'],
                    start=note_data['start'],
                    end=note_data['end'],
                )
                piano.notes.append(note)
            
            midi.instruments.append(piano)
            midi.write(str(midi_output_path))
            
            return midi, notes
        
        loop = asyncio.get_event_loop()
        midi_data, notes_data = await loop.run_in_executor(None, _transcribe)
        
        # Convert to NoteEvent schema
        note_events = [
            NoteEvent(
                pitch=n['pitch'],
                start_time=n['start'],
                end_time=n['end'],
                velocity=n['velocity'],
            )
            for n in notes_data
        ]
        
        tempo = estimate_tempo(midi_data)
        return note_events, midi_output_path, tempo
        
    except Exception as e:
        raise TranscriptionError(f"GPU transcription failed: {str(e)}")


def _pitch_to_notes(
    pitch: np.ndarray,
    periodicity: np.ndarray,
    sample_rate: int,
    hop_length: int,
    min_note_duration: float = 0.05,
) -> list[dict]:
    """
    Convert continuous pitch track to discrete note events.
    
    Uses onset detection and pitch stability to segment notes.
    """
    import librosa
    
    notes = []
    
    # Time per frame
    frame_time = hop_length / sample_rate
    
    # Find voiced regions (non-NaN pitch)
    voiced = ~np.isnan(pitch) & (periodicity > 0.3)
    
    if not np.any(voiced):
        return notes
    
    # Find note boundaries (pitch changes or voice breaks)
    in_note = False
    note_start = 0
    current_pitch = 0
    pitch_buffer = []
    
    for i, (p, v) in enumerate(zip(pitch, voiced)):
        current_time = i * frame_time
        
        if v and not in_note:
            # Start of new note
            in_note = True
            note_start = current_time
            pitch_buffer = [p]
            
        elif v and in_note:
            # Check if pitch changed significantly
            pitch_buffer.append(p)
            buffer_median = np.median(pitch_buffer[-10:])
            
            if abs(librosa.hz_to_midi(p) - librosa.hz_to_midi(buffer_median)) > 0.5:
                # Pitch jump - end current note and start new
                note_end = current_time
                if note_end - note_start >= min_note_duration:
                    median_pitch = np.median(pitch_buffer[:-1])
                    midi_pitch = int(round(librosa.hz_to_midi(median_pitch)))
                    midi_pitch = np.clip(midi_pitch, 0, 127)
                    
                    notes.append({
                        'pitch': int(midi_pitch),
                        'start': note_start,
                        'end': note_end,
                        'velocity': 80,
                    })
                
                # Start new note
                note_start = current_time
                pitch_buffer = [p]
                
        elif not v and in_note:
            # End of note
            in_note = False
            note_end = current_time
            
            if note_end - note_start >= min_note_duration and len(pitch_buffer) > 0:
                median_pitch = np.median(pitch_buffer)
                midi_pitch = int(round(librosa.hz_to_midi(median_pitch)))
                midi_pitch = np.clip(midi_pitch, 0, 127)
                
                notes.append({
                    'pitch': int(midi_pitch),
                    'start': note_start,
                    'end': note_end,
                    'velocity': 80,
                })
            
            pitch_buffer = []
    
    # Handle last note if still in progress
    if in_note and len(pitch_buffer) > 0:
        note_end = len(pitch) * frame_time
        if note_end - note_start >= min_note_duration:
            median_pitch = np.median(pitch_buffer)
            midi_pitch = int(round(librosa.hz_to_midi(median_pitch)))
            midi_pitch = np.clip(midi_pitch, 0, 127)
            
            notes.append({
                'pitch': int(midi_pitch),
                'start': note_start,
                'end': note_end,
                'velocity': 80,
            })
    
    return notes




async def _transcribe_with_basic_pitch(
    audio_path: Path,
    midi_output_path: Path,
    onset_threshold: float,
    frame_threshold: float,
) -> tuple[list[NoteEvent], Path, Optional[float]]:
    """Transcribe using basic-pitch (neural network approach)"""
    try:
        midi_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _transcribe():
            # Run basic-pitch prediction
            model_output, midi_data, note_events_data = predict(
                str(audio_path),
                ICASSP_2022_MODEL_PATH,
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
            )
            
            # Save MIDI file
            midi_data.write(str(midi_output_path))
            
            return midi_data, note_events_data
        
        loop = asyncio.get_event_loop()
        midi_data, note_events_data = await loop.run_in_executor(None, _transcribe)
        
        # Convert to our NoteEvent schema
        notes = []
        for start_time, end_time, pitch, velocity, _ in note_events_data:
            notes.append(NoteEvent(
                pitch=int(pitch),
                start_time=float(start_time),
                end_time=float(end_time),
                velocity=int(velocity * 127),  # Convert 0-1 to 0-127
            ))
        
        # Estimate tempo from MIDI data
        tempo = estimate_tempo(midi_data)
        
        return notes, midi_output_path, tempo
        
    except Exception as e:
        raise TranscriptionError(f"MIDI transcription failed: {str(e)}")


async def _transcribe_with_librosa(
    audio_path: Path,
    midi_output_path: Path,
) -> tuple[list[NoteEvent], Path, Optional[float]]:
    """
    Transcribe using librosa + pretty_midi (traditional DSP approach)
    
    This is a fallback when basic-pitch is not available.
    Works well for monophonic and piano music.
    """
    try:
        import librosa
        
        midi_output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _transcribe():
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
            
            # 1. Detect note onsets
            onset_frames = librosa.onset.onset_detect(
                y=y, sr=sr, units='frames',
                backtrack=True,
                pre_max=20,
                post_max=20,
                pre_avg=100,
                post_avg=100,
                delta=0.2,
                wait=30
            )
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            # 2. Extract pitch using pyin (probabilistic YIN)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=sr,
                frame_length=2048
            )
            
            # 3. Create MIDI file
            midi = pretty_midi.PrettyMIDI()
            piano = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano
            
            # 4. Build notes from onsets and pitch
            for i, onset in enumerate(onset_times):
                # Determine note offset
                if i < len(onset_times) - 1:
                    offset = onset_times[i + 1]
                else:
                    offset = onset + 0.5  # Default duration
                
                # Get pitch at onset time
                onset_frame = librosa.time_to_frames(onset, sr=sr)
                
                # Look ahead a few frames to get stable pitch
                pitch_window = f0[onset_frame:onset_frame + 10]
                voiced_window = voiced_flag[onset_frame:onset_frame + 10]
                
                # Filter to voiced frames only
                voiced_pitches = pitch_window[voiced_window]
                
                if len(voiced_pitches) > 0 and not np.all(np.isnan(voiced_pitches)):
                    # Use median pitch in window
                    pitch_hz = np.nanmedian(voiced_pitches)
                    pitch_midi = int(round(librosa.hz_to_midi(pitch_hz)))
                    
                    # Clamp to valid MIDI range
                    pitch_midi = np.clip(pitch_midi, 0, 127)
                    
                    # Create note
                    note = pretty_midi.Note(
                        velocity=80,
                        pitch=pitch_midi,
                        start=onset,
                        end=offset
                    )
                    piano.notes.append(note)
            
            midi.instruments.append(piano)
            midi.write(str(midi_output_path))
            
            return midi
        
        loop = asyncio.get_event_loop()
        midi_data = await loop.run_in_executor(None, _transcribe)
        
        # Convert to NoteEvent schema
        notes = []
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                notes.append(NoteEvent(
                    pitch=note.pitch,
                    start_time=note.start,
                    end_time=note.end,
                    velocity=note.velocity,
                ))
        
        # Estimate tempo
        tempo = estimate_tempo(midi_data)
        
        return notes, midi_output_path, tempo
        
    except Exception as e:
        raise TranscriptionError(f"Librosa transcription failed: {str(e)}")


def estimate_tempo(midi_data: pretty_midi.PrettyMIDI) -> Optional[float]:
    """
    Estimate tempo from MIDI data
    
    Args:
        midi_data: PrettyMIDI object
    
    Returns:
        Estimated tempo in BPM, or None if cannot estimate
    """
    try:
        # Get tempo changes
        if hasattr(midi_data, '_tick_scales'):
            # Use tempo changes if available
            tempo_changes = midi_data.get_tempo_changes()
            if len(tempo_changes[1]) > 0:
                # Return the first (or most common) tempo
                return float(tempo_changes[1][0])
        
        # Fallback: estimate from note IOIs (inter-onset intervals)
        all_notes = []
        for instrument in midi_data.instruments:
            all_notes.extend([(note.start, note.end) for note in instrument.notes])
        
        if len(all_notes) < 10:
            return None
        
        all_notes.sort(key=lambda x: x[0])
        
        # Calculate inter-onset intervals
        iois = []
        for i in range(1, min(len(all_notes), 100)):  # Use first 100 notes
            ioi = all_notes[i][0] - all_notes[i-1][0]
            if 0.1 < ioi < 2.0:  # Filter outliers
                iois.append(ioi)
        
        if not iois:
            return None
        
        # Estimate beat duration as median IOI
        median_ioi = np.median(iois)
        estimated_bpm = 60.0 / median_ioi
        
        # Clamp to reasonable range
        estimated_bpm = np.clip(estimated_bpm, 40, 200)
        
        return float(estimated_bpm)
        
    except Exception:
        return None


def estimate_key(notes: list[NoteEvent]) -> Optional[str]:
    """
    Estimate musical key from notes
    
    Args:
        notes: List of note events
    
    Returns:
        Estimated key (e.g., "C major"), or None
    """
    if not notes:
        return None
    
    try:
        # Count note occurrences (mod 12 for pitch classes)
        pitch_class_counts = [0] * 12
        for note in notes:
            pc = note.pitch % 12
            duration = note.end_time - note.start_time
            pitch_class_counts[pc] += duration  # Weight by duration
        
        # Major and minor key profiles (Krumhansl-Schmuckler)
        major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        best_correlation = -1
        best_key = None
        
        # Try all 24 keys
        for shift in range(12):
            # Rotate pitch class counts
            rotated = pitch_class_counts[shift:] + pitch_class_counts[:shift]
            
            # Correlate with major profile
            major_corr = np.corrcoef(rotated, major_profile)[0, 1]
            if major_corr > best_correlation:
                best_correlation = major_corr
                best_key = f"{note_names[shift]} major"
            
            # Correlate with minor profile
            minor_corr = np.corrcoef(rotated, minor_profile)[0, 1]
            if minor_corr > best_correlation:
                best_correlation = minor_corr
                best_key = f"{note_names[shift]} minor"
        
        return best_key if best_correlation > 0.6 else None
        
    except Exception:
        return None
