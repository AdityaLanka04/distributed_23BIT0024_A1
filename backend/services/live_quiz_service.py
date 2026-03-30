from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from config import settings
from database import LiveRoomEventRecord, LiveRoomRecord, session_scope
from distributed.cache import delete_cache, get_cache, redis_lock, set_cache
from models.live_quiz import AnswerSubmission, LiveQuizRoom, PlayerStatus, RoomStatus
from models.quiz import QuizResult
from services.analytics_service import AnalyticsService
from services.quiz_service import QuizService
from services.results_service import ResultsService


class LiveQuizService:
    def __init__(
        self,
        quiz_service: Optional[QuizService] = None,
        results_service: Optional[ResultsService] = None,
        analytics_service: Optional[AnalyticsService] = None,
    ):
        self.quiz_service = quiz_service or QuizService()
        self.results_service = results_service or ResultsService()
        self.analytics_service = analytics_service or AnalyticsService()

    async def create_room(
        self,
        quiz_id: str,
        host_id: str,
        username: str,
        max_players: int = 5,
    ) -> LiveQuizRoom:
        now = datetime.utcnow()
        room_id = str(uuid.uuid4())[:8]
        room = LiveQuizRoom(
            room_id=room_id,
            quiz_id=quiz_id,
            host_id=host_id,
            max_players=max(2, min(max_players, settings.live_max_players)),
            players=[
                PlayerStatus(
                    user_id=host_id,
                    username=username,
                    joined_at=now,
                    is_ready=True,
                    connected=True,
                    last_active_at=now,
                )
            ],
            created_at=now,
            expires_at=now + timedelta(seconds=settings.room_ttl_seconds),
            version=1,
            question_time_limit=settings.live_question_seconds,
            last_activity_at=now,
        )

        await self._commit_room(
            room,
            [
                {
                    "type": "room_created",
                    "data": {
                        "host_id": host_id,
                        "username": username,
                        "max_players": room.max_players,
                    },
                }
            ],
        )
        await set_cache(f"user_room:{host_id}", room_id, expire=settings.room_ttl_seconds)
        self._schedule_room_expiry(room)
        return room

    async def join_room(self, room_id: str, user_id: str, username: str) -> tuple[Optional[LiveQuizRoom], List[dict]]:
        async with redis_lock(f"room:{room_id}"):
            room = await self._load_room(room_id)
            if not room:
                return None, []

            now = datetime.utcnow()
            existing = next((player for player in room.players if player.user_id == user_id), None)
            events = []

            if existing:
                was_connected = existing.connected
                existing.username = username
                existing.connected = True
                existing.last_active_at = now
                if not was_connected:
                    events.append(
                        {
                            "type": "player_reconnected",
                            "data": {"user_id": user_id, "username": username},
                        }
                    )
            else:
                if room.status != RoomStatus.WAITING:
                    return None, []

                if len(room.players) >= room.max_players:
                    return None, []

                room.players.append(
                    PlayerStatus(
                        user_id=user_id,
                        username=username,
                        joined_at=now,
                        connected=True,
                        last_active_at=now,
                    )
                )
                events.append(
                    {
                        "type": "player_joined",
                        "data": {
                            "user_id": user_id,
                            "username": username,
                            "player_count": len(room.players),
                        },
                    }
                )

            room.version += 1
            room.last_activity_at = now
            room.expires_at = now + timedelta(seconds=settings.room_ttl_seconds)
            events = await self._commit_room(room, events)

        await set_cache(f"user_room:{user_id}", room_id, expire=settings.room_ttl_seconds)
        return room, events

    async def register_connection(self, room_id: str, user_id: str) -> tuple[Optional[LiveQuizRoom], List[dict]]:
        async with redis_lock(f"room:{room_id}"):
            room = await self._load_room(room_id)
            if not room:
                return None, []

            now = datetime.utcnow()
            events = []
            for player in room.players:
                if player.user_id == user_id:
                    if not player.connected:
                        events.append(
                            {
                                "type": "player_reconnected",
                                "data": {"user_id": user_id, "username": player.username},
                            }
                        )
                    player.connected = True
                    player.last_active_at = now
                    room.version += 1
                    room.last_activity_at = now
                    events = await self._commit_room(room, events)
                    return room, events

            return room, []

    async def set_player_ready(self, room_id: str, user_id: str) -> tuple[Optional[LiveQuizRoom], List[dict]]:
        schedule_timeout = False
        async with redis_lock(f"room:{room_id}"):
            room = await self._load_room(room_id)
            if not room:
                return None, []

            now = datetime.utcnow()
            player = next((player for player in room.players if player.user_id == user_id), None)
            if not player:
                return None, []

            player.is_ready = True
            player.connected = True
            player.last_active_at = now
            room.version += 1
            room.last_activity_at = now

            events = [
                {
                    "type": "player_ready",
                    "data": {"user_id": user_id, "status": room.status.value},
                }
            ]

            if room.status == RoomStatus.WAITING and len(room.players) >= 2 and all(p.is_ready for p in room.players):
                room.status = RoomStatus.IN_PROGRESS
                room.started_at = now
                room.current_question_started_at = now
                room.question_deadline_at = now + timedelta(seconds=room.question_time_limit)
                events[0]["data"]["status"] = room.status.value
                events.append(
                    {
                        "type": "game_start",
                        "data": {
                            "question_index": room.current_question_index,
                            "deadline_at": room.question_deadline_at.isoformat(),
                        },
                    }
                )
                schedule_timeout = True

            events = await self._commit_room(room, events)

        if schedule_timeout:
            self._schedule_question_timeout(room)
        return room, events

    async def submit_answer(self, submission: AnswerSubmission) -> tuple[Optional[LiveQuizRoom], List[dict], bool]:
        room = await self.get_room(submission.room_id)
        if not room:
            return None, [], False

        quiz = await self.quiz_service.get_quiz(room.quiz_id)
        if not quiz or submission.question_index >= len(quiz.questions):
            return None, [], False

        question = quiz.questions[submission.question_index]
        is_correct = question.correct_answer == submission.answer
        schedule_timeout = False
        finalize_results = False

        async with redis_lock(f"room:{submission.room_id}"):
            room = await self._load_room(submission.room_id)
            if not room or room.status != RoomStatus.IN_PROGRESS:
                return room, [], is_correct

            if submission.question_index != room.current_question_index:
                return room, [], is_correct

            player = next((player for player in room.players if player.user_id == submission.user_id), None)
            if not player:
                return room, [], is_correct

            if submission.question_index in player.answered_questions:
                return room, [], is_correct

            now = datetime.utcnow()
            player.answered_questions.append(submission.question_index)
            player.current_question = submission.question_index + 1
            player.connected = True
            player.last_active_at = now

            if is_correct:
                time_bonus = max(0, 1000 - int(submission.time_taken * 100))
                player.score += question.points * 100 + time_bonus

            room.version += 1
            room.last_activity_at = now

            events = [
                {
                    "type": "answer_submitted",
                    "data": {
                        "user_id": submission.user_id,
                        "is_correct": is_correct,
                        "players": [p.model_dump(mode="json") for p in room.players],
                    },
                }
            ]

            all_answered = all(submission.question_index in p.answered_questions for p in room.players)
            is_last_question = submission.question_index >= len(quiz.questions) - 1

            if all_answered and is_last_question:
                room.status = RoomStatus.FINISHED
                room.question_deadline_at = None
                room.players.sort(key=lambda p: p.score, reverse=True)
                finalize_results = True
                events.append(
                    {
                        "type": "game_end",
                        "data": {"players": [p.model_dump(mode="json") for p in room.players]},
                    }
                )
            elif all_answered:
                room.current_question_index += 1
                room.current_question_started_at = now
                room.question_deadline_at = now + timedelta(seconds=room.question_time_limit)
                schedule_timeout = True
                events.append(
                    {
                        "type": "next_question",
                        "data": {
                            "question_index": room.current_question_index,
                            "deadline_at": room.question_deadline_at.isoformat(),
                        },
                    }
                )

            events = await self._commit_room(room, events)

        if finalize_results:
            await self._persist_results(room, quiz)
            self._schedule_analytics(quiz.id)
        elif schedule_timeout:
            self._schedule_question_timeout(room)

        return room, events, is_correct

    async def handle_question_timeout(self, room_id: str, question_index: int) -> tuple[Optional[LiveQuizRoom], List[dict]]:
        schedule_timeout = False
        finalize_results = False
        quiz = None

        async with redis_lock(f"room:{room_id}"):
            room = await self._load_room(room_id)
            if not room or room.status != RoomStatus.IN_PROGRESS:
                return room, []

            if room.current_question_index != question_index:
                return room, []

            if room.question_deadline_at and datetime.utcnow() < room.question_deadline_at:
                return room, []

            quiz = await self.quiz_service.get_quiz(room.quiz_id)
            if not quiz:
                return room, []

            now = datetime.utcnow()
            for player in room.players:
                if question_index not in player.answered_questions:
                    player.answered_questions.append(question_index)
                    player.current_question = question_index + 1
                    player.last_active_at = now

            room.version += 1
            room.last_activity_at = now

            events = [
                {
                    "type": "question_timeout",
                    "data": {
                        "question_index": question_index,
                        "players": [p.model_dump(mode="json") for p in room.players],
                    },
                }
            ]

            is_last_question = question_index >= len(quiz.questions) - 1
            if is_last_question:
                room.status = RoomStatus.FINISHED
                room.question_deadline_at = None
                room.players.sort(key=lambda p: p.score, reverse=True)
                finalize_results = True
                events.append(
                    {
                        "type": "game_end",
                        "data": {"players": [p.model_dump(mode="json") for p in room.players]},
                    }
                )
            else:
                room.current_question_index += 1
                room.current_question_started_at = now
                room.question_deadline_at = now + timedelta(seconds=room.question_time_limit)
                schedule_timeout = True
                events.append(
                    {
                        "type": "next_question",
                        "data": {
                            "question_index": room.current_question_index,
                            "deadline_at": room.question_deadline_at.isoformat(),
                        },
                    }
                )

            events = await self._commit_room(room, events)

        if finalize_results and quiz:
            await self._persist_results(room, quiz)
            self._schedule_analytics(quiz.id)
        elif schedule_timeout:
            self._schedule_question_timeout(room)

        return room, events

    async def expire_room(self, room_id: str) -> tuple[Optional[LiveQuizRoom], List[dict]]:
        async with redis_lock(f"room:{room_id}"):
            room = await self._load_room(room_id)
            if not room:
                return None, []

            if room.status in {RoomStatus.FINISHED, RoomStatus.EXPIRED}:
                return room, []

            if room.expires_at and datetime.utcnow() < room.expires_at:
                return room, []

            room.status = RoomStatus.EXPIRED
            room.version += 1
            room.question_deadline_at = None
            room.last_activity_at = datetime.utcnow()
            events = [{"type": "room_expired", "data": {"room_id": room.room_id}}]
            events = await self._commit_room(room, events, expire_seconds=300)
            return room, events

    async def get_room(self, room_id: str) -> Optional[LiveQuizRoom]:
        return await self._load_room(room_id)

    async def leave_room(self, room_id: str, user_id: str) -> tuple[Optional[LiveQuizRoom], List[dict]]:
        async with redis_lock(f"room:{room_id}"):
            room = await self._load_room(room_id)
            if not room:
                return None, []

            now = datetime.utcnow()
            events = []

            if room.status == RoomStatus.WAITING:
                before_count = len(room.players)
                room.players = [player for player in room.players if player.user_id != user_id]
                await delete_cache(f"user_room:{user_id}")

                if before_count == len(room.players):
                    return room, []

                room.version += 1
                room.last_activity_at = now
                events.append({"type": "player_left", "data": {"user_id": user_id}})

                if room.players and room.host_id == user_id:
                    room.host_id = room.players[0].user_id
                    events.append({"type": "host_changed", "data": {"host_id": room.host_id}})

                if not room.players:
                    await self._delete_room(room.room_id)
                    return None, events

                events = await self._commit_room(room, events)
                return room, events

            for player in room.players:
                if player.user_id == user_id:
                    player.connected = False
                    player.last_active_at = now
                    room.version += 1
                    room.last_activity_at = now
                    events.append({"type": "player_left", "data": {"user_id": user_id}})
                    events = await self._commit_room(room, events)
                    return room, events

            return room, []

    async def get_replay_events(self, room_id: str, last_event_id: int = 0, limit: Optional[int] = None) -> List[dict]:
        limit = limit or settings.room_event_replay_limit
        with session_scope() as session:
            records = (
                session.query(LiveRoomEventRecord)
                .filter(
                    LiveRoomEventRecord.room_id == room_id,
                    LiveRoomEventRecord.id > last_event_id,
                )
                .order_by(LiveRoomEventRecord.id.asc())
                .limit(limit)
                .all()
            )

        replay_events = []
        for record in records:
            payload = dict(record.payload)
            payload["event_id"] = record.id
            payload["created_at"] = record.created_at.isoformat()
            replay_events.append(payload)
        return replay_events

    async def _load_room(self, room_id: str) -> Optional[LiveQuizRoom]:
        room_data = await get_cache(f"room:{room_id}")
        if room_data:
            return LiveQuizRoom(**room_data)

        with session_scope() as session:
            record = session.get(LiveRoomRecord, room_id)
            if not record:
                return None
            room = LiveQuizRoom(**record.snapshot)

        expire_seconds = self._cache_expiry(room)
        await set_cache(f"room:{room_id}", room.model_dump(mode="json"), expire=expire_seconds)
        return room

    async def _commit_room(
        self,
        room: LiveQuizRoom,
        events: List[dict],
        expire_seconds: Optional[int] = None,
    ) -> List[dict]:
        now = datetime.utcnow()
        expire_seconds = expire_seconds or self._cache_expiry(room)
        stored_events = []

        with session_scope() as session:
            record = session.get(LiveRoomRecord, room.room_id)
            if not record:
                record = LiveRoomRecord(
                    room_id=room.room_id,
                    quiz_id=room.quiz_id,
                    host_id=room.host_id,
                    status=room.status.value,
                    version=room.version,
                    last_event_id=room.last_event_id,
                    snapshot=room.model_dump(mode="json"),
                    created_at=room.created_at,
                    updated_at=now,
                    expires_at=room.expires_at,
                )
                session.add(record)

            for event in events:
                payload = {
                    "type": event["type"],
                    "room_id": room.room_id,
                    "data": event.get("data", {}),
                }
                event_record = LiveRoomEventRecord(
                    room_id=room.room_id,
                    quiz_id=room.quiz_id,
                    event_type=event["type"],
                    payload=payload,
                    created_at=now,
                )
                session.add(event_record)
                session.flush()
                payload["event_id"] = event_record.id
                payload["created_at"] = now.isoformat()
                stored_events.append(payload)
                room.last_event_id = event_record.id

            record.quiz_id = room.quiz_id
            record.host_id = room.host_id
            record.status = room.status.value
            record.version = room.version
            record.last_event_id = room.last_event_id
            record.snapshot = room.model_dump(mode="json")
            record.updated_at = now
            record.expires_at = room.expires_at

        await set_cache(f"room:{room.room_id}", room.model_dump(mode="json"), expire=expire_seconds)
        return stored_events

    async def _delete_room(self, room_id: str) -> None:
        with session_scope() as session:
            record = session.get(LiveRoomRecord, room_id)
            if record:
                session.delete(record)
        await delete_cache(f"room:{room_id}")

    async def _persist_results(self, room: LiveQuizRoom, quiz) -> None:
        total_points = sum(question.points * 100 + 1000 for question in quiz.questions)
        for player in room.players:
            percentage = (player.score / total_points * 100) if total_points else 0.0
            await self.results_service.save_result(
                QuizResult(
                    quiz_id=room.quiz_id,
                    user_id=player.user_id,
                    score=player.score,
                    total_points=total_points,
                    percentage=round(percentage, 2),
                    completed_at=datetime.utcnow(),
                )
            )

    def _schedule_room_expiry(self, room: LiveQuizRoom) -> None:
        from distributed.task_queue import expire_live_room

        countdown = max((room.expires_at - datetime.utcnow()).total_seconds(), 1)
        expire_live_room.apply_async(args=[room.room_id], countdown=int(countdown))

    def _schedule_question_timeout(self, room: LiveQuizRoom) -> None:
        from distributed.task_queue import process_question_timeout

        if not room.question_deadline_at:
            return

        countdown = max((room.question_deadline_at - datetime.utcnow()).total_seconds(), 1)
        process_question_timeout.apply_async(
            args=[room.room_id, room.current_question_index],
            countdown=int(countdown),
        )

    def _schedule_analytics(self, quiz_id: str) -> None:
        from distributed.task_queue import generate_quiz_analytics

        generate_quiz_analytics.delay(quiz_id)

    @staticmethod
    def _cache_expiry(room: LiveQuizRoom) -> int:
        if room.expires_at:
            remaining = int((room.expires_at - datetime.utcnow()).total_seconds())
            if remaining > 0:
                return remaining
        return settings.room_ttl_seconds
