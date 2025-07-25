import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.schemas.job import GenerateRequest

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns basic info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "media-generation-api"


def test_generate_endpoint():
    """Test the media generation endpoint."""
    request_data = {
        "prompt": "A beautiful sunset over mountains",
        "parameters": {
            "width": 1024,
            "height": 1024
        }
    }
    
    response = client.post("/api/v1/generate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert "status" in data
    assert "message" in data
    assert data["status"] == "pending"
    
    # Verify job_id is a valid UUID
    job_id = data["job_id"]
    uuid.UUID(job_id)  # Will raise ValueError if invalid


def test_generate_endpoint_validation():
    """Test the generation endpoint validates input."""
    # Test empty prompt
    response = client.post("/api/v1/generate", json={"prompt": ""})
    assert response.status_code == 422
    
    # Test missing prompt
    response = client.post("/api/v1/generate", json={})
    assert response.status_code == 422


def test_status_endpoint_not_found():
    """Test status endpoint with non-existent job ID."""
    fake_job_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/status/{fake_job_id}")
    assert response.status_code == 404


def test_job_details_endpoint_not_found():
    """Test job details endpoint with non-existent job ID."""
    fake_job_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/jobs/{fake_job_id}")
    assert response.status_code == 404


def test_invalid_job_id_format():
    """Test endpoints with invalid job ID format."""
    invalid_job_id = "not-a-valid-uuid"
    
    response = client.get(f"/api/v1/status/{invalid_job_id}")
    assert response.status_code == 422
    
    response = client.get(f"/api/v1/jobs/{invalid_job_id}")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_full_workflow():
    """Test the complete workflow from generation to completion (mock)."""
    # Note: This test requires the database to be initialized
    # In a real test environment, you'd use a test database
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Generate media
        request_data = {
            "prompt": "Test image generation",
            "parameters": {"test": True}
        }
        
        response = await ac.post("/api/v1/generate", json=request_data)
        assert response.status_code == 200
        
        job_data = response.json()
        job_id = job_data["job_id"]
        
        # Check initial status
        response = await ac.get(f"/api/v1/status/{job_id}")
        assert response.status_code == 200
        
        status_data = response.json()
        assert status_data["job_id"] == job_id
        assert status_data["status"] == "pending"
        
        # Get detailed job info
        response = await ac.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        
        job_details = response.json()
        assert job_details["id"] == job_id
        assert job_details["prompt"] == "Test image generation" 