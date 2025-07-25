from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict, Any
import uuid
import logging

from app.schemas.job import (
    GenerateRequest, 
    GenerateResponse, 
    JobStatusResponse,
    JobResponse,
    JobCreate
)
from app.services.job_service import JobService
from app.tasks.media_tasks import generate_media_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["media"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_media(request: GenerateRequest) -> GenerateResponse:
    """
    Generate media asynchronously using the provided prompt and parameters.
    
    This endpoint creates a new job and enqueues it for background processing.
    Returns a job ID that can be used to check status and retrieve results.
    """
    try:
        # Create job in database
        job_data = JobCreate(
            prompt=request.prompt,
            parameters=request.parameters
        )
        
        job = await JobService.create_job(job_data)
        
        # Enqueue background task
        generate_media_task.delay(str(job.id))
        
        logger.info(f"Created job {job.id} for prompt: {request.prompt[:50]}...")
        
        return GenerateResponse(
            job_id=job.id,
            status=job.status.value,
            message=f"Job created successfully. Use job ID {job.id} to check status."
        )
    
    except Exception as e:
        logger.error(f"Failed to create generation job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create generation job: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: uuid.UUID) -> JobStatusResponse:
    """
    Get the status and result of a media generation job.
    
    Returns job status, progress information, and result URL if completed.
    """
    try:
        job = await JobService.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return JobService.job_to_status_response(job)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status for {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job status: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_details(job_id: uuid.UUID) -> JobResponse:
    """
    Get detailed information about a specific job.
    
    Returns comprehensive job information including metadata, timestamps, and results.
    """
    try:
        job = await JobService.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return JobService.job_to_response(job)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job details for {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job details: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "media-generation-api",
        "version": "1.0.0"
    } 