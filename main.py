from fastapi import FastAPI, Depends

from contextlib import asynccontextmanager

from app.scheduler import start_scheduler, stop_scheduler

from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    start_scheduler()

    yield

    stop_scheduler()


app = FastAPI(lifespan=lifespan)


app.include_router(v1_router, prefix="/api/v1")
