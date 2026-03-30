from datetime import datetime
from typing import List, Optional

from database import QuizRecord, session_scope
from distributed.cache import get_cache, set_cache, delete_cache
from models.quiz import Question, Quiz

class QuizService:
    def __init__(self):
        pass

    async def create_quiz(self, quiz: Quiz) -> Quiz:
        quiz.created_at = datetime.utcnow()
        with session_scope() as session:
            session.add(
                QuizRecord(
                    id=quiz.id,
                    title=quiz.title,
                    description=quiz.description,
                    questions=[question.model_dump(mode="json") for question in quiz.questions],
                    duration_minutes=quiz.duration_minutes,
                    created_by=quiz.created_by,
                    created_at=quiz.created_at,
                    is_active=quiz.is_active,
                )
            )
        await set_cache(f"quiz:{quiz.id}", quiz.model_dump(mode='json'), expire=86400)
        return quiz

    async def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        cached = await get_cache(f"quiz:{quiz_id}")
        if cached:
            return Quiz(**cached)
        with session_scope() as session:
            record = session.get(QuizRecord, quiz_id)
            if not record or not record.is_active:
                return None
            quiz = self._to_model(record)
        await set_cache(f"quiz:{quiz_id}", quiz.model_dump(mode='json'), expire=86400)
        return quiz

    async def list_quizzes(self) -> List[Quiz]:
        with session_scope() as session:
            records = (
                session.query(QuizRecord)
                .filter(QuizRecord.is_active.is_(True))
                .order_by(QuizRecord.created_at.desc())
                .all()
            )
            return [self._to_model(record) for record in records]

    async def delete_quiz(self, quiz_id: str):
        with session_scope() as session:
            record = session.get(QuizRecord, quiz_id)
            if record:
                record.is_active = False
        await delete_cache(f"quiz:{quiz_id}")

    @staticmethod
    def _to_model(record: QuizRecord) -> Quiz:
        return Quiz(
            id=record.id,
            title=record.title,
            description=record.description,
            questions=[Question(**question) for question in record.questions],
            duration_minutes=record.duration_minutes,
            created_by=record.created_by,
            created_at=record.created_at,
            is_active=record.is_active,
        )

def calculate_score(quiz_id: str, answers: List[int]) -> dict:
    with session_scope() as session:
        record = session.get(QuizRecord, quiz_id)
        if not record:
            score = sum(1 for ans in answers if ans >= 0)
            total = len(answers)
            percentage = (score / total * 100) if total else 0.0
            return {"score": score, "total_points": total, "percentage": percentage}

        questions = [Question(**question) for question in record.questions]

    score = 0
    total_points = sum(question.points for question in questions)
    for index, question in enumerate(questions):
        answer = answers[index] if index < len(answers) else -1
        if answer == question.correct_answer:
            score += question.points

    percentage = (score / total_points * 100) if total_points else 0.0
    return {"score": score, "total_points": total_points, "percentage": percentage}
