from datetime import datetime
from typing import List

from database import QuizResultRecord, session_scope
from distributed.cache import update_leaderboard
from models.quiz import QuizResult


class ResultsService:
    def __init__(self):
        pass

    async def get_user_results(self, user_id: str) -> List[QuizResult]:
        with session_scope() as session:
            records = (
                session.query(QuizResultRecord)
                .filter(QuizResultRecord.user_id == user_id)
                .order_by(QuizResultRecord.completed_at.desc())
                .all()
            )
            return [self._to_model(record) for record in records]

    async def get_quiz_results(self, quiz_id: str) -> List[QuizResult]:
        with session_scope() as session:
            records = (
                session.query(QuizResultRecord)
                .filter(QuizResultRecord.quiz_id == quiz_id)
                .order_by(QuizResultRecord.completed_at.desc())
                .all()
            )
            return [self._to_model(record) for record in records]

    async def save_result(self, result: QuizResult):
        completed_at = result.completed_at or datetime.utcnow()
        with session_scope() as session:
            session.add(
                QuizResultRecord(
                    quiz_id=result.quiz_id,
                    user_id=result.user_id,
                    score=result.score,
                    total_points=result.total_points,
                    percentage=result.percentage,
                    completed_at=completed_at,
                )
            )
        await update_leaderboard(result.quiz_id, result.user_id, result.score)

    @staticmethod
    def _to_model(record: QuizResultRecord) -> QuizResult:
        return QuizResult(
            quiz_id=record.quiz_id,
            user_id=record.user_id,
            score=record.score,
            total_points=record.total_points,
            percentage=record.percentage,
            completed_at=record.completed_at,
        )
