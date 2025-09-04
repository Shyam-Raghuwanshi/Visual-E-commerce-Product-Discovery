# Enhanced CLIP Service Implementation

This directory contains an enhanced CLIP (Contrastive Language-Image Pre-training) service implementation with comprehensive features for production use.

## Features

### ✅ Core Functionality
- **CLIP Model Integration**: Uses OpenAI's CLIP model (openai/clip-vit-base-patch32)
- **Text Encoding**: Convert text to embedding vectors
- **Image Encoding**: Convert images to embedding vectors
- **Batch Processing**: Efficient processing of multiple texts/images
- **Similarity Computation**: Calculate text-image similarity scores

### ✅ Performance Optimizations
- **Model Caching**: Singleton pattern for model reuse across instances
- **Smart Device Selection**: Automatic GPU/CPU selection based on available resources
- **Memory Management**: Automatic memory cleanup and garbage collection
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Threading**: Multi-threaded processing for improved throughput

### ✅ Production Features
- **Comprehensive Error Handling**: Graceful handling of all edge cases
- **Memory Monitoring**: Real-time memory usage tracking with psutil
- **Logging**: Detailed logging with configurable levels
- **Input Validation**: Robust validation for all input types
- **Resource Cleanup**: Proper cleanup of GPU/CPU resources

### ✅ Configuration
- **Environment Variables**: Configurable via environment variables
- **Flexible Settings**: Adjustable batch sizes, worker counts, and model selection
- **Fallback Mechanisms**: Automatic fallback from GPU to CPU when needed

## Installation

1. Install the required dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. The service will automatically download the CLIP model on first use.

## Usage Examples

### Basic Usage

```python
import asyncio
from app.services.clip_service import CLIPService
from PIL import Image

async def main():
    # Initialize the service
    clip_service = CLIPService()
    
    # Encode text
    text_embedding = await clip_service.encode_text("red apple")
    print(f"Text embedding shape: {text_embedding.shape}")
    
    # Encode image
    image = Image.open("path/to/image.jpg")
    image_embedding = await clip_service.encode_image(image)
    print(f"Image embedding shape: {image_embedding.shape}")
    
    # Compute similarity
    similarity = await clip_service.compute_similarity(text_embedding, image_embedding)
    print(f"Similarity score: {similarity}")
    
    # Cleanup resources
    clip_service.cleanup()

asyncio.run(main())
```

### Batch Processing

```python
import asyncio
from app.services.clip_service import CLIPService
from PIL import Image

async def batch_example():
    clip_service = CLIPService(batch_size=16)
    
    # Batch text encoding
    texts = ["red apple", "blue car", "green tree", "yellow banana"]
    text_embeddings = await clip_service.encode_batch_text(texts)
    print(f"Batch text embeddings shape: {text_embeddings.shape}")
    
    # Batch image encoding
    images = [Image.open(f"image_{i}.jpg") for i in range(4)]
    image_embeddings = await clip_service.encode_batch_images(images)
    print(f"Batch image embeddings shape: {image_embeddings.shape}")

asyncio.run(batch_example())
```

### Configuration

```python
from app.services.clip_service import CLIPService

# Custom configuration
clip_service = CLIPService(
    model_name="openai/clip-vit-base-patch32",
    batch_size=64,
    max_workers=8
)

# Get model information
info = clip_service.get_model_info()
print(f"Model info: {info}")
```

### Error Handling

```python
import asyncio
from app.services.clip_service import CLIPService

async def error_handling_example():
    clip_service = CLIPService()
    
    try:
        # This will raise a ValueError
        await clip_service.encode_text("")
    except ValueError as e:
        print(f"Handled error: {e}")
    
    try:
        # This will raise a ValueError
        await clip_service.encode_image("not_an_image")
    except ValueError as e:
        print(f"Handled error: {e}")

asyncio.run(error_handling_example())
```

## Configuration Options

### Environment Variables

Set these environment variables to configure the service:

```bash
# Model configuration
export CLIP_MODEL_NAME="openai/clip-vit-base-patch32"

# Performance settings
export CLIP_BATCH_SIZE=32
export CLIP_MAX_WORKERS=4

# Memory settings
export CLIP_GPU_MEMORY_THRESHOLD=4.0

# Feature flags
export CLIP_ENABLE_CACHING=true
export CLIP_FALLBACK_TO_CPU=true

# Logging
export CLIP_LOG_LEVEL=INFO
```

### Code Configuration

```python
from app.utils.clip_config import CLIPConfig, VALIDATED_CONFIG

# Use validated configuration
clip_service = CLIPService(**VALIDATED_CONFIG)
```

## API Reference

### CLIPService Class

#### Constructor
```python
CLIPService(model_name="openai/clip-vit-base-patch32", batch_size=32, max_workers=4)
```

#### Methods

- `encode_text(text: str) -> np.ndarray`: Encode single text
- `encode_image(image: Image.Image) -> np.ndarray`: Encode single image
- `encode_batch_text(texts: List[str], batch_size=None) -> np.ndarray`: Encode text batch
- `encode_batch_images(images: List[Image.Image], batch_size=None) -> np.ndarray`: Encode image batch
- `compute_similarity(text_embedding: np.ndarray, image_embedding: np.ndarray) -> float`: Compute similarity
- `get_model_info() -> dict`: Get model information
- `cleanup()`: Clean up resources

## Testing

Run the comprehensive test suite:

```bash
cd backend
python test_clip_service.py
```

The test suite includes:
- Model initialization and caching tests
- Single and batch encoding tests
- Error handling tests
- Memory management tests
- Performance benchmarks
- Similarity computation tests

## Performance Notes

### Memory Usage
- GPU: Requires ~4GB VRAM for optimal performance
- CPU: Requires ~8GB system RAM
- Batch processing reduces per-item memory overhead

### Throughput
- Single encoding: ~50-100 items/second (GPU) / ~10-20 items/second (CPU)
- Batch encoding: ~200-500 items/second (GPU) / ~50-100 items/second (CPU)
- Actual performance depends on hardware and batch size

### Optimization Tips
1. Use batch processing for multiple items
2. Configure appropriate batch sizes for your hardware
3. Enable GPU if available
4. Monitor memory usage with included tools
5. Use the caching feature for repeated model initialization

## Integration with FastAPI

```python
from fastapi import FastAPI, UploadFile, HTTPException
from app.services.clip_service import CLIPService
from PIL import Image
import io

app = FastAPI()
clip_service = CLIPService()

@app.post("/encode/text")
async def encode_text(text: str):
    try:
        embedding = await clip_service.encode_text(text)
        return {"embedding": embedding.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/encode/image")
async def encode_image(file: UploadFile):
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        embedding = await clip_service.encode_image(image)
        return {"embedding": embedding.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/similarity")
async def compute_similarity(text: str, file: UploadFile):
    try:
        # Encode text
        text_embedding = await clip_service.encode_text(text)
        
        # Encode image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_embedding = await clip_service.encode_image(image)
        
        # Compute similarity
        similarity = await clip_service.compute_similarity(text_embedding, image_embedding)
        
        return {"similarity": similarity}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    clip_service.cleanup()
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size
   - Service automatically falls back to CPU
   - Check GPU memory availability

2. **Model Loading Errors**
   - Check internet connection for initial download
   - Verify transformers library version
   - Check disk space for model cache

3. **Performance Issues**
   - Monitor memory usage
   - Adjust batch size based on hardware
   - Use GPU if available

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

clip_service = CLIPService()
```

## Contributing

When extending the CLIP service:

1. Maintain backward compatibility
2. Add comprehensive error handling
3. Include unit tests for new features
4. Update documentation
5. Follow the existing code style
6. Consider memory and performance implications
