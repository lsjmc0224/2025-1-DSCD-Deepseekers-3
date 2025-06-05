# scripts/run_analysis.py

from app.core.db import get_db
from app.analyzer.services import AnalysisService

def run():
    db_generator = get_db()
    db = next(db_generator)

    try:
        service = AnalysisService(db)
        result = service.run_batch_analysis()
        print("분석 완료:", result)
    finally:
        db.close()

if __name__ == "__main__":
    run()
