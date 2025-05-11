from typing import Callable
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
import re
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse, HTMLResponse
from src.database.db import get_db
from src.middleware.middleware import CustomMiddleware
from src.routes import contacts, birthdays, auth, email_tracker, users
from dotenv import load_dotenv
from src.conf.config import config
import logging

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
        decode_responses=True
    )
    await FastAPILimiter.init(redis_client)

    yield

    await redis_client.close()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_agent_ban_list = [r"Python-urllib", r"python-requests", r"bot", r"spider"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


app.add_middleware(CustomMiddleware)

app.include_router(auth.router, prefix="/api", tags=["auth"])

app.include_router(email_tracker.router, prefix="/api", tags=["email_tracking"])

app.include_router(users.router, prefix="/api", tags=["users"])

app.include_router(contacts.router, prefix="/api", tags=["contacts"])

app.include_router(birthdays.router, prefix="/api", tags=["birthdays"])

templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def root(requests: Request):
    return templates.TemplateResponse("index.html", {"request": requests})


@app.get("/healthchecker", status_code=status.HTTP_200_OK)
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await (db.execute(text("SELECT 1")))
        result = result.fetchone()
        if result is None:
            raise Exception()
        return {"message": "Welcome to FastAPI!"}

    except Exception:
        raise HTTPException(status_code=500, detail="Database is not configured.")
