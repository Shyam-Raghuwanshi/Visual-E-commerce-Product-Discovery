from fastapi import UploadFile
import io
import hashlib
import asyncio
import time
import logging
from app.services.clip_service import CLIPService
from app.services.vector_service import VectorService
from app.services.cache_service import cache_service, CacheKey
from app.services.enhanced_image_service import EnhancedImageService
from app.models.schemas import SearchResponse

logger = logging.getLogger(__name__)

class ImageService:
    """Enhanced image service with performance optimizations"""
    
    def __init__(self):
        self.clip_service = CLIPService()
        self.vector_service = VectorService()
        self.enhanced_service = EnhancedImageService()
    
    async def search_by_image(self, file: UploadFile) -> SearchResponse:
        """Search for products using an uploaded image with caching"""
        start_time = time.time()
        
        try:
            # Read image data
            image_bytes = await file.read()
            
            # Generate image hash for caching
            image_hash = hashlib.md5(image_bytes).hexdigest()
            
            # Check cache for search results
            cache_key = CacheKey.search_results(f"image:{image_hash}", {}, 20)
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                logger.info(f"Image search cache hit for hash: {image_hash[:8]}")
                return SearchResponse(**cached_result)
            
            # Use enhanced image service for processing
            response = await self.enhanced_service.search_by_image(image_bytes)
            
            # Cache the result
            await cache_service.set(cache_key, response.dict(), ttl=1800)  # 30 minutes
            
            logger.info(f"Image search completed in {time.time() - start_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Image search error: {e}")
            raise
    
    def validate_image(self, file: UploadFile) -> bool:
        """Validate if uploaded file is a valid image"""
        valid_types = ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp"]
        return file.content_type in valid_types
    
    async def validate_image_detailed(self, file: UploadFile) -> dict:
        """Perform detailed image validation"""
        try:
            image_bytes = await file.read()
            return await self.enhanced_service.validate_image(image_bytes)
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {e}"],
                "warnings": []
            }
    
    async def generate_thumbnails(self, file: UploadFile, sizes: list = None) -> dict:
        """Generate thumbnails for uploaded image"""
        try:
            image_bytes = await file.read()
            return await self.enhanced_service.generate_thumbnails(image_bytes, sizes)
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            return {}
    
    def get_processing_stats(self) -> dict:
        """Get image processing statistics"""
        try:
            return self.enhanced_service.get_processing_stats()
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {}
