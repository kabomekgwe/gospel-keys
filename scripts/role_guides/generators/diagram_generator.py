#!/usr/bin/env python3
"""
Role-Specific Technical Diagram Generator
Generates architecture diagrams, flowcharts, and visualizations for each engineering role
"""

from pathlib import Path
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


class DiagramGenerator:
    """Generate role-specific technical diagrams."""

    def __init__(self, output_dir: Path):
        """Initialize diagram generator.

        Args:
            output_dir: Directory to save generated diagrams
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Color scheme
        self.colors = {
            'primary': '#1F4788',      # Blue
            'secondary': '#00A9E0',    # Cyan
            'success': '#28A745',      # Green
            'warning': '#FFC107',      # Yellow
            'danger': '#DC3545',       # Red
            'gray': '#6C757D',         # Gray
            'light': '#F8F9FA',        # Light gray
            'dark': '#343A40'          # Dark gray
        }

    def generate_backend_diagrams(self) -> List[Path]:
        """Generate Backend Engineer diagrams."""
        diagrams = []

        # 1. API Architecture
        diagrams.append(self._create_api_architecture())

        # 2. Authentication Flow
        diagrams.append(self._create_auth_flow())

        # 3. Database Schema
        diagrams.append(self._create_database_schema())

        # 4. Module Dependencies
        diagrams.append(self._create_module_dependencies())

        return diagrams

    def generate_frontend_diagrams(self) -> List[Path]:
        """Generate Frontend Engineer diagrams."""
        diagrams = []

        # 1. Component Hierarchy
        diagrams.append(self._create_component_hierarchy())

        # 2. State Management Flow
        diagrams.append(self._create_state_management())

        # 3. Routing Structure
        diagrams.append(self._create_routing_structure())

        # 4. Data Flow
        diagrams.append(self._create_frontend_data_flow())

        return diagrams

    def generate_devops_diagrams(self) -> List[Path]:
        """Generate DevOps Engineer diagrams."""
        diagrams = []

        # 1. CI/CD Pipeline
        diagrams.append(self._create_cicd_pipeline())

        # 2. Infrastructure Architecture
        diagrams.append(self._create_infrastructure())

        # 3. Deployment Flow
        diagrams.append(self._create_deployment_flow())

        # 4. Monitoring Stack
        diagrams.append(self._create_monitoring_stack())

        return diagrams

    def generate_security_diagrams(self) -> List[Path]:
        """Generate Security Engineer diagrams."""
        diagrams = []

        # 1. Security Architecture
        diagrams.append(self._create_security_architecture())

        # 2. Authentication/Authorization Flow
        diagrams.append(self._create_auth_authorization_flow())

        # 3. Threat Model
        diagrams.append(self._create_threat_model())

        # 4. Security Layers
        diagrams.append(self._create_security_layers())

        return diagrams

    def generate_qa_diagrams(self) -> List[Path]:
        """Generate QA Engineer diagrams."""
        diagrams = []

        # 1. Test Pyramid
        diagrams.append(self._create_test_pyramid())

        # 2. Test Coverage Map
        diagrams.append(self._create_test_coverage())

        # 3. Testing Workflow
        diagrams.append(self._create_testing_workflow())

        # 4. Test Types Distribution
        diagrams.append(self._create_test_distribution())

        return diagrams

    def generate_database_diagrams(self) -> List[Path]:
        """Generate Database Admin diagrams."""
        diagrams = []

        # 1. Database Schema
        diagrams.append(self._create_db_schema_detailed())

        # 2. Migration Flow
        diagrams.append(self._create_migration_flow())

        # 3. Caching Architecture
        diagrams.append(self._create_caching_architecture())

        # 4. Data Flow
        diagrams.append(self._create_data_flow())

        return diagrams

    def generate_ux_diagrams(self) -> List[Path]:
        """Generate UX Designer diagrams."""
        diagrams = []

        # 1. User Journey Map
        diagrams.append(self._create_user_journey())

        # 2. Information Architecture
        diagrams.append(self._create_information_architecture())

        # 3. Component Library Structure
        diagrams.append(self._create_component_library())

        # 4. Accessibility Compliance
        diagrams.append(self._create_accessibility_compliance())

        return diagrams

    def generate_technical_writer_diagrams(self) -> List[Path]:
        """Generate Technical Writer diagrams."""
        diagrams = []

        # 1. Documentation Structure
        diagrams.append(self._create_docs_structure())

        # 2. Information Hierarchy
        diagrams.append(self._create_info_hierarchy())

        # 3. Content Types
        diagrams.append(self._create_content_types())

        # 4. Documentation Workflow
        diagrams.append(self._create_docs_workflow())

        return diagrams

    # ==================== Backend Engineer Diagrams ====================

    def _create_api_architecture(self) -> Path:
        """Create API architecture diagram."""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'Piano Keys - API Architecture',
                fontsize=20, fontweight='bold', ha='center',
                color=self.colors['primary'])

        # Client Layer
        client = FancyBboxPatch((0.5, 7.5), 2, 1, boxstyle="round,pad=0.1",
                                edgecolor=self.colors['primary'],
                                facecolor=self.colors['light'], linewidth=2)
        ax.add_patch(client)
        ax.text(1.5, 8, 'React Frontend\n(Port 3000)', ha='center', va='center',
                fontsize=11, fontweight='bold')

        # API Gateway
        gateway = FancyBboxPatch((3.5, 7.5), 2, 1, boxstyle="round,pad=0.1",
                                 edgecolor=self.colors['secondary'],
                                 facecolor=self.colors['light'], linewidth=2)
        ax.add_patch(gateway)
        ax.text(4.5, 8, 'FastAPI\n(Port 8000)', ha='center', va='center',
                fontsize=11, fontweight='bold')

        # Authentication
        auth = FancyBboxPatch((6.5, 7.5), 2, 1, boxstyle="round,pad=0.1",
                              edgecolor=self.colors['warning'],
                              facecolor=self.colors['light'], linewidth=2)
        ax.add_patch(auth)
        ax.text(7.5, 8, 'JWT Auth\n(deps.py)', ha='center', va='center',
                fontsize=11, fontweight='bold')

        # API Routes Layer
        routes_y = 5.5
        routes = [
            ('Users\n/api/v1/users', 1.5),
            ('Lessons\n/api/v1/lessons', 3.5),
            ('Practice\n/api/v1/practice', 5.5),
            ('Analysis\n/api/v1/analysis', 7.5)
        ]

        for route_name, x_pos in routes:
            route_box = FancyBboxPatch((x_pos - 0.7, routes_y), 1.4, 0.8,
                                       boxstyle="round,pad=0.05",
                                       edgecolor=self.colors['primary'],
                                       facecolor='#E3F2FD', linewidth=1.5)
            ax.add_patch(route_box)
            ax.text(x_pos, routes_y + 0.4, route_name, ha='center', va='center',
                    fontsize=9)

        # Services Layer
        services_y = 3.5
        services = [
            ('User Service', 1.5),
            ('Lesson Service', 3.5),
            ('Practice Service', 5.5),
            ('Analysis Service', 7.5)
        ]

        for service_name, x_pos in services:
            service_box = FancyBboxPatch((x_pos - 0.7, services_y), 1.4, 0.8,
                                         boxstyle="round,pad=0.05",
                                         edgecolor=self.colors['success'],
                                         facecolor='#E8F5E9', linewidth=1.5)
            ax.add_patch(service_box)
            ax.text(x_pos, services_y + 0.4, service_name, ha='center', va='center',
                    fontsize=9)

        # Data Layer
        data_y = 1.5

        # PostgreSQL
        postgres = FancyBboxPatch((1, data_y), 2, 0.8, boxstyle="round,pad=0.05",
                                  edgecolor=self.colors['primary'],
                                  facecolor='#BBDEFB', linewidth=2)
        ax.add_patch(postgres)
        ax.text(2, data_y + 0.4, 'PostgreSQL\n(Primary DB)', ha='center', va='center',
                fontsize=10, fontweight='bold')

        # Redis
        redis = FancyBboxPatch((4, data_y), 2, 0.8, boxstyle="round,pad=0.05",
                               edgecolor=self.colors['danger'],
                               facecolor='#FFCDD2', linewidth=2)
        ax.add_patch(redis)
        ax.text(5, data_y + 0.4, 'Redis\n(Cache)', ha='center', va='center',
                fontsize=10, fontweight='bold')

        # MinIO
        minio = FancyBboxPatch((7, data_y), 2, 0.8, boxstyle="round,pad=0.05",
                               edgecolor=self.colors['warning'],
                               facecolor='#FFF9C4', linewidth=2)
        ax.add_patch(minio)
        ax.text(8, data_y + 0.4, 'MinIO\n(S3 Storage)', ha='center', va='center',
                fontsize=10, fontweight='bold')

        # Arrows
        # Client -> Gateway
        ax.annotate('', xy=(3.5, 8), xytext=(2.5, 8),
                    arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['primary']))

        # Gateway -> Auth
        ax.annotate('', xy=(6.5, 8), xytext=(5.5, 8),
                    arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['warning']))

        # Gateway -> Routes
        for _, x_pos in routes:
            ax.annotate('', xy=(x_pos, routes_y + 0.8), xytext=(4.5, 7.5),
                        arrowprops=dict(arrowstyle='->', lw=1.5,
                                        color=self.colors['gray'], alpha=0.6))

        # Routes -> Services
        for i, (_, x_pos) in enumerate(routes):
            ax.annotate('', xy=(x_pos, services_y + 0.8), xytext=(x_pos, routes_y),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color=self.colors['primary']))

        # Services -> Data
        for i, (_, x_pos) in enumerate(services):
            if i < 2:  # First two to PostgreSQL
                ax.annotate('', xy=(2, data_y + 0.8), xytext=(x_pos, services_y),
                            arrowprops=dict(arrowstyle='->', lw=1,
                                            color=self.colors['gray'], alpha=0.5))
            if i == 2:  # Third to Redis
                ax.annotate('', xy=(5, data_y + 0.8), xytext=(x_pos, services_y),
                            arrowprops=dict(arrowstyle='->', lw=1,
                                            color=self.colors['gray'], alpha=0.5))
            if i == 3:  # Fourth to MinIO
                ax.annotate('', xy=(8, data_y + 0.8), xytext=(x_pos, services_y),
                            arrowprops=dict(arrowstyle='->', lw=1,
                                            color=self.colors['gray'], alpha=0.5))

        # Legend
        ax.text(0.5, 0.5, 'Layers:', fontsize=10, fontweight='bold')
        ax.text(0.5, 0.2, '• Client Layer (React)\n• API Gateway (FastAPI)\n• Routes\n• Services\n• Data (PostgreSQL, Redis, MinIO)',
                fontsize=8, verticalalignment='top')

        plt.tight_layout()
        output_path = self.output_dir / 'backend_api_architecture.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    def _create_auth_flow(self) -> Path:
        """Create authentication flow diagram."""
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'Authentication Flow - Piano Keys',
                fontsize=20, fontweight='bold', ha='center',
                color=self.colors['primary'])

        # Flow steps
        steps = [
            (8.5, 'User enters credentials'),
            (7.5, 'POST /api/v1/auth/login'),
            (6.5, 'Validate credentials'),
            (5.5, 'Generate JWT token'),
            (4.5, 'Return token to client'),
            (3.5, 'Client stores token'),
            (2.5, 'Attach token to requests'),
            (1.5, 'Verify JWT in deps.py'),
        ]

        for y, text in steps:
            box = FancyBboxPatch((2, y - 0.3), 6, 0.6, boxstyle="round,pad=0.05",
                                 edgecolor=self.colors['primary'],
                                 facecolor=self.colors['light'], linewidth=2)
            ax.add_patch(box)
            ax.text(5, y, text, ha='center', va='center', fontsize=11)

            # Arrow to next step
            if y > 1.5:
                ax.annotate('', xy=(5, y - 0.4), xytext=(5, y - 0.9),
                            arrowprops=dict(arrowstyle='->', lw=2,
                                            color=self.colors['primary']))

        # Security note
        security_box = FancyBboxPatch((1, 0.2), 8, 0.8, boxstyle="round,pad=0.1",
                                      edgecolor=self.colors['danger'],
                                      facecolor='#FFEBEE', linewidth=2)
        ax.add_patch(security_box)
        ax.text(5, 0.6, '⚠️  CRITICAL: Fix authentication bypass in deps.py (lines 30-48)',
                ha='center', va='center', fontsize=10, fontweight='bold',
                color=self.colors['danger'])

        plt.tight_layout()
        output_path = self.output_dir / 'backend_auth_flow.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    def _create_database_schema(self) -> Path:
        """Create database schema diagram."""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'Piano Keys - Database Schema',
                fontsize=20, fontweight='bold', ha='center',
                color=self.colors['primary'])

        # Tables
        tables = [
            {
                'name': 'users',
                'pos': (1, 7),
                'fields': ['id (PK)', 'email', 'password_hash', 'is_superuser', 'created_at']
            },
            {
                'name': 'lessons',
                'pos': (4, 7),
                'fields': ['id (PK)', 'user_id (FK)', 'title', 'difficulty', 'created_at']
            },
            {
                'name': 'practice_sessions',
                'pos': (7, 7),
                'fields': ['id (PK)', 'user_id (FK)', 'lesson_id (FK)', 'score', 'duration']
            },
            {
                'name': 'midi_files',
                'pos': (1, 4),
                'fields': ['id (PK)', 'lesson_id (FK)', 's3_key', 'file_size', 'uploaded_at']
            },
            {
                'name': 'analysis_results',
                'pos': (4, 4),
                'fields': ['id (PK)', 'session_id (FK)', 'accuracy', 'timing_errors', 'analysis']
            },
            {
                'name': 'user_progress',
                'pos': (7, 4),
                'fields': ['id (PK)', 'user_id (FK)', 'lesson_id (FK)', 'completed', 'last_practice']
            }
        ]

        for table in tables:
            x, y = table['pos']
            height = len(table['fields']) * 0.25 + 0.4

            # Table header
            header = FancyBboxPatch((x - 0.9, y - 0.2), 1.8, 0.4,
                                    boxstyle="round,pad=0.05",
                                    edgecolor=self.colors['primary'],
                                    facecolor=self.colors['primary'], linewidth=2)
            ax.add_patch(header)
            ax.text(x, y, table['name'], ha='center', va='center',
                    fontsize=10, fontweight='bold', color='white')

            # Table body
            body = FancyBboxPatch((x - 0.9, y - height), 1.8, height - 0.4,
                                  edgecolor=self.colors['primary'],
                                  facecolor=self.colors['light'], linewidth=2)
            ax.add_patch(body)

            # Fields
            for i, field in enumerate(table['fields']):
                field_y = y - 0.5 - (i * 0.25)
                ax.text(x, field_y, field, ha='center', va='center', fontsize=8)

        # Relationships
        relationships = [
            ((1, 7), (4, 7.2)),      # users -> lessons
            ((1, 7), (7, 7.2)),      # users -> practice_sessions
            ((4, 7 - 1.4), (7, 7)),  # lessons -> practice_sessions
            ((4, 7 - 1.4), (1, 4.5)),# lessons -> midi_files
            ((7, 7 - 1.4), (4, 4.5)),# practice_sessions -> analysis_results
            ((1, 7 - 1.4), (7, 4.2)),# users -> user_progress
        ]

        for (x1, y1), (x2, y2) in relationships:
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='-', lw=1.5,
                                        color=self.colors['gray'],
                                        connectionstyle="arc3,rad=0.3"))

        # Migration note
        migration_box = FancyBboxPatch((1, 0.5), 8, 0.8, boxstyle="round,pad=0.1",
                                       edgecolor=self.colors['warning'],
                                       facecolor='#FFF9C4', linewidth=2)
        ax.add_patch(migration_box)
        ax.text(5, 0.9, '📦 Migration: SQLite → PostgreSQL (Phase 2)',
                ha='center', va='center', fontsize=11, fontweight='bold')

        plt.tight_layout()
        output_path = self.output_dir / 'backend_database_schema.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    def _create_module_dependencies(self) -> Path:
        """Create module dependencies diagram."""
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'Backend Module Dependencies',
                fontsize=20, fontweight='bold', ha='center',
                color=self.colors['primary'])

        # Modules
        modules = [
            ('main.py', 5, 8, self.colors['primary']),
            ('api/deps.py', 2, 6.5, self.colors['warning']),
            ('api/routes', 5, 6.5, self.colors['secondary']),
            ('core/security.py', 8, 6.5, self.colors['warning']),
            ('services', 2, 4.5, self.colors['success']),
            ('models', 5, 4.5, self.colors['primary']),
            ('schemas', 8, 4.5, self.colors['secondary']),
            ('core/config.py', 2, 2.5, self.colors['gray']),
            ('db/session.py', 5, 2.5, self.colors['primary']),
            ('utils', 8, 2.5, self.colors['gray']),
        ]

        for name, x, y, color in modules:
            box = FancyBboxPatch((x - 0.7, y - 0.3), 1.4, 0.6,
                                 boxstyle="round,pad=0.05",
                                 edgecolor=color, facecolor=self.colors['light'],
                                 linewidth=2)
            ax.add_patch(box)
            ax.text(x, y, name, ha='center', va='center', fontsize=9,
                    fontweight='bold')

        # Dependencies
        dependencies = [
            ((5, 7.7), (2, 6.8)),    # main -> deps
            ((5, 7.7), (5, 6.8)),    # main -> routes
            ((5, 7.7), (8, 6.8)),    # main -> security
            ((5, 6.2), (2, 4.8)),    # routes -> services
            ((5, 6.2), (5, 4.8)),    # routes -> models
            ((5, 6.2), (8, 4.8)),    # routes -> schemas
            ((2, 4.2), (5, 4.8)),    # services -> models
            ((2, 4.2), (5, 2.8)),    # services -> db
            ((5, 4.2), (5, 2.8)),    # models -> db
            ((2, 6.2), (8, 6.8)),    # deps -> security
            ((2, 6.2), (5, 4.8)),    # deps -> models
        ]

        for (x1, y1), (x2, y2) in dependencies:
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', lw=1.5,
                                        color=self.colors['gray'], alpha=0.7))

        # Legend
        legend_y = 1
        ax.text(1, legend_y, 'Critical Files:', fontsize=10, fontweight='bold')

        critical = FancyBboxPatch((1, legend_y - 0.5), 1.5, 0.3,
                                  boxstyle="round,pad=0.03",
                                  edgecolor=self.colors['warning'],
                                  facecolor=self.colors['light'], linewidth=2)
        ax.add_patch(critical)
        ax.text(1.75, legend_y - 0.35, 'Security Issues', ha='center', va='center',
                fontsize=8)

        plt.tight_layout()
        output_path = self.output_dir / 'backend_module_dependencies.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    # ==================== QA Engineer Diagrams ====================

    def _create_test_pyramid(self) -> Path:
        """Create test pyramid diagram."""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'Test Pyramid - Piano Keys',
                fontsize=20, fontweight='bold', ha='center',
                color=self.colors['primary'])

        # Pyramid layers
        # E2E Tests (top, 10%)
        e2e_points = [(4, 7), (6, 7), (5.5, 8), (4.5, 8)]
        e2e = mpatches.Polygon(e2e_points, closed=True,
                               edgecolor=self.colors['danger'],
                               facecolor='#FFCDD2', linewidth=3)
        ax.add_patch(e2e)
        ax.text(5, 7.5, 'E2E Tests\n10% (~37 tests)', ha='center', va='center',
                fontsize=11, fontweight='bold')

        # Integration Tests (middle, 20%)
        int_points = [(3.5, 5.5), (6.5, 5.5), (6, 7), (4, 7)]
        integration = mpatches.Polygon(int_points, closed=True,
                                       edgecolor=self.colors['warning'],
                                       facecolor='#FFF9C4', linewidth=3)
        ax.add_patch(integration)
        ax.text(5, 6.25, 'Integration Tests\n20% (~73 tests)', ha='center', va='center',
                fontsize=11, fontweight='bold')

        # Unit Tests (bottom, 70%)
        unit_points = [(2, 3), (8, 3), (6.5, 5.5), (3.5, 5.5)]
        unit = mpatches.Polygon(unit_points, closed=True,
                                edgecolor=self.colors['success'],
                                facecolor='#C8E6C9', linewidth=3)
        ax.add_patch(unit)
        ax.text(5, 4.25, 'Unit Tests\n70% (~255 tests)', ha='center', va='center',
                fontsize=12, fontweight='bold')

        # Current vs Target
        ax.text(1, 2, 'Current Coverage:', fontsize=11, fontweight='bold')
        ax.text(1, 1.6, '12-15% (45 tests)', fontsize=10, color=self.colors['danger'])

        ax.text(6.5, 2, 'Target Coverage:', fontsize=11, fontweight='bold')
        ax.text(6.5, 1.6, '80%+ (365 tests)', fontsize=10, color=self.colors['success'])

        # Gap indicator
        gap_box = FancyBboxPatch((2, 0.5), 6, 0.8, boxstyle="round,pad=0.1",
                                 edgecolor=self.colors['danger'],
                                 facecolor='#FFEBEE', linewidth=2)
        ax.add_patch(gap_box)
        ax.text(5, 0.9, '⚠️ Gap: 320 additional tests needed', ha='center', va='center',
                fontsize=11, fontweight='bold', color=self.colors['danger'])

        plt.tight_layout()
        output_path = self.output_dir / 'qa_test_pyramid.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    def _create_test_coverage(self) -> Path:
        """Create test coverage map."""
        fig, ax = plt.subplots(figsize=(12, 8))

        # Data
        modules = ['API\nRoutes', 'Services', 'Models', 'Utils', 'Auth', 'Database']
        current = [15, 10, 20, 5, 8, 12]  # Current coverage %
        target = [80, 80, 80, 80, 80, 80]  # Target coverage %

        x = np.arange(len(modules))
        width = 0.35

        # Bars
        bars1 = ax.bar(x - width/2, current, width, label='Current',
                       color=self.colors['danger'], alpha=0.8)
        bars2 = ax.bar(x + width/2, target, width, label='Target',
                       color=self.colors['success'], alpha=0.8)

        # Labels
        ax.set_xlabel('Modules', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coverage %', fontsize=12, fontweight='bold')
        ax.set_title('Test Coverage by Module - Piano Keys',
                     fontsize=16, fontweight='bold', color=self.colors['primary'],
                     pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(modules, fontsize=10)
        ax.legend(fontsize=11)
        ax.set_ylim(0, 100)

        # Grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}%',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        output_path = self.output_dir / 'qa_test_coverage.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    def _create_testing_workflow(self) -> Path:
        """Create testing workflow diagram."""
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'Testing Workflow - CI/CD Integration',
                fontsize=18, fontweight='bold', ha='center',
                color=self.colors['primary'])

        # Workflow steps
        steps = [
            (8.5, 'Developer commits code', self.colors['primary']),
            (7.5, 'Pre-commit hooks run', self.colors['gray']),
            (6.5, 'Unit tests execute (Vitest)', self.colors['success']),
            (5.5, 'Integration tests run (Pytest)', self.colors['warning']),
            (4.5, 'E2E tests run (Playwright)', self.colors['danger']),
            (3.5, 'Coverage report generated', self.colors['secondary']),
            (2.5, 'Quality gate check (80%)', self.colors['primary']),
            (1.5, 'Deploy to staging/production', self.colors['success']),
        ]

        for y, text, color in steps:
            box = FancyBboxPatch((2, y - 0.3), 6, 0.6, boxstyle="round,pad=0.05",
                                 edgecolor=color, facecolor=self.colors['light'],
                                 linewidth=2)
            ax.add_patch(box)
            ax.text(5, y, text, ha='center', va='center', fontsize=10)

            # Arrow to next step
            if y > 1.5:
                ax.annotate('', xy=(5, y - 0.4), xytext=(5, y - 0.9),
                            arrowprops=dict(arrowstyle='->', lw=2, color=color))

        # Failure path
        ax.annotate('', xy=(8.5, 2.5), xytext=(8, 2.2),
                    arrowprops=dict(arrowstyle='->', lw=2, color=self.colors['danger'],
                                    linestyle='--'))
        ax.text(8.5, 3, 'Fail', ha='left', va='center', fontsize=9,
                color=self.colors['danger'], fontweight='bold')

        fail_box = FancyBboxPatch((8.5, 1.2), 1.2, 0.6, boxstyle="round,pad=0.05",
                                  edgecolor=self.colors['danger'],
                                  facecolor='#FFEBEE', linewidth=2)
        ax.add_patch(fail_box)
        ax.text(9.1, 1.5, 'Block\nDeploy', ha='center', va='center',
                fontsize=9, fontweight='bold', color=self.colors['danger'])

        plt.tight_layout()
        output_path = self.output_dir / 'qa_testing_workflow.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    def _create_test_distribution(self) -> Path:
        """Create test types distribution pie chart."""
        fig, ax = plt.subplots(figsize=(10, 8))

        # Data
        labels = ['Unit Tests\n(70%)', 'Integration Tests\n(20%)', 'E2E Tests\n(10%)']
        sizes = [255, 73, 37]
        colors = [self.colors['success'], self.colors['warning'], self.colors['danger']]
        explode = (0.05, 0.05, 0.1)  # Explode E2E slice

        # Pie chart
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
                                           colors=colors, autopct='%1.0f%%',
                                           shadow=True, startangle=90,
                                           textprops={'fontsize': 12, 'fontweight': 'bold'})

        # Make percentage text white
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
            autotext.set_fontweight('bold')

        ax.set_title('Target Test Distribution (365 Total Tests)',
                     fontsize=16, fontweight='bold', color=self.colors['primary'],
                     pad=20)

        plt.tight_layout()
        output_path = self.output_dir / 'qa_test_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated: {output_path.name}")
        return output_path

    # ==================== Placeholder methods for other diagrams ====================
    # These will be implemented based on the same patterns above

    def _create_component_hierarchy(self) -> Path:
        """Create frontend component hierarchy."""
        # TODO: Implement
        return self._create_placeholder('frontend_component_hierarchy.png',
                                        'Frontend Component Hierarchy')

    def _create_state_management(self) -> Path:
        """Create state management diagram."""
        return self._create_placeholder('frontend_state_management.png',
                                        'State Management Flow')

    def _create_routing_structure(self) -> Path:
        """Create routing structure."""
        return self._create_placeholder('frontend_routing_structure.png',
                                        'Routing Structure')

    def _create_frontend_data_flow(self) -> Path:
        """Create frontend data flow."""
        return self._create_placeholder('frontend_data_flow.png',
                                        'Frontend Data Flow')

    def _create_cicd_pipeline(self) -> Path:
        """Create CI/CD pipeline."""
        return self._create_placeholder('devops_cicd_pipeline.png',
                                        'CI/CD Pipeline')

    def _create_infrastructure(self) -> Path:
        """Create infrastructure architecture."""
        return self._create_placeholder('devops_infrastructure.png',
                                        'Infrastructure Architecture')

    def _create_deployment_flow(self) -> Path:
        """Create deployment flow."""
        return self._create_placeholder('devops_deployment_flow.png',
                                        'Deployment Flow')

    def _create_monitoring_stack(self) -> Path:
        """Create monitoring stack."""
        return self._create_placeholder('devops_monitoring_stack.png',
                                        'Monitoring Stack')

    def _create_security_architecture(self) -> Path:
        """Create security architecture."""
        return self._create_placeholder('security_architecture.png',
                                        'Security Architecture')

    def _create_auth_authorization_flow(self) -> Path:
        """Create auth/authorization flow."""
        return self._create_placeholder('security_auth_flow.png',
                                        'Authentication & Authorization Flow')

    def _create_threat_model(self) -> Path:
        """Create threat model."""
        return self._create_placeholder('security_threat_model.png',
                                        'Threat Model')

    def _create_security_layers(self) -> Path:
        """Create security layers."""
        return self._create_placeholder('security_layers.png',
                                        'Security Layers')

    def _create_db_schema_detailed(self) -> Path:
        """Create detailed database schema."""
        return self._create_placeholder('database_schema_detailed.png',
                                        'Database Schema (Detailed)')

    def _create_migration_flow(self) -> Path:
        """Create migration flow."""
        return self._create_placeholder('database_migration_flow.png',
                                        'Database Migration Flow')

    def _create_caching_architecture(self) -> Path:
        """Create caching architecture."""
        return self._create_placeholder('database_caching_architecture.png',
                                        'Caching Architecture (Redis)')

    def _create_data_flow(self) -> Path:
        """Create data flow."""
        return self._create_placeholder('database_data_flow.png',
                                        'Data Flow')

    def _create_user_journey(self) -> Path:
        """Create user journey map."""
        return self._create_placeholder('ux_user_journey.png',
                                        'User Journey Map')

    def _create_information_architecture(self) -> Path:
        """Create information architecture."""
        return self._create_placeholder('ux_information_architecture.png',
                                        'Information Architecture')

    def _create_component_library(self) -> Path:
        """Create component library structure."""
        return self._create_placeholder('ux_component_library.png',
                                        'Component Library Structure')

    def _create_accessibility_compliance(self) -> Path:
        """Create accessibility compliance."""
        return self._create_placeholder('ux_accessibility_compliance.png',
                                        'Accessibility Compliance (WCAG AA)')

    def _create_docs_structure(self) -> Path:
        """Create documentation structure."""
        return self._create_placeholder('tech_writer_docs_structure.png',
                                        'Documentation Structure')

    def _create_info_hierarchy(self) -> Path:
        """Create information hierarchy."""
        return self._create_placeholder('tech_writer_info_hierarchy.png',
                                        'Information Hierarchy')

    def _create_content_types(self) -> Path:
        """Create content types."""
        return self._create_placeholder('tech_writer_content_types.png',
                                        'Content Types')

    def _create_docs_workflow(self) -> Path:
        """Create documentation workflow."""
        return self._create_placeholder('tech_writer_docs_workflow.png',
                                        'Documentation Workflow')

    def _create_placeholder(self, filename: str, title: str) -> Path:
        """Create placeholder diagram."""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 5.5, title, fontsize=20, fontweight='bold',
                ha='center', va='center', color=self.colors['primary'])

        # Placeholder message
        ax.text(5, 4.5, '(Diagram implementation in progress)',
                fontsize=12, ha='center', va='center',
                color=self.colors['gray'], style='italic')

        plt.tight_layout()
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✅ Generated placeholder: {filename}")
        return output_path


if __name__ == "__main__":
    # Test diagram generation
    from pathlib import Path

    output_dir = Path(__file__).parent.parent.parent.parent / "output/role_diagrams"
    generator = DiagramGenerator(output_dir)

    print("Testing Diagram Generator...")
    print("=" * 70)

    # Test Backend diagrams
    print("\n📊 Generating Backend Engineer diagrams...")
    backend_diagrams = generator.generate_backend_diagrams()
    print(f"Generated {len(backend_diagrams)} diagrams")

    # Test QA diagrams
    print("\n📊 Generating QA Engineer diagrams...")
    qa_diagrams = generator.generate_qa_diagrams()
    print(f"Generated {len(qa_diagrams)} diagrams")

    print("\n✅ Diagram generator test complete!")
