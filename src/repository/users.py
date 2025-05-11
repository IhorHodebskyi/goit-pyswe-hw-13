from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.user import UserShema
from src.repository.auth import get_user_by_email


async def update_avatar(email: str, url: str | None, db: AsyncSession = Depends(get_db)) -> UserShema:
    user = await get_user_by_email(email=email, db=db)
    user.avatar = url
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
