"""
DocuMind AI — FastAPI Application Entry Point
Configures the application, middleware, error handlers, and startup events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging

# Initialize logging first — before any other imports that might log
setup_logging()
logger = get_logger(__name__)


# ---- Lifespan (startup / shutdown) ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Log startup banner.
    - Attempt to initialize database tables (development only).
      Failure is non-fatal so the health endpoint keeps working.

    Shutdown:
    - Dispose database connections.
    """
    logger.info("=" * 60)
    logger.info("DocuMind AI Backend starting up")
    logger.info("Environment: %s", settings.app_env)
    logger.info("API prefix: %s/v1", settings.api_prefix)
    logger.info("=" * 60)

    # Attempt database table creation in development
    # In production, use Alembic migrations instead
    if settings.is_development:
        try:
            from app.database.base import create_tables
            await create_tables()
            logger.info("Database tables ready.")
        except Exception as exc:
            logger.warning(
                "Database initialization skipped (is PostgreSQL running?): %s", str(exc)
            )
            logger.warning("Health endpoint will still work without a database connection.")

    yield

    logger.info("DocuMind AI Backend shutting down.")
    try:
        from app.database.base import engine
        await engine.dispose()
        logger.info("Database connections closed.")
    except Exception:
        pass


# ---- Application factory ----

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.
    Using a factory function makes it easy to create test instances.
    """
    app = FastAPI(
        title="DocuMind AI",
        description=(
            "Enterprise AI Knowledge Assistant using Retrieval-Augmented Generation (RAG) "
            "for Intelligent Document Retrieval and Question Answering.\n\n"
            "**Phase 1** — Foundation. RAG components are stubs; "
            "connect Pinecone + LLM in Phase 2."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Routers ----
    app.include_router(api_router, prefix=f"{settings.api_prefix}")

    # ---- Global error handlers ----

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error": "NOT_FOUND",
                "message": f"The requested resource was not found: {request.url.path}",
            },
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc) -> JSONResponse:
        logger.error("Unhandled server error on %s: %s", request.url.path, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again or contact support.",
            },
        )

    logger.info("FastAPI application configured successfully.")
    return app


# ---- Application instance ----
app = create_app()
