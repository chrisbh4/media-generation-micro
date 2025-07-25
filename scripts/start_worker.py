#!/usr/bin/env python3
"""
Script to start Celery worker for media generation tasks.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.tasks.celery_app import celery_app

if __name__ == "__main__":
    # Start Celery worker
    celery_app.start([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--queues=media_generation',
        '--pool=solo' if os.name == 'nt' else '--pool=prefork',  # Use solo pool on Windows
    ]) 