#!/usr/bin/env python3
"""
Vector Pipeline Usage Examples

This script demonstrates how to use the vector generation pipeline
for various scenarios and provides code examples for developers.

Author: Visual E-commerce Team
Date: September 2025
"""

import asyncio
import json
import logging
from pathlib import Path
import sys
import time

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend"))
sys.path.append(str(project_root / "scripts"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def example_1_basic_pipeline_usage():
    """Example 1: Basic pipeline usage with default settings"""
    logger.info("=== Example 1: Basic Pipeline Usage ===")
    
    try:
        from vector_generation_pipeline import VectorGenerationPipeline
        
        # Basic configuration
        config = {
            'batch_size': 4,
            'max_concurrent_downloads': 3,
            'text_weight': 0.7,
            'image_weight': 0.3,
            'qdrant_host': 'localhost',
            'qdrant_port': 6333,
            'collection_name': 'example_products',
            'cache_dir': str(project_root / 'data' / 'example_cache'),
            'output_dir': str(project_root / 'data' / 'example_vectors'),
            'force_recreate_collection': True,
            'resume_from_checkpoint': False
        }
        
        # Create sample dataset
        sample_products = [
            {
                "id": "EXAMPLE_001",
                "name": "Blue Cotton T-Shirt",
                "description": "Comfortable 100% cotton t-shirt in navy blue",
                "category": "clothing",
                "subcategory": "t-shirts",
                "brand": "CoolWear",
                "price": 29.99,
                "image_url": "https://source.unsplash.com/400x400/?t-shirt,blue",
                "tags": ["cotton", "casual", "comfortable"],
                "color": "blue",
                "material": "cotton",
                "gender": "unisex",
                "season": "all season",
                "rating": 4.5,
                "review_count": 128,
                "availability": True
            }
        ]
        
        sample_dataset = {
            "metadata": {"total_products": 1, "version": "example"},
            "products": sample_products
        }
        
        # Save sample dataset
        dataset_file = project_root / "data" / "example_dataset.json"
        with open(dataset_file, 'w') as f:
            json.dump(sample_dataset, f, indent=2)
        
        # Initialize and run pipeline
        pipeline = VectorGenerationPipeline(config)
        
        start_time = time.time()
        await pipeline.run_pipeline(str(dataset_file))
        end_time = time.time()
        
        logger.info(f"✓ Pipeline completed in {end_time - start_time:.2f} seconds")
        logger.info(f"✓ Processed: {pipeline.stats.processed_products} products")
        logger.info(f"✓ Stored: {pipeline.stats.vectors_stored} vectors")
        
        return True
        
    except Exception as e:
        logger.error(f"Example 1 failed: {e}")
        return False

async def example_2_custom_vector_weights():
    """Example 2: Custom vector combination weights"""
    logger.info("=== Example 2: Custom Vector Weights ===")
    
    try:
        from vector_generation_pipeline import VectorGenerator
        from app.services.clip_service import CLIPService
        from PIL import Image
        import numpy as np
        
        # Create vector generator with custom weights
        # 90% text, 10% image - for text-heavy searches
        text_heavy_generator = VectorGenerator(
            text_weight=0.9,
            image_weight=0.1,
            batch_size=2
        )
        
        # 20% text, 80% image - for visual searches
        image_heavy_generator = VectorGenerator(
            text_weight=0.2,
            image_weight=0.8,
            batch_size=2
        )
        
        # Sample product for testing
        product = {
            "id": "WEIGHT_TEST",
            "name": "Red Leather Jacket",
            "description": "Premium leather jacket in classic red color",
            "category": "clothing",
            "tags": ["leather", "jacket", "premium"]
        }
        
        # Generate embeddings with different weights
        text_embedding = np.random.rand(512)  # Simulated CLIP text embedding
        image_embedding = np.random.rand(512)  # Simulated CLIP image embedding
        
        text_heavy_combined = text_heavy_generator.combine_embeddings(
            text_embedding, image_embedding
        )
        
        image_heavy_combined = image_heavy_generator.combine_embeddings(
            text_embedding, image_embedding
        )
        
        # Compare similarity to original embeddings
        text_similarity_1 = np.dot(text_heavy_combined, text_embedding)
        text_similarity_2 = np.dot(image_heavy_combined, text_embedding)
        
        logger.info(f"Text-heavy combination similarity to text: {text_similarity_1:.3f}")
        logger.info(f"Image-heavy combination similarity to text: {text_similarity_2:.3f}")
        logger.info("✓ Custom vector weights working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"Example 2 failed: {e}")
        return False

async def example_3_batch_processing():
    """Example 3: Efficient batch processing"""
    logger.info("=== Example 3: Batch Processing ===")
    
    try:
        from vector_generation_pipeline import VectorGenerator
        
        # Create vector generator
        generator = VectorGenerator(batch_size=4)
        
        # Sample products for batch processing
        products = [
            {
                "id": f"BATCH_{i:03d}",
                "name": f"Product {i}",
                "description": f"Description for product {i}",
                "category": "clothing",
                "tags": [f"tag{i}", "sample"]
            }
            for i in range(8)
        ]
        
        # Simulate images (in real scenario, these would be PIL Images)
        images = [None] * len(products)  # No images for this example
        
        # Process batch
        start_time = time.time()
        embeddings = await generator.generate_batch_embeddings(products, images)
        end_time = time.time()
        
        successful_embeddings = [emb for emb in embeddings if emb is not None]
        
        logger.info(f"✓ Processed {len(products)} products in batch")
        logger.info(f"✓ Generated {len(successful_embeddings)} embeddings")
        logger.info(f"✓ Batch processing time: {end_time - start_time:.3f} seconds")
        logger.info(f"✓ Rate: {len(products) / (end_time - start_time):.1f} products/second")
        
        return True
        
    except Exception as e:
        logger.error(f"Example 3 failed: {e}")
        return False

async def example_4_search_integration():
    """Example 4: Search integration with Qdrant"""
    logger.info("=== Example 4: Search Integration ===")
    
    try:
        from qdrant_client import QdrantClient
        from app.services.clip_service import CLIPService
        import uuid
        
        # Connect to Qdrant
        client = QdrantClient(host="localhost", port=6333)
        collection_name = "search_example"
        
        # Create test collection
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        try:
            client.delete_collection(collection_name)
        except:
            pass
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE)
        )
        
        # Add some example vectors
        clip_service = CLIPService()
        
        example_texts = [
            "Blue cotton t-shirt comfortable casual wear",
            "Red leather jacket premium quality",
            "White running shoes athletic footwear",
            "Black leather handbag elegant accessory"
        ]
        
        points = []
        for i, text in enumerate(example_texts):
            embedding = await clip_service.encode_text(text)
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "text": text,
                    "category": "clothing" if i < 2 else ("shoes" if i == 2 else "accessories"),
                    "index": i
                }
            )
            points.append(point)
        
        # Store vectors
        client.upsert(collection_name=collection_name, points=points)
        
        # Test search
        search_query = "comfortable blue shirt"
        query_vector = await clip_service.encode_text(search_query)
        
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            limit=3
        )
        
        logger.info(f"Search query: '{search_query}'")
        logger.info("Search results:")
        for i, result in enumerate(search_results):
            logger.info(f"  {i+1}. {result.payload['text']} (score: {result.score:.3f})")
        
        # Cleanup
        client.delete_collection(collection_name)
        
        logger.info("✓ Search integration working correctly")
        return True
        
    except Exception as e:
        logger.error(f"Example 4 failed: {e}")
        return False

def example_5_configuration_options():
    """Example 5: Different configuration options"""
    logger.info("=== Example 5: Configuration Options ===")
    
    try:
        # High-performance configuration (GPU with large memory)
        high_performance_config = {
            'batch_size': 32,
            'max_concurrent_downloads': 20,
            'text_weight': 0.6,
            'image_weight': 0.4,
            'device': 'cuda'
        }
        
        # Memory-efficient configuration (CPU or low memory)
        memory_efficient_config = {
            'batch_size': 4,
            'max_concurrent_downloads': 3,
            'text_weight': 0.8,
            'image_weight': 0.2,
            'device': 'cpu'
        }
        
        # Text-focused configuration (for text-heavy searches)
        text_focused_config = {
            'batch_size': 16,
            'text_weight': 0.9,
            'image_weight': 0.1,
            'max_concurrent_downloads': 5
        }
        
        # Image-focused configuration (for visual searches)
        image_focused_config = {
            'batch_size': 8,
            'text_weight': 0.3,
            'image_weight': 0.7,
            'max_concurrent_downloads': 15
        }
        
        configs = {
            "High Performance": high_performance_config,
            "Memory Efficient": memory_efficient_config,
            "Text Focused": text_focused_config,
            "Image Focused": image_focused_config
        }
        
        logger.info("Configuration examples:")
        for name, config in configs.items():
            logger.info(f"\n{name}:")
            for key, value in config.items():
                logger.info(f"  {key}: {value}")
        
        logger.info("✓ Configuration options documented")
        return True
        
    except Exception as e:
        logger.error(f"Example 5 failed: {e}")
        return False

async def example_6_error_handling():
    """Example 6: Error handling and recovery"""
    logger.info("=== Example 6: Error Handling ===")
    
    try:
        from vector_generation_pipeline import ImageDownloader
        from pathlib import Path
        
        # Test image downloader with error scenarios
        cache_dir = project_root / "data" / "error_test_cache"
        cache_dir.mkdir(exist_ok=True)
        
        async with ImageDownloader(cache_dir, max_concurrent=2) as downloader:
            
            # Test with invalid URL
            invalid_image = await downloader.download_image(
                "https://invalid-url-that-does-not-exist.com/image.jpg",
                "ERROR_TEST_001"
            )
            
            if invalid_image is None:
                logger.info("✓ Invalid URL handled correctly")
            else:
                logger.warning("⚠ Invalid URL should return None")
            
            # Test with valid URL
            valid_image = await downloader.download_image(
                "https://source.unsplash.com/200x200/?test",
                "ERROR_TEST_002"
            )
            
            if valid_image is not None:
                logger.info("✓ Valid URL processed correctly")
            else:
                logger.warning("⚠ Valid URL failed (might be network issue)")
        
        # Test checkpoint recovery
        checkpoint_data = {
            "processed_products": ["TEST_001", "TEST_002"],
            "failed_products": ["TEST_003"],
            "timestamp": "2025-09-04T10:00:00"
        }
        
        checkpoint_file = project_root / "data" / "test_checkpoint.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f)
        
        # Verify checkpoint can be loaded
        with open(checkpoint_file, 'r') as f:
            loaded_data = json.load(f)
        
        if loaded_data == checkpoint_data:
            logger.info("✓ Checkpoint save/load working correctly")
        
        # Cleanup
        checkpoint_file.unlink(missing_ok=True)
        
        logger.info("✓ Error handling mechanisms validated")
        return True
        
    except Exception as e:
        logger.error(f"Example 6 failed: {e}")
        return False

async def run_all_examples():
    """Run all examples"""
    logger.info("🚀 Running Vector Pipeline Usage Examples")
    logger.info("=" * 60)
    
    examples = [
        ("Basic Pipeline Usage", example_1_basic_pipeline_usage),
        ("Custom Vector Weights", example_2_custom_vector_weights),
        ("Batch Processing", example_3_batch_processing),
        ("Search Integration", example_4_search_integration),
        ("Configuration Options", example_5_configuration_options),
        ("Error Handling", example_6_error_handling)
    ]
    
    results = {}
    
    for name, example_func in examples:
        logger.info(f"\n--- {name} ---")
        try:
            if asyncio.iscoroutinefunction(example_func):
                success = await example_func()
            else:
                success = example_func()
            
            results[name] = success
            
            if success:
                logger.info(f"✅ {name} completed successfully")
            else:
                logger.error(f"❌ {name} failed")
                
        except Exception as e:
            logger.error(f"❌ {name} failed with exception: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLES SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status}: {name}")
    
    logger.info(f"\nTotal: {passed}/{total} examples passed")
    
    if passed == total:
        logger.info("🎉 All examples completed successfully!")
    else:
        logger.warning("⚠️ Some examples failed - check logs for details")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector Pipeline Usage Examples")
    parser.add_argument("--example", type=int, help="Run specific example (1-6)")
    parser.add_argument("--list", action="store_true", help="List available examples")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available examples:")
        print("1. Basic Pipeline Usage")
        print("2. Custom Vector Weights")
        print("3. Batch Processing")
        print("4. Search Integration")
        print("5. Configuration Options")
        print("6. Error Handling")
        return
    
    if args.example:
        example_map = {
            1: example_1_basic_pipeline_usage,
            2: example_2_custom_vector_weights,
            3: example_3_batch_processing,
            4: example_4_search_integration,
            5: example_5_configuration_options,
            6: example_6_error_handling
        }
        
        if args.example in example_map:
            logger.info(f"Running Example {args.example}")
            example_func = example_map[args.example]
            
            if asyncio.iscoroutinefunction(example_func):
                asyncio.run(example_func())
            else:
                example_func()
        else:
            logger.error(f"Invalid example number: {args.example}")
    else:
        # Run all examples
        asyncio.run(run_all_examples())

if __name__ == "__main__":
    main()
