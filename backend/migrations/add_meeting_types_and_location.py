"""Add meeting types and location support for peer-to-peer learning

This migration adds:
1. meeting_type (physical/online) to peer_matches, tutoring_sessions, help_requests, help_offers
2. request_type (asking_help/offering_help) to help_requests and help_offers
3. location field to users for physical meetup matching
4. location fields to help_requests and help_offers
5. meeting details (link, location) to tutoring_sessions

Revision ID: add_meeting_types_location
Revises: add_peer_matching
Create Date: 2025-12-25
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = 'add_meeting_types_location'
down_revision = 'add_peer_matching'
branch_labels = None
depends_on = None


def upgrade():
    # Add location and GPS coordinates to users table
    op.add_column('users', sa.Column('location', sa.String(), nullable=True))
    op.add_column('users', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('longitude', sa.Float(), nullable=True))
    
    # Add meeting_type to peer_matches
    op.add_column('peer_matches', sa.Column(
        'meeting_type',
        sa.Enum('PHYSICAL', 'ONLINE', name='meetingtype'),
        nullable=False,
        server_default='ONLINE'
    ))
    
    # Add meeting details to tutoring_sessions
    op.add_column('tutoring_sessions', sa.Column(
        'meeting_type',
        sa.Enum('PHYSICAL', 'ONLINE', name='meetingtype'),
        nullable=False,
        server_default='ONLINE'
    ))
    op.add_column('tutoring_sessions', sa.Column('meeting_link', sa.String(), nullable=True))
    op.add_column('tutoring_sessions', sa.Column('physical_location', sa.String(), nullable=True))
    
    # Add request_type, meeting_type, and location to help_requests
    op.add_column('help_requests', sa.Column(
        'request_type',
        sa.Enum('ASKING_HELP', 'OFFERING_HELP', name='requesttype'),
        nullable=False,
        server_default='ASKING_HELP'
    ))
    op.add_column('help_requests', sa.Column(
        'meeting_type',
        sa.Enum('PHYSICAL', 'ONLINE', name='meetingtype'),
        nullable=False,
        server_default='ONLINE'
    ))
    op.add_column('help_requests', sa.Column('preferred_location', sa.String(), nullable=True))
    
    # Add request_type, meeting_type, and location to help_offers
    op.add_column('help_offers', sa.Column(
        'request_type',
        sa.Enum('ASKING_HELP', 'OFFERING_HELP', name='requesttype'),
        nullable=False,
        server_default='OFFERING_HELP'
    ))
    op.add_column('help_offers', sa.Column(
        'meeting_type',
        sa.Enum('PHYSICAL', 'ONLINE', name='meetingtype'),
        nullable=False,
        server_default='ONLINE'
    ))
    op.add_column('help_offers', sa.Column('available_location', sa.String(), nullable=True))


def downgrade():
    # Remove columns from help_offers
    op.drop_column('help_offers', 'available_location')
    op.drop_column('help_offers', 'meeting_type')
    op.drop_column('help_offers', 'request_type')
    
    # Remove columns from help_requests
    op.drop_column('help_requests', 'preferred_location')
    op.drop_column('help_requests', 'meeting_type')
    op.drop_column('help_requests', 'request_type')
    
    # Remove columns from tutoring_sessions
    op.drop_column('tutoring_sessions', 'physical_location')
    op.drop_column('tutoring_sessions', 'meeting_link')
    op.drop_column('tutoring_sessions', 'meeting_type')
    
    # Remove meeting_type from peer_matches
    op.drop_column('peer_matches', 'meeting_type')
    
    # Remove location and GPS from users
    op.drop_column('users', 'longitude')
    op.drop_column('users', 'latitude')
    op.drop_column('users', 'location')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS meetingtype')
    op.execute('DROP TYPE IF EXISTS requesttype')
