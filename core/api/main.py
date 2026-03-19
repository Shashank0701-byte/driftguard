import logging
from contextlib import asynccontextmanager
from pathlib import Path
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.api.routes import drift, reconcile
from core.config import settings
from core.db.session import AsyncSessionLocal, init_db
from core.scheduler.poller import run_scan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("driftguard")

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialising database...")
    await init_db()

    async def scheduled_scan():
        async with AsyncSessionLocal() as db:
            await run_scan(db)

    scheduler.add_job(
        scheduled_scan,
        "interval",
        seconds=settings.polling_interval,
        id="drift_scan",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started - polling every {settings.polling_interval}s")

    yield

    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="DriftGuard API",
    description="Infrastructure drift detection engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drift.router)
app.include_router(reconcile.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "name": "DriftGuard",
        "version": "1.0.0",
        "docs": "/docs",
    }
