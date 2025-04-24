"""
초기 테이블 생성 마이그레이션

Revision ID: 001
Revises: 
Create Date: 2023-03-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 테이블 생성
    op.create_table(
        'collection_jobs',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    op.create_index('ix_collection_jobs_type', 'collection_jobs', ['type'])
    op.create_index('ix_collection_jobs_status', 'collection_jobs', ['status'])
    
    # YouTube 비디오 테이블
    op.create_table(
        'youtube_videos',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('youtube_id', sa.String(20), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('duration', sa.String(20), nullable=True),
        sa.Column('channel_id', sa.String(50), nullable=False),
        sa.Column('channel_title', sa.String(255), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('like_count', sa.Integer(), nullable=False, default=0),
        sa.Column('comment_count', sa.Integer(), nullable=False, default=0),
        sa.Column('thumbnail_url', sa.String(255), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('category_id', sa.String(10), nullable=True),
        sa.Column('last_fetched_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    op.create_index('ix_youtube_videos_youtube_id', 'youtube_videos', ['youtube_id'], unique=True)
    op.create_index('ix_youtube_videos_channel_id', 'youtube_videos', ['channel_id'])
    op.create_index('ix_youtube_videos_channel_published', 'youtube_videos', ['channel_id', 'published_at'])
    
    # YouTube 댓글 테이블
    op.create_table(
        'youtube_comments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('video_id', sa.String(36), sa.ForeignKey('youtube_videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('comment_id', sa.String(50), nullable=False, unique=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('author_name', sa.String(100), nullable=False),
        sa.Column('author_channel_id', sa.String(50), nullable=True),
        sa.Column('author_profile_url', sa.String(255), nullable=True),
        sa.Column('like_count', sa.Integer(), nullable=False, default=0),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('is_reply', sa.Boolean(), nullable=False, default=False),
        sa.Column('parent_id', sa.String(50), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_label', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    op.create_index('ix_youtube_comments_video_id', 'youtube_comments', ['video_id'])
    op.create_index('ix_youtube_comments_comment_id', 'youtube_comments', ['comment_id'], unique=True)
    op.create_index('ix_youtube_comments_sentiment', 'youtube_comments', ['sentiment_label', 'sentiment_score'])
    
    # YouTube 감성 분석 결과 테이블
    op.create_table(
        'youtube_sentiment_analysis',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('video_id', sa.String(36), sa.ForeignKey('youtube_videos.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('positive_count', sa.Integer(), nullable=False, default=0),
        sa.Column('negative_count', sa.Integer(), nullable=False, default=0),
        sa.Column('neutral_count', sa.Integer(), nullable=False, default=0),
        sa.Column('positive_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('negative_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('neutral_percentage', sa.Float(), nullable=False, default=0.0),
        sa.Column('average_sentiment_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('positive_keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('negative_keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False),
        sa.Column('analysis_version', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    # 테이블 삭제 (역순)
    op.drop_table('youtube_sentiment_analysis')
    op.drop_table('youtube_comments')
    op.drop_table('youtube_videos')
    op.drop_table('collection_jobs') 