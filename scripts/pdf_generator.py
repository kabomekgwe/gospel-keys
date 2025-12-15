#!/usr/bin/env python3
"""
PDF Converter for Office Documents
Converts DOCX and PPTX files to PDF format.
"""

from pathlib import Path
import subprocess
import sys


def convert_to_pdf(source_file: Path) -> Path:
    """
    Convert DOCX or PPTX file to PDF.

    Args:
        source_file: Path to the source document (.docx or .pptx)

    Returns:
        Path to the generated PDF file

    Note:
        This uses LibreOffice headless mode for conversion.
        Make sure LibreOffice is installed: brew install --cask libreoffice
    """
    output_path = source_file.with_suffix('.pdf')

    print(f"Converting {source_file.name} to PDF...")

    # Try LibreOffice headless conversion
    try:
        # Check if soffice (LibreOffice) is available
        result = subprocess.run(
            ['which', 'soffice'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Use LibreOffice for conversion
            subprocess.run(
                [
                    'soffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', str(source_file.parent),
                    str(source_file)
                ],
                check=True,
                capture_output=True
            )
            print(f"✅ PDF generated: {output_path}")
            return output_path
        else:
            print("⚠️  LibreOffice not found. PDF conversion skipped.")
            print("Install with: brew install --cask libreoffice")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ PDF conversion failed: {e}")
        print("You can manually convert the documents to PDF using Microsoft Office or LibreOffice.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during PDF conversion: {e}")
        return None


def install_libreoffice_instructions():
    """Print instructions for installing LibreOffice."""
    print("\n" + "="*70)
    print("📄 PDF Conversion Requires LibreOffice")
    print("="*70)
    print("\nTo enable automatic PDF conversion, install LibreOffice:")
    print("\n  macOS:   brew install --cask libreoffice")
    print("  Linux:   sudo apt-get install libreoffice")
    print("  Windows: Download from https://www.libreoffice.org/download")
    print("\nAlternatively, you can:")
    print("  1. Open the generated .docx and .pptx files")
    print("  2. Use 'File > Export as PDF' in Microsoft Office")
    print("  3. Or use 'File > Save As PDF' in LibreOffice")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Test if LibreOffice is available
    result = subprocess.run(['which', 'soffice'], capture_output=True)
    if result.returncode != 0:
        install_libreoffice_instructions()
    else:
        print("✅ LibreOffice is installed and ready for PDF conversion")
