from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.user import UserShema


async def update_avatar(user: UserShema, url: str | None, db: AsyncSession = Depends(get_db)) -> UserShema:
    user.avatar = url
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
