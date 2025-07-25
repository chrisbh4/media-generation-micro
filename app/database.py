from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Tortoise ORM configuration
TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url,
    },
    "apps": {
        "models": {
            "models": ["app.models.job"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initialize database connection."""
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connections."""
    try:
        await Tortoise.close_connections()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Failed to close database connections: {e}")


def register_database(app: FastAPI):
    """Register Tortoise ORM with FastAPI app."""
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    ) 