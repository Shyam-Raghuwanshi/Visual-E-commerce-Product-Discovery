"""
Configuration settings for the CLIP service.
This file contains all configurable parameters for the enhanced CLIP implementation.
"""

import os
from typing import Dict, Any

class CLIPConfig:
    """Configuration class for CLIP service settings"""
    
    # Model Configuration
    DEFAULT_MODEL_NAME = "openai/clip-vit-base-patch32"
    ALTERNATIVE_MODELS = [
        "openai/clip-vit-base-patch32",
        "openai/clip-vit-base-patch16",
        "openai/clip-vit-large-patch14"
    ]
    
    # Performance Configuration
    DEFAULT_BATCH_SIZE = 32
    MAX_BATCH_SIZE = 128
    MIN_BATCH_SIZE = 1
    
    # Memory Management
    GPU_MEMORY_THRESHOLD_GB = 4  # Minimum GPU memory for CLIP
    SYSTEM_MEMORY_THRESHOLD_GB = 8  # Warning threshold for system memory
    ENABLE_MEMORY_MONITORING = True
    
    # Threading Configuration
    DEFAULT_MAX_WORKERS = 4
    MAX_WORKERS_LIMIT = 16
    
    # Text Processing
    MAX_TEXT_LENGTH = 77  # CLIP's maximum text token length
    TEXT_TRUNCATION = True
    TEXT_PADDING = True
    
    # Image Processing
    IMAGE_SIZE = (224, 224)  # Standard CLIP image size
    FORCE_RGB_CONVERSION = True
    
    # Caching Configuration
    ENABLE_MODEL_CACHING = True
    CACHE_EMBEDDINGS = False  # Set to True to cache embeddings (requires more memory)
    MAX_EMBEDDING_CACHE_SIZE = 1000
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_PERFORMANCE_METRICS = True
    LOG_MEMORY_USAGE = True
    
    # Error Handling
    RETRY_ON_CUDA_OOM = True
    MAX_RETRIES = 3
    FALLBACK_TO_CPU = True
    
    # Environment Variables
    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        return {
            "model_name": os.getenv("CLIP_MODEL_NAME", cls.DEFAULT_MODEL_NAME),
            "batch_size": int(os.getenv("CLIP_BATCH_SIZE", cls.DEFAULT_BATCH_SIZE)),
            "max_workers": int(os.getenv("CLIP_MAX_WORKERS", cls.DEFAULT_MAX_WORKERS)),
            "gpu_memory_threshold": float(os.getenv("CLIP_GPU_MEMORY_THRESHOLD", cls.GPU_MEMORY_THRESHOLD_GB)),
            "enable_caching": os.getenv("CLIP_ENABLE_CACHING", "true").lower() == "true",
            "log_level": os.getenv("CLIP_LOG_LEVEL", cls.LOG_LEVEL),
            "fallback_to_cpu": os.getenv("CLIP_FALLBACK_TO_CPU", "true").lower() == "true",
        }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize configuration parameters"""
        validated = config.copy()
        
        # Validate batch size
        batch_size = validated.get("batch_size", cls.DEFAULT_BATCH_SIZE)
        validated["batch_size"] = max(cls.MIN_BATCH_SIZE, min(cls.MAX_BATCH_SIZE, batch_size))
        
        # Validate max workers
        max_workers = validated.get("max_workers", cls.DEFAULT_MAX_WORKERS)
        validated["max_workers"] = max(1, min(cls.MAX_WORKERS_LIMIT, max_workers))
        
        # Validate model name
        model_name = validated.get("model_name", cls.DEFAULT_MODEL_NAME)
        if model_name not in cls.ALTERNATIVE_MODELS:
            validated["model_name"] = cls.DEFAULT_MODEL_NAME
        
        return validated

# Default configuration instance
DEFAULT_CONFIG = CLIPConfig.from_env()
VALIDATED_CONFIG = CLIPConfig.validate_config(DEFAULT_CONFIG)
