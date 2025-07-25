#!/usr/bin/env python3
"""
Simple script to test the Media Generation API manually.
Run this after starting the API server.
"""
import requests
import time
import json
import sys


def test_api():
    """Test the API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Media Generation API")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Start with: docker-compose up -d")
        return False
    
    print()
    
    # Test generation endpoint
    print("2. Testing media generation...")
    generation_data = {
        "prompt": "A beautiful sunset over mountains",
        "parameters": {
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 20
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/generate",
            json=generation_data
        )
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print("✅ Job created successfully")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {job_data['status']}")
        else:
            print(f"❌ Job creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating job: {e}")
        return False
    
    print()
    
    # Test status checking
    print("3. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/status/{job_id}")
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Status check successful")
            print(f"   Job ID: {status_data['job_id']}")
            print(f"   Status: {status_data['status']}")
            print(f"   Created: {status_data['created_at']}")
            print(f"   Updated: {status_data['updated_at']}")
            
            if status_data.get('result_url'):
                print(f"   Result URL: {status_data['result_url']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False
    
    print()
    
    # Test detailed job info
    print("4. Testing job details endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/jobs/{job_id}")
        if response.status_code == 200:
            job_details = response.json()
            print("✅ Job details retrieved successfully")
            print(f"   Prompt: {job_details['prompt']}")
            print(f"   Parameters: {json.dumps(job_details['parameters'], indent=2)}")
            print(f"   Retry Count: {job_details['retry_count']}")
            print(f"   Max Retries: {job_details['max_retries']}")
        else:
            print(f"❌ Job details failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting job details: {e}")
        return False
    
    print()
    print("🎉 All API tests passed!")
    print()
    print("📋 Next steps:")
    print("   • Check Celery worker logs: docker-compose logs -f celery_worker")
    print("   • Monitor with Flower: http://localhost:5555")
    print("   • View API docs: http://localhost:8000/docs")
    print(f"   • Check job status again: curl {base_url}/api/v1/status/{job_id}")
    
    return True


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1) 