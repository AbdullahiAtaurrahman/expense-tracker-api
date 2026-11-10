from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> User:
        existing_user = await self.repository.get_user_by_email(user_data.email)

        if existing_user:
            raise ValueError("Email already registered")

        hashed_password = hash_password(user_data.password)

        return await self.repository.create_user(
            email=user_data.email,
            hashed_password=hashed_password,
        )
