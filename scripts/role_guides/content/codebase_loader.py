#!/usr/bin/env python3
"""
Codebase Loader - Loads relevant code files from the Piano Keys project
Extracts code snippets with line numbers for exponentially detailed documentation
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re


class CodebaseLoader:
    """Load and analyze code files from the Piano Keys project."""

    def __init__(self, project_root: Path):
        """
        Initialize codebase loader.

        Args:
            project_root: Path to the Piano Keys project root
        """
        self.project_root = project_root
        self.backend_root = project_root / "backend"
        self.frontend_root = project_root / "frontend"

    def load_file(self, file_path: str) -> Optional[str]:
        """
        Load a file from the codebase.

        Args:
            file_path: Relative path from project root (e.g., "/backend/app/api/deps.py")

        Returns:
            File content as string, or None if file doesn't exist
        """
        # Remove leading slash if present
        file_path = file_path.lstrip('/')

        full_path = self.project_root / file_path

        if not full_path.exists():
            print(f"⚠️  File not found: {full_path}")
            return None

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading file {full_path}: {e}")
            return None

    def load_file_with_line_numbers(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """
        Load a file with line numbers.

        Args:
            file_path: Relative path from project root
            start_line: Optional starting line number (1-indexed)
            end_line: Optional ending line number (inclusive)

        Returns:
            File content with line numbers, formatted for documentation
        """
        content = self.load_file(file_path)

        if content is None:
            return f"# File not found: {file_path}"

        lines = content.split('\n')

        # Apply line range if specified
        if start_line is not None:
            start_idx = max(0, start_line - 1)
        else:
            start_idx = 0

        if end_line is not None:
            end_idx = min(len(lines), end_line)
        else:
            end_idx = len(lines)

        # Format with line numbers
        formatted_lines = []
        for i in range(start_idx, end_idx):
            line_num = i + 1
            formatted_lines.append(f"{line_num:4d} | {lines[i]}")

        return '\n'.join(formatted_lines)

    def extract_function(self, file_path: str, function_name: str) -> Optional[str]:
        """
        Extract a specific function from a file.

        Args:
            file_path: Relative path from project root
            function_name: Name of the function to extract

        Returns:
            Function code with line numbers, or None if not found
        """
        content = self.load_file(file_path)

        if content is None:
            return None

        lines = content.split('\n')

        # Find function definition (supports Python, TypeScript, JavaScript)
        patterns = [
            rf'^def {re.escape(function_name)}\(',  # Python
            rf'^async def {re.escape(function_name)}\(',  # Python async
            rf'^function {re.escape(function_name)}\(',  # JavaScript
            rf'^const {re.escape(function_name)} = ',  # Arrow function
            rf'^export function {re.escape(function_name)}\(',  # Exported function
        ]

        start_line = None
        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.match(pattern, line.strip()):
                    start_line = i
                    break
            if start_line is not None:
                break

        if start_line is None:
            return None

        # Find end of function (simple indentation-based detection)
        end_line = start_line + 1
        base_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Empty lines don't break function
            if not line.strip():
                end_line = i + 1
                continue

            # Check indentation
            current_indent = len(line) - len(line.lstrip())

            # If we're back to base indentation or less, function is done
            if current_indent <= base_indent:
                break

            end_line = i + 1

        return self.load_file_with_line_numbers(file_path, start_line + 1, end_line)

    def get_file_structure(self, directory: str = "") -> List[Dict[str, any]]:
        """
        Get the file structure of a directory.

        Args:
            directory: Relative directory path (e.g., "backend/app/api")

        Returns:
            List of dictionaries with file information
        """
        dir_path = self.project_root / directory if directory else self.project_root

        if not dir_path.exists():
            return []

        files = []

        for item in dir_path.rglob('*'):
            if item.is_file():
                # Skip common non-code files
                if item.suffix in ['.pyc', '.pyo', '.so', '.dylib', '.o']:
                    continue
                if item.name in ['.DS_Store', '__pycache__']:
                    continue

                relative_path = item.relative_to(self.project_root)

                files.append({
                    'path': str(relative_path),
                    'name': item.name,
                    'extension': item.suffix,
                    'size': item.stat().st_size,
                    'type': self._classify_file_type(item)
                })

        return sorted(files, key=lambda x: x['path'])

    def _classify_file_type(self, file_path: Path) -> str:
        """Classify file type based on extension."""
        ext = file_path.suffix.lower()

        if ext in ['.py']:
            return 'Python'
        elif ext in ['.ts', '.tsx']:
            return 'TypeScript'
        elif ext in ['.js', '.jsx']:
            return 'JavaScript'
        elif ext in ['.md']:
            return 'Markdown'
        elif ext in ['.yml', '.yaml']:
            return 'YAML'
        elif ext in ['.json']:
            return 'JSON'
        elif ext in ['.sql']:
            return 'SQL'
        elif ext in ['.sh']:
            return 'Shell'
        elif ext in ['.css', '.scss']:
            return 'Stylesheet'
        else:
            return 'Other'

    def find_files_by_pattern(self, pattern: str, directory: str = "") -> List[str]:
        """
        Find files matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py" or "**/deps.py")
            directory: Directory to search in (relative to project root)

        Returns:
            List of file paths (relative to project root)
        """
        search_dir = self.project_root / directory if directory else self.project_root

        if not search_dir.exists():
            return []

        matches = []
        for file_path in search_dir.glob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.project_root)
                matches.append(str(relative_path))

        return sorted(matches)


if __name__ == "__main__":
    # Test the codebase loader
    project_root = Path(__file__).parent.parent.parent.parent
    loader = CodebaseLoader(project_root)

    # Test loading a critical file
    print("Testing CodebaseLoader...")
    print("=" * 70)

    # Load deps.py with line numbers
    print("\n1. Loading backend/app/api/deps.py (lines 30-48):")
    print("-" * 70)
    deps_code = loader.load_file_with_line_numbers("backend/app/api/deps.py", 30, 48)
    print(deps_code)

    # Find all Python files in backend
    print("\n2. Finding Python files in backend:")
    print("-" * 70)
    py_files = loader.find_files_by_pattern("**/*.py", "backend/app")
    print(f"Found {len(py_files)} Python files")
    for f in py_files[:5]:
        print(f"  - {f}")

    print("\n✅ CodebaseLoader test complete!")
