"""add curriculum tables

Revision ID: d8f3c2a91b45
Revises: 8948c5427069
Create Date: 2024-12-13 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8f3c2a91b45'
down_revision: Union[str, None] = '7787f7a3a199'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_skill_profiles table
    op.create_table(
        'user_skill_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('technical_ability', sa.Integer(), nullable=False, default=1),
        sa.Column('theory_knowledge', sa.Integer(), nullable=False, default=1),
        sa.Column('rhythm_competency', sa.Integer(), nullable=False, default=1),
        sa.Column('ear_training', sa.Integer(), nullable=False, default=1),
        sa.Column('improvisation', sa.Integer(), nullable=False, default=1),
        sa.Column('style_familiarity_json', sa.Text(), nullable=False, default='{}'),
        sa.Column('learning_velocity', sa.String(20), nullable=False, default='medium'),
        sa.Column('preferred_style', sa.String(50), nullable=True),
        sa.Column('weekly_practice_hours', sa.Float(), nullable=False, default=5.0),
        sa.Column('primary_goal', sa.String(100), nullable=True),
        sa.Column('interests_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_skill_profiles_user_id', 'user_skill_profiles', ['user_id'])

    # Create curricula table
    op.create_table(
        'curricula',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_weeks', sa.Integer(), nullable=False, default=12),
        sa.Column('current_week', sa.Integer(), nullable=False, default=1),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('ai_model_used', sa.String(50), nullable=True),
        sa.Column('generation_prompt_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curricula_user_id', 'curricula', ['user_id'])

    # Create curriculum_modules table
    op.create_table(
        'curriculum_modules',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('curriculum_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('theme', sa.String(100), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('start_week', sa.Integer(), nullable=False),
        sa.Column('end_week', sa.Integer(), nullable=False),
        sa.Column('prerequisites_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('outcomes_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('completion_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['curriculum_id'], ['curricula.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_modules_curriculum_id', 'curriculum_modules', ['curriculum_id'])

    # Create curriculum_lessons table
    op.create_table(
        'curriculum_lessons',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('module_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('theory_content_json', sa.Text(), nullable=False, default='{}'),
        sa.Column('concepts_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=False, default=60),
        sa.Column('is_completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['module_id'], ['curriculum_modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_lessons_module_id', 'curriculum_lessons', ['module_id'])

    # Create curriculum_exercises table
    op.create_table(
        'curriculum_exercises',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('lesson_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, default=0),
        sa.Column('exercise_type', sa.String(50), nullable=False),
        sa.Column('content_json', sa.Text(), nullable=False, default='{}'),
        sa.Column('difficulty', sa.String(20), nullable=False, default='beginner'),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=False, default=10),
        sa.Column('target_bpm', sa.Integer(), nullable=True),
        sa.Column('practice_count', sa.Integer(), nullable=False, default=0),
        sa.Column('best_score', sa.Float(), nullable=True),
        sa.Column('is_mastered', sa.Boolean(), nullable=False, default=False),
        sa.Column('mastered_at', sa.DateTime(), nullable=True),
        sa.Column('next_review_at', sa.DateTime(), nullable=True),
        sa.Column('last_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('interval_days', sa.Float(), nullable=False, default=1.0),
        sa.Column('ease_factor', sa.Float(), nullable=False, default=2.5),
        sa.Column('repetition_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lesson_id'], ['curriculum_lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_exercises_lesson_id', 'curriculum_exercises', ['lesson_id'])

    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('curriculum_id', sa.String(36), nullable=True),
        sa.Column('assessment_type', sa.String(50), nullable=False),
        sa.Column('scores_json', sa.Text(), nullable=False, default='{}'),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('ai_feedback_json', sa.Text(), nullable=False, default='{}'),
        sa.Column('recommendations_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['curriculum_id'], ['curricula.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_assessments_user_id', 'assessments')
    op.drop_table('assessments')
    
    op.drop_index('ix_curriculum_exercises_lesson_id', 'curriculum_exercises')
    op.drop_table('curriculum_exercises')
    
    op.drop_index('ix_curriculum_lessons_module_id', 'curriculum_lessons')
    op.drop_table('curriculum_lessons')
    
    op.drop_index('ix_curriculum_modules_curriculum_id', 'curriculum_modules')
    op.drop_table('curriculum_modules')
    
    op.drop_index('ix_curricula_user_id', 'curricula')
    op.drop_table('curricula')
    
    op.drop_index('ix_user_skill_profiles_user_id', 'user_skill_profiles')
    op.drop_table('user_skill_profiles')
