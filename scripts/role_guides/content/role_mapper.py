#!/usr/bin/env python3
"""
Role Mapper - Maps production readiness plan tasks to specific engineering roles
Extracts role-specific tasks, phases, and deliverables
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
import re


class RoleMapper:
    """Map production readiness plan tasks to engineering roles."""

    def __init__(self, plan_file: Path, role_configs_dir: Path):
        """
        Initialize role mapper.

        Args:
            plan_file: Path to production readiness plan markdown
            role_configs_dir: Directory containing role YAML configurations
        """
        self.plan_file = plan_file
        self.role_configs_dir = role_configs_dir
        self.plan_content = self._load_plan()
        self.roles = self._load_role_configs()

    def _load_plan(self) -> str:
        """Load the production readiness plan."""
        if not self.plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {self.plan_file}")

        with open(self.plan_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_role_configs(self) -> Dict[str, Dict]:
        """Load all role configuration files."""
        roles = {}

        for config_file in self.role_configs_dir.glob('*.yaml'):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                role_name = config.get('role_name')
                if role_name:
                    roles[role_name] = config

        return roles

    def get_role_tasks(self, role_name: str) -> List[Dict[str, any]]:
        """
        Get all tasks for a specific role.

        Args:
            role_name: Name of the role (e.g., "Backend Engineer")

        Returns:
            List of tasks with details (file, lines, priority, description)
        """
        if role_name not in self.roles:
            return []

        config = self.roles[role_name]
        tasks = []

        # Extract tasks from critical files
        for file_info in config.get('critical_files', []):
            task = {
                'file': file_info.get('path'),
                'lines': file_info.get('lines') or file_info.get('line'),
                'priority': file_info.get('priority'),
                'task': file_info.get('task'),
                'vulnerability': file_info.get('vulnerability')
            }
            tasks.append(task)

        return tasks

    def get_role_phases(self, role_name: str) -> List[Dict[str, any]]:
        """
        Get all phases for a specific role.

        Args:
            role_name: Name of the role

        Returns:
            List of phases with focus areas
        """
        if role_name not in self.roles:
            return []

        config = self.roles[role_name]
        return config.get('primary_phases', [])

    def get_role_tech_stack(self, role_name: str) -> List[str]:
        """Get technology stack for a role."""
        if role_name not in self.roles:
            return []

        config = self.roles[role_name]
        tech_stack = config.get('technology_stack', [])

        # Handle nested tech stack (like QA engineer with backend/frontend/e2e)
        if isinstance(tech_stack, dict):
            all_tech = []
            for category, techs in tech_stack.items():
                all_tech.extend(techs)
            return all_tech

        return tech_stack

    def get_role_dependencies(self, role_name: str) -> Dict[str, List]:
        """Get role dependencies (blocks and blocked_by)."""
        if role_name not in self.roles:
            return {'blocks': [], 'blocked_by': []}

        config = self.roles[role_name]
        return config.get('dependencies', {'blocks': [], 'blocked_by': []})

    def get_role_success_metrics(self, role_name: str) -> List[Dict[str, str]]:
        """Get success metrics for a role."""
        if role_name not in self.roles:
            return []

        config = self.roles[role_name]
        return config.get('success_metrics', [])

    def get_role_time_estimates(self, role_name: str) -> Dict[str, str]:
        """Get time estimates for a role."""
        if role_name not in self.roles:
            return {}

        config = self.roles[role_name]
        return config.get('time_estimates', {})

    def extract_phase_content(self, phase_num: int) -> str:
        """
        Extract content for a specific phase from the plan.

        Args:
            phase_num: Phase number (1-6)

        Returns:
            Markdown content for that phase
        """
        # Find the phase section in the plan
        pattern = rf'### Phase {phase_num}:.*?(?=###|$)'
        match = re.search(pattern, self.plan_content, re.DOTALL)

        if match:
            return match.group(0)

        return f"Phase {phase_num} content not found"

    def extract_critical_files_section(self) -> str:
        """Extract the Critical Files to Modify section from the plan."""
        pattern = r'## Critical Files to Modify.*?(?=##|$)'
        match = re.search(pattern, self.plan_content, re.DOTALL)

        if match:
            return match.group(0)

        return "Critical Files section not found"

    def extract_success_metrics_section(self) -> str:
        """Extract the Success Metrics section from the plan."""
        pattern = r'## Success Metrics.*?(?=##|$)'
        match = re.search(pattern, self.plan_content, re.DOTALL)

        if match:
            return match.group(0)

        return "Success Metrics section not found"

    def get_all_roles(self) -> List[str]:
        """Get list of all configured roles."""
        return list(self.roles.keys())

    def generate_role_summary(self, role_name: str) -> Dict[str, any]:
        """
        Generate comprehensive summary for a role.

        Args:
            role_name: Name of the role

        Returns:
            Dictionary with all role information
        """
        if role_name not in self.roles:
            return {}

        config = self.roles[role_name]

        summary = {
            'role_name': role_name,
            'description': config.get('role_description'),
            'phases': self.get_role_phases(role_name),
            'tasks': self.get_role_tasks(role_name),
            'tech_stack': self.get_role_tech_stack(role_name),
            'dependencies': self.get_role_dependencies(role_name),
            'success_metrics': self.get_role_success_metrics(role_name),
            'time_estimates': self.get_role_time_estimates(role_name),
            'document_sections': config.get('document_sections', [])
        }

        return summary

    def get_file_to_role_mapping(self) -> Dict[str, List[str]]:
        """
        Create a mapping of files to roles that need to work on them.

        Returns:
            Dictionary mapping file paths to list of role names
        """
        file_mapping = {}

        for role_name, config in self.roles.items():
            for file_info in config.get('critical_files', []):
                file_path = file_info.get('path')
                if file_path:
                    if file_path not in file_mapping:
                        file_mapping[file_path] = []
                    file_mapping[file_path].append(role_name)

        return file_mapping


if __name__ == "__main__":
    # Test the role mapper
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent.parent
    plan_file = project_root / ".claude/plans/production-readiness-plan-source.md"
    configs_dir = Path(__file__).parent.parent / "templates/role_configs"

    mapper = RoleMapper(plan_file, configs_dir)

    print("Testing RoleMapper...")
    print("=" * 70)

    # List all roles
    print("\n1. All configured roles:")
    print("-" * 70)
    for role in mapper.get_all_roles():
        print(f"  - {role}")

    # Get Backend Engineer summary
    print("\n2. Backend Engineer Summary:")
    print("-" * 70)
    summary = mapper.generate_role_summary("Backend Engineer")
    print(f"Description: {summary['description']}")
    print(f"\nPhases ({len(summary['phases'])}):")
    for phase in summary['phases']:
        print(f"  - Phase {phase['phase']}: {phase['name']} (Weeks {phase['weeks']})")

    print(f"\nCritical Tasks ({len(summary['tasks'])}):")
    for task in summary['tasks'][:3]:
        print(f"  - [{task['priority']}] {task['file']}: {task['task']}")

    # File to role mapping
    print("\n3. File to Role Mapping (top 5):")
    print("-" * 70)
    file_mapping = mapper.get_file_to_role_mapping()
    for file_path, roles in list(file_mapping.items())[:5]:
        print(f"  {file_path}")
        for role in roles:
            print(f"    → {role}")

    print("\n✅ RoleMapper test complete!")
