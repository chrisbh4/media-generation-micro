from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from app.config import settings
from app.database import register_database, init_db, close_db
from app.routers.media import router as media_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Media Generation API")
    await init_db()
    
    # Create storage directory if using local storage
    if settings.storage_type == "local":
        storage_path = Path(settings.local_storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage directory created: {storage_path}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Media Generation API")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Media Generation API",
        description="Asynchronous media generation microservice using Replicate API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register database
    register_database(app)
    
    # Include routers
    app.include_router(media_router)
    
    # Mount static files for local media serving
    if settings.storage_type == "local":
        media_path = Path(settings.local_storage_path)
        if media_path.exists():
            app.mount("/media", StaticFiles(directory=str(media_path)), name="media")
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception on {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "path": str(request.url),
                "method": request.method
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Media Generation API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health"
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    ) 