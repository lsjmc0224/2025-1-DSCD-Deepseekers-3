from app.models import InstizPosts, InstizComments, TiktokComments, YoutubeComments, ContentAnalysis, AnalysisLogs
from sqlalchemy.orm import Session
from app.analyzer.factory import AdapterFactory
from datetime import datetime
from typing import List, Dict

class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db
        self.factory = AdapterFactory()

    def get_unanalyzed_instiz_posts(self):
        rows = self.db.query(InstizPosts).filter_by(is_analyzed=False).all()
        return [self.factory.wrap(r) for r in rows]

    def get_unanalyzed_instiz_comments(self):
        rows = self.db.query(InstizComments).filter_by(is_analyzed=False).all()
        return [self.factory.wrap(r) for r in rows]

    def get_unanalyzed_tiktok_comments(self):
        rows = self.db.query(TiktokComments).filter_by(is_analyzed=False).all()
        return [self.factory.wrap(r) for r in rows]

    def get_unanalyzed_youtube_comments(self):
        rows = self.db.query(YoutubeComments).filter_by(is_analyzed=False).all()
        return [self.factory.wrap(r) for r in rows]

    def get_all_unanalyzed(self):
        combined = []
        combined += self.get_unanalyzed_instiz_posts()
        combined += self.get_unanalyzed_instiz_comments()
        combined += self.get_unanalyzed_tiktok_comments()
        combined += self.get_unanalyzed_youtube_comments()
        return combined

    # ✅ 배치 로그 시작
    def start_analysis_log(self) -> int:
        log = AnalysisLogs(started_at=datetime.utcnow())
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log.id

    # ✅ 배치 로그 종료
    def finish_analysis_log(self, log_id: int):
        log = self.db.query(AnalysisLogs).filter_by(id=log_id).first()
        if log:
            log.finished_at = datetime.utcnow()
            self.db.commit()

    # ✅ 분석 결과 다건 저장
    def create_content_analysis_results(self, log_id: int, results: List[Dict]):
        for r in results:
            self.db.add(ContentAnalysis(
                analysis_log_id=log_id,
                source_type=r["source_type"],
                source_id=r["source_id"],
                sentence=r["sentence"],
                sentiment_id=r["sentiment_id"],
                aspect_id=r["aspect_id"],
                evidence_keywords=",".join(r["evidence_keywords"])
            ))
        self.db.commit()

    def mark_as_analyzed(self, original_objects: List[object]):
        """
        분석된 원본 객체들의 is_analyzed 플래그를 True로 설정
        """
        for obj in original_objects:
            if hasattr(obj, "is_analyzed"):
                obj.is_analyzed = True
        self.db.commit()