import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8001))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
    
    # Model Configuration
    CLIP_MODEL_NAME = os.getenv("CLIP_MODEL_NAME", "openai/clip-vit-base-patch32")
    DEVICE = os.getenv("DEVICE", "auto")  # auto, cpu, cuda
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    
    # Search Configuration
    DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", 20))
    MAX_SEARCH_LIMIT = int(os.getenv("MAX_SEARCH_LIMIT", 100))

settings = Settings()
