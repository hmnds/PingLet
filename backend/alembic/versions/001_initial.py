"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create monitored_accounts table
    op.create_table(
        'monitored_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('x_user_id', sa.String(length=255), nullable=True),
        sa.Column('digest_enabled', sa.Boolean(), nullable=False),
        sa.Column('alerts_enabled', sa.Boolean(), nullable=False),
        sa.Column('last_seen_post_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monitored_accounts_id'), 'monitored_accounts', ['id'], unique=False)
    op.create_index(op.f('ix_monitored_accounts_username'), 'monitored_accounts', ['username'], unique=True)
    op.create_index(op.f('ix_monitored_accounts_x_user_id'), 'monitored_accounts', ['x_user_id'], unique=False)
    
    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('x_post_id', sa.String(length=255), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('url', sa.String(length=512), nullable=True),
        sa.Column('raw_json', JSONB(), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('stored_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['monitored_accounts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('x_post_id')
    )
    op.create_index(op.f('ix_posts_id'), 'posts', ['id'], unique=False)
    op.create_index(op.f('ix_posts_x_post_id'), 'posts', ['x_post_id'], unique=True)
    op.create_index(op.f('ix_posts_author_id'), 'posts', ['author_id'], unique=False)
    op.create_index(op.f('ix_posts_created_at'), 'posts', ['created_at'], unique=False)
    
    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_id'), 'topics', ['id'], unique=False)
    op.create_index(op.f('ix_topics_name'), 'topics', ['name'], unique=True)
    
    # Create alert_rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('topic_ids', sa.JSON(), nullable=True),
        sa.Column('allowed_author_ids', sa.JSON(), nullable=True),
        sa.Column('similarity_threshold', sa.Float(), nullable=False),
        sa.Column('cooldown_minutes', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_rules_id'), 'alert_rules', ['id'], unique=False)
    op.create_index(op.f('ix_alert_rules_name'), 'alert_rules', ['name'], unique=True)
    
    # Create alerts_log table
    op.create_table(
        'alerts_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.ForeignKeyConstraint(['rule_id'], ['alert_rules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_log_id'), 'alerts_log', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_log_rule_id'), 'alerts_log', ['rule_id'], unique=False)
    op.create_index(op.f('ix_alerts_log_post_id'), 'alerts_log', ['post_id'], unique=False)
    
    # Create digests table
    op.create_table(
        'digests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('digest_date', sa.Date(), nullable=False),
        sa.Column('content_markdown', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_digests_id'), 'digests', ['id'], unique=False)
    op.create_index(op.f('ix_digests_digest_date'), 'digests', ['digest_date'], unique=True)
    
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_id'), 'settings', ['id'], unique=False)
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_settings_key'), table_name='settings')
    op.drop_index(op.f('ix_settings_id'), table_name='settings')
    op.drop_table('settings')
    op.drop_index(op.f('ix_digests_digest_date'), table_name='digests')
    op.drop_index(op.f('ix_digests_id'), table_name='digests')
    op.drop_table('digests')
    op.drop_index(op.f('ix_alerts_log_post_id'), table_name='alerts_log')
    op.drop_index(op.f('ix_alerts_log_rule_id'), table_name='alerts_log')
    op.drop_index(op.f('ix_alerts_log_id'), table_name='alerts_log')
    op.drop_table('alerts_log')
    op.drop_index(op.f('ix_alert_rules_name'), table_name='alert_rules')
    op.drop_index(op.f('ix_alert_rules_id'), table_name='alert_rules')
    op.drop_table('alert_rules')
    op.drop_index(op.f('ix_topics_name'), table_name='topics')
    op.drop_index(op.f('ix_topics_id'), table_name='topics')
    op.drop_table('topics')
    op.drop_index(op.f('ix_posts_created_at'), table_name='posts')
    op.drop_index(op.f('ix_posts_author_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_x_post_id'), table_name='posts')
    op.drop_index(op.f('ix_posts_id'), table_name='posts')
    op.drop_table('posts')
    op.drop_index(op.f('ix_monitored_accounts_x_user_id'), table_name='monitored_accounts')
    op.drop_index(op.f('ix_monitored_accounts_username'), table_name='monitored_accounts')
    op.drop_index(op.f('ix_monitored_accounts_id'), table_name='monitored_accounts')
    op.drop_table('monitored_accounts')
    op.execute('DROP EXTENSION IF EXISTS vector')


