from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class RoomStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    EXPIRED = "expired"

class PlayerStatus(BaseModel):
    user_id: str
    username: str
    score: int = 0
    current_question: int = 0
    is_ready: bool = False
    joined_at: datetime
    connected: bool = True
    last_active_at: Optional[datetime] = None
    answered_questions: List[int] = Field(default_factory=list)

class LiveQuizRoom(BaseModel):
    room_id: str
    quiz_id: str
    host_id: str
    max_players: int = 5
    players: List[PlayerStatus] = Field(default_factory=list)
    status: RoomStatus = RoomStatus.WAITING
    current_question_index: int = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    current_question_started_at: Optional[datetime] = None
    question_deadline_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    version: int = 0
    last_event_id: int = 0
    question_time_limit: int = 15
    last_activity_at: Optional[datetime] = None

class JoinRoomRequest(BaseModel):
    room_id: str
    user_id: str
    username: str

class AnswerSubmission(BaseModel):
    room_id: str
    user_id: str
    question_index: int
    answer: int
    time_taken: float

class LiveQuizUpdate(BaseModel):
    type: str
    room_id: str
    data: Dict
    event_id: Optional[int] = None
    created_at: Optional[datetime] = None
