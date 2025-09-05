"""
Enhanced image processing service with performance optimizations:
- Thumbnail generation and caching
- Image preprocessing pipeline
- Async batch processing
- Memory-efficient image handling
- Format optimization
"""

import io
import os
import hashlib
import asyncio
import logging
from typing import List, Tuple, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import aiofiles
from app.services.cache_service import cache_service, CacheKey
from app.services.clip_service import CLIPService
from app.services.vector_service import VectorService
from app.models.schemas import SearchResponse
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ImageProcessingStats:
    """Image processing performance statistics"""
    images_processed: int = 0
    thumbnails_generated: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_processing_time: float = 0.0
    total_processing_time: float = 0.0

class ImageOptimizer:
    """Advanced image optimization utilities"""
    
    SUPPORTED_FORMATS = ["JPEG", "PNG", "WEBP", "BMP", "TIFF"]
    THUMBNAIL_SIZES = {
        "small": (150, 150),
        "medium": (300, 300),
        "large": (600, 600)
    }
    
    @staticmethod
    def optimize_for_web(image: Image.Image, quality: int = 85, format: str = "JPEG") -> Tuple[bytes, str]:
        """Optimize image for web delivery"""
        # Convert RGBA to RGB for JPEG
        if format.upper() == "JPEG" and image.mode in ("RGBA", "LA", "P"):
            # Create white background
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
            image = background
        
        # Optimize image
        buffer = io.BytesIO()
        
        if format.upper() == "WEBP":
            image.save(buffer, format="WEBP", quality=quality, optimize=True)
        elif format.upper() == "JPEG":
            image.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=True)
        elif format.upper() == "PNG":
            image.save(buffer, format="PNG", optimize=True)
        else:
            image.save(buffer, format=format)
        
        return buffer.getvalue(), format.lower()
    
    @staticmethod
    def generate_thumbnail(image: Image.Image, size: Tuple[int, int], method: str = "lanczos") -> Image.Image:
        """Generate high-quality thumbnail"""
        # Use high-quality resampling
        if method == "lanczos":
            resample = Image.Resampling.LANCZOS
        elif method == "bicubic":
            resample = Image.Resampling.BICUBIC
        else:
            resample = Image.Resampling.BILINEAR
        
        # Calculate aspect ratio preserving size
        image.thumbnail(size, resample)
        
        # Create new image with exact size (center the thumbnail)
        thumb = Image.new(image.mode, size, (255, 255, 255))
        offset = ((size[0] - image.size[0]) // 2, (size[1] - image.size[1]) // 2)
        thumb.paste(image, offset)
        
        return thumb
    
    @staticmethod
    def enhance_image(image: Image.Image, enhance_options: Dict[str, Any]) -> Image.Image:
        """Apply image enhancements"""
        enhanced = image.copy()
        
        # Auto-contrast enhancement
        if enhance_options.get("auto_contrast", False):
            enhanced = ImageOps.autocontrast(enhanced)
        
        # Sharpening
        if enhance_options.get("sharpen", False):
            enhanced = enhanced.filter(ImageFilter.SHARPEN)
        
        # Color enhancement
        if enhance_options.get("enhance_color", False):
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(1.2)
        
        return enhanced

class EnhancedImageService:
    """Enhanced image service with performance optimizations"""
    
    def __init__(self):
        self.clip_service = CLIPService()
        self.vector_service = VectorService()
        self.optimizer = ImageOptimizer()
        self.stats = ImageProcessingStats()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
        # Cache directories
        self.cache_dir = Path("data/image_cache")
        self.thumbnail_dir = self.cache_dir / "thumbnails"
        self.optimized_dir = self.cache_dir / "optimized"
        
        # Create cache directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        self.optimized_dir.mkdir(parents=True, exist_ok=True)
    
    async def search_by_image(self, image_data: bytes, options: Optional[Dict[str, Any]] = None) -> SearchResponse:
        """Enhanced image search with caching and optimization"""
        start_time = time.time()
        options = options or {}
        
        try:
            # Generate image hash for caching
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # Check cache for search results
            cache_key = CacheKey.search_results(f"image:{image_hash}", options.get("filters", {}), options.get("limit", 20))
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                self.stats.cache_hits += 1
                logger.info(f"Image search cache hit for hash: {image_hash[:8]}")
                return SearchResponse(**cached_result)
            
            self.stats.cache_misses += 1
            
            # Process image
            image = await self._load_and_preprocess_image(image_data, image_hash)
            
            # Generate embedding
            embedding_cache_key = CacheKey.image_embedding(image_hash)
            image_embedding = await cache_service.get(embedding_cache_key)
            
            if image_embedding is None:
                image_embedding = await self.clip_service.encode_image(image)
                await cache_service.set(embedding_cache_key, image_embedding, ttl=7200)  # 2 hours
            
            # Search in vector database
            search_options = {
                "embedding": image_embedding,
                "limit": options.get("limit", 20),
                "filters": options.get("filters", {}),
                "threshold": options.get("threshold", 0.1)
            }
            
            results = await self.vector_service.search_similar(**search_options)
            
            # Create response
            response = SearchResponse(
                products=results["products"],
                total=results["total"],
                query_time=results.get("query_time", 0.0),
                similarity_scores=results["scores"],
                image_hash=image_hash
            )
            
            # Cache the result
            await cache_service.set(cache_key, response.dict(), ttl=1800)  # 30 minutes
            
            # Update stats
            processing_time = time.time() - start_time
            self.stats.images_processed += 1
            self.stats.total_processing_time += processing_time
            self.stats.avg_processing_time = self.stats.total_processing_time / self.stats.images_processed
            
            return response
            
        except Exception as e:
            logger.error(f"Image search error: {e}")
            raise
    
    async def _load_and_preprocess_image(self, image_data: bytes, image_hash: str) -> Image.Image:
        """Load and preprocess image with caching"""
        try:
            # Check if preprocessed image exists in cache
            cached_path = self.optimized_dir / f"{image_hash}.webp"
            
            if cached_path.exists():
                async with aiofiles.open(cached_path, "rb") as f:
                    cached_data = await f.read()
                return Image.open(io.BytesIO(cached_data))
            
            # Load original image
            image = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool, 
                self._process_image_sync, 
                image_data
            )
            
            # Save preprocessed image to cache
            optimized_data, _ = self.optimizer.optimize_for_web(image, quality=90, format="WEBP")
            async with aiofiles.open(cached_path, "wb") as f:
                await f.write(optimized_data)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            # Fallback to direct loading
            return Image.open(io.BytesIO(image_data))
    
    def _process_image_sync(self, image_data: bytes) -> Image.Image:
        """Synchronous image processing"""
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            if image.mode in ('RGBA', 'LA', 'P'):
                # Handle transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            else:
                image = image.convert('RGB')
        
        # Basic optimization
        image = ImageOps.exif_transpose(image)  # Handle EXIF rotation
        
        # Resize if too large (max 2048x2048)
        max_size = 2048
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    async def generate_thumbnails(self, image_data: bytes, sizes: List[str] = None) -> Dict[str, bytes]:
        """Generate thumbnails in multiple sizes"""
        if sizes is None:
            sizes = ["small", "medium", "large"]
        
        start_time = time.time()
        image_hash = hashlib.md5(image_data).hexdigest()
        
        thumbnails = {}
        
        try:
            # Load original image
            image = await self._load_and_preprocess_image(image_data, image_hash)
            
            # Generate thumbnails
            for size_name in sizes:
                if size_name not in self.optimizer.THUMBNAIL_SIZES:
                    continue
                
                # Check cache first
                thumb_path = self.thumbnail_dir / f"{image_hash}_{size_name}.webp"
                
                if thumb_path.exists():
                    async with aiofiles.open(thumb_path, "rb") as f:
                        thumbnails[size_name] = await f.read()
                    continue
                
                # Generate thumbnail
                size = self.optimizer.THUMBNAIL_SIZES[size_name]
                thumbnail = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    self.optimizer.generate_thumbnail,
                    image, size
                )
                
                # Optimize and save
                thumb_data, _ = self.optimizer.optimize_for_web(thumbnail, quality=85, format="WEBP")
                thumbnails[size_name] = thumb_data
                
                # Cache thumbnail
                async with aiofiles.open(thumb_path, "wb") as f:
                    await f.write(thumb_data)
                
                self.stats.thumbnails_generated += 1
            
            logger.info(f"Generated {len(thumbnails)} thumbnails in {time.time() - start_time:.3f}s")
            return thumbnails
            
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            return {}
    
    async def batch_process_images(self, image_list: List[bytes], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process multiple images efficiently"""
        options = options or {}
        batch_size = options.get("batch_size", 5)
        
        results = []
        
        # Process in batches to manage memory
        for i in range(0, len(image_list), batch_size):
            batch = image_list[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [
                self._process_single_image(image_data, options)
                for image_data in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    results.append({"error": str(result)})
                else:
                    results.append(result)
        
        return results
    
    async def _process_single_image(self, image_data: bytes, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single image and return metadata"""
        try:
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # Basic image info
            image = Image.open(io.BytesIO(image_data))
            
            result = {
                "hash": image_hash,
                "size": image.size,
                "mode": image.mode,
                "format": image.format,
                "file_size": len(image_data)
            }
            
            # Generate embedding if requested
            if options.get("generate_embedding", False):
                processed_image = await self._load_and_preprocess_image(image_data, image_hash)
                embedding = await self.clip_service.encode_image(processed_image)
                result["embedding"] = embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            
            # Generate thumbnails if requested
            if options.get("generate_thumbnails", False):
                thumbnails = await self.generate_thumbnails(image_data)
                result["thumbnails"] = {size: len(data) for size, data in thumbnails.items()}
            
            return result
            
        except Exception as e:
            logger.error(f"Single image processing error: {e}")
            return {"error": str(e)}
    
    async def validate_image(self, image_data: bytes) -> Dict[str, Any]:
        """Comprehensive image validation"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            validation = {
                "valid": True,
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "file_size": len(image_data),
                "warnings": [],
                "errors": []
            }
            
            # Check format support
            if image.format not in self.optimizer.SUPPORTED_FORMATS:
                validation["warnings"].append(f"Format {image.format} may not be fully supported")
            
            # Check size limits
            max_dimension = 4096
            if max(image.size) > max_dimension:
                validation["warnings"].append(f"Image size {image.size} exceeds recommended maximum {max_dimension}px")
            
            # Check file size (10MB limit)
            max_file_size = 10 * 1024 * 1024
            if len(image_data) > max_file_size:
                validation["errors"].append(f"File size {len(image_data)} bytes exceeds maximum {max_file_size} bytes")
                validation["valid"] = False
            
            # Check for corruption
            try:
                image.verify()
            except Exception as e:
                validation["errors"].append(f"Image verification failed: {e}")
                validation["valid"] = False
            
            return validation
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Image loading failed: {e}"],
                "warnings": []
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get image processing statistics"""
        return {
            "images_processed": self.stats.images_processed,
            "thumbnails_generated": self.stats.thumbnails_generated,
            "cache_hits": self.stats.cache_hits,
            "cache_misses": self.stats.cache_misses,
            "cache_hit_rate": self.stats.cache_hits / (self.stats.cache_hits + self.stats.cache_misses) if (self.stats.cache_hits + self.stats.cache_misses) > 0 else 0,
            "avg_processing_time": self.stats.avg_processing_time,
            "total_processing_time": self.stats.total_processing_time,
            "cache_dir_size": sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file()),
            "thumbnail_count": len(list(self.thumbnail_dir.glob('*.webp'))),
            "optimized_count": len(list(self.optimized_dir.glob('*.webp')))
        }
    
    async def cleanup_cache(self, max_age_days: int = 7) -> Dict[str, int]:
        """Clean up old cached images"""
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        cleaned = {"thumbnails": 0, "optimized": 0}
        
        # Clean thumbnails
        for thumb_file in self.thumbnail_dir.glob('*.webp'):
            if thumb_file.stat().st_mtime < cutoff_time:
                thumb_file.unlink()
                cleaned["thumbnails"] += 1
        
        # Clean optimized images
        for opt_file in self.optimized_dir.glob('*.webp'):
            if opt_file.stat().st_mtime < cutoff_time:
                opt_file.unlink()
                cleaned["optimized"] += 1
        
        logger.info(f"Cleaned {cleaned['thumbnails']} thumbnails and {cleaned['optimized']} optimized images")
        return cleaned
