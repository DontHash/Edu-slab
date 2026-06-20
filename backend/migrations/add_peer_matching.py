"""Add peer matching tables

Revision ID: add_peer_matching
Revises: 
Create Date: 2025-12-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_peer_matching'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Create student_chapter_performance table
    op.create_table(
        'student_chapter_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('chapter', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('accuracy_percentage', sa.Integer(), nullable=False),
        sa.Column('total_questions_attempted', sa.Integer(), nullable=True, default=0),
        sa.Column('correct_answers', sa.Integer(), nullable=True, default=0),
        sa.Column('weakness_level', sa.String(), nullable=False),
        sa.Column('is_strong_chapter', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_weak_chapter', sa.Boolean(), nullable=True, default=False),
        sa.Column('last_assessed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_chapter_performance_id'), 'student_chapter_performance', ['id'], unique=False)

    # Create peer_matches table
    op.create_table(
        'peer_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('learner_id', sa.Integer(), nullable=False),
        sa.Column('chapter', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('tutor_score', sa.Float(), nullable=False),
        sa.Column('learner_score', sa.Float(), nullable=False),
        sa.Column('compatibility_score', sa.Float(), nullable=True),
        sa.Column('preference_rank_tutor', sa.Integer(), nullable=True),
        sa.Column('preference_rank_learner', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'COMPLETED', name='matchstatus'), nullable=True),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tutor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peer_matches_id'), 'peer_matches', ['id'], unique=False)

    # Create tutoring_sessions table
    op.create_table(
        'tutoring_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('topics_covered', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tutor_rating', sa.Integer(), nullable=True),
        sa.Column('learner_rating', sa.Integer(), nullable=True),
        sa.Column('tutor_feedback', sa.Text(), nullable=True),
        sa.Column('learner_feedback', sa.Text(), nullable=True),
        sa.Column('learner_progress', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['peer_matches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tutoring_sessions_id'), 'tutoring_sessions', ['id'], unique=False)


    # Create help_requests table
    op.create_table(
        'help_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('chapter', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('urgency', sa.String(), nullable=True, default='normal'),
        sa.Column('student_score', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'FULFILLED', 'CANCELLED', name='helprequeststatus'), nullable=True),
        sa.Column('matched_with', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('fulfilled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['matched_with'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_help_requests_id'), 'help_requests', ['id'], unique=False)

    # Create help_offers table
    op.create_table(
        'help_offers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tutor_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('chapter', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('availability', sa.String(), nullable=True),
        sa.Column('tutor_score', sa.Float(), nullable=True),
        sa.Column('max_students', sa.Integer(), nullable=True, default=3),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('current_students', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tutor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_help_offers_id'), 'help_offers', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_help_offers_id'), table_name='help_offers')
    op.drop_table('help_offers')
    op.drop_index(op.f('ix_help_requests_id'), table_name='help_requests')
    op.drop_table('help_requests')
    op.drop_index(op.f('ix_tutoring_sessions_id'), table_name='tutoring_sessions')
    op.drop_table('tutoring_sessions')
    op.drop_index(op.f('ix_peer_matches_id'), table_name='peer_matches')
    op.drop_table('peer_matches')
    op.drop_index(op.f('ix_student_chapter_performance_id'), table_name='student_chapter_performance')
    op.drop_table('student_chapter_performance')
    op.execute('DROP TYPE matchstatus')
    op.execute('DROP TYPE helprequeststatus')
