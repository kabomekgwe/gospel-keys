#!/usr/bin/env python3
"""
Generate All Role-Specific Technical Diagrams
Creates architecture diagrams, flowcharts, and visualizations for all 8 engineering roles
"""

from pathlib import Path
import sys

# Add role_guides directory to path
sys.path.insert(0, str(Path(__file__).parent / "role_guides/generators"))

from diagram_generator import DiagramGenerator


def main():
    """Generate all role-specific technical diagrams."""
    print("=" * 70)
    print("📊 Piano Keys - Role-Specific Technical Diagram Generator")
    print("=" * 70)
    print()
    print("Generating comprehensive technical diagrams for 8 engineering roles:")
    print("  - Backend Engineer (4 diagrams)")
    print("  - Frontend Engineer (4 diagrams)")
    print("  - DevOps/SRE Engineer (4 diagrams)")
    print("  - Security Engineer (4 diagrams)")
    print("  - QA/Test Engineer (4 diagrams)")
    print("  - Database Administrator (4 diagrams)")
    print("  - UI/UX Designer (4 diagrams)")
    print("  - Technical Writer (4 diagrams)")
    print()
    print("Total: 32 technical diagrams")
    print("=" * 70)

    # Setup
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output/role_diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Output directory: {output_dir}")
    print()

    # Initialize generator
    generator = DiagramGenerator(output_dir)

    all_diagrams = []

    # Generate diagrams for each role
    print("=" * 70)
    print("📊 Generating Role-Specific Diagrams")
    print("=" * 70)

    # Backend Engineer
    print("\n1️⃣  Backend Engineer")
    print("-" * 70)
    backend_diagrams = generator.generate_backend_diagrams()
    all_diagrams.extend(backend_diagrams)
    print(f"   ✅ Generated {len(backend_diagrams)} diagrams")

    # Frontend Engineer
    print("\n2️⃣  Frontend Engineer")
    print("-" * 70)
    frontend_diagrams = generator.generate_frontend_diagrams()
    all_diagrams.extend(frontend_diagrams)
    print(f"   ✅ Generated {len(frontend_diagrams)} diagrams")

    # DevOps Engineer
    print("\n3️⃣  DevOps/SRE Engineer")
    print("-" * 70)
    devops_diagrams = generator.generate_devops_diagrams()
    all_diagrams.extend(devops_diagrams)
    print(f"   ✅ Generated {len(devops_diagrams)} diagrams")

    # Security Engineer
    print("\n4️⃣  Security Engineer")
    print("-" * 70)
    security_diagrams = generator.generate_security_diagrams()
    all_diagrams.extend(security_diagrams)
    print(f"   ✅ Generated {len(security_diagrams)} diagrams")

    # QA Engineer
    print("\n5️⃣  QA/Test Engineer")
    print("-" * 70)
    qa_diagrams = generator.generate_qa_diagrams()
    all_diagrams.extend(qa_diagrams)
    print(f"   ✅ Generated {len(qa_diagrams)} diagrams")

    # Database Administrator
    print("\n6️⃣  Database Administrator")
    print("-" * 70)
    db_diagrams = generator.generate_database_diagrams()
    all_diagrams.extend(db_diagrams)
    print(f"   ✅ Generated {len(db_diagrams)} diagrams")

    # UX Designer
    print("\n7️⃣  UI/UX Designer")
    print("-" * 70)
    ux_diagrams = generator.generate_ux_diagrams()
    all_diagrams.extend(ux_diagrams)
    print(f"   ✅ Generated {len(ux_diagrams)} diagrams")

    # Technical Writer
    print("\n8️⃣  Technical Writer")
    print("-" * 70)
    writer_diagrams = generator.generate_technical_writer_diagrams()
    all_diagrams.extend(writer_diagrams)
    print(f"   ✅ Generated {len(writer_diagrams)} diagrams")

    # Summary
    print()
    print("=" * 70)
    print("✨ Generation Complete!")
    print("=" * 70)
    print()
    print(f"📊 Total diagrams generated: {len(all_diagrams)}")
    print()

    # List all generated files
    print("📁 Generated Files:")
    print()

    # Group by role
    roles = {
        'Backend Engineer': 'backend_',
        'Frontend Engineer': 'frontend_',
        'DevOps/SRE Engineer': 'devops_',
        'Security Engineer': 'security_',
        'QA/Test Engineer': 'qa_',
        'Database Administrator': 'database_',
        'UI/UX Designer': 'ux_',
        'Technical Writer': 'tech_writer_'
    }

    for role_name, prefix in roles.items():
        role_files = [f for f in all_diagrams if f.name.startswith(prefix)]
        if role_files:
            print(f"  {role_name} ({len(role_files)} diagrams):")
            for f in role_files:
                size_kb = f.stat().st_size // 1024
                print(f"     - {f.name} ({size_kb} KB)")
            print()

    # Calculate total size
    total_size = sum(f.stat().st_size for f in all_diagrams) // 1024
    print(f"💾 Total size: {total_size} KB")
    print()

    print("💡 Next Steps:")
    print("  1. Review the generated diagrams")
    print("  2. Embed diagrams in Word documents")
    print("  3. Add diagrams to PowerPoint presentations")
    print("  4. Share with engineering teams")
    print()
    print(f"All diagrams are in: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
