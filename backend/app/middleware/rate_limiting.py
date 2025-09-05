import time
from typing import Dict, Tuple
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
import os
from datetime import datetime, timedelta

# Redis connection for distributed rate limiting
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.from_url(redis_url, decode_responses=True)
    redis_available = True
except:
    redis_client = None
    redis_available = False

# In-memory store as fallback
memory_store = {}

def get_identifier(request: Request):
    """Get client identifier for rate limiting"""
    # Try to get API key from headers
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Fall back to IP address
    return get_remote_address(request)

# Create limiter instance
limiter = Limiter(key_func=get_identifier)

class CustomRateLimiter:
    """Custom rate limiter with different limits for different endpoints"""
    
    def __init__(self):
        self.limits = {
            "search": {"requests": 100, "window": 3600},  # 100 requests per hour
            "upload": {"requests": 50, "window": 3600},   # 50 uploads per hour
            "product": {"requests": 200, "window": 3600}, # 200 product requests per hour
            "default": {"requests": 1000, "window": 3600} # Default limit
        }
    
    def is_allowed(self, identifier: str, endpoint_type: str = "default") -> Tuple[bool, Dict]:
        """Check if request is allowed"""
        limit_config = self.limits.get(endpoint_type, self.limits["default"])
        window_seconds = limit_config["window"]
        max_requests = limit_config["requests"]
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        if redis_available:
            return self._check_redis_limit(identifier, endpoint_type, window_start, current_time, max_requests)
        else:
            return self._check_memory_limit(identifier, endpoint_type, window_start, current_time, max_requests)
    
    def _check_redis_limit(self, identifier: str, endpoint_type: str, window_start: float, current_time: float, max_requests: int) -> Tuple[bool, Dict]:
        """Check rate limit using Redis"""
        try:
            key = f"rate_limit:{endpoint_type}:{identifier}"
            
            # Remove old entries
            redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_requests = redis_client.zcard(key)
            
            # Check if limit exceeded
            if current_requests >= max_requests:
                ttl = redis_client.ttl(key)
                return False, {
                    "requests_remaining": 0,
                    "reset_time": current_time + ttl,
                    "limit": max_requests
                }
            
            # Add current request
            redis_client.zadd(key, {str(current_time): current_time})
            redis_client.expire(key, 3600)  # 1 hour expiry
            
            return True, {
                "requests_remaining": max_requests - current_requests - 1,
                "reset_time": current_time + 3600,
                "limit": max_requests
            }
            
        except Exception:
            # Fall back to memory store
            return self._check_memory_limit(identifier, endpoint_type, window_start, current_time, max_requests)
    
    def _check_memory_limit(self, identifier: str, endpoint_type: str, window_start: float, current_time: float, max_requests: int) -> Tuple[bool, Dict]:
        """Check rate limit using in-memory store"""
        key = f"{endpoint_type}:{identifier}"
        
        if key not in memory_store:
            memory_store[key] = []
        
        # Remove old entries
        memory_store[key] = [req_time for req_time in memory_store[key] if req_time > window_start]
        
        # Check if limit exceeded
        if len(memory_store[key]) >= max_requests:
            oldest_request = min(memory_store[key]) if memory_store[key] else current_time
            return False, {
                "requests_remaining": 0,
                "reset_time": oldest_request + 3600,
                "limit": max_requests
            }
        
        # Add current request
        memory_store[key].append(current_time)
        
        return True, {
            "requests_remaining": max_requests - len(memory_store[key]),
            "reset_time": current_time + 3600,
            "limit": max_requests
        }

# Global rate limiter instance
rate_limiter = CustomRateLimiter()

def check_rate_limit(identifier: str, endpoint_type: str = "default"):
    """Decorator function to check rate limits"""
    allowed, info = rate_limiter.is_allowed(identifier, endpoint_type)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": info["limit"],
                "reset_time": info["reset_time"],
                "message": f"Too many requests. Try again after {datetime.fromtimestamp(info['reset_time'])}"
            },
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(info["reset_time"])),
                "Retry-After": str(int(info["reset_time"] - time.time()))
            }
        )
    
    return info

async def rate_limit_middleware(request: Request, call_next):
    """Middleware to apply rate limiting"""
    # Skip rate limiting for health checks
    if request.url.path in ["/", "/api/health", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        return response
    
    identifier = get_identifier(request)
    
    # Determine endpoint type
    endpoint_type = "default"
    if "/search/" in request.url.path:
        endpoint_type = "search"
    elif "/upload" in request.url.path:
        endpoint_type = "upload"
    elif "/products/" in request.url.path:
        endpoint_type = "product"
    
    # Check rate limit
    try:
        info = check_rate_limit(identifier, endpoint_type)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["requests_remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(info["reset_time"]))
        
        return response
        
    except HTTPException as e:
        # Rate limit exceeded
        raise e
