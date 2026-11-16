import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.scheduler import start_scheduler, stop_scheduler
from app.api.v1.router import router as v1_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):

    start_scheduler()

    yield

    stop_scheduler()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(v1_router, prefix="/api/v1")
