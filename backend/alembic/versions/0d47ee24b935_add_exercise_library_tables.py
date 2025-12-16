"""add_exercise_library_tables

Revision ID: 0d47ee24b935
Revises: 170e726b0a9d
Create Date: 2025-12-16 22:02:08.910680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d47ee24b935'
down_revision: Union[str, Sequence[str], None] = '170e726b0a9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add exercise library tables for template-driven content."""

    # Template Curriculum Library
    op.create_table(
        'curriculum_library',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('curriculum_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('style_tags_json', sa.Text(), default='[]'),  # JSON list
        sa.Column('level', sa.String(50), nullable=False),  # beginner, intermediate, etc.
        sa.Column('estimated_total_weeks', sa.Integer(), nullable=False),

        # Source metadata
        sa.Column('source_file', sa.String(500), nullable=False),
        sa.Column('ai_provider', sa.String(50), nullable=False),  # claude, gemini, etc.
        sa.Column('imported_at', sa.DateTime(), nullable=False),

        # Statistics
        sa.Column('total_modules', sa.Integer(), default=0),
        sa.Column('total_lessons', sa.Integer(), default=0),
        sa.Column('total_exercises', sa.Integer(), default=0),

        # Full curriculum JSON
        sa.Column('curriculum_json', sa.Text(), nullable=False),  # Complete template data

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Exercise Library
    op.create_table(
        'exercise_library',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('exercise_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('curriculum_id', sa.String(100), nullable=False, index=True),
        sa.Column('module_id', sa.String(100), nullable=False),
        sa.Column('lesson_id', sa.String(100), nullable=False),

        # Exercise data
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('exercise_type', sa.String(50), nullable=False),  # scale, progression, etc.
        sa.Column('difficulty', sa.String(20), nullable=False),  # beginner, intermediate, etc.
        sa.Column('estimated_duration_minutes', sa.Integer(), default=10),

        # Content (JSON)
        sa.Column('content_json', sa.Text(), nullable=False),
        sa.Column('midi_prompt', sa.Text(), nullable=True),

        # Generated files
        sa.Column('midi_file_path', sa.String(500), nullable=True),
        sa.Column('audio_file_path', sa.String(500), nullable=True),

        # Metadata
        sa.Column('tags_json', sa.Text(), default='[]'),  # JSON list
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('source_template', sa.String(500), nullable=False),

        # Usage tracking
        sa.Column('times_accessed', sa.Integer(), default=0),
        sa.Column('avg_completion_time', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),

        # Foreign key to curriculum library
        sa.ForeignKeyConstraint(
            ['curriculum_id'],
            ['curriculum_library.curriculum_id'],
            ondelete='CASCADE'
        ),
    )

    # User Exercise Progress (for spaced repetition)
    op.create_table(
        'user_exercise_progress',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('exercise_id', sa.String(100), nullable=False, index=True),

        # Spaced repetition data
        sa.Column('ease_factor', sa.Float(), default=2.5),  # SM-2 algorithm
        sa.Column('interval', sa.Integer(), default=1),  # Days until next review
        sa.Column('repetitions', sa.Integer(), default=0),
        sa.Column('last_reviewed', sa.DateTime(), nullable=True),
        sa.Column('next_review', sa.DateTime(), nullable=True),

        # Performance tracking
        sa.Column('times_practiced', sa.Integer(), default=0),
        sa.Column('total_practice_time_seconds', sa.Integer(), default=0),
        sa.Column('best_score', sa.Float(), nullable=True),
        sa.Column('avg_score', sa.Float(), nullable=True),
        sa.Column('is_mastered', sa.Boolean(), default=False),
        sa.Column('mastered_at', sa.DateTime(), nullable=True),

        # Quality ratings history (JSON array)
        sa.Column('quality_ratings_json', sa.Text(), default='[]'),

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),

        # Foreign keys
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['exercise_id'],
            ['exercise_library.exercise_id'],
            ondelete='CASCADE'
        ),

        # Unique constraint: one progress record per user per exercise
        sa.UniqueConstraint('user_id', 'exercise_id', name='uq_user_exercise'),
    )

    # Indexes for common queries
    op.create_index('ix_exercise_library_type_difficulty', 'exercise_library', ['exercise_type', 'difficulty'])
    op.create_index('ix_exercise_library_curriculum_type', 'exercise_library', ['curriculum_id', 'exercise_type'])
    op.create_index('ix_user_exercise_progress_next_review', 'user_exercise_progress', ['user_id', 'next_review'])


def downgrade() -> None:
    """Downgrade schema - Remove exercise library tables."""
    op.drop_index('ix_user_exercise_progress_next_review', table_name='user_exercise_progress')
    op.drop_index('ix_exercise_library_curriculum_type', table_name='exercise_library')
    op.drop_index('ix_exercise_library_type_difficulty', table_name='exercise_library')

    op.drop_table('user_exercise_progress')
    op.drop_table('exercise_library')
    op.drop_table('curriculum_library')
