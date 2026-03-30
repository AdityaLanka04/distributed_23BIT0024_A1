from celery import Celery
from datetime import datetime
from typing import List
import asyncio

from config import settings
from models.quiz import QuizResult

celery_app = Celery(
    "quiz_tasks",
    broker=settings.celery_broker,
    backend=settings.celery_backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

def init_celery():
    return celery_app

@celery_app.task(name="calculate_quiz_result")
def calculate_quiz_result(quiz_id: str, user_id: str, answers: List[int]):
    from services.quiz_service import calculate_score
    from services.results_service import ResultsService

    result_data = calculate_score(quiz_id, answers)
    result = QuizResult(
        quiz_id=quiz_id,
        user_id=user_id,
        score=result_data["score"],
        total_points=result_data["total_points"],
        percentage=result_data["percentage"],
        completed_at=datetime.utcnow(),
    )
    asyncio.run(ResultsService().save_result(result))
    generate_quiz_analytics.delay(quiz_id)
    return result.model_dump(mode="json")

@celery_app.task(name="send_quiz_notification")
def send_quiz_notification(user_id: str, quiz_id: str, message: str):
    print(f"Notification to {user_id}: {message}")
    return {"status": "sent", "user_id": user_id}

@celery_app.task(name="generate_quiz_analytics")
def generate_quiz_analytics(quiz_id: str):
    from services.analytics_service import generate_analytics
    return generate_analytics(quiz_id)


async def _broadcast_events(room_id: str, events: List[dict]) -> None:
    from distributed.cache import publish_message

    for event in events:
        await publish_message(f"room:{room_id}", event)


@celery_app.task(name="expire_live_room")
def expire_live_room(room_id: str):
    from services.live_quiz_service import LiveQuizService

    room, events = asyncio.run(LiveQuizService().expire_room(room_id))
    if events:
        asyncio.run(_broadcast_events(room_id, events))
    return {"room_id": room_id, "expired": bool(room and room.status == "expired")}


@celery_app.task(name="process_question_timeout")
def process_question_timeout(room_id: str, question_index: int):
    from services.live_quiz_service import LiveQuizService

    room, events = asyncio.run(LiveQuizService().handle_question_timeout(room_id, question_index))
    if events:
        asyncio.run(_broadcast_events(room_id, events))
    return {
        "room_id": room_id,
        "question_index": question_index,
        "processed": bool(events),
        "status": room.status if room else None,
    }
