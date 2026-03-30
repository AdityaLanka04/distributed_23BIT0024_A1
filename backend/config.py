from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    database_url: str = "postgresql://user:password@postgres/quizdb"
    secret_key: str = "your-secret-key-change-in-production"
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
    )
    room_ttl_seconds: int = 7200
    room_lock_timeout_seconds: int = 10
    room_lock_wait_seconds: int = 5
    room_event_replay_limit: int = 100
    live_question_seconds: int = 15
    live_max_players: int = 25
    rate_limit_window_seconds: int = 10
    rate_limit_requests: int = 25
    auth_rate_limit_window_seconds: int = 60
    auth_rate_limit_requests: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


settings = Settings()
