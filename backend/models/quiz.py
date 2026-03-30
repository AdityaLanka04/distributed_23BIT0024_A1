from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Question(BaseModel):
    id: Optional[str] = None
    question_text: str
    options: List[str]
    correct_answer: int
    points: int = 1

class Quiz(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    questions: List[Question]
    duration_minutes: int
    created_by: str
    created_at: Optional[datetime] = None
    is_active: bool = True

class QuizSubmission(BaseModel):
    quiz_id: str
    user_id: str
    answers: List[int]
    submitted_at: Optional[datetime] = None

class QuizResult(BaseModel):
    quiz_id: str
    user_id: str
    score: int
    total_points: int
    percentage: float
    completed_at: datetime
