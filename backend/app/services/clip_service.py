import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import logging
import gc
import asyncio
from functools import lru_cache
from typing import List, Union, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading
from contextlib import contextmanager
import os
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLIPModelCache:
    """Singleton class to manage CLIP model caching"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.model = None
            self.processor = None
            self.device = None
            self.model_name = None
            self._initialized = True

class CLIPService:
    """
    Enhanced CLIP Service with proper error handling, memory management, 
    batch processing, and model caching capabilities.
    """
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", 
                 batch_size: int = 32, max_workers: int = 4,
                 gpu_memory_threshold: float = 4.0, enable_caching: bool = True,
                 log_level: str = "INFO", fallback_to_cpu: bool = True,
                 **kwargs):
        """
        Initialize CLIP service with enhanced features.
        
        Args:
            model_name: CLIP model identifier
            batch_size: Maximum batch size for processing
            max_workers: Maximum number of worker threads
            gpu_memory_threshold: Minimum GPU memory in GB for CUDA usage
            enable_caching: Enable model caching
            log_level: Logging level
            fallback_to_cpu: Whether to fallback to CPU on GPU errors
            **kwargs: Additional configuration parameters (ignored)
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.gpu_memory_threshold = gpu_memory_threshold
        self.enable_caching = enable_caching
        self.fallback_to_cpu = fallback_to_cpu
        self.cache = CLIPModelCache()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Device selection with memory management
        self.device = self._select_device()
        logger.info(f"Using device: {self.device}")
        
        # Load model if not cached
        self._ensure_model_loaded()
    
    def _select_device(self) -> str:
        """Smart device selection based on available resources"""
        if torch.cuda.is_available():
            # Check GPU memory
            gpu_memory = torch.cuda.get_device_properties(0).total_memory
            gpu_memory_gb = gpu_memory / (1024**3)
            
            if gpu_memory_gb >= self.gpu_memory_threshold:
                return "cuda"
            else:
                logger.warning(f"GPU memory ({gpu_memory_gb:.1f}GB) insufficient for CLIP. Using CPU.")
        
        # Check system RAM
        system_memory = psutil.virtual_memory()
        if system_memory.total < 8 * (1024**3):  # Less than 8GB RAM
            logger.warning("Low system memory detected. Consider reducing batch size.")
        
        return "cpu"
    
    def _ensure_model_loaded(self):
        """Ensure model is loaded with proper caching"""
        if (self.cache.model is None or 
            self.cache.model_name != self.model_name or 
            self.cache.device != self.device):
            self._load_model()
    
    def _load_model(self):
        """Load CLIP model and processor with comprehensive error handling"""
        try:
            logger.info(f"Loading CLIP model: {self.model_name}")
            
            # Clear any existing model to free memory
            if self.cache.model is not None:
                del self.cache.model
                del self.cache.processor
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
            
            # Load model and processor
            self.cache.model = CLIPModel.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.cache.processor = CLIPProcessor.from_pretrained(self.model_name)
            
            # Move to device and set eval mode
            self.cache.model.to(self.device)
            self.cache.model.eval()
            
            # Cache model info
            self.cache.device = self.device
            self.cache.model_name = self.model_name
            
            logger.info("CLIP model loaded successfully")
            
        except torch.cuda.OutOfMemoryError:
            logger.error("CUDA out of memory. Falling back to CPU.")
            self.device = "cpu"
            self._load_model_cpu_fallback()
            
        except Exception as e:
            logger.error(f"Error loading CLIP model: {e}")
            # Try CPU fallback
            if self.device != "cpu":
                logger.info("Attempting CPU fallback...")
                self.device = "cpu"
                self._load_model_cpu_fallback()
            else:
                raise RuntimeError(f"Failed to load CLIP model: {e}")
    
    def _load_model_cpu_fallback(self):
        """Fallback method to load model on CPU"""
        try:
            self.cache.model = CLIPModel.from_pretrained(self.model_name)
            self.cache.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.cache.model.to("cpu")
            self.cache.model.eval()
            self.cache.device = "cpu"
            self.cache.model_name = self.model_name
            logger.info("CLIP model loaded on CPU successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load CLIP model even on CPU: {e}")
    
    @contextmanager
    def _memory_management(self):
        """Context manager for memory management during inference"""
        try:
            yield
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def _validate_inputs(self, inputs: Union[str, List[str], Image.Image, List[Image.Image]]) -> bool:
        """Validate input data"""
        if inputs is None:
            return False
        
        if isinstance(inputs, list) and len(inputs) == 0:
            return False
        
        if isinstance(inputs, str) and len(inputs.strip()) == 0:
            return False
        
        return True
    
    def _process_in_batches(self, items: List, process_func, batch_size: Optional[int] = None) -> np.ndarray:
        """Process items in batches for memory efficiency"""
        if batch_size is None:
            batch_size = self.batch_size
        
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_result = process_func(batch)
            results.append(batch_result)
        
        return np.vstack(results) if results else np.array([])
    
    async def encode_text(self, text: str) -> np.ndarray:
        """
        Encode single text to embedding vector with error handling.
        
        Args:
            text: Input text string
            
        Returns:
            Normalized embedding vector
            
        Raises:
            ValueError: If text is invalid
            RuntimeError: If encoding fails
        """
        if not self._validate_inputs(text):
            raise ValueError("Invalid text input")
        
        try:
            self._ensure_model_loaded()
            
            with self._memory_management():
                inputs = self.cache.processor(
                    text=[text], 
                    return_tensors="pt", 
                    padding=True,
                    truncation=True,
                    max_length=77
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    text_features = self.cache.model.get_text_features(**inputs)
                    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                return text_features.cpu().numpy()[0]
                
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise RuntimeError(f"Failed to encode text: {e}")
    
    async def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Encode single image to embedding vector with error handling.
        
        Args:
            image: PIL Image object
            
        Returns:
            Normalized embedding vector
            
        Raises:
            ValueError: If image is invalid
            RuntimeError: If encoding fails
        """
        if not isinstance(image, Image.Image):
            raise ValueError("Input must be a PIL Image")
        
        try:
            self._ensure_model_loaded()
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            with self._memory_management():
                inputs = self.cache.processor(
                    images=[image], 
                    return_tensors="pt", 
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    image_features = self.cache.model.get_image_features(**inputs)
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                return image_features.cpu().numpy()[0]
                
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise RuntimeError(f"Failed to encode image: {e}")
    
    async def encode_batch_text(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Encode multiple texts to embedding vectors with batch processing.
        
        Args:
            texts: List of text strings
            batch_size: Override default batch size
            
        Returns:
            Array of normalized embedding vectors
            
        Raises:
            ValueError: If texts list is invalid
            RuntimeError: If encoding fails
        """
        if not self._validate_inputs(texts):
            raise ValueError("Invalid texts input")
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in texts if text and text.strip()]
        if not valid_texts:
            raise ValueError("No valid texts provided")
        
        try:
            self._ensure_model_loaded()
            
            def process_batch(batch_texts):
                with torch.no_grad():
                    inputs = self.cache.processor(
                        text=batch_texts, 
                        return_tensors="pt", 
                        padding=True, 
                        truncation=True,
                        max_length=77
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    text_features = self.cache.model.get_text_features(**inputs)
                    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                    
                    return text_features.cpu().numpy()
            
            # Process in batches if list is large
            if len(valid_texts) > (batch_size or self.batch_size):
                return self._process_in_batches(valid_texts, process_batch, batch_size)
            else:
                with self._memory_management():
                    return process_batch(valid_texts)
                    
        except Exception as e:
            logger.error(f"Error encoding batch texts: {e}")
            raise RuntimeError(f"Failed to encode batch texts: {e}")
    
    async def encode_batch_images(self, images: List[Image.Image], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Encode multiple images to embedding vectors with batch processing.
        
        Args:
            images: List of PIL Image objects
            batch_size: Override default batch size
            
        Returns:
            Array of normalized embedding vectors
            
        Raises:
            ValueError: If images list is invalid
            RuntimeError: If encoding fails
        """
        if not self._validate_inputs(images):
            raise ValueError("Invalid images input")
        
        # Validate and convert images
        valid_images = []
        for img in images:
            if isinstance(img, Image.Image):
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                valid_images.append(img)
        
        if not valid_images:
            raise ValueError("No valid images provided")
        
        try:
            self._ensure_model_loaded()
            
            def process_batch(batch_images):
                with torch.no_grad():
                    inputs = self.cache.processor(
                        images=batch_images, 
                        return_tensors="pt", 
                        padding=True
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    image_features = self.cache.model.get_image_features(**inputs)
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                    
                    return image_features.cpu().numpy()
            
            # Process in batches if list is large
            if len(valid_images) > (batch_size or self.batch_size):
                return self._process_in_batches(valid_images, process_batch, batch_size)
            else:
                with self._memory_management():
                    return process_batch(valid_images)
                    
        except Exception as e:
            logger.error(f"Error encoding batch images: {e}")
            raise RuntimeError(f"Failed to encode batch images: {e}")
    
    async def compute_similarity(self, text_embedding: np.ndarray, image_embedding: np.ndarray) -> float:
        """
        Compute cosine similarity between text and image embeddings.
        
        Args:
            text_embedding: Text embedding vector
            image_embedding: Image embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Ensure embeddings are normalized
            text_norm = text_embedding / np.linalg.norm(text_embedding)
            image_norm = image_embedding / np.linalg.norm(image_embedding)
            
            # Compute cosine similarity
            similarity = np.dot(text_norm, image_norm)
            
            # Convert to 0-1 range
            return (similarity + 1) / 2
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise RuntimeError(f"Failed to compute similarity: {e}")
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.cache.model_name,
            "device": self.cache.device,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "model_loaded": self.cache.model is not None
        }
    
    async def cleanup(self):
        """Clean up resources asynchronously"""
        try:
            if hasattr(self, 'cache') and self.cache.model is not None:
                del self.cache.model
                del self.cache.processor
                self.cache.model = None
                self.cache.processor = None
                
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            gc.collect()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
                
            logger.info("CLIP service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def cleanup_sync(self):
        """Synchronous cleanup for destructor"""
        try:
            if hasattr(self, 'cache') and self.cache.model is not None:
                del self.cache.model
                del self.cache.processor
                self.cache.model = None
                self.cache.processor = None
                
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            gc.collect()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
                
            logger.info("CLIP service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup_sync()
