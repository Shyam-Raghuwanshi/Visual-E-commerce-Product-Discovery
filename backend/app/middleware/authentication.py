import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import time

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API Keys for different access levels
API_KEYS = {
    "basic": os.getenv("BASIC_API_KEY", "basic_api_key_123"),
    "premium": os.getenv("PREMIUM_API_KEY", "premium_api_key_456"),
    "enterprise": os.getenv("ENTERPRISE_API_KEY", "enterprise_api_key_789")
}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthLevel:
    """Authentication levels"""
    NONE = "none"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    JWT = "jwt"

def get_api_key_level(api_key: str) -> Optional[str]:
    """Get the access level for an API key"""
    for level, key in API_KEYS.items():
        if api_key == key:
            return level
    return None

async def verify_api_key(request: Request) -> Optional[Dict[str, Any]]:
    """Verify API key from request headers"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
    
    level = get_api_key_level(api_key)
    if not level:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return {
        "auth_type": "api_key",
        "level": level,
        "api_key": api_key
    }

async def verify_jwt_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Verify JWT token from Authorization header"""
    if not credentials:
        return None
    
    try:
        payload = verify_token(credentials.credentials)
        return {
            "auth_type": "jwt",
            "level": "jwt",
            "user_id": payload.get("sub"),
            "payload": payload
        }
    except HTTPException:
        return None

async def get_current_user(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user (API key or JWT)"""
    # Try API key first
    api_auth = await verify_api_key(request)
    if api_auth:
        return api_auth
    
    # Try JWT token
    jwt_auth = await verify_jwt_token(credentials)
    if jwt_auth:
        return jwt_auth
    
    # No authentication provided
    return {
        "auth_type": "none",
        "level": "none"
    }

def require_auth_level(required_level: str):
    """Decorator to require specific authentication level"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and user from kwargs
            request = kwargs.get('request')
            current_user = kwargs.get('current_user')
            
            if not current_user or current_user.get("level") == "none":
                if required_level != "none":
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication required"
                    )
            
            user_level = current_user.get("level", "none")
            
            # Check if user has required access level
            level_hierarchy = ["none", "basic", "premium", "enterprise", "jwt"]
            required_index = level_hierarchy.index(required_level) if required_level in level_hierarchy else 0
            user_index = level_hierarchy.index(user_level) if user_level in level_hierarchy else 0
            
            if user_index < required_index:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions. Required: {required_level}, Current: {user_level}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class AuthenticationMiddleware:
    """Authentication middleware for different endpoint types"""
    
    def __init__(self):
        self.endpoint_auth_requirements = {
            "/api/search/image": AuthLevel.BASIC,
            "/api/search/text": AuthLevel.NONE,  # Free tier
            "/api/search/combined": AuthLevel.PREMIUM,
            "/api/search/filters": AuthLevel.PREMIUM,
            "/api/products/": AuthLevel.NONE,  # Free tier
            "/api/upload": AuthLevel.BASIC,
        }
    
    def get_required_auth_level(self, path: str) -> str:
        """Get required authentication level for a path"""
        for endpoint, level in self.endpoint_auth_requirements.items():
            if path.startswith(endpoint):
                return level
        return AuthLevel.NONE
    
    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate request based on path requirements"""
        required_level = self.get_required_auth_level(request.url.path)
        
        # Skip authentication for health checks and docs
        if request.url.path in ["/", "/api/health", "/docs", "/redoc", "/openapi.json"]:
            return {"auth_type": "none", "level": "none"}
        
        current_user = await get_current_user(request)
        
        # Check if authentication is required
        if required_level != AuthLevel.NONE and current_user.get("level") == "none":
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication required",
                    "required_level": required_level,
                    "message": "This endpoint requires authentication. Please provide a valid API key or JWT token."
                }
            )
        
        # Check if user has sufficient permissions
        level_hierarchy = ["none", "basic", "premium", "enterprise", "jwt"]
        required_index = level_hierarchy.index(required_level) if required_level in level_hierarchy else 0
        user_index = level_hierarchy.index(current_user.get("level", "none")) if current_user.get("level") in level_hierarchy else 0
        
        if user_index < required_index:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Insufficient permissions",
                    "required_level": required_level,
                    "current_level": current_user.get("level"),
                    "message": f"This endpoint requires {required_level} level access or higher."
                }
            )
        
        return current_user

# Global authentication middleware instance
auth_middleware = AuthenticationMiddleware()

async def authentication_middleware(request: Request, call_next):
    """Middleware to handle authentication"""
    try:
        # Authenticate the request
        user = await auth_middleware.authenticate_request(request)
        
        # Add user info to request state
        request.state.user = user
        
        # Process request
        response = await call_next(request)
        
        # Add auth headers to response
        if user.get("auth_type") != "none":
            response.headers["X-Auth-Level"] = user.get("level", "none")
            response.headers["X-Auth-Type"] = user.get("auth_type", "none")
        
        return response
        
    except HTTPException as e:
        raise e
