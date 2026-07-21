"""
Entry point for the Managed Container Service FastAPI backend.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.routes import chat
from app.core.config import settings
from app.db.session import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    logger.info("Initializing application...")
    await init_db()
    logger.info("Database connection initialized.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="Managed Container Service API",
    description="Backend API for chat-based LLM interaction.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request timing for Azure Monitor."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
    return response


# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint for Azure App Service."""
    return {"status": "healthy", "service": "chat-api"}


# OpenTelemetry instrumentation for Azure Monitor
FastAPIInstrumentor.instrument_app(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)