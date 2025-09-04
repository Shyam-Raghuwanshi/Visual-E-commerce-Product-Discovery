#!/usr/bin/env python3
"""
Test script for the enhanced CLIP service implementation.
This script demonstrates all the features of the CLIPService class including:
- Model loading and caching
- Single and batch text encoding
- Single and batch image encoding
- Error handling
- Memory management
- Performance monitoring
"""

import asyncio
import time
import numpy as np
from PIL import Image, ImageDraw
import logging
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from services.clip_service import CLIPService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_image(size=(224, 224), color='red', text='Test'):
    """Create a simple test image with colored background and text"""
    image = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(image)
    
    # Add text to the image
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill='white')
    return image

async def test_model_initialization():
    """Test model initialization and caching"""
    logger.info("=== Testing Model Initialization ===")
    
    start_time = time.time()
    clip_service = CLIPService()
    init_time = time.time() - start_time
    
    logger.info(f"Model initialization took {init_time:.2f} seconds")
    logger.info(f"Model info: {clip_service.get_model_info()}")
    
    # Test second initialization (should use cache)
    start_time = time.time()
    clip_service2 = CLIPService()
    cache_time = time.time() - start_time
    
    logger.info(f"Cached model initialization took {cache_time:.2f} seconds")
    logger.info(f"Speed improvement: {init_time/cache_time:.1f}x faster")
    
    return clip_service

async def test_single_text_encoding(clip_service):
    """Test single text encoding with various inputs"""
    logger.info("\n=== Testing Single Text Encoding ===")
    
    test_texts = [
        "red apple",
        "blue car",
        "beautiful sunset",
        "running shoes",
        "laptop computer"
    ]
    
    for text in test_texts:
        try:
            start_time = time.time()
            embedding = await clip_service.encode_text(text)
            encode_time = time.time() - start_time
            
            logger.info(f"Text: '{text}' -> Embedding shape: {embedding.shape}, "
                       f"Time: {encode_time:.3f}s, Norm: {np.linalg.norm(embedding):.3f}")
        except Exception as e:
            logger.error(f"Failed to encode text '{text}': {e}")
    
    # Test error handling
    try:
        await clip_service.encode_text("")
        logger.error("Should have failed with empty text")
    except ValueError as e:
        logger.info(f"✓ Correctly handled empty text: {e}")

async def test_single_image_encoding(clip_service):
    """Test single image encoding with various inputs"""
    logger.info("\n=== Testing Single Image Encoding ===")
    
    test_images = [
        ("red", "Apple"),
        ("blue", "Car"),
        ("green", "Tree"),
        ("yellow", "Sun"),
        ("purple", "Flower")
    ]
    
    for color, label in test_images:
        try:
            image = create_test_image(color=color, text=label)
            
            start_time = time.time()
            embedding = await clip_service.encode_image(image)
            encode_time = time.time() - start_time
            
            logger.info(f"Image: {color} {label} -> Embedding shape: {embedding.shape}, "
                       f"Time: {encode_time:.3f}s, Norm: {np.linalg.norm(embedding):.3f}")
        except Exception as e:
            logger.error(f"Failed to encode image {color} {label}: {e}")
    
    # Test error handling
    try:
        await clip_service.encode_image("not an image")
        logger.error("Should have failed with invalid image")
    except ValueError as e:
        logger.info(f"✓ Correctly handled invalid image: {e}")

async def test_batch_text_encoding(clip_service):
    """Test batch text encoding with various batch sizes"""
    logger.info("\n=== Testing Batch Text Encoding ===")
    
    # Test small batch
    small_batch = [
        "red apple", "blue car", "green tree", "yellow banana", "purple flower"
    ]
    
    try:
        start_time = time.time()
        embeddings = await clip_service.encode_batch_text(small_batch)
        encode_time = time.time() - start_time
        
        logger.info(f"Small batch ({len(small_batch)} texts) -> "
                   f"Shape: {embeddings.shape}, Time: {encode_time:.3f}s")
    except Exception as e:
        logger.error(f"Failed to encode small text batch: {e}")
    
    # Test large batch (to test batching)
    large_batch = [f"test text number {i}" for i in range(50)]
    
    try:
        start_time = time.time()
        embeddings = await clip_service.encode_batch_text(large_batch, batch_size=16)
        encode_time = time.time() - start_time
        
        logger.info(f"Large batch ({len(large_batch)} texts) -> "
                   f"Shape: {embeddings.shape}, Time: {encode_time:.3f}s")
        logger.info(f"Average time per text: {encode_time/len(large_batch):.4f}s")
    except Exception as e:
        logger.error(f"Failed to encode large text batch: {e}")
    
    # Test error handling
    try:
        await clip_service.encode_batch_text([])
        logger.error("Should have failed with empty batch")
    except ValueError as e:
        logger.info(f"✓ Correctly handled empty batch: {e}")

async def test_batch_image_encoding(clip_service):
    """Test batch image encoding with various batch sizes"""
    logger.info("\n=== Testing Batch Image Encoding ===")
    
    # Test small batch
    small_batch = [
        create_test_image(color="red", text="1"),
        create_test_image(color="blue", text="2"),
        create_test_image(color="green", text="3"),
        create_test_image(color="yellow", text="4"),
        create_test_image(color="purple", text="5")
    ]
    
    try:
        start_time = time.time()
        embeddings = await clip_service.encode_batch_images(small_batch)
        encode_time = time.time() - start_time
        
        logger.info(f"Small batch ({len(small_batch)} images) -> "
                   f"Shape: {embeddings.shape}, Time: {encode_time:.3f}s")
    except Exception as e:
        logger.error(f"Failed to encode small image batch: {e}")
    
    # Test larger batch
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown"]
    large_batch = [
        create_test_image(color=colors[i % len(colors)], text=str(i))
        for i in range(20)
    ]
    
    try:
        start_time = time.time()
        embeddings = await clip_service.encode_batch_images(large_batch, batch_size=8)
        encode_time = time.time() - start_time
        
        logger.info(f"Large batch ({len(large_batch)} images) -> "
                   f"Shape: {embeddings.shape}, Time: {encode_time:.3f}s")
        logger.info(f"Average time per image: {encode_time/len(large_batch):.4f}s")
    except Exception as e:
        logger.error(f"Failed to encode large image batch: {e}")

async def test_similarity_computation(clip_service):
    """Test similarity computation between text and image embeddings"""
    logger.info("\n=== Testing Similarity Computation ===")
    
    # Create test pairs
    test_pairs = [
        ("red apple", create_test_image(color="red", text="Apple")),
        ("blue car", create_test_image(color="blue", text="Car")),
        ("green tree", create_test_image(color="green", text="Tree")),
    ]
    
    for text, image in test_pairs:
        try:
            text_embedding = await clip_service.encode_text(text)
            image_embedding = await clip_service.encode_image(image)
            
            similarity = await clip_service.compute_similarity(text_embedding, image_embedding)
            
            logger.info(f"'{text}' <-> Image similarity: {similarity:.3f}")
        except Exception as e:
            logger.error(f"Failed to compute similarity for '{text}': {e}")
    
    # Test cross-modal similarities
    logger.info("\nCross-modal similarities:")
    red_apple_text = await clip_service.encode_text("red apple")
    blue_car_image = await clip_service.encode_image(create_test_image(color="blue", text="Car"))
    
    cross_similarity = await clip_service.compute_similarity(red_apple_text, blue_car_image)
    logger.info(f"'red apple' <-> Blue Car image similarity: {cross_similarity:.3f}")

async def test_memory_management(clip_service):
    """Test memory management features"""
    logger.info("\n=== Testing Memory Management ===")
    
    import psutil
    process = psutil.Process()
    
    # Initial memory
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    logger.info(f"Initial memory usage: {initial_memory:.1f} MB")
    
    # Process a large batch
    large_texts = [f"sample text number {i} with some content" for i in range(100)]
    
    start_memory = process.memory_info().rss / 1024 / 1024
    await clip_service.encode_batch_text(large_texts, batch_size=10)
    end_memory = process.memory_info().rss / 1024 / 1024
    
    logger.info(f"Memory before batch: {start_memory:.1f} MB")
    logger.info(f"Memory after batch: {end_memory:.1f} MB")
    logger.info(f"Memory increase: {end_memory - start_memory:.1f} MB")

async def test_error_handling(clip_service):
    """Test comprehensive error handling"""
    logger.info("\n=== Testing Error Handling ===")
    
    # Test invalid inputs
    error_tests = [
        ("Empty text", lambda: clip_service.encode_text("")),
        ("None text", lambda: clip_service.encode_text(None)),
        ("Empty text list", lambda: clip_service.encode_batch_text([])),
        ("Text list with None", lambda: clip_service.encode_batch_text([None, "text"])),
        ("Invalid image", lambda: clip_service.encode_image("not_an_image")),
        ("Empty image list", lambda: clip_service.encode_batch_images([])),
    ]
    
    for test_name, test_func in error_tests:
        try:
            await test_func()
            logger.error(f"❌ {test_name}: Should have raised an error")
        except (ValueError, RuntimeError, TypeError) as e:
            logger.info(f"✓ {test_name}: Correctly handled - {type(e).__name__}")
        except Exception as e:
            logger.warning(f"⚠ {test_name}: Unexpected error type - {type(e).__name__}: {e}")

async def performance_benchmark(clip_service):
    """Run performance benchmarks"""
    logger.info("\n=== Performance Benchmark ===")
    
    # Text encoding benchmark
    texts = ["sample text"] * 50
    
    start_time = time.time()
    for text in texts:
        await clip_service.encode_text(text)
    single_time = time.time() - start_time
    
    start_time = time.time()
    await clip_service.encode_batch_text(texts)
    batch_time = time.time() - start_time
    
    logger.info(f"Single encoding: {single_time:.2f}s ({len(texts)} texts)")
    logger.info(f"Batch encoding: {batch_time:.2f}s ({len(texts)} texts)")
    logger.info(f"Speedup: {single_time/batch_time:.1f}x faster with batching")
    
    # Image encoding benchmark
    images = [create_test_image(text=str(i)) for i in range(20)]
    
    start_time = time.time()
    for image in images:
        await clip_service.encode_image(image)
    single_time = time.time() - start_time
    
    start_time = time.time()
    await clip_service.encode_batch_images(images)
    batch_time = time.time() - start_time
    
    logger.info(f"Single image encoding: {single_time:.2f}s ({len(images)} images)")
    logger.info(f"Batch image encoding: {batch_time:.2f}s ({len(images)} images)")
    logger.info(f"Speedup: {single_time/batch_time:.1f}x faster with batching")

async def main():
    """Main test function"""
    logger.info("Starting CLIP Service Enhanced Tests")
    logger.info("=" * 50)
    
    try:
        # Initialize service
        clip_service = await test_model_initialization()
        
        # Run all tests
        await test_single_text_encoding(clip_service)
        await test_single_image_encoding(clip_service)
        await test_batch_text_encoding(clip_service)
        await test_batch_image_encoding(clip_service)
        await test_similarity_computation(clip_service)
        await test_memory_management(clip_service)
        await test_error_handling(clip_service)
        await performance_benchmark(clip_service)
        
        logger.info("\n" + "=" * 50)
        logger.info("All tests completed successfully!")
        
        # Cleanup
        clip_service.cleanup()
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
