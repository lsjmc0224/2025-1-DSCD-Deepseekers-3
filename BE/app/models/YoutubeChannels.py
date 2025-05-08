from sqlalchemy import Column, Text, Integer, TIMESTAMP, Index
from app.core.db import Base

class YoutubeChannels(Base):
    __tablename__ = "youtube_channels"
    id = Column(Text, primary_key=True, comment="API에서 가져온 채널 ID")
    name = Column(Text, comment="채널명")
    subscriber_count = Column(Integer, comment="구독자 수")
    updated_at = Column(TIMESTAMP, comment="채널 정보 갱신 시각")

    __table_args__ = (
        Index("idx_youtube_channels_subscriber_count", "subscriber_count"),
    ) 