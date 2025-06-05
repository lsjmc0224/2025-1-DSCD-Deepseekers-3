from datetime import datetime
from sqlalchemy.orm import Session
from app.analyzer.analyzer import Analyzer
from app.analyzer.repositories import AnalysisRepository
from app.models import ContentAnalysis


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalysisRepository(db)
        self.analyzer = Analyzer()

    def run_batch_analysis(self):
        # 1. 로그 시작 시간 기록
        started_at = datetime.now()
        log_id = self.repo.start_analysis_log()

        # 2. 분석할 데이터 가져오기
        unanalyzed_items = self.repo.get_all_unanalyzed()

        all_results = []

        for item in unanalyzed_items:
            raw_text = item.content
            original = item.get_original()
            source_type = original.__table__.name
            source_id = str(original.id)

            analysis_results = self.analyzer.run(raw_text)

            for result in analysis_results:
                all_results.append({
                    "analysis_log_id": log_id,
                    "source_type": source_type,
                    "source_id": source_id,
                    "sentence": result["content"],
                    "aspect_id": result["aspect_id"],
                    "sentiment_id": result["sentiment_id"],
                    "evidence_keywords": result["evidence_keywords"]
                })

        print(all_results)
        # 3. 분석 결과 저장
        if all_results:
            self.repo.create_content_analysis_results(log_id, all_results)

        # 4. 원본 is_analyzed 업데이트
        self.repo.mark_as_analyzed([item.get_original() for item in unanalyzed_items])

        # 5. 로그 종료 시간 기록
        self.repo.finish_analysis_log(log_id=log_id)

        return {
            "log_id": log_id,
            "analyzed_count": len(all_results),
            "source_count": len(unanalyzed_items)
        }
