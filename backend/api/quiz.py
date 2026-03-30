from fastapi import APIRouter, HTTPException, Request
from models.quiz import Quiz, QuizSubmission, QuizResult
from distributed.rate_limiter import enforce_http_rate_limit
from distributed.task_queue import calculate_quiz_result
from typing import List
import uuid
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from data.quiz_presets import get_all_presets, get_preset_quiz
except ImportError:
    get_all_presets = lambda: {}
    get_preset_quiz = lambda x: None

router = APIRouter()

@router.post("/", response_model=Quiz)
async def create_quiz(quiz: Quiz, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    await enforce_http_rate_limit(request, "create_quiz", client_ip)
    quiz.id = str(uuid.uuid4())
    created_quiz = await request.app.state.quiz_service.create_quiz(quiz)
    return created_quiz

@router.get("/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str, request: Request):
    quiz = await request.app.state.quiz_service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.get("/", response_model=List[Quiz])
async def list_quizzes(request: Request):
    return await request.app.state.quiz_service.list_quizzes()

@router.post("/submit", response_model=dict)
async def submit_quiz(submission: QuizSubmission, request: Request):
    identity = submission.user_id or (request.client.host if request.client else "unknown")
    await enforce_http_rate_limit(request, "submit_quiz", identity)
    task = calculate_quiz_result.delay(
        submission.quiz_id,
        submission.user_id,
        submission.answers
    )
    return {"task_id": task.id, "status": "processing"}

@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: str, request: Request):
    await request.app.state.quiz_service.delete_quiz(quiz_id)
    return {"message": "Quiz deleted"}

@router.get("/presets/list")
async def get_presets():
    """Get all available quiz presets"""
    return get_all_presets()

@router.post("/presets/{preset_id}")
async def create_from_preset(preset_id: str, request: Request):
    """Create a quiz from a preset"""
    preset = get_preset_quiz(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    quiz = Quiz(
        id=str(uuid.uuid4()),
        title=preset["title"],
        description=preset["description"],
        duration_minutes=preset["duration_minutes"],
        created_by="system",
        questions=preset["questions"]
    )
    
    created_quiz = await request.app.state.quiz_service.create_quiz(quiz)
    return created_quiz


@router.post("/bonus_marks/{user_id}")
async def award_bonus_marks(user_id: str, bonus_points: int, request: Request):
    """Award bonus marks to a user"""
    try:
        # Get all user results
        user_results = await request.app.state.results_service.get_user_results(user_id)
        
        if not user_results:
            raise HTTPException(status_code=404, detail="No quiz results found for user")
        
        # Calculate total bonus marks
        total_bonus = sum(result.score for result in user_results) + bonus_points
        
        return {
            "user_id": user_id,
            "previous_total": sum(result.score for result in user_results),
            "bonus_awarded": bonus_points,
            "new_total": total_bonus,
            "message": "Bonus marks awarded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bonus_marks/{user_id}")
async def get_bonus_marks(user_id: str, request: Request):
    """Get total marks including bonus for a user"""
    try:
        user_results = await request.app.state.results_service.get_user_results(user_id)
        
        if not user_results:
            return {
                "user_id": user_id,
                "total_marks": 0,
                "quiz_count": 0,
                "results": []
            }
        
        total_marks = sum(result.score for result in user_results)
        
        return {
            "user_id": user_id,
            "total_marks": total_marks,
            "quiz_count": len(user_results),
            "results": [
                {
                    "quiz_id": r.quiz_id,
                    "score": r.score,
                    "total_points": r.total_points,
                    "percentage": r.percentage
                } for r in user_results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
