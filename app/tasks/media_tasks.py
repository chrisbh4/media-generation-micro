import asyncio
import logging
from typing import Dict, Any
import uuid
from celery import current_task
from celery.exceptions import Retry

from app.tasks.celery_app import celery_app, get_event_loop
from app.services.job_service import JobService
from app.services.media_service import MediaService
from app.services.storage_service import StorageService
from app.models.job import JobStatus
from app.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
media_service = MediaService()
storage_service = StorageService()


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def generate_media_task(self, job_id_str: str):
    """
    Async task for generating media using Replicate API.
    
    Args:
        job_id_str: String representation of job UUID
    """
    job_id = uuid.UUID(job_id_str)
    loop = get_event_loop()
    
    try:
        # Run async media generation
        return loop.run_until_complete(_process_media_generation(job_id, self))
    except Exception as exc:
        logger.error(f"Task failed for job {job_id}: {exc}")
        
        # Mark job as failed in database
        loop.run_until_complete(_handle_task_failure(job_id, str(exc)))
        
        # Retry if retries are available
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id}, attempt {self.request.retries + 1}")
            raise self.retry(exc=exc, countdown=settings.retry_delay * (settings.exponential_backoff_base ** self.request.retries))
        
        raise exc


async def _process_media_generation(job_id: uuid.UUID, task) -> Dict[str, Any]:
    """Process media generation for a job."""
    logger.info(f"Starting media generation for job {job_id}")
    
    # Get job from database
    job = await JobService.get_job(job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")
    
    try:
        # Update job status to processing
        await JobService.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Start media generation
        logger.info(f"Starting Replicate generation for job {job_id}")
        prediction_id = await media_service.generate_media(job.prompt, job.parameters)
        
        # Update job with Replicate ID
        await JobService.update_job_status(
            job_id, 
            JobStatus.PROCESSING, 
            replicate_id=prediction_id
        )
        
        # Wait for completion with timeout
        logger.info(f"Waiting for completion of prediction {prediction_id}")
        result = await media_service.wait_for_completion(prediction_id, max_wait_time=300)
        
        if result["status"] == "succeeded" and result.get("output"):
            # Download generated media
            media_url = result["output"][0]  # Assuming first output is the image
            logger.info(f"Downloading media from {media_url}")
            media_content = await media_service.download_media(media_url)
            
            # Store media
            file_extension = storage_service.get_file_extension_from_url(media_url)
            public_url, storage_path = await storage_service.store_media(
                media_content, job_id, file_extension
            )
            
            # Complete job
            await JobService.complete_job(job_id, public_url, storage_path)
            
            logger.info(f"Job {job_id} completed successfully")
            return {
                "job_id": str(job_id),
                "status": "completed",
                "result_url": public_url,
                "storage_path": storage_path
            }
        
        elif result["status"] == "failed":
            error_msg = result.get("error", "Unknown error from Replicate")
            await JobService.fail_job(job_id, error_msg)
            raise Exception(f"Replicate generation failed: {error_msg}")
        
        else:
            raise Exception(f"Unexpected result status: {result['status']}")
    
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        await _handle_task_failure(job_id, str(e))
        raise


async def _handle_task_failure(job_id: uuid.UUID, error_message: str):
    """Handle task failure by updating job status."""
    try:
        job = await JobService.get_job(job_id)
        if not job:
            return
        
        # Check if job can be retried
        if job.can_retry:
            await JobService.increment_retry_count(job_id)
            logger.info(f"Job {job_id} will be retried. Retry count: {job.retry_count + 1}")
        else:
            await JobService.fail_job(job_id, error_message)
            logger.error(f"Job {job_id} failed permanently: {error_message}")
    
    except Exception as e:
        logger.error(f"Error handling task failure for job {job_id}: {e}")


@celery_app.task
def cleanup_old_jobs():
    """Periodic task to clean up old completed/failed jobs."""
    loop = get_event_loop()
    return loop.run_until_complete(_cleanup_old_jobs())


async def _cleanup_old_jobs():
    """Clean up jobs older than 30 days."""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    # This would be implemented based on your cleanup requirements
    logger.info(f"Cleanup task ran at {datetime.utcnow()}")
    return {"cleaned_jobs": 0, "cutoff_date": cutoff_date.isoformat()}


# Health check task
@celery_app.task
def health_check():
    """Health check task for monitoring."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    } 