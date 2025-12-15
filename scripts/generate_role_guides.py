#!/usr/bin/env python3
"""
Main Role Guides Generator
Generates exponentially detailed implementation guides for all 8 engineering roles
Creates Word documents, PowerPoint presentations, and PDF versions
"""

from pathlib import Path
import sys

# Add role_guides directory to path
sys.path.insert(0, str(Path(__file__).parent / "role_guides/generators"))
sys.path.insert(0, str(Path(__file__).parent / "role_guides/content"))

from role_docx_generator import RoleDocxGenerator
from role_pptx_generator import RolePptxGenerator


def main():
    """Generate all role-specific implementation guides."""
    print("=" * 70)
    print("📚 Piano Keys - Role-Specific Implementation Guides Generator")
    print("=" * 70)
    print()
    print("Generating EXPONENTIALLY DETAILED guides for 8 engineering roles:")
    print("  - Backend Engineer")
    print("  - Frontend Engineer")
    print("  - DevOps/SRE Engineer")
    print("  - Security Engineer")
    print("  - QA/Test Engineer")
    print("  - Database Administrator")
    print("  - UI/UX Designer")
    print("  - Technical Writer")
    print()
    print("Each role receives:")
    print("  📄 Word Document (50-100 pages, exponentially detailed)")
    print("  📊 PowerPoint Presentation (30-50 slides)")
    print("  📑 PDF versions of both")
    print()
    print("=" * 70)

    # Paths
    project_root = Path(__file__).parent.parent
    plan_file = project_root / ".claude/plans/production-readiness-plan-source.md"
    configs_dir = Path(__file__).parent / "role_guides/templates/role_configs"
    output_dir = project_root / "output/role_guides"

    # Verify source file exists
    if not plan_file.exists():
        print(f"\n❌ Source file not found: {plan_file}")
        print("Looking for production readiness plan markdown file...")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Output directory: {output_dir}")
    print()

    # Step 1: Generate Word documents
    print("=" * 70)
    print("📄 Step 1/3: Generating Word Documents (Exponentially Detailed)")
    print("=" * 70)

    try:
        docx_generator = RoleDocxGenerator(project_root, plan_file, configs_dir, output_dir)
        docx_files = docx_generator.generate_all_roles()
        print(f"\n✅ Generated {len(docx_files)} Word documents")

        total_size = sum(f.stat().st_size for f in docx_files)
        print(f"   Total size: {total_size // 1024} KB")
    except Exception as e:
        print(f"\n❌ Word generation failed: {e}")
        import traceback
        traceback.print_exc()
        docx_files = []

    print()

    # Step 2: Generate PowerPoint presentations
    print("=" * 70)
    print("📊 Step 2/3: Generating PowerPoint Presentations")
    print("=" * 70)

    try:
        pptx_generator = RolePptxGenerator(project_root, plan_file, configs_dir, output_dir)
        pptx_files = pptx_generator.generate_all_roles()
        print(f"\n✅ Generated {len(pptx_files)} PowerPoint presentations")

        total_size = sum(f.stat().st_size for f in pptx_files)
        print(f"   Total size: {total_size // 1024} KB")
    except Exception as e:
        print(f"\n❌ PowerPoint generation failed: {e}")
        import traceback
        traceback.print_exc()
        pptx_files = []

    print()

    # Step 3: Convert to PDF
    print("=" * 70)
    print("📑 Step 3/3: Converting to PDF")
    print("=" * 70)

    pdf_files = []

    # Import PDF generator
    sys.path.insert(0, str(Path(__file__).parent))
    from pdf_generator import convert_to_pdf

    # Convert Word documents
    for docx_file in docx_files:
        pdf_file = convert_to_pdf(docx_file)
        if pdf_file:
            pdf_files.append(pdf_file)

    # Convert PowerPoint presentations
    for pptx_file in pptx_files:
        pdf_file = convert_to_pdf(pptx_file)
        if pdf_file:
            pdf_files.append(pdf_file)

    if pdf_files:
        print(f"\n✅ Generated {len(pdf_files)} PDF files")
    else:
        print("\n⚠️  PDF conversion skipped (LibreOffice not installed)")
        print("You can manually convert documents using Microsoft Office or LibreOffice")

    print()

    # Summary
    print("=" * 70)
    print("✨ Generation Complete!")
    print("=" * 70)
    print()
    print("📁 Generated Files:")
    print()

    if docx_files:
        print(f"  📄 Word Documents ({len(docx_files)}):")
        for f in docx_files:
            size_kb = f.stat().st_size // 1024
            print(f"     - {f.name} ({size_kb} KB)")
        print()

    if pptx_files:
        print(f"  📊 PowerPoint Presentations ({len(pptx_files)}):")
        for f in pptx_files:
            size_kb = f.stat().st_size // 1024
            print(f"     - {f.name} ({size_kb} KB)")
        print()

    if pdf_files:
        print(f"  📑 PDF Files ({len(pdf_files)}):")
        for f in pdf_files:
            size_kb = f.stat().st_size // 1024
            print(f"     - {f.name} ({size_kb} KB)")
        print()

    print("💡 Next Steps:")
    print("  1. Review the generated implementation guides")
    print("  2. Share with engineering teams")
    print("  3. Use as reference during implementation")
    print("  4. Track progress against success metrics")
    print()
    print(f"All files are in: {output_dir}")
    print("=" * 70)

    # Print statistics
    print()
    print("📊 Generation Statistics:")
    print("=" * 70)
    print(f"  Roles documented: 8")
    print(f"  Word documents: {len(docx_files)}")
    print(f"  PowerPoint presentations: {len(pptx_files)}")
    print(f"  PDF files: {len(pdf_files)}")
    print(f"  Total documents: {len(docx_files) + len(pptx_files) + len(pdf_files)}")

    if docx_files:
        total_kb = sum(f.stat().st_size for f in docx_files) // 1024
        avg_kb = total_kb // len(docx_files)
        print(f"  Average Word doc size: {avg_kb} KB")
        print(f"  Total documentation size: {(total_kb + sum(f.stat().st_size for f in pptx_files + pdf_files)) // 1024} KB")

    print("=" * 70)


if __name__ == "__main__":
    main()
