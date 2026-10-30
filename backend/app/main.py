import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables
from app.modules.auth.router import router as auth_router
from app.modules.tests.router import router as test_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxam_ai")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    create_db_and_tables()
    logger.info("Database tables initialized.")
    yield


app = FastAPI(
    title="Proxam AI API",
    description="Online examination platform with AI-assisted browser proctoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(test_router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "Proxam AI API",
        "version": "1.0.0",
    }
