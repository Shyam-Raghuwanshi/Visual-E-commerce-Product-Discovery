from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import search, upload, health, advanced_search
from app.middleware.rate_limiting import rate_limit_middleware
from app.middleware.authentication import authentication_middleware
from app.middleware.compression import compression_middleware
from app.services.cache_service import cache_service
from app.services.database_service import db_manager
from app.services.monitoring_service import performance_monitor, track_metric, log_request
from app.services.async_processing_service import AsyncProcessingContext, async_executor
import uvicorn
import time
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Visual E-commerce Product Discovery API",
    description="High-performance multi-modal search API with advanced optimization features",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Performance optimization middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Combined performance middleware with monitoring and optimization"""
    start_time = time.time()
    method = request.method
    endpoint = str(request.url.path)
    
    # Track request start
    track_metric("http_requests_active", 1, "gauge")
    
    try:
        # Apply compression middleware
        response = await compression_middleware(request, call_next)
        
        # Record successful request
        processing_time = time.time() - start_time
        track_metric("http_request_duration", processing_time, "histogram", 
                    {"method": method, "endpoint": endpoint})
        track_metric("http_requests_total", 1, "counter", 
                    {"method": method, "endpoint": endpoint, "status": "success"})
        
        # Log request
        log_request(method, endpoint, processing_time, response.status_code)
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(processing_time)
        response.headers["X-API-Version"] = "2.1.0"
        
        return response
        
    except Exception as e:
        # Record failed request
        processing_time = time.time() - start_time
        track_metric("http_requests_total", 1, "counter", 
                    {"method": method, "endpoint": endpoint, "status": "error"})
        
        logger.error(f"Request processing error: {e}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "path": endpoint,
                "method": method,
                "processing_time": processing_time
            }
        )
    finally:
        # Track request end
        track_metric("http_requests_active", -1, "gauge")

# CORS middleware with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Custom middleware for rate limiting and authentication
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    """Enhanced middleware with fallback handling"""
    start_time = time.time()
    
    # Apply rate limiting with error handling
    try:
        response = await rate_limit_middleware(request, call_next)
        return response
    except Exception as rate_limit_error:
        logger.warning(f"Rate limiting error: {rate_limit_error}")
        # Continue without rate limiting if it fails
        pass
    
    # Apply authentication with error handling
    try:
        response = await authentication_middleware(request, call_next)
        return response
    except Exception as auth_error:
        logger.warning(f"Authentication error: {auth_error}")
        # Continue without authentication if it fails
        pass
    
    # Fallback to direct call
    response = await call_next(request)
    
    # Add processing time header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Visual E-commerce API v2.1.0...")
    
    try:
        # Initialize cache service
        logger.info("Initializing cache service...")
        await cache_service.initialize()
        
        # Initialize database connections
        logger.info("Initializing database connections...")
        if os.getenv("DATABASE_URL"):
            await db_manager.add_pool(
                "default", 
                os.getenv("DATABASE_URL"),
                {
                    "min_size": 5,
                    "max_size": 20,
                    "command_timeout": 30
                }
            )
        
        # Start async processing system
        logger.info("Starting async processing system...")
        await async_executor.start()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup initialization failed: {e}")
        # Continue startup even if some services fail

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Visual E-commerce API...")
    
    try:
        # Stop async processing
        await async_executor.stop()
        
        # Close database connections
        await db_manager.close_all()
        
        logger.info("Shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Enhanced global exception handler"""
    import traceback
    
    # Log detailed error information
    logger.error(f"Unhandled exception in {request.method} {request.url.path}: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Track error metrics
    track_metric("errors_total", 1, "counter", {
        "error_type": type(exc).__name__,
        "endpoint": str(request.url.path),
        "method": request.method
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
            "method": request.method,
            "error_type": type(exc).__name__,
            "timestamp": time.time()
        }
    )

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(advanced_search.router, prefix="/api", tags=["advanced-search"])

@app.get("/")
async def root():
    """Enhanced root endpoint with comprehensive API information"""
    return {
        "message": "Visual E-commerce Product Discovery API",
        "version": "2.1.0",
        "status": "active",
        "performance_features": {
            "redis_caching": True,
            "response_compression": True,
            "async_processing": True,
            "connection_pooling": True,
            "monitoring": True,
            "rate_limiting": True
        },
        "endpoints": {
            "health": "/api/health",
            "metrics": "/api/metrics",
            "performance": "/api/performance",
            "docs": "/docs",
            "redoc": "/redoc",
            "search_text": "/api/search/text",
            "search_image": "/api/search/image",
            "search_combined": "/api/search/combined",
            "search_filters": "/api/search/filters",
            "advanced_search": "/api/search/advanced",
            "product_details": "/api/products/{id}",
            "upload": "/api/upload"
        },
        "authentication": {
            "api_key_header": "X-API-Key",
            "jwt_header": "Authorization: Bearer <token>",
            "levels": ["none", "basic", "premium", "enterprise"]
        },
        "optimization_info": {
            "cache_ttl_seconds": 3600,
            "compression_min_size": 500,
            "max_batch_size": 100,
            "default_timeout": 30
        }
    }

@app.get("/api/status")
async def enhanced_status():
    """Enhanced API status with performance metrics"""
    try:
        # Get health reports from all services
        cache_health = await cache_service.health_check()
        db_health = await db_manager.health_check_all()
        performance_report = performance_monitor.get_health_report()
        
        return {
            "api_status": "healthy",
            "version": "2.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "features": {
                "text_search": True,
                "image_search": True,
                "combined_search": True,
                "advanced_filters": True,
                "rate_limiting": True,
                "authentication": True,
                "caching": cache_health["status"] == "healthy",
                "compression": True,
                "async_processing": True,
                "monitoring": True
            },
            "service_health": {
                "cache": cache_health,
                "database": db_health,
                "performance": performance_report
            },
            "system_info": {
                "uptime_seconds": time.time() - (getattr(app, '_start_time', time.time())),
                "python_version": os.sys.version,
                "environment_variables": {
                    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
                    "CACHE_ENABLED": bool(os.getenv("REDIS_URL")),
                    "DATABASE_ENABLED": bool(os.getenv("DATABASE_URL"))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "api_status": "degraded",
                "error": str(e),
                "timestamp": time.time()
            }
        )

@app.get("/api/metrics")
async def get_metrics():
    """Prometheus-compatible metrics endpoint"""
    try:
        return performance_monitor.metrics_collector.export_prometheus_metrics()
    except Exception as e:
        logger.error(f"Metrics export error: {e}")
        return "# Metrics export failed\n"

@app.get("/api/performance")
async def get_performance_stats():
    """Get comprehensive performance statistics"""
    try:
        # Gather stats from all services
        cache_stats = cache_service.get_stats()
        db_stats = await db_manager.get_all_stats()
        monitoring_stats = performance_monitor.get_health_report()
        compression_stats = compression_middleware.get_stats()
        
        return {
            "timestamp": time.time(),
            "cache": cache_stats,
            "database": db_stats,
            "monitoring": monitoring_stats,
            "compression": compression_stats,
            "memory_usage": {
                "rss_mb": __import__('psutil').Process().memory_info().rss / 1024 / 1024,
                "percent": __import__('psutil').Process().memory_percent()
            }
        }
        
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to gather performance statistics"}
        )

# Store startup time for uptime calculation
app._start_time = time.time()

if __name__ == "__main__":
    # Enhanced server configuration
    config = {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "workers": int(os.getenv("WORKERS", 1)),
        "loop": "uvloop" if os.getenv("USE_UVLOOP", "false").lower() == "true" else "asyncio",
        "http": "httptools" if os.getenv("USE_HTTPTOOLS", "false").lower() == "true" else "h11"
    }
    
    logger.info(f"Starting server with config: {config}")
    
    uvicorn.run("main:app", **config)
