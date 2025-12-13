#!/usr/bin/env python
"""View Curriculum - Export curriculum to readable formats

Usage:
    python view_curriculum.py              # Display in terminal
    python view_curriculum.py --json       # Export to JSON
    python view_curriculum.py --markdown   # Export to Markdown
"""

import asyncio
import json
import sys
from pathlib import Path
from sqlalchemy import select

from app.database.session import async_session_maker
from app.database.curriculum_models import (
    Curriculum,
    CurriculumModule,
    CurriculumLesson,
    CurriculumExercise,
)
from app.services.curriculum_service import CurriculumService


async def view_curriculum(curriculum_id: str = None, format: str = "terminal"):
    """View curriculum in specified format"""

    async with async_session_maker() as session:
        service = CurriculumService(session)

        # Get latest curriculum if no ID specified
        if not curriculum_id:
            result = await session.execute(
                select(Curriculum).order_by(Curriculum.created_at.desc()).limit(1)
            )
            curriculum = result.scalar_one_or_none()
            if not curriculum:
                print("No curriculum found in database!")
                return
        else:
            curriculum = await service.get_curriculum_with_details(curriculum_id)

        # Load full details
        curriculum = await service.get_curriculum_with_details(curriculum.id)

        if format == "json":
            export_json(curriculum)
        elif format == "markdown":
            export_markdown(curriculum)
        else:
            display_terminal(curriculum)


def display_terminal(curriculum: Curriculum):
    """Display curriculum in terminal"""
    print("=" * 80)
    print(f"📚 {curriculum.title}")
    print("=" * 80)
    print(f"\n📋 Description: {curriculum.description}")
    print(f"⏱️  Duration: {curriculum.duration_weeks} weeks")
    print(f"📊 Status: {curriculum.status}")
    print(f"🆔 ID: {curriculum.id}")

    total_exercises = 0

    for i, module in enumerate(curriculum.modules, 1):
        print(f"\n{'=' * 80}")
        print(f"📘 MODULE {i}: {module.title}")
        print(f"{'=' * 80}")
        print(f"Weeks: {module.start_week}-{module.end_week}")
        print(f"Theme: {module.theme}")

        if module.outcomes_json:
            outcomes = json.loads(module.outcomes_json)
            if outcomes:
                print("\n🎯 Learning Outcomes:")
                for outcome in outcomes:
                    print(f"   • {outcome}")

        for j, lesson in enumerate(module.lessons, 1):
            print(f"\n   {'─' * 70}")
            print(f"   📖 LESSON {j}: {lesson.title}")
            print(f"   {'─' * 70}")
            print(f"   Week {lesson.week_number} • {len(lesson.exercises)} exercises • {lesson.estimated_duration_minutes} min")

            if lesson.theory_content_json:
                theory = json.loads(lesson.theory_content_json)
                if theory and "summary" in theory:
                    print(f"\n   💡 Theory: {theory['summary']}")

            print(f"\n   📝 Exercises:")
            for k, exercise in enumerate(lesson.exercises, 1):
                total_exercises += 1
                content = json.loads(exercise.content_json)

                print(f"\n      {k}. {exercise.title}")
                print(f"         Type: {exercise.exercise_type} | Difficulty: {exercise.difficulty}")
                print(f"         Duration: {exercise.estimated_duration_minutes} min | BPM: {exercise.target_bpm or 'N/A'}")

                if exercise.exercise_type == "progression" and "chords" in content:
                    chords = " → ".join(content["chords"])
                    print(f"         Chords: {chords}")
                    if "key" in content:
                        print(f"         Key: {content['key']}")

                if exercise.practice_count > 0:
                    print(f"         Practice: {exercise.practice_count} times | Best: {exercise.best_score or 'N/A'}")

    print(f"\n{'=' * 80}")
    print(f"📊 TOTALS")
    print(f"{'=' * 80}")
    print(f"Modules: {len(curriculum.modules)}")
    print(f"Lessons: {sum(len(m.lessons) for m in curriculum.modules)}")
    print(f"Exercises: {total_exercises}")
    print(f"Total Hours: ~{total_exercises * 12 / 60:.1f} hours")
    print("=" * 80)


def export_json(curriculum: Curriculum):
    """Export curriculum to JSON file"""
    output = {
        "id": curriculum.id,
        "title": curriculum.title,
        "description": curriculum.description,
        "duration_weeks": curriculum.duration_weeks,
        "status": curriculum.status,
        "modules": []
    }

    for module in curriculum.modules:
        module_data = {
            "title": module.title,
            "theme": module.theme,
            "weeks": f"{module.start_week}-{module.end_week}",
            "outcomes": json.loads(module.outcomes_json or "[]"),
            "lessons": []
        }

        for lesson in module.lessons:
            lesson_data = {
                "title": lesson.title,
                "week": lesson.week_number,
                "duration_minutes": lesson.estimated_duration_minutes,
                "theory": json.loads(lesson.theory_content_json or "{}"),
                "exercises": []
            }

            for exercise in lesson.exercises:
                exercise_data = {
                    "title": exercise.title,
                    "type": exercise.exercise_type,
                    "difficulty": exercise.difficulty,
                    "duration_minutes": exercise.estimated_duration_minutes,
                    "bpm": exercise.target_bpm,
                    "content": json.loads(exercise.content_json)
                }
                lesson_data["exercises"].append(exercise_data)

            module_data["lessons"].append(lesson_data)

        output["modules"].append(module_data)

    filename = f"curriculum_{curriculum.id[:8]}.json"
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Exported to: {filename}")


def export_markdown(curriculum: Curriculum):
    """Export curriculum to Markdown file"""
    lines = [
        f"# {curriculum.title}",
        "",
        f"**Duration:** {curriculum.duration_weeks} weeks  ",
        f"**Status:** {curriculum.status}  ",
        f"**ID:** `{curriculum.id}`",
        "",
        f"## Description",
        "",
        curriculum.description or "N/A",
        "",
    ]

    for i, module in enumerate(curriculum.modules, 1):
        lines.extend([
            f"## Module {i}: {module.title}",
            "",
            f"**Weeks:** {module.start_week}-{module.end_week}  ",
            f"**Theme:** {module.theme}",
            "",
        ])

        outcomes = json.loads(module.outcomes_json or "[]")
        if outcomes:
            lines.append("**Learning Outcomes:**")
            for outcome in outcomes:
                lines.append(f"- {outcome}")
            lines.append("")

        for j, lesson in enumerate(module.lessons, 1):
            lines.extend([
                f"### Lesson {j}: {lesson.title}",
                "",
                f"**Week {lesson.week_number}** | {len(lesson.exercises)} exercises | {lesson.estimated_duration_minutes} min",
                "",
            ])

            theory = json.loads(lesson.theory_content_json or "{}")
            if theory and "summary" in theory:
                lines.extend([
                    "**Theory:**",
                    theory["summary"],
                    "",
                ])

            lines.append("**Exercises:**")
            lines.append("")

            for k, exercise in enumerate(lesson.exercises, 1):
                content = json.loads(exercise.content_json)
                lines.append(f"{k}. **{exercise.title}**")
                lines.append(f"   - Type: {exercise.exercise_type}")
                lines.append(f"   - Difficulty: {exercise.difficulty}")
                lines.append(f"   - Duration: {exercise.estimated_duration_minutes} min")

                if exercise.exercise_type == "progression" and "chords" in content:
                    chords = " → ".join(content["chords"])
                    lines.append(f"   - Progression: `{chords}`")
                    if "key" in content:
                        lines.append(f"   - Key: {content['key']}")

                lines.append("")

            lines.append("")

    filename = f"curriculum_{curriculum.id[:8]}.md"
    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Exported to: {filename}")


if __name__ == "__main__":
    format = "terminal"
    curriculum_id = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "--json":
            format = "json"
        elif sys.argv[1] == "--markdown" or sys.argv[1] == "--md":
            format = "markdown"
        elif sys.argv[1].startswith("--"):
            print("Usage: python view_curriculum.py [--json|--markdown]")
            sys.exit(1)
        else:
            curriculum_id = sys.argv[1]

    asyncio.run(view_curriculum(curriculum_id, format))
