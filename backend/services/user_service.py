from datetime import datetime
from typing import Optional

from passlib.context import CryptContext

from database import UserRecord, session_scope
from models.user import User, UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        pass

    async def create_user(self, user_id: str, user_data: UserCreate) -> User:
        created_at = datetime.utcnow()
        with session_scope() as session:
            record = UserRecord(
                id=user_id,
                username=user_data.username,
                email=str(user_data.email),
                full_name=user_data.full_name,
                password_hash=pwd_context.hash(user_data.password),
                created_at=created_at,
            )
            session.add(record)

        return User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            created_at=created_at,
        )

    async def get_user(self, user_id: str) -> Optional[User]:
        with session_scope() as session:
            record = session.get(UserRecord, user_id)
            return self._to_model(record) if record else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        with session_scope() as session:
            record = session.query(UserRecord).filter(UserRecord.username == username).one_or_none()
            return self._to_model(record) if record else None

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        with session_scope() as session:
            record = session.query(UserRecord).filter(UserRecord.username == username).one_or_none()
            if not record or not pwd_context.verify(password, record.password_hash):
                return None
            return self._to_model(record)

    @staticmethod
    def _to_model(record: UserRecord) -> User:
        return User(
            id=record.id,
            username=record.username,
            email=record.email,
            full_name=record.full_name,
            is_admin=record.is_admin,
            created_at=record.created_at,
        )
