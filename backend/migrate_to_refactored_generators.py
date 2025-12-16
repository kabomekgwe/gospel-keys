#!/usr/bin/env python3
"""
Migration script to update all API routes to use refactored generators.

This script updates the imports in API route files to use the new refactored
generator services.

Usage:
    python migrate_to_refactored_generators.py
"""

import re
from pathlib import Path


def update_import(file_path: Path, old_import: str, new_import: str):
    """Update import statement in a file."""
    content = file_path.read_text()

    # Replace the import
    updated_content = content.replace(old_import, new_import)

    if content != updated_content:
        file_path.write_text(updated_content)
        print(f"✅ Updated {file_path.name}")
        return True
    else:
        print(f"⏭️  Skipped {file_path.name} (no changes needed)")
        return False


def migrate_routes():
    """Migrate all API route files to use refactored generators."""
    routes_dir = Path("app/api/routes")

    if not routes_dir.exists():
        print(f"❌ Routes directory not found: {routes_dir}")
        return

    migrations = [
        {
            "file": "gospel.py",
            "old": "from app.services.gospel_generator import gospel_generator_service",
            "new": "from app.services.gospel_generator_refactored import gospel_generator_service"
        },
        {
            "file": "jazz.py",
            "old": "from app.services.jazz_generator import jazz_generator_service",
            "new": "from app.services.jazz_generator_refactored import jazz_generator_service"
        },
        {
            "file": "blues.py",
            "old": "from app.services.blues_generator import blues_generator_service",
            "new": "from app.services.blues_generator_refactored import blues_generator_service"
        },
        {
            "file": "neosoul.py",
            "old": "from app.services.neosoul_generator import neosoul_generator_service",
            "new": "from app.services.neosoul_generator_refactored import neosoul_generator_service"
        },
        {
            "file": "classical.py",
            "old": "from app.services.classical_generator import classical_generator_service",
            "new": "from app.services.classical_generator_refactored import classical_generator_service"
        }
    ]

    total_updated = 0
    for migration in migrations:
        file_path = routes_dir / migration["file"]

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        if update_import(file_path, migration["old"], migration["new"]):
            total_updated += 1

    print(f"\n✨ Migration complete! Updated {total_updated} files.")
    print("\nNext steps:")
    print("1. Run tests: pytest tests/")
    print("2. Verify API responses: python -m pytest tests/integration/")
    print("3. Start server and test manually")
    print("4. If all tests pass, rename refactored files to remove '_refactored' suffix")


def rollback_routes():
    """Rollback to original generators if needed."""
    routes_dir = Path("app/api/routes")

    migrations = [
        {
            "file": "gospel.py",
            "old": "from app.services.gospel_generator_refactored import gospel_generator_service",
            "new": "from app.services.gospel_generator import gospel_generator_service"
        },
        {
            "file": "jazz.py",
            "old": "from app.services.jazz_generator_refactored import jazz_generator_service",
            "new": "from app.services.jazz_generator import jazz_generator_service"
        },
        {
            "file": "blues.py",
            "old": "from app.services.blues_generator_refactored import blues_generator_service",
            "new": "from app.services.blues_generator import blues_generator_service"
        },
        {
            "file": "neosoul.py",
            "old": "from app.services.neosoul_generator_refactored import neosoul_generator_service",
            "new": "from app.services.neosoul_generator import neosoul_generator_service"
        },
        {
            "file": "classical.py",
            "old": "from app.services.classical_generator_refactored import classical_generator_service",
            "new": "from app.services.classical_generator import classical_generator_service"
        }
    ]

    total_updated = 0
    for migration in migrations:
        file_path = routes_dir / migration["file"]

        if file_path.exists():
            if update_import(file_path, migration["old"], migration["new"]):
                total_updated += 1

    print(f"\n✨ Rollback complete! Reverted {total_updated} files.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("🔄 Rolling back to original generators...\n")
        rollback_routes()
    else:
        print("🚀 Migrating to refactored generators...\n")
        migrate_routes()
