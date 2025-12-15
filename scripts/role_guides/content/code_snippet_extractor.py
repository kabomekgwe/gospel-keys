#!/usr/bin/env python3
"""
Code Snippet Extractor - Extracts exponentially detailed code snippets for roles
Combines codebase loading with role mapping to create comprehensive code examples
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from codebase_loader import CodebaseLoader
from role_mapper import RoleMapper


class CodeSnippetExtractor:
    """Extract detailed code snippets for role-specific documentation."""

    def __init__(
        self,
        project_root: Path,
        plan_file: Path,
        role_configs_dir: Path
    ):
        """
        Initialize code snippet extractor.

        Args:
            project_root: Path to Piano Keys project root
            plan_file: Path to production readiness plan
            role_configs_dir: Path to role configuration files
        """
        self.loader = CodebaseLoader(project_root)
        self.mapper = RoleMapper(plan_file, role_configs_dir)

    def extract_task_code(
        self,
        task: Dict[str, any],
        context_lines: int = 10
    ) -> Dict[str, any]:
        """
        Extract code for a specific task with full context.

        Args:
            task: Task dictionary from role mapper
            context_lines: Number of context lines before/after target lines

        Returns:
            Dictionary with code snippets, analysis, and metadata
        """
        file_path = task.get('file')
        lines_spec = task.get('lines')
        priority = task.get('priority')
        task_description = task.get('task')

        result = {
            'file': file_path,
            'task': task_description,
            'priority': priority,
            'exists': False,
            'current_code': None,
            'full_file': None,
            'analysis': None
        }

        # Check if file exists
        content = self.loader.load_file(file_path)

        if content is None:
            result['analysis'] = f"NEW FILE: {file_path} needs to be created"
            return result

        result['exists'] = True

        # Parse line specification
        if lines_spec:
            start_line, end_line = self._parse_line_spec(lines_spec)

            # Add context
            context_start = max(1, start_line - context_lines)
            context_end = end_line + context_lines

            result['current_code'] = self.loader.load_file_with_line_numbers(
                file_path,
                context_start,
                context_end
            )

            result['target_lines'] = f"{start_line}-{end_line}"
        else:
            # No specific lines, show relevant section or full file
            result['current_code'] = self.loader.load_file_with_line_numbers(file_path)
            result['target_lines'] = "entire file"

        # Add full file content for reference
        result['full_file'] = content

        # Generate analysis
        result['analysis'] = self._analyze_code(content, task)

        return result

    def _parse_line_spec(self, lines_spec: str) -> Tuple[int, int]:
        """
        Parse line specification like "30-48" or "17".

        Args:
            lines_spec: Line specification string

        Returns:
            Tuple of (start_line, end_line)
        """
        if isinstance(lines_spec, int):
            return (lines_spec, lines_spec)

        lines_spec = str(lines_spec)

        if '-' in lines_spec:
            parts = lines_spec.split('-')
            return (int(parts[0]), int(parts[1]))
        else:
            line_num = int(lines_spec)
            return (line_num, line_num)

    def _analyze_code(self, content: str, task: Dict[str, any]) -> str:
        """
        Analyze code and provide insights.

        Args:
            content: File content
            task: Task information

        Returns:
            Analysis text
        """
        lines = content.split('\n')
        analysis_parts = []

        # File statistics
        analysis_parts.append(f"File statistics:")
        analysis_parts.append(f"  - Total lines: {len(lines)}")
        analysis_parts.append(f"  - Non-empty lines: {sum(1 for line in lines if line.strip())}")

        # Check for common patterns
        if 'def ' in content or 'async def ' in content:
            function_count = len([line for line in lines if line.strip().startswith(('def ', 'async def '))])
            analysis_parts.append(f"  - Functions: {function_count}")

        if 'class ' in content:
            class_count = len([line for line in lines if line.strip().startswith('class ')])
            analysis_parts.append(f"  - Classes: {class_count}")

        # Task-specific analysis
        if task.get('vulnerability'):
            analysis_parts.append(f"\n⚠️  SECURITY VULNERABILITY: {task['vulnerability']}")

        # Check for common issues
        if 'console.log' in content:
            console_count = content.count('console.log')
            analysis_parts.append(f"\n⚠️  Console.log statements found: {console_count}")

        if 'SECRET_KEY' in content and '=' in content:
            analysis_parts.append("\n⚠️  Potential hardcoded secret detected")

        if 'TODO' in content or 'FIXME' in content:
            todo_count = content.count('TODO') + content.count('FIXME')
            analysis_parts.append(f"\n📝 TODO/FIXME comments: {todo_count}")

        return '\n'.join(analysis_parts)

    def extract_all_role_code(self, role_name: str) -> List[Dict[str, any]]:
        """
        Extract all code snippets for a role.

        Args:
            role_name: Name of the role

        Returns:
            List of code snippets with full details
        """
        tasks = self.mapper.get_role_tasks(role_name)
        snippets = []

        for task in tasks:
            snippet = self.extract_task_code(task)
            snippets.append(snippet)

        return snippets

    def generate_before_after_example(
        self,
        file_path: str,
        lines_spec: str,
        proposed_fix: str
    ) -> Dict[str, str]:
        """
        Generate before/after code comparison.

        Args:
            file_path: Path to file
            lines_spec: Line specification
            proposed_fix: Proposed code fix

        Returns:
            Dictionary with before and after code
        """
        start_line, end_line = self._parse_line_spec(lines_spec)

        before_code = self.loader.load_file_with_line_numbers(
            file_path,
            start_line,
            end_line
        )

        return {
            'before': before_code,
            'after': proposed_fix,
            'file': file_path,
            'lines': f"{start_line}-{end_line}"
        }

    def extract_related_files(self, file_path: str) -> List[str]:
        """
        Find related files (imports, similar names, same directory).

        Args:
            file_path: Path to primary file

        Returns:
            List of related file paths
        """
        related = []

        # Get directory
        file_obj = Path(file_path)
        directory = str(file_obj.parent)

        # Find files in same directory
        same_dir_files = self.loader.find_files_by_pattern("*", directory)
        related.extend(same_dir_files[:10])  # Limit to 10

        # TODO: Could analyze imports to find related files

        return related

    def generate_testing_code_example(
        self,
        file_path: str,
        function_name: str
    ) -> Optional[str]:
        """
        Generate example test code for a function.

        Args:
            file_path: Path to file containing function
            function_name: Name of function to test

        Returns:
            Example test code or None
        """
        # Extract the function
        function_code = self.loader.extract_function(file_path, function_name)

        if function_code is None:
            return None

        # Generate test template
        if '.py' in file_path:
            # Python test
            test_code = f'''
# Test for {function_name} in {file_path}

import pytest
from {file_path.replace('/', '.').replace('.py', '')} import {function_name}


def test_{function_name}_success():
    """Test {function_name} with valid input."""
    # Arrange
    # TODO: Set up test data

    # Act
    result = {function_name}(...)

    # Assert
    assert result is not None
    # TODO: Add specific assertions


def test_{function_name}_error_handling():
    """Test {function_name} error handling."""
    # Arrange
    # TODO: Set up invalid test data

    # Act & Assert
    with pytest.raises(Exception):
        {function_name}(...)
'''
        elif '.ts' in file_path or '.tsx' in file_path:
            # TypeScript test
            test_code = f'''
// Test for {function_name} in {file_path}

import {{ describe, it, expect }} from 'vitest';
import {{ {function_name} }} from '{file_path.replace('.tsx', '').replace('.ts', '')}';


describe('{function_name}', () => {{
  it('should work with valid input', () => {{
    // Arrange
    // TODO: Set up test data

    // Act
    const result = {function_name}(...);

    // Assert
    expect(result).toBeDefined();
    // TODO: Add specific assertions
  }});

  it('should handle errors', () => {{
    // Arrange
    // TODO: Set up invalid test data

    // Act & Assert
    expect(() => {function_name}(...)).toThrow();
  }});
}});
'''
        else:
            return None

        return test_code


if __name__ == "__main__":
    # Test the code snippet extractor
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent.parent
    plan_file = project_root / ".claude/plans/production-readiness-plan-source.md"
    configs_dir = Path(__file__).parent.parent / "templates/role_configs"

    extractor = CodeSnippetExtractor(project_root, plan_file, configs_dir)

    print("Testing CodeSnippetExtractor...")
    print("=" * 70)

    # Extract Backend Engineer code
    print("\n1. Extracting Backend Engineer code snippets:")
    print("-" * 70)

    snippets = extractor.extract_all_role_code("Backend Engineer")

    print(f"Found {len(snippets)} code snippets for Backend Engineer\n")

    # Show first snippet (critical auth bypass)
    if snippets:
        snippet = snippets[0]
        print(f"Task: {snippet['task']}")
        print(f"File: {snippet['file']}")
        print(f"Priority: {snippet['priority']}")
        print(f"Exists: {snippet['exists']}")
        print(f"\nAnalysis:")
        print(snippet['analysis'])

        if snippet['current_code']:
            print(f"\nCurrent Code (with context):")
            print(snippet['current_code'][:500] + "...")  # Show first 500 chars

    print("\n✅ CodeSnippetExtractor test complete!")
