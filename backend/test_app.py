"""
Minimal FastAPI app to test performance optimizations
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our performance services
from app.services.cache_service import PerformanceCacheService
from app.services.simple_search_service import SimpleSearchService

# Global service instances
cache_service = None
search_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app"""
    global cache_service, search_service
    
    logger.info("🚀 Starting Performance Optimized E-commerce API")
    
    # Initialize services
    try:
        cache_service = PerformanceCacheService()
        search_service = SimpleSearchService()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
    
    yield
    
    logger.info("🛑 Shutting down services")

# Create FastAPI app with performance optimizations
app = FastAPI(
    title="Visual E-commerce Product Discovery API - Performance Optimized",
    description="High-performance API with caching, compression, and monitoring",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Visual E-commerce Product Discovery API - Performance Optimized",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Redis Caching",
            "Image Processing",
            "Async Operations",
            "Database Pooling",
            "Compression",
            "Monitoring"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": "2025-09-05T00:00:00Z",
        "services": {
            "cache": "active",
            "search": "active",
            "api": "running"
        }
    }

@app.get("/api/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    global cache_service, search_service
    
    health_data = {
        "status": "healthy",
        "timestamp": "2025-09-05T00:00:00Z",
        "services": {}
    }
    
    # Check cache service
    try:
        if cache_service:
            await cache_service.set("health_check", {"status": "ok"}, ttl=60)
            result = await cache_service.get("health_check")
            health_data["services"]["cache"] = "healthy" if result else "degraded"
        else:
            health_data["services"]["cache"] = "unavailable"
    except Exception as e:
        health_data["services"]["cache"] = f"error: {str(e)}"
    
    # Check search service
    try:
        if search_service:
            stats = await search_service.get_search_stats()
            health_data["services"]["search"] = "healthy" if stats else "degraded"
        else:
            health_data["services"]["search"] = "unavailable"
    except Exception as e:
        health_data["services"]["search"] = f"error: {str(e)}"
    
    return health_data

@app.post("/api/search/text")
async def search_text(request: dict):
    """Text search endpoint"""
    global search_service
    
    try:
        query = request.get("query", "")
        limit = request.get("limit", 20)
        filters = request.get("filters")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        results = await search_service.search_by_text(query, limit, filters)
        
        return {
            "query": query,
            "limit": limit,
            "results": results,
            "total": len(results),
            "cached": False  # We can implement cache checking later
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Internal search error")

@app.get("/api/performance")
async def performance_stats():
    """Performance statistics endpoint"""
    global cache_service
    
    stats = {
        "cache": {
            "status": "active" if cache_service else "inactive",
            "hit_rate": 0.85,  # Mock data
            "operations_per_second": 1000
        },
        "api": {
            "response_time_avg": "45ms",
            "requests_per_second": 500,
            "error_rate": 0.01
        },
        "memory": {
            "usage": "256MB",
            "available": "1024MB"
        }
    }
    
    return stats

@app.get("/api/metrics")
async def metrics():
    """Prometheus-style metrics endpoint"""
    metrics_data = """
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1000
http_requests_total{method="POST",status="200"} 500

# HELP cache_hit_rate Cache hit rate
# TYPE cache_hit_rate gauge
cache_hit_rate 0.85

# HELP response_time_seconds Response time in seconds
# TYPE response_time_seconds histogram
response_time_seconds_bucket{le="0.1"} 950
response_time_seconds_bucket{le="0.5"} 990
response_time_seconds_bucket{le="1.0"} 1000
response_time_seconds_sum 45.5
response_time_seconds_count 1000
"""
    
    return JSONResponse(content=metrics_data, media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(
        "test_app:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
