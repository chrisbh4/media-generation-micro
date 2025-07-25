from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class GenerateRequest(BaseModel):
    """Request schema for media generation."""
    prompt: str = Field(..., min_length=1, max_length=2000, description="Text prompt for media generation")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional generation parameters")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or only whitespace')
        return v.strip()


class GenerateResponse(BaseModel):
    """Response schema for generation request."""
    job_id: UUID = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")


class JobCreate(BaseModel):
    """Schema for creating a new job."""
    prompt: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    max_retries: Optional[int] = Field(default=3, ge=0, le=10)


class JobResponse(BaseModel):
    """Response schema for job details."""
    id: UUID
    prompt: str
    parameters: Dict[str, Any]
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_url: Optional[str] = None
    media_path: Optional[str] = None
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    replicate_id: Optional[str] = None

    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Response schema for job status endpoint."""
    job_id: UUID
    status: JobStatus
    progress: Optional[str] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    retry_count: int
    
    class Config:
        from_attributes = True 