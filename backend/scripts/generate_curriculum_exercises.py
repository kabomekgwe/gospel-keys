#!/usr/bin/env python3
"""
Batch Exercise Generation Script

Generates MIDI files and exercise metadata from curriculum templates.
This script processes all exercises in templates and creates:
1. MIDI files for each exercise with midi_prompt
2. Optional audio files (WAV) using Rust engine
3. Exercise metadata JSON files
4. Database entries for exercise library

Usage:
    python scripts/generate_curriculum_exercises.py --template templates/new-templates/deepseek-3.md
    python scripts/generate_curriculum_exercises.py --all  # Process all templates
    python scripts/generate_curriculum_exercises.py --index  # Create template index only
"""

import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import List
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.template_parser import template_parser
from app.services.ai_generator import ai_generator_service
from app.schemas.curriculum import (
    TemplateCurriculum,
    TemplateExercise,
    ExerciseTypeEnum,
)
from app.schemas.ai import ArrangeRequest, LickStyle, Difficulty as AIDifficulty
from app.core.config import settings


class ExerciseGenerator:
    """Generate MIDI/audio files from exercise specifications"""

    def __init__(self, output_dir: Path, generate_audio: bool = False):
        self.output_dir = output_dir
        self.generate_audio = generate_audio
        self.ai_service = ai_generator_service

        # Create output directory structure
        self.midi_dir = output_dir / "midi"
        self.audio_dir = output_dir / "audio"
        self.metadata_dir = output_dir / "metadata"

        self.midi_dir.mkdir(parents=True, exist_ok=True)
        if generate_audio:
            self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    async def generate_exercise(
        self,
        exercise: TemplateExercise,
        curriculum_id: str,
        module_id: str,
        lesson_id: str
    ) -> dict:
        """Generate MIDI (and optionally audio) for a single exercise

        Returns:
            dict with generation results
        """
        result = {
            "exercise_id": exercise.id or f"{lesson_id}_{exercise.title.replace(' ', '_')}",
            "success": False,
            "midi_path": None,
            "audio_path": None,
            "error": None
        }

        try:
            # Skip if no MIDI prompt
            if not exercise.midi_prompt:
                result["error"] = "No MIDI prompt provided"
                return result

            # Generate based on exercise type
            midi_path = None

            if exercise.exercise_type == ExerciseTypeEnum.PROGRESSION:
                # Use arrange_progression for chord progressions
                midi_path = await self._generate_progression_midi(
                    exercise,
                    curriculum_id,
                    module_id,
                    lesson_id
                )
            elif exercise.exercise_type == ExerciseTypeEnum.LICK:
                # Generate lick MIDI
                midi_path = await self._generate_lick_midi(
                    exercise,
                    curriculum_id,
                    module_id,
                    lesson_id
                )
            elif exercise.exercise_type in [ExerciseTypeEnum.SCALE, ExerciseTypeEnum.ARPEGGIO]:
                # Generate scale/arpeggio MIDI
                midi_path = await self._generate_scale_midi(
                    exercise,
                    curriculum_id,
                    module_id,
                    lesson_id
                )
            else:
                # For other types, use AI to interpret the MIDI prompt
                midi_path = await self._generate_generic_midi(
                    exercise,
                    curriculum_id,
                    module_id,
                    lesson_id
                )

            if midi_path:
                result["midi_path"] = str(midi_path)
                result["success"] = True

                # Generate audio if requested
                if self.generate_audio:
                    audio_path = await self._synthesize_audio(midi_path)
                    if audio_path:
                        result["audio_path"] = str(audio_path)

                # Update exercise metadata
                exercise.midi_file_path = str(midi_path)
                if result.get("audio_path"):
                    exercise.audio_file_path = result["audio_path"]

        except Exception as e:
            result["error"] = str(e)
            print(f"Error generating exercise {exercise.title}: {e}")

        return result

    async def _generate_progression_midi(
        self,
        exercise: TemplateExercise,
        curriculum_id: str,
        module_id: str,
        lesson_id: str
    ) -> Path:
        """Generate MIDI for chord progression exercise"""
        content = exercise.content

        # Extract parameters
        chords = content.chords or []
        key = content.key or "C"
        tempo = content.midi_hints.tempo_bpm if content.midi_hints else 60

        if not chords:
            raise ValueError("No chords specified for progression")

        # Use arrange_progression endpoint
        request = ArrangeRequest(
            chords=chords,
            key=key,
            tempo=tempo,
            style=LickStyle.GOSPEL,  # Default, could be extracted from metadata
            application="practice",
            time_signature="4/4"
        )

        response = await self.ai_service.arrange_progression(request)

        if response.success:
            # Copy MIDI to organized location
            source_path = Path(response.midi_file_path)
            filename = f"{curriculum_id}_{module_id}_{lesson_id}_{exercise.id or 'ex'}.mid"
            dest_path = self.midi_dir / filename

            import shutil
            shutil.copy(source_path, dest_path)

            return dest_path
        else:
            raise ValueError(f"MIDI generation failed: {response.error}")

    async def _generate_lick_midi(
        self,
        exercise: TemplateExercise,
        curriculum_id: str,
        module_id: str,
        lesson_id: str
    ) -> Path:
        """Generate MIDI for lick exercise"""
        # Would use generate_licks endpoint
        # For now, placeholder
        raise NotImplementedError("Lick MIDI generation not yet implemented")

    async def _generate_scale_midi(
        self,
        exercise: TemplateExercise,
        curriculum_id: str,
        module_id: str,
        lesson_id: str
    ) -> Path:
        """Generate MIDI for scale/arpeggio exercise"""
        # Would generate scale patterns programmatically
        # For now, placeholder
        raise NotImplementedError("Scale MIDI generation not yet implemented")

    async def _generate_generic_midi(
        self,
        exercise: TemplateExercise,
        curriculum_id: str,
        module_id: str,
        lesson_id: str
    ) -> Path:
        """Generate MIDI for generic exercise types using AI interpretation"""
        # Would use AI to interpret midi_prompt and generate MIDI
        # For now, placeholder
        raise NotImplementedError("Generic MIDI generation not yet implemented")

    async def _synthesize_audio(self, midi_path: Path) -> Path:
        """Synthesize audio from MIDI using Rust engine"""
        try:
            from rust_audio_engine import synthesize_midi

            soundfont_path = settings.SOUNDFONT_PATH or "default.sf2"
            audio_filename = midi_path.stem + ".wav"
            audio_path = self.audio_dir / audio_filename

            duration = synthesize_midi(
                midi_path=str(midi_path),
                output_path=str(audio_path),
                soundfont_path=soundfont_path,
                use_gpu=True,
                reverb=True
            )

            return audio_path if audio_path.exists() else None
        except Exception as e:
            print(f"Audio synthesis failed: {e}")
            return None


async def process_template(
    template_file: Path,
    output_dir: Path,
    generate_audio: bool = False,
    curriculum_filter: str = None
):
    """Process a single template file and generate all exercises"""
    print(f"\n{'='*60}")
    print(f"Processing template: {template_file.name}")
    print(f"{'='*60}\n")

    # Parse template
    curriculums = template_parser.parse_template_file(template_file)
    print(f"Found {len(curriculums)} curriculum(s)")

    # Filter if requested
    if curriculum_filter:
        curriculums = [c for c in curriculums if c.id == curriculum_filter]
        print(f"Filtered to 1 curriculum: {curriculum_filter}")

    # Initialize generator
    generator = ExerciseGenerator(output_dir, generate_audio)

    # Statistics
    total_exercises = 0
    generated_exercises = 0
    errors = []

    # Process each curriculum
    for curriculum in curriculums:
        print(f"\n📚 Curriculum: {curriculum.title}")
        print(f"   Skill Level: {curriculum.level.value}")
        print(f"   Modules: {len(curriculum.modules)}")

        for module in curriculum.modules:
            print(f"\n  📂 Module: {module.title} (Weeks {module.start_week}-{module.end_week})")

            for lesson in module.lessons:
                print(f"\n    📖 Lesson {lesson.week_number}: {lesson.title}")
                print(f"       Exercises: {len(lesson.exercises)}")

                for exercise in lesson.exercises:
                    total_exercises += 1
                    print(f"       🎹 {exercise.title} ({exercise.exercise_type.value}) ", end="")

                    result = await generator.generate_exercise(
                        exercise,
                        curriculum_id=curriculum.id or "curriculum",
                        module_id=module.id or f"module_{module.start_week}",
                        lesson_id=lesson.id or f"lesson_{lesson.week_number}"
                    )

                    if result["success"]:
                        print("✅")
                        generated_exercises += 1
                    else:
                        print(f"❌ ({result['error']})")
                        errors.append({
                            "exercise": exercise.title,
                            "error": result["error"]
                        })

        # Save curriculum metadata
        metadata_file = generator.metadata_dir / f"{curriculum.id or 'curriculum'}.json"
        with open(metadata_file, 'w') as f:
            json.dump(curriculum.model_dump(mode='json'), f, indent=2, default=str)

    # Print summary
    print(f"\n{'='*60}")
    print(f"GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total exercises found: {total_exercises}")
    print(f"Successfully generated: {generated_exercises}")
    print(f"Failed: {len(errors)}")
    print(f"Success rate: {generated_exercises/total_exercises*100:.1f}%")

    if errors:
        print(f"\nErrors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error['exercise']}: {error['error']}")


async def main():
    parser = argparse.ArgumentParser(
        description="Generate MIDI files from curriculum templates"
    )
    parser.add_argument(
        "--template",
        type=str,
        help="Path to specific template file to process"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all templates in templates/new-templates/"
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="Create template index only (no generation)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backend/data/exercises",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Also generate audio files (requires Rust engine)"
    )
    parser.add_argument(
        "--curriculum",
        type=str,
        help="Only process specific curriculum by ID"
    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    # Index-only mode
    if args.index:
        print("Creating template index...")
        index = template_parser.index_all_templates()

        # Save index
        index_file = output_dir / "template_index.json"
        index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(index_file, 'w') as f:
            json.dump(index.model_dump(mode='json'), f, indent=2, default=str)

        print(f"✅ Index created: {index_file}")
        print(f"   Total curriculums: {index.total_curriculums}")
        print(f"   Total exercises: {index.total_exercises}")
        print(f"   Genres: {', '.join(index.genres_available)}")
        print(f"   Providers: {', '.join(index.providers)}")
        return

    # Process templates
    if args.all:
        # Process all templates
        template_files = list(Path("templates/new-templates").glob("*.json")) + list(
            Path("templates/new-templates").glob("*.md")
        )
    elif args.template:
        template_files = [Path(args.template)]
    else:
        parser.print_help()
        return

    # Process each template
    start_time = time.time()
    for template_file in template_files:
        try:
            await process_template(
                template_file,
                output_dir,
                generate_audio=args.audio,
                curriculum_filter=args.curriculum
            )
        except Exception as e:
            print(f"\n❌ Error processing {template_file.name}: {e}")

    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
