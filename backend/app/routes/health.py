from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import logging
from datetime import datetime
import asyncio

# Import performance services
try:
    from app.services.cache_service import cache_service
    CACHE_SERVICE_AVAILABLE = True
except ImportError:
    CACHE_SERVICE_AVAILABLE = False

try:
    from app.services.database_service import db_manager
    DATABASE_SERVICE_AVAILABLE = True
except ImportError:
    DATABASE_SERVICE_AVAILABLE = False

try:
    from app.services.monitoring_service import performance_monitor
    MONITORING_SERVICE_AVAILABLE = True
except ImportError:
    MONITORING_SERVICE_AVAILABLE = False

try:
    from app.services.enhanced_image_service import EnhancedImageService
    enhanced_image_service = EnhancedImageService()
    IMAGE_SERVICE_AVAILABLE = True
except ImportError:
    IMAGE_SERVICE_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "uptime": time.time()
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Comprehensive health check with all services"""
    start_time = time.time()
    health_report = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "check_duration_ms": 0,
        "services": {},
        "performance": {},
        "warnings": [],
        "errors": []
    }
    
    # Check cache service
    if CACHE_SERVICE_AVAILABLE:
        try:
            cache_health = await cache_service.health_check()
            health_report["services"]["cache"] = cache_health
            
            if cache_health["status"] != "healthy":
                health_report["warnings"].append("Cache service is not healthy")
                
        except Exception as e:
            health_report["services"]["cache"] = {"status": "error", "error": str(e)}
            health_report["errors"].append(f"Cache health check failed: {e}")
    else:
        health_report["services"]["cache"] = {"status": "not_available"}
        health_report["warnings"].append("Cache service not available")
    
    # Check database service
    if DATABASE_SERVICE_AVAILABLE:
        try:
            db_health = await db_manager.health_check_all()
            health_report["services"]["database"] = db_health
            
            if db_health.get("overall_status") != "healthy":
                health_report["warnings"].append("Database service is not healthy")
                
        except Exception as e:
            health_report["services"]["database"] = {"status": "error", "error": str(e)}
            health_report["errors"].append(f"Database health check failed: {e}")
    else:
        health_report["services"]["database"] = {"status": "not_available"}
        health_report["warnings"].append("Database service not available")
    
    # Check monitoring service
    if MONITORING_SERVICE_AVAILABLE:
        try:
            monitoring_health = performance_monitor.get_health_report()
            health_report["performance"] = monitoring_health
            
        except Exception as e:
            health_report["performance"] = {"error": str(e)}
            health_report["errors"].append(f"Monitoring health check failed: {e}")
    else:
        health_report["warnings"].append("Monitoring service not available")
    
    # Check image processing service
    if IMAGE_SERVICE_AVAILABLE:
        try:
            image_stats = enhanced_image_service.get_processing_stats()
            health_report["services"]["image_processing"] = {
                "status": "healthy",
                "stats": image_stats
            }
        except Exception as e:
            health_report["services"]["image_processing"] = {"status": "error", "error": str(e)}
            health_report["errors"].append(f"Image service health check failed: {e}")
    else:
        health_report["services"]["image_processing"] = {"status": "not_available"}
        health_report["warnings"].append("Enhanced image service not available")
    
    # Memory check
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        health_report["services"]["system"] = {
            "status": "healthy",
            "memory_rss_mb": memory_info.rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent(),
            "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0
        }
        
        # Check for memory warnings
        if process.memory_percent() > 80:
            health_report["warnings"].append(f"High memory usage: {process.memory_percent():.1f}%")
        
    except Exception as e:
        health_report["services"]["system"] = {"status": "error", "error": str(e)}
        health_report["errors"].append(f"System health check failed: {e}")
    
    # Determine overall health status
    if health_report["errors"]:
        health_report["status"] = "unhealthy"
    elif health_report["warnings"]:
        health_report["status"] = "warning"
    else:
        health_report["status"] = "healthy"
    
    # Record check duration
    health_report["check_duration_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_report

@router.get("/health/cache")
async def cache_health():
    """Cache-specific health check"""
    if not CACHE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Cache service not available")
    
    try:
        health = await cache_service.health_check()
        stats = cache_service.get_stats()
        
        return {
            "health": health,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cache health check failed: {e}")

@router.get("/health/database")
async def database_health():
    """Database-specific health check"""
    if not DATABASE_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        health = await db_manager.health_check_all()
        stats = await db_manager.get_all_stats()
        
        return {
            "health": health,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database health check failed: {e}")

@router.get("/health/performance")
async def performance_health():
    """Performance monitoring health check"""
    if not MONITORING_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Monitoring service not available")
    
    try:
        health_report = performance_monitor.get_health_report()
        
        return {
            "report": health_report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Performance health check failed: {e}")

@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe - simple check"""
    return {"status": "alive", "timestamp": time.time()}

@router.get("/health/ready")
async def readiness_probe():
    """Kubernetes readiness probe - check if ready to serve traffic"""
    ready = True
    checks = {}
    
    # Quick cache check
    if CACHE_SERVICE_AVAILABLE:
        try:
            await asyncio.wait_for(cache_service.health_check(), timeout=2.0)
            checks["cache"] = True
        except:
            checks["cache"] = False
            ready = False
    
    # Quick database check
    if DATABASE_SERVICE_AVAILABLE:
        try:
            await asyncio.wait_for(db_manager.health_check_all(), timeout=2.0)
            checks["database"] = True
        except:
            checks["database"] = False
            ready = False
    
    if ready:
        return {"status": "ready", "checks": checks, "timestamp": time.time()}
    else:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not_ready", "checks": checks, "timestamp": time.time()}
        )
