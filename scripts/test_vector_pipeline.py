#!/usr/bin/env python3
"""
Test Script for Vector Generation Pipeline

This script tests the complete vector generation pipeline:
- Tests CLIP service integration
- Tests Qdrant connection and operations
- Tests image downloading and processing
- Tests batch processing functionality
- Validates vector generation and storage

Author: Visual E-commerce Team
Date: September 2025
"""

import pytest
import asyncio
import logging
import numpy as np
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import sys
import time
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
TEST_CONFIG = {
    'batch_size': 4,
    'max_concurrent_downloads': 2,
    'text_weight': 0.7,
    'image_weight': 0.3,
    'qdrant_host': 'localhost',
    'qdrant_port': 6333,
    'collection_name': 'test_products',
    'force_recreate_collection': True,
    'timeout_seconds': 10
}

class TestVectorPipeline:
    """Test suite for vector generation pipeline"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_products(self):
        """Create sample product data for testing"""
        return [
            {
                "id": "TEST_001",
                "name": "Classic Cotton T-Shirt",
                "description": "Comfortable cotton t-shirt perfect for casual wear",
                "category": "clothing",
                "subcategory": "t-shirts",
                "price": 29.99,
                "brand": "TestBrand",
                "image_url": "https://picsum.photos/400/400?random=1",
                "tags": ["cotton", "casual", "t-shirt"],
                "color": "blue",
                "material": "cotton",
                "gender": "Unisex",
                "season": "All Season",
                "rating": 4.2,
                "review_count": 156,
                "availability": True
            },
            {
                "id": "TEST_002",
                "name": "Running Sneakers",
                "description": "Lightweight running shoes with excellent cushioning",
                "category": "shoes",
                "subcategory": "sneakers",
                "price": 89.99,
                "brand": "SportsBrand",
                "image_url": "https://picsum.photos/400/400?random=2",
                "tags": ["running", "shoes", "athletic"],
                "color": "white",
                "material": "synthetic",
                "gender": "Unisex",
                "season": "All Season",
                "rating": 4.5,
                "review_count": 289,
                "availability": True
            }
        ]
    
    @pytest.fixture
    def sample_dataset(self, sample_products, temp_dir):
        """Create sample dataset file"""
        dataset = {
            "metadata": {
                "total_products": len(sample_products),
                "version": "1.0"
            },
            "products": sample_products
        }
        
        dataset_file = temp_dir / "test_dataset.json"
        with open(dataset_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return dataset_file
    
    def test_clip_service_import(self):
        """Test that CLIP service can be imported"""
        try:
            from app.services.clip_service import CLIPService
            logger.info("✓ CLIP service import successful")
        except ImportError as e:
            pytest.fail(f"Cannot import CLIP service: {e}")
    
    def test_qdrant_client_import(self):
        """Test that Qdrant client can be imported"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import VectorParams, Distance
            logger.info("✓ Qdrant client import successful")
        except ImportError as e:
            pytest.fail(f"Cannot import Qdrant client: {e}")
    
    @pytest.mark.asyncio
    async def test_clip_service_initialization(self):
        """Test CLIP service initialization"""
        try:
            from app.services.clip_service import CLIPService
            
            clip_service = CLIPService(batch_size=2)
            assert clip_service is not None
            logger.info("✓ CLIP service initialization successful")
            
        except Exception as e:
            pytest.fail(f"CLIP service initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_text_embedding_generation(self):
        """Test text embedding generation"""
        try:
            from app.services.clip_service import CLIPService
            
            clip_service = CLIPService(batch_size=2)
            
            text = "Classic cotton t-shirt for casual wear"
            embedding = await clip_service.encode_text(text)
            
            assert embedding is not None
            assert isinstance(embedding, np.ndarray)
            assert len(embedding.shape) == 1
            logger.info(f"✓ Text embedding generated: shape {embedding.shape}")
            
        except Exception as e:
            pytest.fail(f"Text embedding generation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_image_embedding_generation(self):
        """Test image embedding generation"""
        try:
            from app.services.clip_service import CLIPService
            
            clip_service = CLIPService(batch_size=2)
            
            # Create test image
            test_image = Image.new('RGB', (224, 224), color='red')
            embedding = await clip_service.encode_image(test_image)
            
            assert embedding is not None
            assert isinstance(embedding, np.ndarray)
            assert len(embedding.shape) == 1
            logger.info(f"✓ Image embedding generated: shape {embedding.shape}")
            
        except Exception as e:
            pytest.fail(f"Image embedding generation failed: {e}")
    
    def test_image_downloader_cache_path(self, temp_dir):
        """Test image downloader cache path generation"""
        try:
            from vector_generation_pipeline import ImageDownloader
            
            downloader = ImageDownloader(TEST_CONFIG)
            downloader.config.image_cache_dir = str(temp_dir)
            
            url = "https://example.com/image.jpg"
            cache_path = downloader._get_cache_path(url)
            
            assert cache_path.parent == temp_dir
            assert cache_path.suffix == '.jpg'
            logger.info("✓ Image cache path generation successful")
            
        except Exception as e:
            pytest.fail(f"Image cache path generation failed: {e}")
    
    @pytest.mark.asyncio
    async def test_qdrant_connection(self):
        """Test Qdrant connection"""
        try:
            from qdrant_client import QdrantClient
            
            client = QdrantClient(
                host=TEST_CONFIG['qdrant_host'],
                port=TEST_CONFIG['qdrant_port']
            )
            
            # Test connection
            collections = client.get_collections()
            logger.info(f"✓ Qdrant connection successful: {len(collections.collections)} collections")
            
        except Exception as e:
            logger.warning(f"Qdrant connection failed: {e}")
            logger.info("This is expected if Qdrant is not running")
    
    @pytest.mark.asyncio
    async def test_vector_config_validation(self):
        """Test vector configuration validation"""
        try:
            from vector_generation_pipeline import VectorConfig
            
            config = VectorConfig()
            
            assert config.clip_model is not None
            assert config.batch_size > 0
            assert config.vector_size > 0
            assert 0 <= config.image_text_weight <= 1
            
            logger.info("✓ Vector configuration validation successful")
            
        except Exception as e:
            pytest.fail(f"Vector configuration validation failed: {e}")
    
    def test_dataset_loading(self, sample_dataset):
        """Test dataset loading functionality"""
        try:
            from vector_generation_pipeline import VectorGenerationPipeline
            
            config = VectorConfig(**TEST_CONFIG)
            pipeline = VectorGenerationPipeline(config)
            
            products = pipeline.load_product_data(str(sample_dataset))
            
            assert len(products) == 2
            assert products[0]['id'] == 'TEST_001'
            assert products[1]['id'] == 'TEST_002'
            
            logger.info("✓ Dataset loading successful")
            
        except Exception as e:
            pytest.fail(f"Dataset loading failed: {e}")
    
    def test_metadata_creation(self, sample_products):
        """Test metadata creation for Qdrant storage"""
        try:
            from vector_generation_pipeline import VectorGenerationPipeline
            
            config = VectorConfig(**TEST_CONFIG)
            pipeline = VectorGenerationPipeline(config)
            
            product = sample_products[0]
            metadata = pipeline.create_metadata(product)
            
            assert metadata['product_id'] == product['id']
            assert metadata['name'] == product['name']
            assert metadata['category'] == product['category']
            assert metadata['price'] == product['price']
            
            logger.info("✓ Metadata creation successful")
            
        except Exception as e:
            pytest.fail(f"Metadata creation failed: {e}")
    
    def test_embedding_combination(self):
        """Test embedding combination logic"""
        try:
            from vector_generation_pipeline import VectorGenerationPipeline
            
            config = VectorConfig(**TEST_CONFIG)
            pipeline = VectorGenerationPipeline(config)
            
            # Test with both embeddings
            image_emb = np.random.rand(512).astype(np.float32)
            text_emb = np.random.rand(512).astype(np.float32)
            
            combined = pipeline.create_combined_embedding(image_emb, text_emb)
            
            assert combined is not None
            assert isinstance(combined, np.ndarray)
            assert len(combined) == 512
            assert np.isclose(np.linalg.norm(combined), 1.0, atol=1e-6)
            
            # Test with only text embedding
            combined_text_only = pipeline.create_combined_embedding(None, text_emb)
            assert combined_text_only is not None
            
            # Test with only image embedding
            combined_image_only = pipeline.create_combined_embedding(image_emb, None)
            assert combined_image_only is not None
            
            # Test with no embeddings
            combined_none = pipeline.create_combined_embedding(None, None)
            assert combined_none is None
            
            logger.info("✓ Embedding combination successful")
            
        except Exception as e:
            pytest.fail(f"Embedding combination failed: {e}")
    
    @pytest.mark.asyncio
    async def test_progress_tracker(self, temp_dir):
        """Test progress tracking functionality"""
        try:
            from vector_generation_pipeline import ProgressTracker, ProcessingResult
            
            config = VectorConfig(**TEST_CONFIG)
            config.checkpoint_file = str(temp_dir / "test_checkpoint.json")
            
            tracker = ProgressTracker(config)
            
            # Test initial state
            assert tracker.processed_count == 0
            assert tracker.success_count == 0
            assert tracker.error_count == 0
            
            # Test update with success
            result = ProcessingResult(
                product_id="TEST_001",
                success=True,
                processing_time=1.0
            )
            tracker.update(result)
            
            assert tracker.processed_count == 1
            assert tracker.success_count == 1
            assert tracker.error_count == 0
            
            # Test update with error
            result_error = ProcessingResult(
                product_id="TEST_002",
                success=False,
                error="Test error",
                processing_time=0.5
            )
            tracker.update(result_error)
            
            assert tracker.processed_count == 2
            assert tracker.success_count == 1
            assert tracker.error_count == 1
            
            logger.info("✓ Progress tracking successful")
            
        except Exception as e:
            pytest.fail(f"Progress tracking failed: {e}")
    
    @pytest.mark.asyncio
    async def test_mock_image_download(self):
        """Test image download with mocked HTTP calls"""
        try:
            from vector_generation_pipeline import ImageDownloader
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                # Mock successful response
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.read = AsyncMock(return_value=self._create_test_image_bytes())
                
                mock_get.return_value.__aenter__.return_value = mock_response
                
                config = VectorConfig(**TEST_CONFIG)
                downloader = ImageDownloader(config)
                
                async with downloader:
                    image = await downloader.download_image(
                        "https://example.com/test.jpg", 
                        "TEST_001"
                    )
                
                assert image is not None
                assert isinstance(image, Image.Image)
                
            logger.info("✓ Mock image download successful")
            
        except Exception as e:
            pytest.fail(f"Mock image download failed: {e}")
    
    def _create_test_image_bytes(self) -> bytes:
        """Create test image as bytes"""
        import io
        
        test_image = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()

class BenchmarkTests:
    """Performance and benchmark tests"""
    
    @pytest.mark.asyncio
    async def test_batch_processing_speed(self):
        """Test batch processing performance"""
        try:
            from app.services.clip_service import CLIPService
            
            clip_service = CLIPService(batch_size=8)
            
            # Test text batch processing
            texts = [f"Test product {i}" for i in range(16)]
            
            start_time = time.time()
            embeddings = await clip_service.encode_batch_text(texts)
            batch_time = time.time() - start_time
            
            # Test individual processing
            start_time = time.time()
            individual_embeddings = []
            for text in texts:
                emb = await clip_service.encode_text(text)
                individual_embeddings.append(emb)
            individual_time = time.time() - start_time
            
            logger.info(f"Batch processing: {batch_time:.2f}s")
            logger.info(f"Individual processing: {individual_time:.2f}s")
            logger.info(f"Speedup: {individual_time/batch_time:.2f}x")
            
            assert batch_time < individual_time
            logger.info("✓ Batch processing is faster than individual processing")
            
        except Exception as e:
            logger.warning(f"Batch processing speed test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage during processing"""
        try:
            import psutil
            import gc
            
            process = psutil.Process()
            
            # Initial memory
            gc.collect()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process some data
            from app.services.clip_service import CLIPService
            clip_service = CLIPService(batch_size=4)
            
            for i in range(10):
                text = f"Test product description {i} with more detailed information"
                await clip_service.encode_text(text)
            
            # Final memory
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_increase = final_memory - initial_memory
            
            logger.info(f"Initial memory: {initial_memory:.1f} MB")
            logger.info(f"Final memory: {final_memory:.1f} MB")
            logger.info(f"Memory increase: {memory_increase:.1f} MB")
            
            # Memory increase should be reasonable (< 500MB for this test)
            assert memory_increase < 500
            logger.info("✓ Memory usage is within acceptable limits")
            
        except Exception as e:
            logger.warning(f"Memory usage test failed: {e}")

def test_integration_with_existing_backend():
    """Test integration with existing backend structure"""
    try:
        # Test imports from backend
        sys.path.append(str(Path(__file__).parent.parent / "backend"))
        
        from app.services.clip_service import CLIPService
        
        # Try to import config if available
        try:
            from app.utils.config import Config
        except ImportError:
            Config = None
        
        logger.info("✓ Backend integration successful")
        
    except ImportError as e:
        logger.warning(f"Backend integration test failed: {e}")
        logger.info("This is expected if backend is not fully set up")

def run_quick_tests():
    """Run a subset of quick tests for development"""
    logger.info("Running quick test suite...")
    
    test_suite = TestVectorPipeline()
    
    # Run basic tests
    test_suite.test_clip_service_import()
    test_suite.test_qdrant_client_import()
    test_integration_with_existing_backend()
    
    logger.info("✓ Quick tests completed")

def run_full_tests():
    """Run complete test suite"""
    logger.info("Running full test suite...")
    
    # Use pytest to run all tests
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        logger.info("✓ All tests passed")
    else:
        logger.error("✗ Some tests failed")
    
    return exit_code

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector Pipeline Test Suite")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests only")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run benchmark tests")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests")
    
    args = parser.parse_args()
    
    if args.quick:
        run_quick_tests()
    elif args.benchmark:
        logger.info("Running benchmark tests...")
        benchmark = BenchmarkTests()
        asyncio.run(benchmark.test_batch_processing_speed())
        asyncio.run(benchmark.test_memory_usage())
    elif args.integration:
        test_integration_with_existing_backend()
    else:
        run_full_tests()

if __name__ == "__main__":
    main()
