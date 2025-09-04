#!/usr/bin/env python3
"""
Vector Generation Pipeline for Visual E-commerce Product Discovery

This pipeline:
- Loads product data from JSON
- Downloads and processes product images
- Generates CLIP embeddings for both images and text descriptions
- Combines image and text vectors with proper weighting
- Stores vectors in Qdrant with metadata
- Includes progress tracking and error recovery
- Handles batch processing for large datasets

Author: Visual E-commerce Team
Date: September 2025
"""

import json
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import hashlib
import aiohttp
import aiofiles
from PIL import Image
import io
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from tqdm import tqdm
import traceback

# Add backend app to path for CLIP service import
sys.path.append(str(Path(__file__).parent.parent / "backend"))

try:
    from app.services.clip_service import CLIPService
    from app.services.vector_service import VectorService
    from app.utils.config import Config
    CLIP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"CLIP service not available: {e}")
    CLIP_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from qdrant_client.http import models as rest
    QDRANT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Qdrant client not available: {e}")
    QDRANT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vector_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingStats:
    """Statistics for processing pipeline"""
    total_products: int = 0
    processed_products: int = 0
    failed_products: int = 0
    skipped_products: int = 0
    images_downloaded: int = 0
    images_failed: int = 0
    text_embeddings_generated: int = 0
    image_embeddings_generated: int = 0
    vectors_stored: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_processing_rate(self) -> float:
        """Calculate processing rate in products per second"""
        if not self.start_time or not self.end_time:
            return 0.0
        
        duration = (self.end_time - self.start_time).total_seconds()
        return self.processed_products / duration if duration > 0 else 0.0

class ImageDownloader:
    """Async image downloader with caching and error handling"""
    
    def __init__(self, cache_dir: Path, max_concurrent: int = 10):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path for URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    async def download_image(self, url: str, product_id: str) -> Optional[Image.Image]:
        """Download and cache image with error handling"""
        async with self.semaphore:
            try:
                cache_path = self._get_cache_path(url)
                
                # Check cache first
                if cache_path.exists():
                    try:
                        return Image.open(cache_path).convert('RGB')
                    except Exception as e:
                        logger.warning(f"Cached image corrupted for {product_id}: {e}")
                        cache_path.unlink(missing_ok=True)
                
                # Download image
                async with self.session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Validate image
                        try:
                            image = Image.open(io.BytesIO(image_data)).convert('RGB')
                            
                            # Cache image
                            image.save(cache_path, 'JPEG', quality=85)
                            
                            return image
                            
                        except Exception as e:
                            logger.error(f"Invalid image data for {product_id}: {e}")
                            return None
                    else:
                        logger.warning(f"Failed to download image for {product_id}: HTTP {response.status}")
                        return None
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout downloading image for {product_id}")
                return None
            except Exception as e:
                logger.error(f"Error downloading image for {product_id}: {e}")
                return None
    
    def download_image_sync(self, url: str, product_id: str) -> Optional[Image.Image]:
        """Synchronous image download fallback"""
        try:
            cache_path = self._get_cache_path(url)
            
            # Check cache first
            if cache_path.exists():
                try:
                    return Image.open(cache_path).convert('RGB')
                except Exception:
                    cache_path.unlink(missing_ok=True)
            
            # Download image
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content)).convert('RGB')
                image.save(cache_path, 'JPEG', quality=85)
                return image
            else:
                logger.warning(f"Failed to download image for {product_id}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading image for {product_id}: {e}")
            return None

class VectorGenerator:
    """Generate and combine CLIP embeddings for products"""
    
    def __init__(self, 
                 text_weight: float = 0.7, 
                 image_weight: float = 0.3,
                 batch_size: int = 16):
        """
        Initialize vector generator
        
        Args:
            text_weight: Weight for text embeddings in final vector
            image_weight: Weight for image embeddings in final vector
            batch_size: Batch size for CLIP processing
        """
        self.text_weight = text_weight
        self.image_weight = image_weight
        self.batch_size = batch_size
        
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP service not available. Please install required dependencies.")
        
        self.clip_service = CLIPService(batch_size=batch_size)
        
    def create_text_description(self, product: Dict[str, Any]) -> str:
        """Create comprehensive text description for embedding"""
        components = []
        
        # Product name (highest priority)
        if product.get('name'):
            components.append(product['name'])
        
        # Category and subcategory
        if product.get('category'):
            components.append(product['category'])
        if product.get('subcategory'):
            components.append(product['subcategory'].replace('-', ' '))
        
        # Brand
        if product.get('brand'):
            components.append(product['brand'])
        
        # Key attributes
        for attr in ['color', 'material', 'gender', 'season']:
            if product.get(attr):
                components.append(str(product[attr]))
        
        # Description (if available)
        if product.get('description'):
            components.append(product['description'])
        
        # Tags
        tags = product.get('tags', [])
        if isinstance(tags, list):
            components.extend(tags)
        elif isinstance(tags, str):
            try:
                tag_list = json.loads(tags) if tags.startswith('[') else [tags]
                components.extend(tag_list)
            except:
                components.append(tags)
        
        return ' '.join(str(comp) for comp in components if comp)
    
    async def generate_text_embedding(self, product: Dict[str, Any]) -> Optional[np.ndarray]:
        """Generate text embedding for product"""
        try:
            text_description = self.create_text_description(product)
            if not text_description.strip():
                logger.warning(f"Empty text description for product {product.get('id', 'unknown')}")
                return None
            
            embedding = await self.clip_service.encode_text(text_description)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating text embedding for {product.get('id', 'unknown')}: {e}")
            return None
    
    async def generate_image_embedding(self, image: Image.Image, product_id: str) -> Optional[np.ndarray]:
        """Generate image embedding"""
        try:
            embedding = await self.clip_service.encode_image(image)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image embedding for {product_id}: {e}")
            return None
    
    def combine_embeddings(self, 
                          text_embedding: Optional[np.ndarray], 
                          image_embedding: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """Combine text and image embeddings with weighting"""
        if text_embedding is None and image_embedding is None:
            return None
        
        if text_embedding is None:
            return image_embedding
        
        if image_embedding is None:
            return text_embedding
        
        # Weighted combination
        combined = (self.text_weight * text_embedding + 
                   self.image_weight * image_embedding)
        
        # Normalize the combined vector
        combined = combined / np.linalg.norm(combined)
        
        return combined
    
    async def generate_batch_embeddings(self, 
                                       products: List[Dict[str, Any]], 
                                       images: List[Optional[Image.Image]]) -> List[Optional[np.ndarray]]:
        """Generate embeddings for a batch of products"""
        text_embeddings = []
        image_embeddings = []
        
        # Generate text embeddings in batch
        try:
            texts = [self.create_text_description(product) for product in products]
            valid_texts = [text for text in texts if text.strip()]
            
            if valid_texts:
                batch_text_embeddings = await self.clip_service.encode_batch_text(valid_texts)
                text_embedding_iter = iter(batch_text_embeddings)
                
                for text in texts:
                    if text.strip():
                        text_embeddings.append(next(text_embedding_iter))
                    else:
                        text_embeddings.append(None)
            else:
                text_embeddings = [None] * len(products)
                
        except Exception as e:
            logger.error(f"Error generating batch text embeddings: {e}")
            text_embeddings = [None] * len(products)
        
        # Generate image embeddings in batch
        try:
            valid_images = [img for img in images if img is not None]
            
            if valid_images:
                batch_image_embeddings = await self.clip_service.encode_batch_images(valid_images)
                image_embedding_iter = iter(batch_image_embeddings)
                
                for img in images:
                    if img is not None:
                        image_embeddings.append(next(image_embedding_iter))
                    else:
                        image_embeddings.append(None)
            else:
                image_embeddings = [None] * len(products)
                
        except Exception as e:
            logger.error(f"Error generating batch image embeddings: {e}")
            image_embeddings = [None] * len(products)
        
        # Combine embeddings
        combined_embeddings = []
        for text_emb, image_emb in zip(text_embeddings, image_embeddings):
            combined = self.combine_embeddings(text_emb, image_emb)
            combined_embeddings.append(combined)
        
        return combined_embeddings

class QdrantStorage:
    """Handle Qdrant vector storage"""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 6333,
                 collection_name: str = "products"):
        """Initialize Qdrant client"""
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not available. Please install qdrant-client.")
        
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        
    def create_collection(self, vector_size: int = 512, force_recreate: bool = False):
        """Create Qdrant collection"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name 
                                  for col in collections.collections)
            
            if collection_exists and force_recreate:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
                collection_exists = False
            
            if not collection_exists:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def prepare_metadata(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare product metadata for storage"""
        metadata = {}
        
        # Essential fields
        for field in ['id', 'name', 'category', 'subcategory', 'brand', 'price']:
            if field in product:
                metadata[field] = product[field]
        
        # Optional fields
        for field in ['color', 'material', 'gender', 'season', 'size', 
                     'rating', 'review_count', 'availability']:
            if field in product and product[field] is not None:
                metadata[field] = product[field]
        
        # Handle tags
        tags = product.get('tags', [])
        if isinstance(tags, list):
            metadata['tags'] = tags[:10]  # Limit tags
        elif isinstance(tags, str):
            try:
                tag_list = json.loads(tags) if tags.startswith('[') else [tags]
                metadata['tags'] = tag_list[:10]
            except:
                metadata['tags'] = [tags]
        
        # Add processing metadata
        metadata['processed_at'] = datetime.now().isoformat()
        
        return metadata
    
    def store_vectors(self, products: List[Dict[str, Any]], 
                     vectors: List[Optional[np.ndarray]]) -> int:
        """Store vectors in Qdrant"""
        points = []
        stored_count = 0
        
        for product, vector in zip(products, vectors):
            if vector is None:
                continue
            
            try:
                point_id = hashlib.md5(product['id'].encode()).hexdigest()
                metadata = self.prepare_metadata(product)
                
                point = PointStruct(
                    id=point_id,
                    vector=vector.tolist(),
                    payload=metadata
                )
                points.append(point)
                stored_count += 1
                
            except Exception as e:
                logger.error(f"Error preparing point for {product.get('id', 'unknown')}: {e}")
                continue
        
        if points:
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f"Stored {len(points)} vectors in Qdrant")
                
            except Exception as e:
                logger.error(f"Error storing vectors in Qdrant: {e}")
                raise
        
        return stored_count

class VectorGenerationPipeline:
    """Main pipeline for vector generation and storage"""
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None):
        """Initialize pipeline with configuration"""
        self.config = config or self._default_config()
        self.stats = ProcessingStats()
        self.progress_bar = None
        
        # Initialize components
        self.image_downloader = None
        self.vector_generator = None
        self.qdrant_storage = None
        
        # Setup directories
        self.cache_dir = Path(self.config['cache_dir'])
        self.output_dir = Path(self.config['output_dir'])
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _default_config(self) -> Dict[str, Any]:
        """Default pipeline configuration"""
        return {
            'batch_size': 16,
            'max_concurrent_downloads': 10,
            'text_weight': 0.7,
            'image_weight': 0.3,
            'qdrant_host': 'localhost',
            'qdrant_port': 6333,
            'collection_name': 'products',
            'cache_dir': 'data/image_cache',
            'output_dir': 'data/vectors',
            'force_recreate_collection': False,
            'save_embeddings': True,
            'resume_from_checkpoint': True
        }
    
    def load_products(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load products from JSON dataset"""
        try:
            logger.info(f"Loading dataset from {dataset_path}")
            
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            products = data.get('products', [])
            logger.info(f"Loaded {len(products)} products")
            
            return products
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def save_checkpoint(self, products: List[Dict[str, Any]], 
                       processed_indices: set, 
                       checkpoint_path: Path):
        """Save processing checkpoint"""
        try:
            checkpoint_data = {
                'processed_indices': list(processed_indices),
                'stats': self.stats.to_dict(),
                'config': self.config,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    def load_checkpoint(self, checkpoint_path: Path) -> Optional[set]:
        """Load processing checkpoint"""
        try:
            if not checkpoint_path.exists():
                return None
            
            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            processed_indices = set(checkpoint_data.get('processed_indices', []))
            logger.info(f"Loaded checkpoint with {len(processed_indices)} processed products")
            
            return processed_indices
            
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return None
    
    async def process_batch(self, 
                           batch_products: List[Dict[str, Any]], 
                           batch_indices: List[int]) -> Tuple[List[Optional[np.ndarray]], List[int]]:
        """Process a batch of products"""
        # Download images
        images = []
        
        for product in batch_products:
            image_url = product.get('image_url')
            product_id = product.get('id', 'unknown')
            
            if image_url:
                try:
                    image = await self.image_downloader.download_image(image_url, product_id)
                    images.append(image)
                    
                    if image:
                        self.stats.images_downloaded += 1
                    else:
                        self.stats.images_failed += 1
                        
                except Exception as e:
                    logger.error(f"Error downloading image for {product_id}: {e}")
                    images.append(None)
                    self.stats.images_failed += 1
            else:
                images.append(None)
        
        # Generate embeddings
        try:
            embeddings = await self.vector_generator.generate_batch_embeddings(
                batch_products, images
            )
            
            # Update stats
            for embedding in embeddings:
                if embedding is not None:
                    self.stats.text_embeddings_generated += 1
                    if any(img is not None for img in images):
                        self.stats.image_embeddings_generated += 1
            
            return embeddings, batch_indices
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(batch_products), batch_indices
    
    async def run_pipeline(self, dataset_path: str):
        """Run the complete vector generation pipeline"""
        try:
            self.stats.start_time = datetime.now()
            logger.info("Starting vector generation pipeline")
            
            # Load products
            products = self.load_products(dataset_path)
            self.stats.total_products = len(products)
            
            if not products:
                logger.error("No products to process")
                return
            
            # Initialize components
            logger.info("Initializing pipeline components...")
            
            self.vector_generator = VectorGenerator(
                text_weight=self.config['text_weight'],
                image_weight=self.config['image_weight'],
                batch_size=self.config['batch_size']
            )
            
            self.qdrant_storage = QdrantStorage(
                host=self.config['qdrant_host'],
                port=self.config['qdrant_port'],
                collection_name=self.config['collection_name']
            )
            
            # Create Qdrant collection
            self.qdrant_storage.create_collection(
                vector_size=512,  # CLIP embedding size
                force_recreate=self.config['force_recreate_collection']
            )
            
            # Setup checkpoint
            checkpoint_path = self.output_dir / 'processing_checkpoint.json'
            processed_indices = set()
            
            if self.config['resume_from_checkpoint']:
                loaded_indices = self.load_checkpoint(checkpoint_path)
                if loaded_indices:
                    processed_indices = loaded_indices
            
            # Initialize progress bar
            remaining_products = len(products) - len(processed_indices)
            self.progress_bar = tqdm(
                total=remaining_products,
                desc="Processing products",
                unit="products"
            )
            
            # Process in batches
            async with ImageDownloader(
                self.cache_dir,
                max_concurrent=self.config['max_concurrent_downloads']
            ) as image_downloader:
                
                self.image_downloader = image_downloader
                batch_size = self.config['batch_size']
                
                for i in range(0, len(products), batch_size):
                    batch_end = min(i + batch_size, len(products))
                    batch_indices = list(range(i, batch_end))
                    
                    # Skip already processed products
                    unprocessed_indices = [idx for idx in batch_indices 
                                         if idx not in processed_indices]
                    
                    if not unprocessed_indices:
                        continue
                    
                    batch_products = [products[idx] for idx in unprocessed_indices]
                    
                    try:
                        # Process batch
                        embeddings, indices = await self.process_batch(
                            batch_products, unprocessed_indices
                        )
                        
                        # Store in Qdrant
                        stored_count = self.qdrant_storage.store_vectors(
                            batch_products, embeddings
                        )
                        
                        self.stats.vectors_stored += stored_count
                        self.stats.processed_products += len(batch_products)
                        
                        # Update processed indices
                        processed_indices.update(unprocessed_indices)
                        
                        # Update progress
                        self.progress_bar.update(len(batch_products))
                        
                        # Save checkpoint periodically
                        if len(processed_indices) % (batch_size * 10) == 0:
                            self.save_checkpoint(products, processed_indices, checkpoint_path)
                        
                    except Exception as e:
                        logger.error(f"Error processing batch {i}-{batch_end}: {e}")
                        self.stats.failed_products += len(batch_products)
                        traceback.print_exc()
                        continue
            
            # Final checkpoint save
            self.save_checkpoint(products, processed_indices, checkpoint_path)
            
            # Close progress bar
            if self.progress_bar:
                self.progress_bar.close()
            
            self.stats.end_time = datetime.now()
            
            # Save final statistics
            await self.save_final_stats()
            
            logger.info("Vector generation pipeline completed!")
            self.print_final_stats()
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            traceback.print_exc()
            raise
    
    async def save_final_stats(self):
        """Save final processing statistics"""
        try:
            stats_file = self.output_dir / 'processing_stats.json'
            
            with open(stats_file, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Statistics saved to {stats_file}")
            
        except Exception as e:
            logger.error(f"Error saving statistics: {e}")
    
    def print_final_stats(self):
        """Print final processing statistics"""
        logger.info("=" * 60)
        logger.info("VECTOR GENERATION PIPELINE RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total products: {self.stats.total_products}")
        logger.info(f"Processed products: {self.stats.processed_products}")
        logger.info(f"Failed products: {self.stats.failed_products}")
        logger.info(f"Images downloaded: {self.stats.images_downloaded}")
        logger.info(f"Images failed: {self.stats.images_failed}")
        logger.info(f"Text embeddings: {self.stats.text_embeddings_generated}")
        logger.info(f"Image embeddings: {self.stats.image_embeddings_generated}")
        logger.info(f"Vectors stored: {self.stats.vectors_stored}")
        
        if self.stats.start_time and self.stats.end_time:
            duration = self.stats.end_time - self.stats.start_time
            rate = self.stats.get_processing_rate()
            logger.info(f"Processing time: {duration}")
            logger.info(f"Processing rate: {rate:.2f} products/second")
        
        logger.info("=" * 60)

def main():
    """Main function to run the vector generation pipeline"""
    try:
        # Configuration
        config = {
            'batch_size': 8,  # Smaller batch for memory efficiency
            'max_concurrent_downloads': 5,
            'text_weight': 0.7,
            'image_weight': 0.3,
            'qdrant_host': 'localhost',
            'qdrant_port': 6333,
            'collection_name': 'products',
            'cache_dir': str(Path(__file__).parent.parent / 'data' / 'image_cache'),
            'output_dir': str(Path(__file__).parent.parent / 'data' / 'vectors'),
            'force_recreate_collection': False,
            'save_embeddings': True,
            'resume_from_checkpoint': True
        }
        
        # Dataset path
        dataset_path = Path(__file__).parent.parent / 'data' / 'product_dataset.json'
        
        if not dataset_path.exists():
            logger.error(f"Dataset not found: {dataset_path}")
            logger.info("Please run create_product_dataset.py first")
            return
        
        # Check dependencies
        if not CLIP_AVAILABLE:
            logger.error("CLIP service not available. Please check your backend setup.")
            logger.info("To fix this, ensure the backend dependencies are installed:")
            logger.info("cd backend && pip install -r requirements.txt")
            return
        
        if not QDRANT_AVAILABLE:
            logger.error("Qdrant client not available. Please install: pip install qdrant-client")
            logger.info("To fix this, run: pip install qdrant-client")
            return
        
        # Verify Qdrant is running
        try:
            from qdrant_client import QdrantClient
            test_client = QdrantClient(host=config['qdrant_host'], port=config['qdrant_port'])
            test_client.get_collections()
            logger.info("Qdrant connection verified")
        except Exception as e:
            logger.error(f"Cannot connect to Qdrant: {e}")
            logger.info("Please ensure Qdrant is running:")
            logger.info("docker run -p 6333:6333 qdrant/qdrant")
            return
        
        # Initialize and run pipeline
        pipeline = VectorGenerationPipeline(config)
        asyncio.run(pipeline.run_pipeline(str(dataset_path)))
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
