from fastapi import APIRouter, HTTPException, Request
from models.user import User, UserCreate, UserLogin
from config import settings
from distributed.rate_limiter import enforce_http_rate_limit
import uuid

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user: UserCreate, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    await enforce_http_rate_limit(
        request,
        "register",
        client_ip,
        limit=settings.auth_rate_limit_requests,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )

    existing = await request.app.state.user_service.get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = str(uuid.uuid4())
    new_user = await request.app.state.user_service.create_user(user_id, user)
    return new_user

@router.post("/login")
async def login(credentials: UserLogin, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    await enforce_http_rate_limit(
        request,
        "login",
        client_ip,
        limit=settings.auth_rate_limit_requests,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )

    user = await request.app.state.user_service.authenticate(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user": user, "token": "jwt_token_here"}

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, request: Request):
    user = await request.app.state.user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
