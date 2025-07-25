import asyncio
import httpx
from typing import Dict, Any, Optional
import uuid
from app.config import settings


class ReplicateClient:
    """Client for interacting with Replicate API."""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }
    
    def _process_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate parameters, including size filter handling."""
        processed_params = parameters.copy()
        
        # Check if filters.size exists and set the size value into setSize() function
        if "filters" in processed_params and isinstance(processed_params["filters"], dict):
            filters = processed_params["filters"]
            if "size" in filters and filters["size"]:
                # Call setSize function with the size value
                processed_params["width"] = filters["size"]
                processed_params["height"] = filters["size"]
                print(f"🔧 Applied size filter: {filters['size']}x{filters['size']}")
        
        return processed_params
    
    async def create_prediction(self, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prediction on Replicate."""
        # Process parameters including size filters
        processed_params = self._process_parameters(parameters)
        
        # Mock implementation - replace with actual Replicate API call
        if not self.api_token or self.api_token in ["", "your_replicate_api_token_here", "your_actual_replicate_api_token_here"]:
            return await self._mock_create_prediction(prompt, processed_params)
        
        async with httpx.AsyncClient() as client:
            payload = {
                "version": "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                "input": {
                    "prompt": prompt,
                    **processed_params
                }
            }
            
            response = await client.post(
                f"{self.base_url}/predictions",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_prediction(self, prediction_id: str) -> Dict[str, Any]:
        """Get prediction status and result."""
        # Mock implementation - replace with actual Replicate API call
        if not self.api_token or self.api_token in ["", "your_replicate_api_token_here", "your_actual_replicate_api_token_here"]:
            return await self._mock_get_prediction(prediction_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/predictions/{prediction_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def _mock_create_prediction(self, prompt: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock implementation for testing without real API token."""
        mock_id = str(uuid.uuid4())
        return {
            "id": mock_id,
            "status": "starting",
            "input": {
                "prompt": prompt,
                **parameters
            },
            "created_at": "2023-12-01T12:00:00.000Z",
            "urls": {
                "get": f"https://api.replicate.com/v1/predictions/{mock_id}",
                "cancel": f"https://api.replicate.com/v1/predictions/{mock_id}/cancel"
            }
        }
    
    async def _mock_get_prediction(self, prediction_id: str) -> Dict[str, Any]:
        """Mock implementation for testing."""
        # Simulate processing time
        await asyncio.sleep(2)
        
        return {
            "id": prediction_id,
            "status": "succeeded",
            "input": {
                "prompt": "A beautiful landscape"
            },
            "output": [
                f"https://replicate.delivery/pbxt/mock-image-{prediction_id}.jpg"
            ],
            "created_at": "2023-12-01T12:00:00.000Z",
            "completed_at": "2023-12-01T12:00:10.000Z"
        }


class MediaService:
    """Service for handling media generation operations."""
    
    def __init__(self):
        self.replicate_client = ReplicateClient(settings.replicate_api_token)
    
    async def generate_media(self, prompt: str, parameters: Dict[str, Any]) -> str:
        """Start media generation and return prediction ID."""
        prediction = await self.replicate_client.create_prediction(prompt, parameters)
        return prediction["id"]
    
    async def check_generation_status(self, prediction_id: str) -> Dict[str, Any]:
        """Check the status of a media generation job."""
        return await self.replicate_client.get_prediction(prediction_id)
    
    async def wait_for_completion(self, prediction_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """Wait for generation to complete with polling."""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status_data = await self.check_generation_status(prediction_id)
            
            if status_data["status"] in ["succeeded", "failed", "canceled"]:
                return status_data
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait_time:
                raise TimeoutError(f"Generation timed out after {max_wait_time} seconds")
            
            # Wait before next check
            await asyncio.sleep(5)
    
    async def download_media(self, media_url: str) -> bytes:
        """Download media content from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(media_url, timeout=60.0)
            response.raise_for_status()
            return response.content 