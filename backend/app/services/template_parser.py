"""Template Parser Service

Parses curriculum templates from multiple formats (JSON, Markdown, Python dict syntax)
and converts them into standardized TemplateCurriculum objects.

Supports templates from:
- Claude (markdown with Python dict)
- Gemini (markdown/JSON)
- DeepSeek (markdown/JSON)
- Grok (JSON)
- Perplexity (JSON)
- ChatGPT (JSON)
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from app.schemas.curriculum import (
    TemplateCurriculum,
    TemplateModule,
    TemplateLesson,
    TemplateExercise,
    EnhancedExerciseContent,
    TheoryContent,
    MIDIHints,
    ExerciseTypeEnum,
    DifficultyLevelEnum,
    SkillLevelEnum,
    TemplateMetadata,
    TemplateIndex,
)


class TemplateParser:
    """Parse curriculum templates from multiple AI providers"""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def parse_template_file(self, file_path: Path) -> List[TemplateCurriculum]:
        """Parse a template file and extract all curriculums

        Args:
            file_path: Path to template file

        Returns:
            List of TemplateCurriculum objects extracted from file
        """
        # Detect format
        file_format = self._detect_format(file_path)
        ai_provider = self._detect_provider(file_path.name)

        # Parse based on format
        if file_format == "json":
            raw_data = self._parse_json(file_path)
        elif file_format == "markdown":
            raw_data = self._parse_markdown_with_python(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")

        # Convert to TemplateCurriculum objects
        curriculums = self._convert_to_template_curriculums(
            raw_data,
            source_file=str(file_path),
            ai_provider=ai_provider
        )

        return curriculums

    def _detect_format(self, file_path: Path) -> str:
        """Detect template file format"""
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            return "json"
        elif suffix == ".md":
            return "markdown"
        else:
            raise ValueError(f"Unknown file type: {suffix}")

    def _detect_provider(self, filename: str) -> str:
        """Detect AI provider from filename"""
        filename_lower = filename.lower()
        if "claude" in filename_lower:
            return "claude"
        elif "gemini" in filename_lower or "gimi" in filename_lower:
            return "gemini"
        elif "deepseek" in filename_lower:
            return "deepseek"
        elif "grok" in filename_lower:
            return "grok"
        elif "perplexity" in filename_lower:
            return "perplexity"
        elif "chatgpt" in filename_lower:
            return "chatgpt"
        else:
            return "unknown"

    def _parse_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse pure JSON file (handles multiple JSON objects)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

            # Try parsing as single JSON object first
            try:
                return json.loads(content)
            except json.JSONDecodeError as first_error:
                # If fails due to "Extra data", parse multiple JSON objects
                if "Extra data" in str(first_error):
                    decoder = json.JSONDecoder()
                    idx = 0
                    objects = []

                    while idx < len(content):
                        content_from_idx = content[idx:].lstrip()
                        if not content_from_idx:
                            break
                        try:
                            obj, end_idx = decoder.raw_decode(content_from_idx)
                            objects.append(obj)
                            idx += len(content[idx:]) - len(content_from_idx) + end_idx
                        except json.JSONDecodeError:
                            break

                    # Return as dict of curriculum objects
                    if len(objects) > 1:
                        return {f"curriculum_{i}": obj for i, obj in enumerate(objects)}
                    elif len(objects) == 1:
                        return objects[0]
                    else:
                        raise first_error  # Re-raise original error
                else:
                    # For other JSON errors, try line-by-line parsing
                    objects = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if line:
                            try:
                                obj = json.loads(line)
                                objects.append(obj)
                            except json.JSONDecodeError:
                                continue

                    if objects:
                        if len(objects) > 1:
                            return {f"curriculum_{i}": obj for i, obj in enumerate(objects)}
                        else:
                            return objects[0]
                    else:
                        raise first_error  # Re-raise original error

    def _parse_markdown_with_python(self, file_path: Path) -> Dict[str, Any]:
        """Parse markdown file containing Python dict syntax

        Example formats:
        ```python
        GOSPEL_KEYS_ESSENTIALS = {
            "title": "...",
            ...
        }
        ```
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract Python dict definitions
        # Pattern: VARIABLE_NAME = { ... }
        pattern = r'([A-Z_]+)\s*=\s*(\{[\s\S]*?\n\})'
        matches = re.finditer(pattern, content)

        all_curriculums = {}
        for match in matches:
            var_name = match.group(1)
            dict_content = match.group(2)

            # Try to safely evaluate the dict
            try:
                # Replace True/False with lowercase for JSON compatibility
                dict_content = dict_content.replace('True', 'true').replace('False', 'false')
                curriculum_data = json.loads(dict_content)
                all_curriculums[var_name] = curriculum_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try a more lenient approach
                print(f"Warning: Could not parse {var_name} from {file_path.name}")
                continue

        return all_curriculums

    def _convert_to_template_curriculums(
        self,
        raw_data: Dict[str, Any],
        source_file: str,
        ai_provider: str
    ) -> List[TemplateCurriculum]:
        """Convert raw parsed data to TemplateCurriculum objects

        Handles both:
        1. Single curriculum (raw_data is the curriculum dict)
        2. Multiple curriculums (raw_data is dict of curriculum_id -> curriculum dict)
        """
        curriculums = []

        # Case 1: Single curriculum (has 'title' key at root)
        if "title" in raw_data and "modules" in raw_data:
            curriculum = self._build_curriculum(
                raw_data,
                source_file=source_file,
                ai_provider=ai_provider
            )
            curriculums.append(curriculum)
        # Case 2: Multiple curriculums (dict of dicts)
        else:
            for curriculum_id, curriculum_data in raw_data.items():
                if isinstance(curriculum_data, dict) and "title" in curriculum_data:
                    curriculum = self._build_curriculum(
                        curriculum_data,
                        curriculum_id=curriculum_id,
                        source_file=source_file,
                        ai_provider=ai_provider
                    )
                    curriculums.append(curriculum)

        return curriculums

    def _build_curriculum(
        self,
        data: Dict[str, Any],
        curriculum_id: Optional[str] = None,
        source_file: str = "",
        ai_provider: str = ""
    ) -> TemplateCurriculum:
        """Build a TemplateCurriculum object from raw data"""
        # Parse modules
        modules = []
        for module_data in data.get("modules", []):
            module = self._build_module(module_data)
            modules.append(module)

        # Determine skill level
        level_str = data.get("level", "beginner")
        skill_level = self._parse_skill_level(level_str)

        return TemplateCurriculum(
            id=curriculum_id or data.get("id"),
            title=data.get("title", "Untitled Curriculum"),
            description=data.get("description", ""),
            style_tags=data.get("style_tags", []),
            level=skill_level,
            estimated_total_weeks=data.get("estimated_total_weeks", 12),
            modules=modules,
            source_file=source_file,
            created_at=datetime.now(),
            ai_provider=ai_provider
        )

    def _build_module(self, data: Dict[str, Any]) -> TemplateModule:
        """Build a TemplateModule object from raw data"""
        # Parse lessons
        lessons = []
        for lesson_data in data.get("lessons", []):
            lesson = self._build_lesson(lesson_data)
            lessons.append(lesson)

        return TemplateModule(
            id=data.get("id"),
            title=data.get("title", "Untitled Module"),
            description=data.get("description", ""),
            theme=data.get("theme"),
            start_week=data.get("start_week", 1),
            end_week=data.get("end_week", 4),
            prerequisites=data.get("prerequisites", []),
            outcomes=data.get("outcomes", []),
            lessons=lessons
        )

    def _build_lesson(self, data: Dict[str, Any]) -> TemplateLesson:
        """Build a TemplateLesson object from raw data"""
        # Parse theory content
        theory_content = None
        if "theory_content" in data:
            theory_data = data["theory_content"]
            theory_content = TheoryContent(
                summary=theory_data.get("summary", ""),
                key_points=theory_data.get("key_points", []),
                recommended_keys=theory_data.get("recommended_keys")
            )

        # Parse exercises
        exercises = []
        for exercise_data in data.get("exercises", []):
            exercise = self._build_exercise(exercise_data)
            exercises.append(exercise)

        return TemplateLesson(
            id=data.get("id"),
            title=data.get("title", "Untitled Lesson"),
            description=data.get("description", ""),
            week_number=data.get("week_number", 1),
            concepts=data.get("concepts", []),
            theory_content=theory_content,
            exercises=exercises,
            prerequisites=data.get("prerequisites", []),
            learning_objectives=data.get("learning_objectives", [])
        )

    def _build_exercise(self, data: Dict[str, Any]) -> TemplateExercise:
        """Build a TemplateExercise object from raw data"""
        # Parse content
        content_data = data.get("content", {})
        content = self._build_exercise_content(content_data)

        # Parse exercise type
        exercise_type_str = data.get("exercise_type", "scale")
        exercise_type = self._parse_exercise_type(exercise_type_str)

        # Parse difficulty
        difficulty_str = data.get("difficulty", "beginner")
        difficulty = self._parse_difficulty(difficulty_str)

        return TemplateExercise(
            id=data.get("id"),
            title=data.get("title", "Untitled Exercise"),
            description=data.get("description", ""),
            exercise_type=exercise_type,
            content=content,
            midi_prompt=data.get("midi_prompt"),
            difficulty=difficulty,
            estimated_duration_minutes=data.get("estimated_duration_minutes", 10),
            tags=data.get("tags", [])
        )

    def _build_exercise_content(self, data: Dict[str, Any]) -> EnhancedExerciseContent:
        """Build EnhancedExerciseContent from raw data"""
        # Parse MIDI hints if present
        midi_hints = None
        if "midi_hints" in data:
            hints_data = data["midi_hints"]
            midi_hints = MIDIHints(
                tempo_bpm=hints_data.get("tempo_bpm", 60),
                swing=hints_data.get("swing", False),
                articulation=hints_data.get("articulation", "legato"),
                voicing_type=hints_data.get("voicing_type"),
                time_signature=hints_data.get("time_signature", "4/4")
            )

        return EnhancedExerciseContent(
            key=data.get("key"),
            chords=data.get("chords"),
            scale=data.get("scale"),
            pattern=data.get("pattern"),
            notes_per_step=data.get("notes_per_step"),
            include_inversions=data.get("include_inversions"),
            hands=data.get("hands"),
            octaves=data.get("octaves"),
            roman_numerals=data.get("roman_numerals"),
            left_hand=data.get("left_hand"),
            right_hand=data.get("right_hand"),
            chord=data.get("chord"),
            voicing_type=data.get("voicing_type"),
            notes=data.get("notes"),
            inversions=data.get("inversions"),
            midi_notes=data.get("midi_notes"),
            effects=data.get("effects"),
            style=data.get("style"),
            midi_hints=midi_hints,
            extra={k: v for k, v in data.items() if k not in [
                "key", "chords", "scale", "pattern", "notes_per_step",
                "include_inversions", "hands", "octaves", "roman_numerals",
                "left_hand", "right_hand", "chord", "voicing_type",
                "notes", "inversions", "midi_notes", "effects", "style", "midi_hints"
            ]}
        )

    def _parse_exercise_type(self, type_str: str) -> ExerciseTypeEnum:
        """Parse exercise type string to enum"""
        type_map = {
            "scale": ExerciseTypeEnum.SCALE,
            "progression": ExerciseTypeEnum.PROGRESSION,
            "voicing": ExerciseTypeEnum.VOICING,
            "rhythm": ExerciseTypeEnum.RHYTHM,
            "lick": ExerciseTypeEnum.LICK,
            "repertoire": ExerciseTypeEnum.REPERTOIRE,
            "arpeggio": ExerciseTypeEnum.ARPEGGIO,
            "dynamics": ExerciseTypeEnum.DYNAMICS,
            "aural": ExerciseTypeEnum.AURAL,
            "ear_training": ExerciseTypeEnum.AURAL,
            "transcription": ExerciseTypeEnum.TRANSCRIPTION,
            "reharmonization": ExerciseTypeEnum.REHARMONIZATION,
            "sight_reading": ExerciseTypeEnum.SIGHT_READING,
            "improvisation": ExerciseTypeEnum.IMPROVISATION,
            "comping": ExerciseTypeEnum.COMPING,
            "walking_bass": ExerciseTypeEnum.WALKING_BASS,
            "melody_harmonization": ExerciseTypeEnum.MELODY_HARMONIZATION,
            "modal_exploration": ExerciseTypeEnum.MODAL_EXPLORATION,
            "polyrhythm": ExerciseTypeEnum.POLYRHYTHM,
            "production": ExerciseTypeEnum.PRODUCTION,
            "drill": ExerciseTypeEnum.DRILL,
        }
        return type_map.get(type_str.lower(), ExerciseTypeEnum.SCALE)

    def _parse_difficulty(self, difficulty_str: str) -> DifficultyLevelEnum:
        """Parse difficulty string to enum"""
        difficulty_map = {
            "beginner": DifficultyLevelEnum.BEGINNER,
            "intermediate": DifficultyLevelEnum.INTERMEDIATE,
            "advanced": DifficultyLevelEnum.ADVANCED,
            "master": DifficultyLevelEnum.MASTER,
        }
        return difficulty_map.get(difficulty_str.lower(), DifficultyLevelEnum.BEGINNER)

    def _parse_skill_level(self, level_str: str) -> SkillLevelEnum:
        """Parse skill level string to enum"""
        level_map = {
            "beginner": SkillLevelEnum.BEGINNER,
            "intermediate": SkillLevelEnum.INTERMEDIATE,
            "advanced": SkillLevelEnum.ADVANCED,
            "master": SkillLevelEnum.MASTER,
            "beginner_to_intermediate": SkillLevelEnum.BEGINNER_TO_INTERMEDIATE,
            "intermediate_to_advanced": SkillLevelEnum.INTERMEDIATE_TO_ADVANCED,
        }
        return level_map.get(level_str.lower(), SkillLevelEnum.BEGINNER)

    def extract_metadata(self, file_path: Path) -> TemplateMetadata:
        """Extract metadata from a template file without full parsing"""
        try:
            # Parse the file
            curriculums = self.parse_template_file(file_path)

            # Aggregate statistics
            total_modules = sum(len(c.modules) for c in curriculums)
            total_lessons = sum(len(m.lessons) for c in curriculums for m in c.modules)
            total_exercises = sum(
                len(l.exercises)
                for c in curriculums
                for m in c.modules
                for l in m.lessons
            )

            # Extract genres
            all_genres = set()
            for curriculum in curriculums:
                all_genres.update(curriculum.style_tags)

            # Extract skill levels
            skill_levels = list(set(c.level for c in curriculums))

            # Check for features
            has_midi_prompts = any(
                ex.midi_prompt is not None
                for c in curriculums
                for m in c.modules
                for l in m.lessons
                for ex in l.exercises
            )

            has_ear_training = any(
                ex.exercise_type == ExerciseTypeEnum.AURAL
                for c in curriculums
                for m in c.modules
                for l in m.lessons
                for ex in l.exercises
            )

            has_theory_content = any(
                l.theory_content is not None
                for c in curriculums
                for m in c.modules
                for l in m.lessons
            )

            # Calculate average weeks
            avg_weeks = (
                sum(c.estimated_total_weeks for c in curriculums) / len(curriculums)
                if curriculums
                else 0
            )

            return TemplateMetadata(
                file_path=str(file_path),
                file_name=file_path.name,
                file_format=self._detect_format(file_path),
                ai_provider=curriculums[0].ai_provider if curriculums else "unknown",
                curriculum_count=len(curriculums),
                total_modules=total_modules,
                total_lessons=total_lessons,
                total_exercises=total_exercises,
                genres_covered=list(all_genres),
                skill_levels=skill_levels,
                has_midi_prompts=has_midi_prompts,
                has_ear_training=has_ear_training,
                has_theory_content=has_theory_content,
                avg_weeks_per_curriculum=avg_weeks
            )
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return None

    def index_all_templates(self) -> TemplateIndex:
        """Index all template files in templates directory"""
        template_files = list(self.templates_dir.glob("**/*.json")) + list(
            self.templates_dir.glob("**/*.md")
        )

        metadata_list = []
        for file_path in template_files:
            metadata = self.extract_metadata(file_path)
            if metadata:
                metadata_list.append(metadata)

        # Aggregate statistics
        total_curriculums = sum(m.curriculum_count for m in metadata_list)
        total_exercises = sum(m.total_exercises for m in metadata_list)

        all_genres = set()
        for metadata in metadata_list:
            all_genres.update(metadata.genres_covered)

        providers = list(set(m.ai_provider for m in metadata_list))

        return TemplateIndex(
            templates=metadata_list,
            total_curriculums=total_curriculums,
            total_exercises=total_exercises,
            genres_available=list(all_genres),
            providers=providers,
            indexed_at=datetime.now()
        )


# Global parser instance
# Determine templates directory relative to backend directory
_backend_dir = Path(__file__).parent.parent.parent  # Go up to backend/
_templates_dir = _backend_dir.parent / "templates" / "new-templates"  # Up to project root, then templates
template_parser = TemplateParser(_templates_dir)
