from datetime import datetime

from sqlalchemy import func

from database import LiveRoomEventRecord, QuizAnalyticsRecord, QuizResultRecord, session_scope
from distributed.cache import get_cache, set_cache


class AnalyticsService:
    async def record_counter(self, quiz_id: str, counter: str, increment: int = 1) -> None:
        key = f"analytics:{quiz_id}:counters"
        cached = await get_cache(key) or {}
        cached[counter] = cached.get(counter, 0) + increment
        await set_cache(key, cached, expire=86400)

    async def generate_analytics(self, quiz_id: str) -> dict:
        with session_scope() as session:
            result_stats = (
                session.query(
                    func.count(QuizResultRecord.id),
                    func.avg(QuizResultRecord.score),
                    func.avg(QuizResultRecord.percentage),
                )
                .filter(QuizResultRecord.quiz_id == quiz_id)
                .one()
            )
            events = session.query(LiveRoomEventRecord).filter(LiveRoomEventRecord.quiz_id == quiz_id).all()

            event_counts = {}
            for event in events:
                event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        cache_counts = await get_cache(f"analytics:{quiz_id}:counters") or {}
        players_joined = event_counts.get("player_joined", 0)
        completed_games = event_counts.get("game_end", 0)
        completion_rate = (completed_games / players_joined * 100) if players_joined else 0.0

        snapshot = {
            "quiz_id": quiz_id,
            "total_attempts": int(result_stats[0] or 0),
            "average_score": round(float(result_stats[1] or 0.0), 2),
            "average_percentage": round(float(result_stats[2] or 0.0), 2),
            "completion_rate": round(completion_rate, 2),
            "rooms_created": event_counts.get("room_created", 0),
            "players_joined": players_joined,
            "reconnections": event_counts.get("player_reconnected", 0),
            "answers_submitted": event_counts.get("answer_submitted", 0),
            "timed_out_questions": event_counts.get("question_timeout", 0),
            "completed_games": completed_games,
            "rate_limited_requests": cache_counts.get("rate_limited_requests", 0),
            "generated_at": datetime.utcnow().isoformat(),
        }

        with session_scope() as session:
            record = session.get(QuizAnalyticsRecord, quiz_id)
            if record:
                record.snapshot = snapshot
                record.updated_at = datetime.utcnow()
            else:
                session.add(
                    QuizAnalyticsRecord(
                        quiz_id=quiz_id,
                        snapshot=snapshot,
                        updated_at=datetime.utcnow(),
                    )
                )

        return snapshot


def generate_analytics(quiz_id: str) -> dict:
    import asyncio

    return asyncio.run(AnalyticsService().generate_analytics(quiz_id))
