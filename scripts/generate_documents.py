#!/usr/bin/env python3
"""
Document Generation Script for Piano Keys Production Readiness Plan
Generates Word, PowerPoint, and PDF documents from the markdown plan.
"""

import sys
from pathlib import Path
from datetime import date

# Import custom generators
from docx_generator import create_word_document
from pptx_generator import create_powerpoint_presentation
from pdf_generator import convert_to_pdf


def main():
    """Generate all documents from the production readiness plan."""
    print("="*70)
    print("📄 Piano Keys - Document Generation")
    print("="*70)
    print()

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    plan_file = project_root / ".claude/plans/production-readiness-plan-source.md"
    output_dir = project_root / "output"

    # Verify source file exists
    if not plan_file.exists():
        print(f"❌ Source file not found: {plan_file}")
        print("Looking for production readiness plan markdown file...")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    print()

    # Generate Word document
    print("📄 Step 1/4: Generating Word document...")
    print("-" * 70)
    try:
        docx_path = create_word_document(plan_file, output_dir)
        print(f"✅ Word document created: {docx_path.name}")
    except Exception as e:
        print(f"❌ Word generation failed: {e}")
        docx_path = None

    print()

    # Generate PowerPoint presentation
    print("📊 Step 2/4: Generating PowerPoint presentation...")
    print("-" * 70)
    try:
        pptx_path = create_powerpoint_presentation(plan_file, output_dir)
        print(f"✅ PowerPoint created: {pptx_path.name}")
    except Exception as e:
        print(f"❌ PowerPoint generation failed: {e}")
        pptx_path = None

    print()

    # Convert to PDF
    print("📑 Step 3/4: Converting to PDF...")
    print("-" * 70)

    pdf_docs = []
    if docx_path and docx_path.exists():
        pdf_plan = convert_to_pdf(docx_path)
        if pdf_plan:
            pdf_docs.append(pdf_plan)

    if pptx_path and pptx_path.exists():
        pdf_presentation = convert_to_pdf(pptx_path)
        if pdf_presentation:
            pdf_docs.append(pdf_presentation)

    print()

    # Summary
    print("="*70)
    print("✨ Document Generation Complete!")
    print("="*70)
    print()
    print("📁 Generated Files:")
    print()

    if docx_path and docx_path.exists():
        print(f"  📄 Word:        {docx_path}")

    if pptx_path and pptx_path.exists():
        print(f"  📊 PowerPoint:  {pptx_path}")

    for pdf in pdf_docs:
        print(f"  📑 PDF:         {pdf}")

    print()
    print("💡 Next Steps:")
    print("  1. Open the Word document for detailed planning")
    print("  2. Use the PowerPoint for presentations")
    print("  3. Share PDF versions with stakeholders")
    print()
    print(f"All files are in: {output_dir}")
    print("="*70)


if __name__ == "__main__":
    main()
