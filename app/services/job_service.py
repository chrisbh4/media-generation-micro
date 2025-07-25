import uuid
from datetime import datetime
from typing import Optional, List
from tortoise.exceptions import DoesNotExist

from app.models.job import Job, JobStatus as ModelJobStatus
from app.schemas.job import JobCreate, JobResponse, JobStatusResponse


class JobService:
    """Service for managing job operations."""
    
    @staticmethod
    async def create_job(job_data: JobCreate) -> Job:
        """Create a new job in the database."""
        job = await Job.create(
            id=uuid.uuid4(),
            prompt=job_data.prompt,
            parameters=job_data.parameters,
            max_retries=job_data.max_retries or 3,
            status=ModelJobStatus.PENDING
        )
        return job
    
    @staticmethod
    async def get_job(job_id: uuid.UUID) -> Optional[Job]:
        """Get a job by ID."""
        try:
            return await Job.get(id=job_id)
        except DoesNotExist:
            return None
    
    @staticmethod
    async def update_job_status(
        job_id: uuid.UUID, 
        status: ModelJobStatus,
        error_message: Optional[str] = None,
        replicate_id: Optional[str] = None
    ) -> Optional[Job]:
        """Update job status and related fields."""
        job = await JobService.get_job(job_id)
        if not job:
            return None
        
        job.status = status
        job.updated_at = datetime.utcnow()
        
        if status == ModelJobStatus.PROCESSING and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in [ModelJobStatus.COMPLETED, ModelJobStatus.FAILED]:
            job.completed_at = datetime.utcnow()
        
        if error_message:
            job.error_message = error_message
        
        if replicate_id:
            job.replicate_id = replicate_id
        
        await job.save()
        return job
    
    @staticmethod
    async def increment_retry_count(job_id: uuid.UUID) -> Optional[Job]:
        """Increment the retry count for a job."""
        job = await JobService.get_job(job_id)
        if not job:
            return None
        
        job.retry_count += 1
        job.status = ModelJobStatus.RETRYING
        job.updated_at = datetime.utcnow()
        await job.save()
        return job
    
    @staticmethod
    async def complete_job(
        job_id: uuid.UUID, 
        result_url: str, 
        media_path: str
    ) -> Optional[Job]:
        """Mark job as completed with result data."""
        job = await JobService.get_job(job_id)
        if not job:
            return None
        
        job.status = ModelJobStatus.COMPLETED
        job.result_url = result_url
        job.media_path = media_path
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        await job.save()
        return job
    
    @staticmethod
    async def fail_job(job_id: uuid.UUID, error_message: str) -> Optional[Job]:
        """Mark job as failed with error message."""
        job = await JobService.get_job(job_id)
        if not job:
            return None
        
        job.status = ModelJobStatus.FAILED
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        await job.save()
        return job
    
    @staticmethod
    async def get_jobs_by_status(status: ModelJobStatus) -> List[Job]:
        """Get all jobs with a specific status."""
        return await Job.filter(status=status).all()
    
    @staticmethod
    async def get_retryable_jobs() -> List[Job]:
        """Get all jobs that can be retried."""
        return await Job.filter(
            status=ModelJobStatus.FAILED,
            retry_count__lt=Job.max_retries
        ).all()
    
    @staticmethod
    def job_to_response(job: Job) -> JobResponse:
        """Convert Job model to JobResponse schema."""
        return JobResponse(
            id=job.id,
            prompt=job.prompt,
            parameters=job.parameters,
            status=job.status.value,
            created_at=job.created_at,
            updated_at=job.updated_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            result_url=job.result_url,
            media_path=job.media_path,
            retry_count=job.retry_count,
            max_retries=job.max_retries,
            error_message=job.error_message,
            replicate_id=job.replicate_id
        )
    
    @staticmethod
    def job_to_status_response(job: Job) -> JobStatusResponse:
        """Convert Job model to JobStatusResponse schema."""
        return JobStatusResponse(
            job_id=job.id,
            status=job.status.value,
            result_url=job.result_url,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
            retry_count=job.retry_count
        ) 