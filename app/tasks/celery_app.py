from celery import Celery
from app.config import settings
import asyncio


def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    celery_app = Celery(
        "media_generation",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.tasks.media_tasks"]
    )
    
    # Celery configuration
    celery_app.conf.update(
        # Task routing
        task_routes={
            "app.tasks.media_tasks.generate_media_task": {"queue": "media_generation"},
        },
        
        # Task execution
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        
        # Result backend settings
        result_expires=3600,  # 1 hour
        
        # Worker settings
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        
        # Retry settings
        task_retry_delay=60,  # 1 minute
        task_max_retries=3,
        
        # Beat scheduler settings (if needed)
        beat_schedule={},
    )
    
    return celery_app


# Global Celery instance
celery_app = create_celery_app()


# Event loop setup for async tasks
def get_event_loop():
    """Get or create event loop for async operations."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop 