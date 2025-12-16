"""Import curriculum templates into database"""
import asyncio
import json
from pathlib import Path

from app.database.session import async_session_maker
from app.services.exercise_library_service import get_exercise_library_service
from app.services.template_parser import template_parser


async def import_all_templates():
    """Import all templates from new-templates directory"""
    templates_dir = Path(__file__).parent.parent / "templates" / "new-templates"

    if not templates_dir.exists():
        print(f"Templates directory not found: {templates_dir}")
        return

    print(f"Scanning templates directory: {templates_dir}")
    template_files = list(templates_dir.glob("*.json")) + list(templates_dir.glob("*.md"))
    print(f"Found {len(template_files)} template files")

    total_curricula = 0
    total_exercises = 0
    total_errors = 0

    async with async_session_maker() as db:
        service = get_exercise_library_service(db)

        for template_file in template_files:
            print(f"\nProcessing: {template_file.name}")

            try:
                # Parse template
                curriculums = template_parser.parse_template_file(template_file)
                print(f"  Found {len(curriculums)} curriculums")

                # Import each curriculum
                for curriculum in curriculums:
                    print(f"  Importing: {curriculum.title}")
                    stats = await service.import_from_template(curriculum)

                    total_curricula += 1
                    total_exercises += stats["exercises_imported"]
                    total_errors += len(stats["errors"])

                    print(f"    ✅ {stats['exercises_imported']} exercises imported")
                    if stats["errors"]:
                        print(f"    ⚠️  {len(stats['errors'])} errors")
                        for error in stats["errors"][:3]:  # Show first 3 errors
                            print(f"       - {error}")

            except Exception as e:
                print(f"  ❌ Error processing {template_file.name}: {e}")
                total_errors += 1

    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Total curricula imported: {total_curricula}")
    print(f"Total exercises imported: {total_exercises}")
    print(f"Total errors: {total_errors}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(import_all_templates())
