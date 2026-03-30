import asyncio
import json
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect

from config import settings
from distributed.cache import publish_message, subscribe_channel
from distributed.rate_limiter import enforce_http_rate_limit, enforce_websocket_rate_limit
from models.live_quiz import AnswerSubmission, JoinRoomRequest, LiveQuizRoom, RoomStatus


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    def add(self, websocket: WebSocket, room_id: str) -> None:
        self.active_connections.setdefault(room_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        if room_id in self.active_connections and websocket in self.active_connections[room_id]:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_events(self, room_id: str, events: List[dict]) -> None:
        for event in events:
            await publish_message(f"room:{room_id}", event)

    async def send_to_local_connections(self, room_id: str, message: dict) -> None:
        if room_id not in self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections[room_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection, room_id)


manager = ConnectionManager()


async def _record_rate_limited_room(request: Request, room_id: str) -> None:
    room = await request.app.state.live_quiz_service.get_room(room_id)
    if room:
        await request.app.state.analytics_service.record_counter(room.quiz_id, "rate_limited_requests")


async def _record_rate_limited_quiz(request: Request, quiz_id: str) -> None:
    await request.app.state.analytics_service.record_counter(quiz_id, "rate_limited_requests")


@router.post("/create", response_model=LiveQuizRoom)
async def create_live_room(quiz_id: str, host_id: str, username: str, max_players: int, request: Request):
    identity = host_id or (request.client.host if request.client else "unknown")
    try:
        await enforce_http_rate_limit(request, "live_create", identity)
    except HTTPException:
        await _record_rate_limited_quiz(request, quiz_id)
        raise

    quiz = await request.app.state.quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail=f"Quiz not found: {quiz_id}")

    room = await request.app.state.live_quiz_service.create_room(quiz_id, host_id, username, max_players)
    return room


@router.post("/join", response_model=LiveQuizRoom)
async def join_live_room(join_request: JoinRoomRequest, request: Request):
    identity = join_request.user_id or (request.client.host if request.client else "unknown")
    try:
        await enforce_http_rate_limit(request, "live_join", identity)
    except HTTPException:
        await _record_rate_limited_room(request, join_request.room_id)
        raise

    room, events = await request.app.state.live_quiz_service.join_room(
        join_request.room_id,
        join_request.user_id,
        join_request.username,
    )
    if not room:
        raise HTTPException(status_code=400, detail="Cannot join room - room not found, full, or already started")

    if events:
        await manager.broadcast_events(join_request.room_id, events)

    return room


@router.post("/ready")
async def set_ready(room_id: str, user_id: str, request: Request):
    identity = user_id or (request.client.host if request.client else "unknown")
    try:
        await enforce_http_rate_limit(request, "live_ready", identity)
    except HTTPException:
        await _record_rate_limited_room(request, room_id)
        raise

    room, events = await request.app.state.live_quiz_service.set_player_ready(room_id, user_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if events:
        await manager.broadcast_events(room_id, events)

    return {"status": "ok", "room": room}


@router.post("/answer")
async def submit_answer(submission: AnswerSubmission, request: Request):
    identity = submission.user_id or (request.client.host if request.client else "unknown")
    try:
        await enforce_http_rate_limit(request, "live_answer", identity, limit=40, window_seconds=10)
    except HTTPException:
        await _record_rate_limited_room(request, submission.room_id)
        raise

    room, events, is_correct = await request.app.state.live_quiz_service.submit_answer(submission)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if events:
        await manager.broadcast_events(submission.room_id, events)

    return {"correct": is_correct, "room": room}


@router.get("/room/{room_id}", response_model=LiveQuizRoom)
async def get_room(room_id: str, request: Request):
    room = await request.app.state.live_quiz_service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await websocket.accept()

    client_ip = websocket.client.host if websocket.client else "unknown"
    await enforce_websocket_rate_limit(
        websocket,
        "live_connect",
        f"{client_ip}:{room_id}:{user_id}",
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    manager.add(websocket, room_id)
    pubsub = await subscribe_channel(f"room:{room_id}")
    last_event_id = int(websocket.query_params.get("last_event_id", "0") or 0)

    async def listen_redis():
        try:
            async for message in pubsub.listen():
                if message and message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await manager.send_to_local_connections(room_id, data)
                    except Exception:
                        continue
        except asyncio.CancelledError:
            pass
        finally:
            try:
                await pubsub.unsubscribe(f"room:{room_id}")
                await pubsub.close()
            except Exception:
                pass

    listener_task = asyncio.create_task(listen_redis())

    try:
        room, presence_events = await websocket.app.state.live_quiz_service.register_connection(room_id, user_id)
        if not room:
            await websocket.send_json({"type": "room_missing", "room_id": room_id})
            return

        replay_events = await websocket.app.state.live_quiz_service.get_replay_events(room_id, last_event_id)

        await websocket.send_json(
            {
                "type": "connected",
                "data": {
                    "room_id": room_id,
                    "user_id": user_id,
                    "room": room.model_dump(mode="json"),
                    "last_event_id": room.last_event_id,
                    "status": room.status.value,
                },
            }
        )

        if presence_events:
            await manager.broadcast_events(room_id, presence_events)

        for event in replay_events:
            await websocket.send_json(event)

        while True:
            data = await websocket.receive_text()
            await enforce_websocket_rate_limit(
                websocket,
                "live_message",
                f"{client_ip}:{room_id}:{user_id}",
                limit=40,
                window_seconds=10,
            )
            message = json.loads(data)
            await publish_message(f"room:{room_id}", message)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, room_id)
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass

        room, events = await websocket.app.state.live_quiz_service.leave_room(room_id, user_id)
        if room is None and not events:
            return

        if events and room and room.status != RoomStatus.EXPIRED:
            await manager.broadcast_events(room_id, events)
