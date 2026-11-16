from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import oauth2_scheme, decode_access_token
from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)

    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")

    if not isinstance(user_id, str) or not user_id.isdigit():
        raise credentials_exception

    repository = UserRepository(session)

    user = await repository.get_user_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    return user
