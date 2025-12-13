"""Audio Pipeline Service for Exercise Audio Generation

Converts MIDI files and exercise content into high-quality audio using:
1. FluidSynth (MIDI → WAV with piano soundfont)
2. Stable Audio (AI-generated audio from text prompts)
"""

import json
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Optional, Literal

from app.database.curriculum_models import CurriculumExercise
from app.services.stable_audio_service import stable_audio_service
from app.services.midi_generation_service import midi_generation_service
from app.core.config import settings

logger = logging.getLogger(__name__)

# Import Rust audio engine (M4 GPU-accelerated)
try:
    import rust_audio_engine
    RUST_ENGINE_AVAILABLE = True
    logger.info("🚀 Rust audio engine loaded (M4 GPU acceleration enabled)")
except ImportError:
    RUST_ENGINE_AVAILABLE = False
    logger.warning("Rust audio engine not available, falling back to FluidSynth")

AudioMethod = Literal["fluidsynth", "stable_audio", "both"]


class AudioPipelineService:
    """Service for generating exercise audio via multiple methods"""

    def __init__(self):
        self.output_dir = Path(settings.OUTPUTS_DIR) / "exercises" / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # FluidSynth settings
        self.soundfont_path = Path(settings.BASE_DIR) / "soundfonts" / "TimGM6mb.sf2"
        self.sample_rate = 44100

        # Check if FluidSynth is available
        self.fluidsynth_available = self._check_fluidsynth()

        # Check if soundfont exists
        if not self.soundfont_path.exists():
            logger.warning(f"Soundfont not found at {self.soundfont_path}")
            logger.warning("Download from: https://sourceforge.net/projects/androidframe/files/soundfonts/")

    def _check_fluidsynth(self) -> bool:
        """Check if FluidSynth is installed on the system"""
        try:
            result = subprocess.run(
                ["fluidsynth", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"FluidSynth detected: {result.stdout.split()[0]}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("FluidSynth not found. Install with: brew install fluidsynth")

        return False

    async def generate_exercise_audio(
        self,
        exercise: CurriculumExercise,
        method: AudioMethod = "both",
        midi_path: Optional[Path] = None
    ) -> Dict[str, Optional[Path]]:
        """Generate audio for a curriculum exercise

        Args:
            exercise: CurriculumExercise model instance
            method: Audio generation method ("fluidsynth", "stable_audio", "both")
            midi_path: Pre-generated MIDI file path (optional)

        Returns:
            Dict with audio file paths: {"fluidsynth": Path, "stable_audio": Path}
        """
        try:
            result = {"fluidsynth": None, "stable_audio": None}

            # Generate MIDI if not provided
            if not midi_path:
                midi_path = await midi_generation_service.generate_exercise_midi(exercise)

            # Generate FluidSynth audio
            if method in ["fluidsynth", "both"]:
                if self.fluidsynth_available and self.soundfont_path.exists():
                    fluidsynth_path = await self.generate_fluidsynth_audio(
                        midi_path=midi_path,
                        exercise_id=exercise.id
                    )
                    result["fluidsynth"] = fluidsynth_path
                else:
                    logger.warning("FluidSynth or soundfont unavailable, skipping")

            # Generate Stable Audio
            if method in ["stable_audio", "both"]:
                stable_audio_path = await self.generate_stable_audio_from_exercise(
                    exercise=exercise
                )
                result["stable_audio"] = stable_audio_path

            return result

        except Exception as e:
            logger.error(f"Failed to generate audio for exercise {exercise.id}: {e}")
            raise e

    async def generate_rust_audio(
        self,
        midi_path: Path,
        exercise_id: str,
        use_gpu: bool = True,
        reverb: bool = True
    ) -> Path:
        """Generate WAV audio from MIDI using Rust engine (M4 GPU-accelerated)

        This is 100x faster than FluidSynth subprocess!

        Args:
            midi_path: Path to MIDI file
            exercise_id: Exercise identifier
            use_gpu: Enable Metal GPU acceleration (default: True)
            reverb: Enable reverb effect (default: True)

        Returns:
            Path to generated WAV file
        """
        if not RUST_ENGINE_AVAILABLE:
            raise RuntimeError("Rust audio engine not available")

        if not self.soundfont_path.exists():
            raise FileNotFoundError(f"Soundfont not found: {self.soundfont_path}")

        output_path = self.output_dir / f"{exercise_id}_fluidsynth.wav"

        try:
            # Run Rust synthesis in executor (it's fast, but still I/O bound)
            loop = asyncio.get_event_loop()

            def _run_rust_synthesis():
                logger.info(f"🚀 Running Rust synthesis (M4 GPU): {midi_path}")
                start_time = asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0

                duration = rust_audio_engine.synthesize_midi(
                    midi_path=str(midi_path),
                    output_path=str(output_path),
                    soundfont_path=str(self.soundfont_path),
                    sample_rate=self.sample_rate,
                    use_gpu=use_gpu,
                    reverb=reverb
                )

                elapsed = asyncio.get_event_loop().time() - start_time if hasattr(asyncio.get_event_loop(), 'time') else 0
                logger.info(f"✅ Rust synthesis complete in {elapsed:.2f}s (audio duration: {duration:.2f}s)")
                return output_path

            result_path = await loop.run_in_executor(None, _run_rust_synthesis)
            return result_path

        except Exception as e:
            logger.error(f"Rust synthesis failed: {e}")
            raise e

    async def generate_fluidsynth_audio(
        self,
        midi_path: Path,
        exercise_id: str,
        gain: float = 0.5
    ) -> Path:
        """Generate WAV audio from MIDI using FluidSynth or Rust engine

        Automatically uses Rust engine (100x faster) if available,
        falls back to FluidSynth subprocess.

        Args:
            midi_path: Path to MIDI file
            exercise_id: Exercise identifier
            gain: Audio gain level (0.0-1.0)

        Returns:
            Path to generated WAV file
        """
        # Use Rust engine if available (100x faster!)
        if RUST_ENGINE_AVAILABLE and self.soundfont_path.exists():
            try:
                return await self.generate_rust_audio(
                    midi_path=midi_path,
                    exercise_id=exercise_id,
                    use_gpu=True,
                    reverb=True
                )
            except Exception as e:
                logger.warning(f"Rust engine failed, falling back to FluidSynth: {e}")

        # Fallback to FluidSynth subprocess
        if not self.fluidsynth_available:
            raise RuntimeError("Neither Rust engine nor FluidSynth is available")

        if not self.soundfont_path.exists():
            raise FileNotFoundError(f"Soundfont not found: {self.soundfont_path}")

        output_path = self.output_dir / f"{exercise_id}_fluidsynth.wav"

        # FluidSynth command
        # -ni: non-interactive, -g: gain, -F: output file, -r: sample rate
        command = [
            "fluidsynth",
            "-ni",
            str(self.soundfont_path),
            str(midi_path),
            "-F", str(output_path),
            "-r", str(self.sample_rate),
            "-g", str(gain)
        ]

        try:
            # Run FluidSynth in executor to avoid blocking
            loop = asyncio.get_event_loop()

            def _run_fluidsynth():
                logger.info(f"Running FluidSynth: {' '.join(command)}")
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    raise RuntimeError(f"FluidSynth failed: {result.stderr}")

                return output_path

            result_path = await loop.run_in_executor(None, _run_fluidsynth)
            logger.info(f"FluidSynth audio generated: {result_path}")
            return result_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("FluidSynth timeout (>60s)")
        except Exception as e:
            logger.error(f"FluidSynth generation failed: {e}")
            raise e

    async def generate_stable_audio_from_exercise(
        self,
        exercise: CurriculumExercise,
        duration: Optional[float] = None,
        num_inference_steps: int = 100
    ) -> Path:
        """Generate AI audio from exercise using Stable Audio

        Args:
            exercise: CurriculumExercise model instance
            duration: Audio duration in seconds (auto-calculated if None)
            num_inference_steps: Quality vs speed (50-200)

        Returns:
            Path to generated WAV file
        """
        try:
            # Build prompt from exercise content
            prompt = self._build_stable_audio_prompt(exercise)

            # Calculate duration if not provided
            if duration is None:
                duration = self._estimate_duration(exercise)

            # Output path
            output_path = self.output_dir / f"{exercise.id}_stable_audio.wav"

            # Generate audio using Stable Audio service
            result_path = await stable_audio_service.generate_audio(
                prompt=prompt,
                duration=duration,
                num_inference_steps=num_inference_steps,
                output_path=output_path
            )

            logger.info(f"Stable Audio generated: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Stable Audio generation failed: {e}")
            raise e

    def _build_stable_audio_prompt(self, exercise: CurriculumExercise) -> str:
        """Build text prompt for Stable Audio from exercise content

        Args:
            exercise: CurriculumExercise model instance

        Returns:
            Text prompt string
        """
        try:
            content = json.loads(exercise.content_json)
            exercise_type = exercise.exercise_type

            # Base prompt
            prompt_parts = ["Piano"]

            # Add style/mood
            if "style" in content:
                prompt_parts.append(content["style"])

            # Type-specific details
            if exercise_type == "progression":
                chords = content.get("chords", [])
                key = content.get("key", "C")
                chord_str = ", ".join(chords[:4])  # Limit to first 4
                prompt_parts.append(f"chord progression in {key}: {chord_str}")

            elif exercise_type == "scale":
                scale = content.get("scale", "major")
                key = content.get("key", "C")
                prompt_parts.append(f"{key} {scale} scale")

            elif exercise_type == "voicing":
                chord = content.get("chord", "Cmaj7")
                prompt_parts.append(f"{chord} voicing")

            # Add tempo indication
            bpm = exercise.target_bpm or 90
            if bpm < 80:
                prompt_parts.append("slow tempo")
            elif bpm > 140:
                prompt_parts.append("fast tempo")
            else:
                prompt_parts.append("moderate tempo")

            # Add difficulty/style hints
            if exercise.difficulty in ["advanced", "expert"]:
                prompt_parts.append("complex voicings")

            prompt = ", ".join(prompt_parts)

            logger.debug(f"Built Stable Audio prompt: {prompt}")
            return prompt

        except Exception as e:
            logger.warning(f"Failed to build detailed prompt: {e}")
            return "Piano music"

    def _estimate_duration(self, exercise: CurriculumExercise) -> float:
        """Estimate audio duration from exercise content

        Args:
            exercise: CurriculumExercise model instance

        Returns:
            Duration in seconds
        """
        try:
            content = json.loads(exercise.content_json)
            exercise_type = exercise.exercise_type
            bpm = exercise.target_bpm or 90

            if exercise_type == "progression":
                num_chords = len(content.get("chords", []))
                beats_per_chord = 4
                total_beats = num_chords * beats_per_chord
                duration = (total_beats / bpm) * 60

            elif exercise_type == "scale":
                octaves = content.get("octaves", 2)
                # Rough estimate: 2 octaves ~ 10 seconds at 100 BPM
                duration = octaves * 5 * (100 / bpm)

            elif exercise_type == "voicing":
                # Single chord held
                duration = 4.0

            else:
                # Default duration
                duration = exercise.estimated_duration_minutes * 60 * 0.5

            # Clamp to Stable Audio limits (1-47 seconds)
            return min(max(duration, 5.0), 47.0)

        except Exception as e:
            logger.warning(f"Duration estimation failed: {e}")
            return 10.0  # Safe default


# Singleton instance
audio_pipeline_service = AudioPipelineService()
