from tortoise.models import Model
from tortoise import fields
from enum import Enum
from datetime import datetime
from typing import Optional


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Job(Model):
    """Job model for tracking media generation tasks."""
    
    id = fields.UUIDField(pk=True)
    
    # Job metadata
    prompt = fields.TextField()
    parameters = fields.JSONField(default=dict)
    status = fields.CharEnumField(JobStatus, default=JobStatus.PENDING)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    
    # Results and storage
    result_url = fields.TextField(null=True)
    media_path = fields.TextField(null=True)
    
    # Error handling
    retry_count = fields.IntField(default=0)
    max_retries = fields.IntField(default=3)
    error_message = fields.TextField(null=True)
    
    # External service tracking
    replicate_id = fields.TextField(null=True)
    
    class Meta:
        table = "jobs"
        ordering = ["-created_at"]
    
    def __str__(self) -> str:
        return f"Job({self.id}, {self.status}, '{self.prompt[:50]}...')"
    
    @property
    def is_terminal_status(self) -> bool:
        """Check if the job has reached a terminal status."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED]
    
    @property
    def can_retry(self) -> bool:
        """Check if the job can be retried."""
        return self.retry_count < self.max_retries and self.status == JobStatus.FAILED 