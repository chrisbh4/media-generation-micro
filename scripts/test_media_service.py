#!/usr/bin/env python3
"""
Test script for media service functionality.
Tests both size filter handling and API token validation.
"""

import asyncio
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.media_service import MediaService
from app.config import settings


async def test_size_filter():
    """Test the size filter functionality."""
    print("\n🧪 Testing size filter functionality...")
    
    media_service = MediaService()
    
    # Test parameters with size filter
    test_parameters = {
        "filters": {
            "size": 512
        },
        "guidance_scale": 7.5,
        "num_inference_steps": 50
    }
    
    print(f"📝 Test parameters: {test_parameters}")
    
    try:
        # This will call the _process_parameters method internally
        prediction_id = await media_service.generate_media(
            "A beautiful landscape", 
            test_parameters
        )
        print(f"✅ Media generation started successfully: {prediction_id}")
        
        # Check status
        status = await media_service.check_generation_status(prediction_id)
        print(f"📊 Generation status: {status['status']}")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_without_size_filter():
    """Test without size filter."""
    print("\n🧪 Testing without size filter...")
    
    media_service = MediaService()
    
    # Test parameters without size filter
    test_parameters = {
        "guidance_scale": 7.5,
        "num_inference_steps": 50
    }
    
    print(f"📝 Test parameters: {test_parameters}")
    
    try:
        prediction_id = await media_service.generate_media(
            "A serene mountain view", 
            test_parameters
        )
        print(f"✅ Media generation started successfully: {prediction_id}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_config_validation():
    """Test configuration validation."""
    print("\n🧪 Testing configuration validation...")
    print(f"📊 Replicate API token configured: {bool(settings.replicate_api_token)}")
    print(f"📊 Token value (masked): {settings.replicate_api_token[:8] + '...' if settings.replicate_api_token else 'None'}")
    
    if not settings.replicate_api_token or settings.replicate_api_token in ["", "your_replicate_api_token_here", "your_actual_replicate_api_token_here"]:
        print("⚠️  Using mock implementation (token not configured)")
        return "mock"
    else:
        print("✅ Real Replicate API will be used")
        return "real"


async def main():
    """Run all tests."""
    print("🚀 Starting Media Service Tests")
    print("=" * 50)
    
    # Test configuration
    api_mode = test_config_validation()
    
    # Test size filter functionality
    size_filter_test = await test_size_filter()
    
    # Test without size filter
    no_filter_test = await test_without_size_filter()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Configuration: {api_mode} API mode")
    print(f"   Size filter test: {'✅ PASSED' if size_filter_test else '❌ FAILED'}")
    print(f"   No filter test: {'✅ PASSED' if no_filter_test else '❌ FAILED'}")
    
    if size_filter_test and no_filter_test:
        print("\n🎉 All tests passed!")
        
        if api_mode == "mock":
            print("\n💡 To use real Replicate API:")
            print("   1. Get your API token from: https://replicate.com/account/api-tokens")
            print("   2. Edit .env file and set: REPLICATE_API_TOKEN=your_actual_token")
            print("   3. Restart the application")
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 