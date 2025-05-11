from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from src.database.db import get_db
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/amail_tracking", tags=["email_tracking"])


@router.get("/{username}", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def email_tracker(username: str, response: Response, db: Session = Depends(get_db)):
    logger.info(f"email_tracker {username}")
    return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")
