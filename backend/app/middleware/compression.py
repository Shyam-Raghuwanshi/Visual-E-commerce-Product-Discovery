"""
Request/Response compression middleware for performance optimization.
Supports gzip, brotli, and deflate compression with intelligent content-type detection.
"""

import gzip
import zlib
import io
import json
from typing import List, Optional, Union, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    brotli = None
    BROTLI_AVAILABLE = False

try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    orjson = None
    ORJSON_AVAILABLE = False

logger = logging.getLogger(__name__)

class CompressionConfig:
    """Configuration for compression middleware"""
    
    def __init__(self):
        self.min_size = 500  # Minimum response size to compress (bytes)
        self.compression_level = 6  # Default compression level (1-9)
        self.brotli_quality = 4  # Brotli quality (0-11)
        
        # Content types to compress
        self.compressible_types = {
            "application/json",
            "application/javascript",
            "text/html",
            "text/css",
            "text/plain",
            "text/xml",
            "application/xml",
            "application/rss+xml",
            "application/atom+xml",
            "image/svg+xml",
            "application/x-javascript",
            "text/javascript"
        }
        
        # Content types to never compress
        self.excluded_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "video/mp4",
            "video/mpeg",
            "audio/mpeg",
            "application/zip",
            "application/gzip",
            "application/x-rar-compressed"
        }

class CompressionStats:
    """Compression performance statistics"""
    
    def __init__(self):
        self.total_requests = 0
        self.compressed_requests = 0
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.compression_times = []
        self.max_history = 1000
    
    def record_compression(self, original_size: int, compressed_size: int, compression_time: float):
        """Record compression statistics"""
        self.total_requests += 1
        self.compressed_requests += 1
        self.total_original_size += original_size
        self.total_compressed_size += compressed_size
        
        self.compression_times.append(compression_time)
        if len(self.compression_times) > self.max_history:
            self.compression_times = self.compression_times[-self.max_history:]
    
    def record_request(self):
        """Record a request (compressed or not)"""
        self.total_requests += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        compression_ratio = (
            self.total_compressed_size / self.total_original_size
            if self.total_original_size > 0 else 1.0
        )
        
        compression_rate = (
            self.compressed_requests / self.total_requests
            if self.total_requests > 0 else 0.0
        )
        
        avg_compression_time = (
            sum(self.compression_times) / len(self.compression_times)
            if self.compression_times else 0.0
        )
        
        return {
            "total_requests": self.total_requests,
            "compressed_requests": self.compressed_requests,
            "compression_rate": compression_rate,
            "total_original_size": self.total_original_size,
            "total_compressed_size": self.total_compressed_size,
            "compression_ratio": compression_ratio,
            "bytes_saved": self.total_original_size - self.total_compressed_size,
            "avg_compression_time_ms": avg_compression_time * 1000,
            "compression_efficiency": (1 - compression_ratio) * 100
        }

class ResponseCompressor:
    """High-performance response compression"""
    
    def __init__(self, config: CompressionConfig):
        self.config = config
        self.stats = CompressionStats()
    
    def get_accepted_encodings(self, request: Request) -> List[str]:
        """Parse Accept-Encoding header and return supported encodings in preference order"""
        accept_encoding = request.headers.get("accept-encoding", "")
        
        # Parse encoding preferences
        encodings = []
        for encoding in accept_encoding.split(","):
            encoding = encoding.strip()
            
            # Handle quality values (q=0.8)
            if ";" in encoding:
                enc_name, quality = encoding.split(";", 1)
                enc_name = enc_name.strip()
                try:
                    q_value = float(quality.split("=")[1])
                    if q_value > 0:
                        encodings.append((enc_name, q_value))
                except (ValueError, IndexError):
                    encodings.append((enc_name, 1.0))
            else:
                encodings.append((encoding, 1.0))
        
        # Sort by quality value (highest first)
        encodings.sort(key=lambda x: x[1], reverse=True)
        
        # Return supported encodings in order of preference
        supported = []
        for enc_name, _ in encodings:
            if enc_name == "br" and BROTLI_AVAILABLE:
                supported.append("br")
            elif enc_name == "gzip":
                supported.append("gzip")
            elif enc_name == "deflate":
                supported.append("deflate")
        
        return supported
    
    def should_compress(self, response: Response, content_type: str, content_length: int) -> bool:
        """Determine if response should be compressed"""
        # Check if already compressed
        if response.headers.get("content-encoding"):
            return False
        
        # Check minimum size
        if content_length < self.config.min_size:
            return False
        
        # Check content type
        if content_type:
            # Extract main content type
            main_type = content_type.split(";")[0].strip().lower()
            
            # Skip excluded types
            if main_type in self.config.excluded_types:
                return False
            
            # Check if compressible
            if main_type not in self.config.compressible_types:
                # Allow compression for unknown text/* types
                if not main_type.startswith("text/"):
                    return False
        
        return True
    
    def compress_brotli(self, data: bytes) -> bytes:
        """Compress data using Brotli"""
        if not BROTLI_AVAILABLE:
            raise ValueError("Brotli compression not available")
        
        return brotli.compress(data, quality=self.config.brotli_quality)
    
    def compress_gzip(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=self.config.compression_level) as f:
            f.write(data)
        return buffer.getvalue()
    
    def compress_deflate(self, data: bytes) -> bytes:
        """Compress data using deflate"""
        return zlib.compress(data, level=self.config.compression_level)
    
    def compress_response(self, content: bytes, encoding: str) -> bytes:
        """Compress response content with specified encoding"""
        import time
        start_time = time.time()
        
        try:
            if encoding == "br":
                compressed_content = self.compress_brotli(content)
            elif encoding == "gzip":
                compressed_content = self.compress_gzip(content)
            elif encoding == "deflate":
                compressed_content = self.compress_deflate(content)
            else:
                raise ValueError(f"Unsupported encoding: {encoding}")
            
            compression_time = time.time() - start_time
            self.stats.record_compression(len(content), len(compressed_content), compression_time)
            
            logger.debug(f"Compressed {len(content)} bytes to {len(compressed_content)} bytes "
                        f"({(1 - len(compressed_content)/len(content))*100:.1f}% reduction) "
                        f"using {encoding} in {compression_time*1000:.2f}ms")
            
            return compressed_content
            
        except Exception as e:
            logger.error(f"Compression failed with {encoding}: {e}")
            self.stats.record_request()
            return content

class JSONOptimizer:
    """Optimized JSON serialization for better performance"""
    
    @staticmethod
    def optimize_json_response(data: Any) -> bytes:
        """Optimize JSON serialization"""
        if ORJSON_AVAILABLE:
            # Use orjson for faster serialization
            return orjson.dumps(data)
        else:
            # Fallback to standard json with optimizations
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

class CompressionMiddleware:
    """FastAPI middleware for response compression"""
    
    def __init__(self, config: Optional[CompressionConfig] = None):
        self.config = config or CompressionConfig()
        self.compressor = ResponseCompressor(self.config)
        self.json_optimizer = JSONOptimizer()
    
    async def __call__(self, request: Request, call_next):
        """Compression middleware implementation"""
        # Process the request
        response = await call_next(request)
        
        # Get accepted encodings
        accepted_encodings = self.compressor.get_accepted_encodings(request)
        
        if not accepted_encodings:
            self.compressor.stats.record_request()
            return response
        
        # Get response content
        content = b""
        content_type = response.headers.get("content-type", "")
        
        # Handle different response types
        if hasattr(response, 'body'):
            content = response.body
        elif hasattr(response, 'content'):
            if isinstance(response.content, str):
                content = response.content.encode('utf-8')
            else:
                content = response.content
        else:
            # Try to get content from response iterator
            try:
                if hasattr(response, '__iter__'):
                    content = b"".join([chunk for chunk in response])
            except Exception:
                self.compressor.stats.record_request()
                return response
        
        content_length = len(content)
        
        # Check if compression should be applied
        if not self.compressor.should_compress(response, content_type, content_length):
            self.compressor.stats.record_request()
            return response
        
        # Choose best encoding
        best_encoding = accepted_encodings[0]
        
        try:
            # Optimize JSON responses
            if content_type.startswith("application/json") and content:
                try:
                    # Parse and re-serialize for optimization
                    data = json.loads(content.decode('utf-8'))
                    content = self.json_optimizer.optimize_json_response(data)
                    content_length = len(content)
                except Exception as e:
                    logger.debug(f"JSON optimization failed: {e}")
            
            # Compress content
            compressed_content = self.compressor.compress_response(content, best_encoding)
            
            # Create new response with compressed content
            compressed_response = Response(
                content=compressed_content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Update headers
            compressed_response.headers["content-encoding"] = best_encoding
            compressed_response.headers["content-length"] = str(len(compressed_content))
            compressed_response.headers["vary"] = "Accept-Encoding"
            
            # Add compression info header (for debugging)
            compression_ratio = len(compressed_content) / content_length if content_length > 0 else 1.0
            compressed_response.headers["x-compression-ratio"] = f"{compression_ratio:.3f}"
            compressed_response.headers["x-original-size"] = str(content_length)
            compressed_response.headers["x-compressed-size"] = str(len(compressed_content))
            
            return compressed_response
            
        except Exception as e:
            logger.error(f"Response compression failed: {e}")
            self.compressor.stats.record_request()
            return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        return self.compressor.stats.get_stats()

# Pre-configured compression middleware instances
class CompressionLevel:
    """Pre-configured compression levels"""
    
    @staticmethod
    def fast() -> CompressionMiddleware:
        """Fast compression (lower CPU usage)"""
        config = CompressionConfig()
        config.compression_level = 3
        config.brotli_quality = 2
        config.min_size = 1000
        return CompressionMiddleware(config)
    
    @staticmethod
    def balanced() -> CompressionMiddleware:
        """Balanced compression (default)"""
        config = CompressionConfig()
        config.compression_level = 6
        config.brotli_quality = 4
        config.min_size = 500
        return CompressionMiddleware(config)
    
    @staticmethod
    def maximum() -> CompressionMiddleware:
        """Maximum compression (higher CPU usage)"""
        config = CompressionConfig()
        config.compression_level = 9
        config.brotli_quality = 8
        config.min_size = 200
        return CompressionMiddleware(config)

# Global compression middleware instance
compression_middleware = CompressionLevel.balanced()

# Utility functions
def get_compression_stats() -> Dict[str, Any]:
    """Get global compression statistics"""
    return compression_middleware.get_stats()

def create_compressed_json_response(data: Any, status_code: int = 200) -> JSONResponse:
    """Create a pre-compressed JSON response"""
    if ORJSON_AVAILABLE:
        content = orjson.dumps(data)
        media_type = "application/json"
    else:
        content = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        media_type = "application/json; charset=utf-8"
    
    return JSONResponse(
        content=json.loads(content) if isinstance(content, (str, bytes)) else data,
        status_code=status_code,
        media_type=media_type
    )
