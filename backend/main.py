from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import quiz, user, results, live_quiz
from config import settings
from database import init_db
from distributed.cache import init_redis
from distributed.task_queue import init_celery
from services.analytics_service import AnalyticsService
from services.quiz_service import QuizService
from services.live_quiz_service import LiveQuizService
from services.results_service import ResultsService
from services.user_service import UserService

app = FastAPI(title="Distributed Quiz Management System")


app.state.quiz_service = QuizService()
app.state.user_service = UserService()
app.state.results_service = ResultsService()
app.state.analytics_service = AnalyticsService()
app.state.live_quiz_service = LiveQuizService(
    quiz_service=app.state.quiz_service,
    results_service=app.state.results_service,
    analytics_service=app.state.analytics_service,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(results.router, prefix="/api/results", tags=["results"])
app.include_router(live_quiz.router, prefix="/api/live", tags=["live-quiz"])

@app.on_event("startup")
async def startup():
    init_db()
    await init_redis()
    init_celery()

@app.get("/")
def root():
    return {"message": "Distributed Quiz Management System API"}

@app.get("/health")
def health():
    return {"status": "healthy"}
