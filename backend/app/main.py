"""FastAPI application entry point."""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import chat as chat_router
from app.api import graph as graph_router
from app.api import index as index_router
from app.config import settings
from app.database import check_db_connection, ensure_database_schema
from app.services.graphrag import graphrag_service

# Configure logging
log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance.
    """
    # Startup
    logger.info("Starting MythologyGraphRAG application...")
    logger.info(
        f"Model providers configured - "
        f"Index: {settings.get_index_provider()}, "
        f"Query: {settings.get_query_provider()}"
    )

    # Check database connection
    db_ok = await check_db_connection()
    if not db_ok:
        logger.error("Failed to connect to database")
    else:
        logger.info("Database connection established")
        await ensure_database_schema()

    # Check model provider connection
    try:
        provider_ok = await graphrag_service.check_provider_health()
        if provider_ok:
            provider = settings.get_query_provider()
            logger.info(f"{provider.capitalize()} connection established")
            models = await graphrag_service.verify_models()
            logger.info(f"Models available: {models}")
    except Exception as e:
        logger.warning(f"Model provider connection check failed: {e}")
        logger.warning("GraphRAG features will be unavailable")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="MythologyGraphRAG API",
    description="Educational GraphRAG application for mythology knowledge graphs",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests with timing information.

    Args:
        request: Incoming request.
        call_next: Next middleware in chain.

    Returns:
        Response from the next middleware.
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Duration: {duration:.3f}s"
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.

    Args:
        request: Incoming request.
        exc: Exception raised.

    Returns:
        JSON error response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if not settings.debug else str(exc),
        },
    )


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Args:
        request: Incoming request.
        exc: Validation error.

    Returns:
        JSON error response with validation details.
    """
    logger.warning(f"Validation error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "details": exc.errors()},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status information.
    """
    db_ok = await check_db_connection()

    provider = settings.get_query_provider()
    provider_ok = False
    try:
        provider_ok = await graphrag_service.check_provider_health()
    except Exception:
        pass

    return {
        "status": "healthy" if (db_ok and provider_ok) else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "model_provider": provider,
        "model_provider_status": "connected" if provider_ok else "disconnected",
    }


# Register API routers
app.include_router(chat_router.router, prefix="/api/chat", tags=["Chat"])
app.include_router(graph_router.router, prefix="/api/graph", tags=["Graph"])
app.include_router(index_router.router, prefix="/api/index", tags=["Index"])

# Serve frontend SPA
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    logger.info(f"Serving frontend from {frontend_dist}")
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SPA for all non-API routes."""
        if (
            full_path.startswith("api/")
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("files/")
        ):
            raise HTTPException(status_code=404, detail="Not found")

        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)

        raise HTTPException(status_code=404, detail="Frontend not found")
else:
    logger.warning(f"Frontend dist directory not found at {frontend_dist}")
