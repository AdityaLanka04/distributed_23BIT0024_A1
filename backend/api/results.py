from fastapi import APIRouter, Request
from models.quiz import QuizResult
from distributed.cache import get_leaderboard
from typing import List

router = APIRouter()

@router.get("/user/{user_id}", response_model=List[QuizResult])
async def get_user_results(user_id: str, request: Request):
    return await request.app.state.results_service.get_user_results(user_id)

@router.get("/quiz/{quiz_id}", response_model=List[QuizResult])
async def get_quiz_results(quiz_id: str, request: Request):
    return await request.app.state.results_service.get_quiz_results(quiz_id)

@router.get("/leaderboard/{quiz_id}")
async def get_quiz_leaderboard(quiz_id: str, limit: int = 10):
    leaderboard = await get_leaderboard(quiz_id, limit)
    return {"quiz_id": quiz_id, "leaderboard": leaderboard}

@router.get("/analytics/{quiz_id}")
async def get_quiz_analytics(quiz_id: str, request: Request):
    analytics = await request.app.state.analytics_service.generate_analytics(quiz_id)
    return analytics
