from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    ApexTrackException,
    apextrack_exception_handler,
    global_unhandled_exception_handler,
)
from app.core.logging import logger, setup_logging


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm ML model on startup to avoid request-time latency and cold-start timeouts
    try:
        from app.ml.model_loader import HFModelLoader
        if HFModelLoader.is_configured():
            logger.info("Lifespan: Pre-warming Hugging Face model on startup...")
            HFModelLoader.load_model_and_processor()
            logger.info("Lifespan: Model successfully pre-warmed and ready for inference.")
    except Exception as e:
        logger.warning(f"Lifespan: Model pre-warming deferred: {str(e)}")
    yield


def create_application() -> FastAPI:
    """
    Application factory initializing FastAPI, CORS, Exception Handlers, and Routers.
    """
    # Setup structured logging
    setup_logging()
    logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION} ({settings.APP_ENV})")

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS robustly for production and local development
    origins = settings.ALLOWED_ORIGINS
    if isinstance(origins, list) and ("*" in origins or not origins):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Register Exception Handlers
    app.add_exception_handler(ApexTrackException, apextrack_exception_handler)
    app.add_exception_handler(Exception, global_unhandled_exception_handler)

    # Register Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
