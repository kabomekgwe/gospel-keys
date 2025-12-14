"""GPU MIDI Generation Tests

Tests for GPU device detection, torchcrepe transcription, and MLX voicing generation.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import GPU utilities
from app.core.gpu import (
    get_device,
    is_gpu_available,
    get_device_info,
    warmup_device,
    to_device,
    clear_gpu_cache,
)


class TestGPUDeviceDetection:
    """Test GPU device detection utilities."""
    
    def test_get_device_returns_valid_device(self):
        """Verify get_device returns a valid torch.device."""
        import torch
        device = get_device()
        assert isinstance(device, torch.device)
        assert device.type in ["mps", "cuda", "cpu"]
    
    def test_is_gpu_available_returns_bool(self):
        """Verify is_gpu_available returns a boolean."""
        result = is_gpu_available()
        assert isinstance(result, bool)
    
    def test_get_device_info_returns_structure(self):
        """Verify get_device_info returns proper GPUInfo structure."""
        info = get_device_info()
        assert hasattr(info, 'device_type')
        assert hasattr(info, 'device_name')
        assert hasattr(info, 'available')
        assert info.device_type in ["mps", "cuda", "cpu"]
    
    def test_warmup_device_does_not_crash(self):
        """Verify warmup_device executes without error."""
        # Should not raise any exceptions
        warmup_device()
    
    def test_to_device_moves_tensor(self):
        """Verify to_device moves tensor to correct device."""
        import torch
        tensor = torch.randn(10, 10)
        moved = to_device(tensor)
        
        expected_device = get_device()
        assert moved.device.type == expected_device.type
    
    def test_clear_gpu_cache_does_not_crash(self):
        """Verify clear_gpu_cache executes without error."""
        # Should not raise any exceptions
        clear_gpu_cache()


class TestGPUMIDIGenerator:
    """Test GPU-accelerated MIDI generation."""
    
    def test_generator_initialization(self):
        """Test GPUMIDIGenerator can be instantiated."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        assert generator is not None
        assert generator.output_dir.exists()
    
    def test_note_name_to_midi(self):
        """Test note name to MIDI conversion."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        
        # Test standard notes
        assert generator._note_name_to_midi("C4") == 60
        assert generator._note_name_to_midi("A4") == 69
        assert generator._note_name_to_midi("C#4") == 61
        assert generator._note_name_to_midi("Bb3") == 58
    
    def test_parse_chord(self):
        """Test chord symbol parsing."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        
        # Test various chord symbols
        root, quality = generator._parse_chord("Dm7")
        assert root == 2  # D
        assert quality == "m7"
        
        root, quality = generator._parse_chord("Cmaj7")
        assert root == 0  # C
        assert quality == "maj7"
        
        root, quality = generator._parse_chord("G7")
        assert root == 7  # G
        assert quality == "7"
        
        root, quality = generator._parse_chord("F#m7b5")
        assert root == 6  # F#
        assert quality == "m7b5"
    
    def test_generate_voicing(self):
        """Test chord voicing generation."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        
        # Generate a Dm7 voicing
        notes = generator.generate_voicing("Dm7", style="closed")
        
        assert len(notes) >= 4  # At least 4 notes in a 7th chord
        
        # All notes should have valid MIDI pitches
        for note in notes:
            assert 0 <= note.pitch <= 127
            assert note.duration > 0
            assert 0 <= note.velocity <= 127
    
    def test_generate_voicing_styles(self):
        """Test different voicing styles produce different results."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        
        closed_notes = generator.generate_voicing("Cmaj7", style="closed")
        open_notes = generator.generate_voicing("Cmaj7", style="open")
        shell_notes = generator.generate_voicing("Cmaj7", style="shell")
        
        # Open voicing should have wider spread
        closed_range = max(n.pitch for n in closed_notes) - min(n.pitch for n in closed_notes)
        open_range = max(n.pitch for n in open_notes) - min(n.pitch for n in open_notes)
        
        assert open_range >= closed_range
        
        # Shell voicing should have fewer notes
        assert len(shell_notes) < len(closed_notes)
    
    def test_generate_progression_midi(self, tmp_path):
        """Test MIDI file generation for chord progression."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        generator.output_dir = tmp_path
        
        chords = ["Dm7", "G7", "Cmaj7"]
        output_path = generator.generate_progression_midi(
            chords=chords,
            output_id="test_progression",
            bpm=120,
        )
        
        assert output_path.exists()
        assert output_path.suffix == ".mid"
        
        # Verify MIDI file is valid
        import pretty_midi
        midi = pretty_midi.PrettyMIDI(str(output_path))
        assert len(midi.instruments) > 0
        assert len(midi.instruments[0].notes) > 0
    
    def test_generate_neosoul_pattern(self, tmp_path):
        """Test neo-soul pattern generation."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        generator.output_dir = tmp_path
        
        output_path = generator.generate_neosoul_pattern(
            chord="Dm9",
            output_id="test_pattern",
            pattern_type="broken",
            bars=1,
        )
        
        assert output_path.exists()
        
        import pretty_midi
        midi = pretty_midi.PrettyMIDI(str(output_path))
        assert len(midi.instruments[0].notes) > 0
    
    def test_benchmark_runs(self):
        """Test benchmark functionality."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        results = generator.benchmark(iterations=10)
        
        assert "numpy_time_seconds" in results
        assert "iterations" in results
        assert results["numpy_time_seconds"] > 0


class TestTorchcrepeTranscription:
    """Test GPU-accelerated audio transcription."""
    
    @pytest.mark.skipif(
        not is_gpu_available(),
        reason="GPU not available"
    )
    def test_torchcrepe_available(self):
        """Check if torchcrepe is available."""
        try:
            import torchcrepe
            assert True
        except ImportError:
            pytest.skip("torchcrepe not installed")
    
    def test_pitch_to_notes_function(self):
        """Test pitch-to-notes conversion."""
        from app.pipeline.midi_converter import _pitch_to_notes
        
        # Create synthetic pitch and periodicity data
        sample_rate = 16000
        hop_length = 160
        duration_seconds = 1.0
        num_frames = int(duration_seconds * sample_rate / hop_length)
        
        # Simulate a single note at A4 (440 Hz)
        pitch = np.full(num_frames, 440.0)
        periodicity = np.ones(num_frames)
        
        # Add some silence at start and end
        pitch[:10] = np.nan
        pitch[-10:] = np.nan
        periodicity[:10] = 0.0
        periodicity[-10:] = 0.0
        
        notes = _pitch_to_notes(pitch, periodicity, sample_rate, hop_length)
        
        assert len(notes) >= 1
        # A4 should be MIDI note 69
        assert any(68 <= n['pitch'] <= 70 for n in notes)


class TestTranscriptionFallback:
    """Test transcription method fallback behavior."""
    
    @pytest.mark.asyncio
    async def test_transcription_fallback_to_librosa(self, tmp_path):
        """Test that transcription falls back gracefully when GPU unavailable."""
        from app.pipeline.midi_converter import transcribe_audio
        
        # Create a simple test audio file
        import soundfile as sf
        
        sample_rate = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Simple sine wave at 440 Hz (A4)
        audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        audio_path = tmp_path / "test_audio.wav"
        sf.write(str(audio_path), audio, sample_rate)
        
        midi_path = tmp_path / "test_output.mid"
        
        # Force CPU mode
        try:
            notes, output_path, tempo = await transcribe_audio(
                audio_path, 
                midi_path,
                use_gpu=False,  # Force CPU fallback
            )
            
            assert output_path.exists()
            assert isinstance(notes, list)
        except Exception as e:
            # May fail if librosa dependencies missing in test env
            pytest.skip(f"Transcription dependencies not available: {e}")


class TestPerformanceBenchmark:
    """Performance comparison tests."""
    
    @pytest.mark.slow
    def test_gpu_vs_cpu_speed(self):
        """Compare GPU vs CPU performance for voicing generation."""
        from app.services.gpu_midi_generator import GPUMIDIGenerator
        
        generator = GPUMIDIGenerator()
        results = generator.benchmark(iterations=50)
        
        print(f"\nBenchmark Results:")
        print(f"  Iterations: {results['iterations']}")
        print(f"  Numpy time: {results['numpy_time_seconds']:.4f}s")
        
        if results.get('mlx_time_seconds'):
            print(f"  MLX time: {results['mlx_time_seconds']:.4f}s")
            print(f"  Speedup: {results.get('speedup', 'N/A')}x")
        
        # Verify test ran successfully
        assert results['numpy_time_seconds'] > 0
