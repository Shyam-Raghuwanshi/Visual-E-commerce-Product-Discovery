#!/usr/bin/env python3
"""
Simple test script to verify performance optimizations
without heavy model downloads
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_performance_services():
    """Test our performance optimization services"""
    print("🚀 Testing Performance Optimization Services")
    print("=" * 50)
    
    # Test 1: Cache Service
    try:
        from app.services.cache_service import PerformanceCacheService
        cache_service = PerformanceCacheService()
        
        # Test basic cache operations
        await cache_service.set("test_key", {"message": "Hello World"}, ttl=60)
        result = await cache_service.get("test_key")
        
        if result and result.get("message") == "Hello World":
            print("✅ Cache Service: WORKING")
        else:
            print("❌ Cache Service: FAILED")
            
    except Exception as e:
        print(f"❌ Cache Service: ERROR - {e}")
    
    # Test 2: Enhanced Image Service
    try:
        from app.services.enhanced_image_service import EnhancedImageService
        image_service = EnhancedImageService()
        
        # Test image service initialization
        stats = await image_service.get_stats()
        if stats.get("status") == "active":
            print("✅ Image Service: WORKING")
        else:
            print("❌ Image Service: FAILED")
            
    except Exception as e:
        print(f"❌ Image Service: ERROR - {e}")
    
    # Test 3: Database Service
    try:
        from app.services.database_service import AsyncDatabasePool
        db_service = AsyncDatabasePool()
        
        # Test database service
        health = await db_service.health_check()
        if health.get("status") in ["healthy", "degraded"]:
            print("✅ Database Service: WORKING")
        else:
            print("❌ Database Service: FAILED")
            
    except Exception as e:
        print(f"❌ Database Service: ERROR - {e}")
    
    # Test 4: Monitoring Service
    try:
        from app.services.monitoring_service import MetricsCollector
        monitor_service = MetricsCollector()
        
        # Test monitoring
        metrics = monitor_service.get_metrics_summary()
        if "uptime" in metrics:
            print("✅ Monitoring Service: WORKING")
        else:
            print("❌ Monitoring Service: FAILED")
            
    except Exception as e:
        print(f"❌ Monitoring Service: ERROR - {e}")
    
    # Test 5: Async Processing Service
    try:
        from app.services.async_processing_service import AsyncProcessingService
        async_service = AsyncProcessingService()
        
        # Test async processing
        stats = await async_service.get_stats()
        if stats.get("status") == "active":
            print("✅ Async Processing Service: WORKING")
        else:
            print("❌ Async Processing Service: FAILED")
            
    except Exception as e:
        print(f"❌ Async Processing Service: ERROR - {e}")
    
    # Test 6: Simple Search Service
    try:
        from app.services.simple_search_service import SimpleSearchService
        search_service = SimpleSearchService()
        
        # Test search
        results = await search_service.search_by_text("test query", limit=5)
        if results and len(results) > 0:
            print("✅ Search Service: WORKING")
        else:
            print("❌ Search Service: FAILED")
            
    except Exception as e:
        print(f"❌ Search Service: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Performance Optimization Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_performance_services())
