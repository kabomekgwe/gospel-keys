"""Add Phase 3 real-time analysis tables

Revision ID: 170e726b0a9d
Revises: 2b8b44072eaa
Create Date: 2025-12-15 15:01:06.251774

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '170e726b0a9d'
down_revision: Union[str, Sequence[str], None] = '2b8b44072eaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add Phase 3 real-time analysis tables."""

    # 1. Create realtime_sessions table
    op.create_table(
        'realtime_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('piece_name', sa.String(length=255), nullable=True),
        sa.Column('genre', sa.String(length=50), nullable=True),
        sa.Column('target_tempo', sa.Integer(), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('websocket_session_id', sa.String(length=255), nullable=True),
        sa.Column('chunks_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_realtime_sessions_user_id'), 'realtime_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_realtime_sessions_started_at'), 'realtime_sessions', ['started_at'], unique=False)

    # 2. Create performances table
    op.create_table(
        'performances',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('recording_started_at', sa.DateTime(), nullable=False),
        sa.Column('recording_duration', sa.Float(), nullable=True),
        sa.Column('audio_path', sa.String(length=500), nullable=True),
        sa.Column('midi_path', sa.String(length=500), nullable=True),
        sa.Column('sample_rate', sa.Integer(), nullable=False, server_default='44100'),
        sa.Column('audio_format', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['realtime_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performances_session_id'), 'performances', ['session_id'], unique=False)

    # 3. Create analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('performance_id', sa.String(), nullable=False),
        sa.Column('pitch_accuracy', sa.Float(), nullable=True),
        sa.Column('rhythm_accuracy', sa.Float(), nullable=True),
        sa.Column('dynamics_range', sa.Float(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('avg_pitch_deviation_cents', sa.Float(), nullable=True),
        sa.Column('timing_consistency', sa.Float(), nullable=True),
        sa.Column('tempo_stability', sa.Float(), nullable=True),
        sa.Column('note_accuracy_rate', sa.Float(), nullable=True),
        sa.Column('total_notes_detected', sa.Integer(), nullable=True),
        sa.Column('total_onsets_detected', sa.Integer(), nullable=True),
        sa.Column('total_dynamics_events', sa.Integer(), nullable=True),
        sa.Column('feedback_json', sa.Text(), nullable=True),
        sa.Column('difficulty_estimate', sa.String(length=20), nullable=True),
        sa.Column('genre_match_score', sa.Float(), nullable=True),
        sa.Column('analysis_engine_version', sa.String(length=50), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['performances.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_results_performance_id'), 'analysis_results', ['performance_id'], unique=False)
    op.create_index(op.f('ix_analysis_results_created_at'), 'analysis_results', ['created_at'], unique=False)

    # 4. Create progress_metrics table
    op.create_table(
        'progress_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.DateTime(), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('total_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_practice_time_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_pitch_accuracy', sa.Float(), nullable=True),
        sa.Column('avg_rhythm_accuracy', sa.Float(), nullable=True),
        sa.Column('avg_dynamics_range', sa.Float(), nullable=True),
        sa.Column('avg_overall_score', sa.Float(), nullable=True),
        sa.Column('improvement_rate', sa.Float(), nullable=True),
        sa.Column('consistency_score', sa.Float(), nullable=True),
        sa.Column('genre_breakdown_json', sa.Text(), nullable=True),
        sa.Column('milestones_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_progress_metrics_user_id'), 'progress_metrics', ['user_id'], unique=False)
    op.create_index(op.f('ix_progress_metrics_metric_date'), 'progress_metrics', ['metric_date'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Drop Phase 3 tables."""
    op.drop_index(op.f('ix_progress_metrics_metric_date'), table_name='progress_metrics')
    op.drop_index(op.f('ix_progress_metrics_user_id'), table_name='progress_metrics')
    op.drop_table('progress_metrics')

    op.drop_index(op.f('ix_analysis_results_created_at'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_performance_id'), table_name='analysis_results')
    op.drop_table('analysis_results')

    op.drop_index(op.f('ix_performances_session_id'), table_name='performances')
    op.drop_table('performances')

    op.drop_index(op.f('ix_realtime_sessions_started_at'), table_name='realtime_sessions')
    op.drop_index(op.f('ix_realtime_sessions_user_id'), table_name='realtime_sessions')
    op.drop_table('realtime_sessions')
