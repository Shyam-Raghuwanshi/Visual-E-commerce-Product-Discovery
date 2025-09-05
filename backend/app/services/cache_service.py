"""
Advanced caching service with Redis and in-memory fallback for performance optimization.
Supports multiple cache strategies, automatic invalidation, and performance monitoring.
"""

import json
import pickle
import hashlib
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import os
from dataclasses import dataclass
from collections import defaultdict
import time

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import redis
        REDIS_AVAILABLE = True
    except ImportError:
        redis = None
        REDIS_AVAILABLE = False

try:
    from aiocache import Cache, cached
    from aiocache.serializers import PickleSerializer
    AIOCACHE_AVAILABLE = True
except ImportError:
    AIOCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_size: int = 0
    avg_get_time: float = 0.0
    avg_set_time: float = 0.0

class CacheKey:
    """Cache key generation utilities"""
    
    @staticmethod
    def search_results(query: str, filters: Dict, limit: int) -> str:
        """Generate cache key for search results"""
        key_data = {
            "query": query.lower().strip() if query else "",
            "filters": sorted(filters.items()) if filters else [],
            "limit": limit
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"search:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    @staticmethod
    def image_embedding(image_hash: str) -> str:
        """Generate cache key for image embeddings"""
        return f"img_embed:{image_hash}"
    
    @staticmethod
    def text_embedding(text: str) -> str:
        """Generate cache key for text embeddings"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"txt_embed:{text_hash}"
    
    @staticmethod
    def product_details(product_id: str) -> str:
        """Generate cache key for product details"""
        return f"product:{product_id}"
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        """Generate cache key for user profiles"""
        return f"user:{user_id}"
    
    @staticmethod
    def recommendations(user_id: str, context: str) -> str:
        """Generate cache key for user recommendations"""
        return f"rec:{user_id}:{context}"

class PerformanceCacheService:
    """High-performance caching service with Redis and fallback mechanisms"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_ttl: Dict[str, datetime] = {}
        self.stats = CacheStats()
        self.operation_times = defaultdict(list)
        self.max_memory_items = 10000
        self.default_ttl = 3600  # 1 hour
        
        # TTL configurations for different cache types
        self.ttl_config = {
            "search": 1800,      # 30 minutes
            "embed": 7200,       # 2 hours
            "product": 3600,     # 1 hour
            "user": 1800,        # 30 minutes
            "rec": 900,          # 15 minutes
        }
    
    async def initialize(self):
        """Initialize Redis connection with fallback"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using memory cache only")
            return
            
        try:
            if hasattr(redis, 'from_url'):
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    max_connections=20
                )
            else:
                # Fallback for older redis versions
                self.redis_client = redis.Redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            # Test connection
            if hasattr(self.redis_client, 'ping'):
                await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed, using memory cache only: {e}")
            self.redis_client = None
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with performance tracking"""
        start_time = time.time()
        
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    value = await self.redis_client.get(key)
                    if value is not None:
                        self.stats.hits += 1
                        self._record_operation_time("get", time.time() - start_time)
                        return pickle.loads(value)
                except Exception as e:
                    logger.error(f"Redis get error for key {key}: {e}")
                    self.stats.errors += 1
            
            # Fallback to memory cache
            if key in self.memory_cache:
                # Check TTL
                if key in self.memory_cache_ttl:
                    if datetime.now() > self.memory_cache_ttl[key]:
                        del self.memory_cache[key]
                        del self.memory_cache_ttl[key]
                        self.stats.misses += 1
                        return default
                
                self.stats.hits += 1
                self._record_operation_time("get", time.time() - start_time)
                return self.memory_cache[key]
            
            self.stats.misses += 1
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats.errors += 1
            return default
        finally:
            self._record_operation_time("get", time.time() - start_time)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        start_time = time.time()
        
        if ttl is None:
            # Determine TTL based on key prefix
            key_type = key.split(":")[0]
            ttl = self.ttl_config.get(key_type, self.default_ttl)
        
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    serialized_value = pickle.dumps(value)
                    await self.redis_client.setex(key, ttl, serialized_value)
                    self.stats.sets += 1
                    self._record_operation_time("set", time.time() - start_time)
                    return True
                except Exception as e:
                    logger.error(f"Redis set error for key {key}: {e}")
                    self.stats.errors += 1
            
            # Fallback to memory cache
            self._cleanup_memory_cache()
            self.memory_cache[key] = value
            self.memory_cache_ttl[key] = datetime.now() + timedelta(seconds=ttl)
            self.stats.sets += 1
            self._record_operation_time("set", time.time() - start_time)
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            # Delete from Redis
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except Exception as e:
                    logger.error(f"Redis delete error for key {key}: {e}")
            
            # Delete from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.memory_cache_ttl:
                del self.memory_cache_ttl[key]
            
            self.stats.deletes += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.stats.errors += 1
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        deleted_count = 0
        
        try:
            # Delete from Redis
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        deleted_count += await self.redis_client.delete(*keys)
                except Exception as e:
                    logger.error(f"Redis pattern delete error for pattern {pattern}: {e}")
            
            # Delete from memory cache
            memory_keys_to_delete = [k for k in self.memory_cache.keys() if self._matches_pattern(k, pattern)]
            for key in memory_keys_to_delete:
                del self.memory_cache[key]
                if key in self.memory_cache_ttl:
                    del self.memory_cache_ttl[key]
                deleted_count += 1
            
            self.stats.deletes += deleted_count
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache pattern delete error for pattern {pattern}: {e}")
            self.stats.errors += 1
            return 0
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache efficiently"""
        results = {}
        
        if not keys:
            return results
        
        # Try Redis first
        if self.redis_client:
            try:
                values = await self.redis_client.mget(keys)
                for i, (key, value) in enumerate(zip(keys, values)):
                    if value is not None:
                        results[key] = pickle.loads(value)
                        self.stats.hits += 1
                    else:
                        self.stats.misses += 1
                return results
            except Exception as e:
                logger.error(f"Redis mget error: {e}")
                self.stats.errors += 1
        
        # Fallback to memory cache
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        
        return results
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache efficiently"""
        if not mapping:
            return True
        
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    pipe = self.redis_client.pipeline()
                    for key, value in mapping.items():
                        key_ttl = ttl or self.ttl_config.get(key.split(":")[0], self.default_ttl)
                        serialized_value = pickle.dumps(value)
                        pipe.setex(key, key_ttl, serialized_value)
                    await pipe.execute()
                    self.stats.sets += len(mapping)
                    return True
                except Exception as e:
                    logger.error(f"Redis mset error: {e}")
                    self.stats.errors += 1
            
            # Fallback to memory cache
            for key, value in mapping.items():
                await self.set(key, value, ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache mset error: {e}")
            self.stats.errors += 1
            return False
    
    def _cleanup_memory_cache(self):
        """Clean up memory cache to prevent memory leaks"""
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove expired items first
            expired_keys = []
            now = datetime.now()
            for key, expiry in self.memory_cache_ttl.items():
                if now > expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                del self.memory_cache_ttl[key]
            
            # If still too many items, remove oldest
            if len(self.memory_cache) >= self.max_memory_items:
                # Remove 20% of items (FIFO)
                keys_to_remove = list(self.memory_cache.keys())[:int(self.max_memory_items * 0.2)]
                for key in keys_to_remove:
                    if key in self.memory_cache:
                        del self.memory_cache[key]
                    if key in self.memory_cache_ttl:
                        del self.memory_cache_ttl[key]
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for memory cache"""
        if "*" not in pattern:
            return key == pattern
        
        # Convert Redis-style pattern to Python regex-style
        import re
        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", key))
    
    def _record_operation_time(self, operation: str, duration: float):
        """Record operation timing for performance monitoring"""
        self.operation_times[operation].append(duration)
        
        # Keep only last 1000 operations per type
        if len(self.operation_times[operation]) > 1000:
            self.operation_times[operation] = self.operation_times[operation][-1000:]
        
        # Update average
        times = self.operation_times[operation]
        if operation == "get":
            self.stats.avg_get_time = sum(times) / len(times)
        elif operation == "set":
            self.stats.avg_set_time = sum(times) / len(times)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        hit_rate = self.stats.hits / (self.stats.hits + self.stats.misses) if (self.stats.hits + self.stats.misses) > 0 else 0
        
        return {
            "cache_stats": {
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "hit_rate": hit_rate,
                "sets": self.stats.sets,
                "deletes": self.stats.deletes,
                "errors": self.stats.errors,
                "avg_get_time_ms": self.stats.avg_get_time * 1000,
                "avg_set_time_ms": self.stats.avg_set_time * 1000,
            },
            "redis_connected": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "operation_counts": {
                "get_operations": len(self.operation_times["get"]),
                "set_operations": len(self.operation_times["set"]),
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        health = {
            "redis_connected": False,
            "redis_latency_ms": None,
            "memory_cache_items": len(self.memory_cache),
            "status": "unhealthy"
        }
        
        if self.redis_client:
            try:
                start_time = time.time()
                await self.redis_client.ping()
                latency = (time.time() - start_time) * 1000
                health["redis_connected"] = True
                health["redis_latency_ms"] = round(latency, 2)
            except Exception as e:
                logger.error(f"Redis health check failed: {e}")
        
        health["status"] = "healthy" if health["redis_connected"] or health["memory_cache_items"] >= 0 else "unhealthy"
        return health

# Decorator for automatic caching
def cache_result(ttl: int = 3600, key_prefix: str = "cached"):
    """Decorator to automatically cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": sorted(kwargs.items())
            }
            key_str = json.dumps(key_data, sort_keys=True)
            cache_key = f"{key_prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"
            
            # Try to get from cache
            if hasattr(wrapper, "_cache_service"):
                cached_result = await wrapper._cache_service.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            if hasattr(wrapper, "_cache_service"):
                await wrapper._cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global cache service instance
cache_service = PerformanceCacheService()

# Convenience functions
async def get_cached(key: str, default: Any = None) -> Any:
    """Get value from global cache"""
    return await cache_service.get(key, default)

async def set_cached(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in global cache"""
    return await cache_service.set(key, value, ttl)

async def delete_cached(key: str) -> bool:
    """Delete key from global cache"""
    return await cache_service.delete(key)

async def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate cache keys matching pattern"""
    return await cache_service.delete_pattern(pattern)
