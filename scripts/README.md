# Scripts Directory

This directory contains utility scripts for setting up and managing the Visual E-commerce Product Discovery system.

## Dataset Creation Scripts

### Overview
The dataset creation system provides comprehensive tools for generating, validating, and managing product datasets for the visual e-commerce platform.

### Quick Start

#### 1. Basic Dataset Creation (Recommended)
```bash
# Check dependencies
python setup_dataset_creation.py --check-deps

# Create basic dataset (1000+ products)
python setup_dataset_creation.py --create-basic --count 1000

# Validate the created dataset
python setup_dataset_creation.py --validate data/product_dataset.json
```

#### 2. Enhanced Dataset Creation (Advanced)
```bash
# Install enhanced dependencies
python setup_dataset_creation.py --install-deps enhanced

# Create enhanced dataset with real data integration
python setup_dataset_creation.py --create-enhanced --count 1200

# Validate the enhanced dataset
python setup_dataset_creation.py --validate data/enhanced_product_dataset.json
```

### Available Scripts

#### 1. `setup_dataset_creation.py` - Main Setup and Runner
**Purpose**: Comprehensive dataset creation management
**Features**:
- Dependency checking and installation
- Environment setup
- Dataset creation with multiple modes
- Validation and quality checks
- Integration guidance

**Usage**:
```bash
# Show setup guide
python setup_dataset_creation.py --guide

# Check dependencies
python setup_dataset_creation.py --check-deps

# Install dependencies
python setup_dataset_creation.py --install-deps enhanced

# Create datasets
python setup_dataset_creation.py --create-basic --count 1000
python setup_dataset_creation.py --create-enhanced --count 1200

# Validate datasets
python setup_dataset_creation.py --validate data/product_dataset.json

# List available datasets
python setup_dataset_creation.py --list-datasets
```

#### 2. `create_product_dataset.py` - Basic Dataset Generator
**Purpose**: Generate synthetic product datasets
**Features**:
- 1000+ diverse product entries
- Multiple categories (clothing, shoes, accessories)
- Realistic product information
- Data validation and cleaning
- JSON export format

**Product Fields**:
- `id`, `name`, `description`, `category`, `subcategory`
- `price`, `brand`, `image_url`, `tags`
- `color`, `size`, `material`, `gender`, `season`
- `rating`, `review_count`, `availability`, `created_at`

#### 3. `enhanced_dataset_creator.py` - Advanced Dataset Generator
**Purpose**: Create enhanced datasets with real data integration
**Features**:
- Hugging Face dataset integration
- Real data + synthetic data hybrid
- Enhanced product attributes
- Multi-tier pricing
- Sustainability scores
- Advanced categorization

**Additional Fields**:
- `sku`, `weight`, `dimensions`, `care_instructions`
- `sustainability_score`, `discount_percentage`, `stock_quantity`
- `source` (synthetic/huggingface/api)

#### 4. `validate_dataset.py` - Dataset Validation
**Purpose**: Comprehensive dataset validation and analysis
**Features**:
- Data quality checks
- Statistical analysis
- Duplicate detection
- Export validation reports
- Quality scoring

**Validation Checks**:
- Field presence and coverage
- Data type validation
- Format validation (URLs, etc.)
- Range validation (prices, ratings)
- Duplicate detection
- Consistency analysis

#### 5. `run_dataset_creation.py` - Simple Runner
**Purpose**: Simple interface for dataset creation
**Usage**:
```bash
python run_dataset_creation.py --mode basic --count 1000
python run_dataset_creation.py --mode enhanced --count 1200
python run_dataset_creation.py --mode both --count 1000
```

### Dataset Structure

#### Basic Dataset Format
```json
{
  "metadata": {
    "total_products": 1000,
    "generated_at": "2025-09-04T10:30:00",
    "version": "1.0",
    "categories": ["clothing", "shoes", "accessories"],
    "description": "Fashion/Product dataset for Visual E-commerce"
  },
  "products": [
    {
      "id": "PROD_A1B2C3D4",
      "name": "Classic Cotton T-Shirt",
      "description": "Comfortable cotton t-shirt perfect for everyday wear...",
      "category": "clothing",
      "subcategory": "t-shirts",
      "price": 29.99,
      "brand": "Nike",
      "image_url": "https://source.unsplash.com/400x400/?t-shirt,fashion",
      "tags": ["clothing", "t-shirts", "cotton", "casual"],
      "color": "blue",
      "size": "M",
      "material": "cotton",
      "gender": "Men",
      "season": "All Season",
      "rating": 4.2,
      "review_count": 156,
      "availability": true,
      "created_at": "2025-09-04T10:30:00"
    }
  ]
}
```

#### Enhanced Dataset Additional Fields
```json
{
  "sku": "SKU_12345678",
  "weight": 150.5,
  "dimensions": {
    "length": 70.0,
    "width": 50.0,
    "sleeve_length": 25.0
  },
  "care_instructions": [
    "Machine wash cold",
    "Tumble dry low",
    "Do not bleach"
  ],
  "sustainability_score": 3.8,
  "discount_percentage": 15,
  "stock_quantity": 45,
  "source": "synthetic"
}
```

### Dependencies

#### Basic Mode (Minimal)
- Python 3.8+
- Standard library only
- `requests` (for image URLs)

#### Enhanced Mode (Full Features)
```bash
pip install pandas numpy datasets transformers torch requests Pillow
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Integration with Backend

After creating datasets, integrate them with the backend:

1. **Load into Vector Database**:
```bash
cd ../backend
python -m app.services.vector_service --load-dataset ../data/product_dataset.json
```

2. **Process Images with CLIP**:
```bash
python test_clip_service.py
```

3. **Start Backend Server**:
```bash
uvicorn main:app --reload
```

### Data Quality Guidelines

#### Quality Metrics
- **Completeness**: All required fields present
- **Validity**: Correct data types and formats
- **Uniqueness**: No duplicate IDs or exact matches
- **Consistency**: Uniform formatting and categories
- **Accuracy**: Realistic prices and attributes

#### Best Practices
1. Always validate datasets after creation
2. Review quality scores (aim for >85%)
3. Check for duplicate products
4. Verify image URL accessibility
5. Ensure price ranges are realistic
6. Test integration with backend services

### Troubleshooting

#### Common Issues

1. **Missing Dependencies**:
```bash
python setup_dataset_creation.py --install-deps enhanced
```

2. **Low Quality Scores**:
- Check data validation errors
- Review duplicate detection results
- Verify field completeness

3. **Integration Issues**:
- Ensure JSON format is valid
- Check file permissions
- Verify backend configuration

4. **Memory Issues**:
- Reduce batch size for large datasets
- Use basic mode for lower memory usage
- Clear cache between runs

### Performance Considerations

- **Basic Mode**: ~1000 products in 30-60 seconds
- **Enhanced Mode**: ~1200 products in 2-5 minutes (includes API calls)
- **Memory Usage**: 100-500MB depending on dataset size
- **Output Size**: ~1-10MB JSON files

### Future Enhancements

- [ ] Image processing and optimization
- [ ] Additional data sources (APIs, web scraping)
- [ ] Multi-language support
- [ ] Advanced categorization (ML-based)
- [ ] Real-time data updates
- [ ] Performance optimizations

### Support

For issues or questions:
1. Check the validation report for data quality issues
2. Review the setup guide for dependency problems
3. Consult the backend integration documentation
4. Check logs for detailed error messages

## Vector Generation Pipeline

### Overview
The vector generation pipeline creates CLIP embeddings for both product images and text descriptions, combines them optimally, and stores them in Qdrant for similarity search.

### 🚀 Quick Start

#### Complete Pipeline Setup (Recommended)
```bash
# Run complete setup (includes dataset creation, Qdrant setup, and vector generation)
python setup_vector_pipeline.py

# Or skip vector generation for setup only
python setup_vector_pipeline.py --skip-vectors

# Check current status
python setup_vector_pipeline.py --check-only
```

#### Manual Step-by-Step
```bash
# 1. Create product dataset (if not exists)
python create_product_dataset.py

# 2. Setup Qdrant vector database
python setup_qdrant.py setup

# 3. Run vector generation pipeline
python vector_generation_pipeline.py

# 4. Test the pipeline
python test_vector_pipeline.py --quick
```

### Pipeline Components

#### 1. `vector_generation_pipeline.py` - Main Pipeline
**Purpose**: Complete vector generation and storage pipeline

**Features**:
- ✅ Loads product data from JSON
- ✅ Downloads and caches product images
- ✅ Generates CLIP embeddings for text and images
- ✅ Combines embeddings with optimal weighting (70% image, 30% text)
- ✅ Stores vectors in Qdrant with metadata
- ✅ Progress tracking and checkpoint recovery
- ✅ Batch processing for memory efficiency
- ✅ Comprehensive error handling

**Configuration**:
```python
config = {
    'batch_size': 16,
    'max_concurrent_downloads': 8,
    'text_weight': 0.7,
    'image_weight': 0.3,
    'qdrant_host': 'localhost',
    'qdrant_port': 6333,
    'collection_name': 'product_vectors',
    'image_cache_dir': 'data/images',
    'checkpoint_file': 'data/pipeline_checkpoint.json'
}
```

#### 2. `setup_vector_pipeline.py` - Complete Setup
**Purpose**: Automated setup and execution of entire pipeline

**Phases**:
1. **System Requirements**: Check Python version, disk space, memory
2. **Dependencies**: Install and verify required packages
3. **Vector Database**: Setup and configure Qdrant
4. **Backend Services**: Verify CLIP service availability
5. **Product Dataset**: Create or validate product data
6. **Vector Generation**: Run embedding generation pipeline
7. **Testing**: Validate search functionality

**Usage**:
```bash
# Complete setup
python setup_vector_pipeline.py

# Setup without vector generation
python setup_vector_pipeline.py --skip-vectors

# Status check only
python setup_vector_pipeline.py --check-only
```

#### 3. `test_vector_pipeline.py` - Testing Suite
**Purpose**: Comprehensive testing of pipeline components

**Test Categories**:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Backend service integration
- **Performance Tests**: Batch processing benchmarks
- **Memory Tests**: Resource usage validation

**Usage**:
```bash
# Quick tests (development)
python test_vector_pipeline.py --quick

# Full test suite
python test_vector_pipeline.py

# Benchmark tests
python test_vector_pipeline.py --benchmark

# Integration tests only
python test_vector_pipeline.py --integration
```

#### 4. `run_vector_pipeline.py` - Pipeline Runner
**Purpose**: Orchestrate pipeline execution with status monitoring

**Features**:
- Dependency checking
- Qdrant connection verification
- Dataset validation
- Pipeline execution monitoring
- Results validation

### Technical Architecture

#### Image Processing Flow
```
Product URLs → Image Downloader → Cache → CLIP Image Encoder → Image Embeddings
```

#### Text Processing Flow
```
Product Data → Text Combiner → CLIP Text Encoder → Text Embeddings
```

#### Vector Combination Flow
```
Image Embeddings (70%) + Text Embeddings (30%) → Normalized Combined Vector
```

#### Storage Flow
```
Combined Vectors + Metadata → Qdrant Collection → Indexed for Search
```

### Configuration Options

#### Vector Configuration (`VectorConfig`)
```python
@dataclass
class VectorConfig:
    # CLIP settings
    clip_model: str = "openai/clip-vit-base-patch32"
    image_text_weight: float = 0.7  # 70% image, 30% text
    
    # Batch processing
    batch_size: int = 16
    max_concurrent_downloads: int = 8
    
    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "product_vectors"
    vector_size: int = 512  # CLIP ViT-B/32 embedding size
    
    # Image processing
    image_cache_dir: str = "data/images"
    max_image_size: int = 512
    timeout_seconds: int = 30
    
    # Error handling
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Progress tracking
    checkpoint_interval: int = 100
    checkpoint_file: str = "data/pipeline_checkpoint.json"
```

#### Performance Tuning
- **Batch Size**: Adjust based on available memory (16 recommended)
- **Concurrent Downloads**: Balance speed vs. server load (8 recommended)
- **Image/Text Weight**: Optimize for your use case (0.7/0.3 default)
- **Cache Directory**: Use fast storage for image cache

### Dependencies

#### Core Requirements
```
torch>=2.0.0
transformers>=4.30.0
qdrant-client>=1.6.0
Pillow>=9.0.0
numpy>=1.21.0
aiohttp>=3.8.0
tqdm>=4.65.0
```

#### Full Requirements (requirements_vector.txt)
```bash
pip install -r requirements_vector.txt
```

### Data Processing Pipeline

#### 1. Dataset Loading
- Loads product data from JSON
- Validates required fields
- Filters invalid entries

#### 2. Image Processing
- **Download**: Concurrent image fetching with retry logic
- **Cache**: Local storage to avoid re-downloading
- **Validation**: Image format and size validation
- **Processing**: Resize and normalize for CLIP

#### 3. Text Processing
- **Combination**: Merge name, description, category, tags
- **Cleaning**: Remove special characters, normalize whitespace
- **Optimization**: Create search-optimized text representations

#### 4. Embedding Generation
- **Batch Processing**: Process multiple items together for efficiency
- **CLIP Integration**: Use backend CLIP service
- **Error Handling**: Graceful handling of model failures
- **Quality Control**: Validate embedding dimensions and values

#### 5. Vector Storage
- **Metadata Preparation**: Extract relevant product attributes
- **Vector Combination**: Weighted combination of image and text embeddings
- **Qdrant Storage**: Bulk insertion with proper indexing
- **Validation**: Verify storage success and searchability

### Progress Tracking

#### Checkpoint System
- **Automatic Checkpoints**: Save progress every 100 products
- **Resume Capability**: Continue from last successful point
- **Status Tracking**: Monitor success/error rates
- **Performance Metrics**: Track processing speed and efficiency

#### Monitoring
```python
# Progress information
{
    "processed_count": 450,
    "success_count": 432,
    "error_count": 18,
    "processed_ids": ["PROD_001", "PROD_002", ...],
    "elapsed_time": 342.5,
    "processing_rate": 1.31  # products per second
}
```

### Error Handling

#### Retry Mechanisms
- **Image Downloads**: 3 retry attempts with exponential backoff
- **CLIP Processing**: Automatic fallback and error recovery
- **Qdrant Operations**: Connection retry and batch retry logic

#### Error Recovery
- **Checkpoint Recovery**: Resume from last successful state
- **Partial Failures**: Continue processing despite individual failures
- **Graceful Degradation**: Process available data even with some failures

### Performance Characteristics

#### Typical Performance
- **Dataset Size**: 1200 products
- **Processing Time**: 15-30 minutes (depending on system)
- **Memory Usage**: 2-4GB peak usage
- **Storage Requirements**: 100MB-2GB (images + vectors)

#### Optimization Tips
1. **GPU Usage**: Ensure CUDA available for faster CLIP processing
2. **SSD Storage**: Use SSD for image cache directory
3. **Network**: Stable internet for image downloads
4. **Memory**: 8GB+ RAM recommended for large datasets
5. **Batch Size**: Adjust based on available memory

### Integration with Backend

#### CLIP Service Integration
```python
# Backend CLIP service usage
from app.services.clip_service import CLIPService

clip_service = CLIPService(batch_size=16)
text_embedding = await clip_service.encode_text("product description")
image_embedding = await clip_service.encode_image(pil_image)
```

#### Qdrant Integration
```python
# Direct Qdrant operations
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)
results = client.search(
    collection_name="product_vectors",
    query_vector=search_vector,
    limit=10
)
```

### Troubleshooting

#### Common Issues

1. **Memory Errors**:
   - Reduce batch_size to 8 or 4
   - Close other applications
   - Use CPU instead of GPU if GPU memory limited

2. **Network Issues**:
   - Check internet connection
   - Reduce max_concurrent_downloads
   - Increase timeout_seconds

3. **Qdrant Connection**:
   - Verify Qdrant is running: `docker ps`
   - Check port availability: `netstat -ln | grep 6333`
   - Restart Qdrant container if needed

4. **CLIP Model Issues**:
   - Verify backend services are running
   - Check model downloads completed
   - Ensure sufficient disk space for models

#### Debug Mode
```bash
# Enable detailed logging
export PYTHONPATH="${PYTHONPATH}:../backend"
python vector_generation_pipeline.py --log-level DEBUG
```

#### Monitoring Progress
```bash
# Check pipeline status
tail -f vector_pipeline.log

# Monitor checkpoint file
watch -n 5 "jq '.processed_count' data/pipeline_checkpoint.json"

# Check Qdrant collection
curl http://localhost:6333/collections/product_vectors
```

### Vector Database Setup

See the existing setup scripts for Qdrant vector database configuration.

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
cd scripts
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
cd scripts
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 setup_qdrant.py
```

## 🔧 Features

### Main Setup Script (`setup_qdrant.py`)
- ✅ Docker container management for Qdrant
- ✅ Automatic connection with retry logic
- ✅ Collection creation with 512-dimensional vectors
- ✅ Optimized indexing for fast similarity search
- ✅ Bulk data insertion capabilities
- ✅ Advanced search with filtering
- ✅ Comprehensive error handling
- ✅ Health monitoring and diagnostics

### Utility Functions (`qdrant_utils.py`)
- 📊 Collection statistics and analytics
- 💾 Backup and restore functionality
- 🧹 Collection maintenance tools
- ⚡ Performance optimization

## 📋 Usage Examples

### Health Check
```python
from setup_qdrant import QdrantDatabaseManager

db_manager = QdrantDatabaseManager()
await db_manager.connect()
health_info = await db_manager.health_check()
print(health_info)
```

### Bulk Insert Products
```python
from setup_qdrant import ProductData
import numpy as np

products = [
    ProductData(
        id="1",
        name="iPhone 15 Pro",
        description="Latest Apple smartphone",
        price=999.99,
        category="electronics",
        brand="Apple",
        image_url="https://example.com/image.jpg",
        embedding=np.random.rand(512).astype(np.float32)
    )
]

await db_manager.bulk_insert_products(products)
```

### Search Similar Products
```python
query_vector = np.random.rand(512).astype(np.float32)
results = await db_manager.search_similar_products(
    query_vector=query_vector,
    limit=10,
    category="electronics",
    min_price=100.0,
    max_price=1000.0
)
```

## 🐳 Docker Configuration

The script automatically manages a Qdrant Docker container with:
- **Container Name**: `qdrant-ecommerce`
- **HTTP Port**: 6333
- **gRPC Port**: 6334
- **Persistent Storage**: `qdrant_storage` volume

## 🔍 Collection Schema

### Vector Configuration
- **Size**: 512 dimensions (CLIP embeddings)
- **Distance**: Cosine similarity
- **Collection Name**: `products`

### Indexed Fields
- `category` - Keyword index for category filtering
- `brand` - Keyword index for brand filtering
- `price` - Float index for price range filtering
- `name` - Text index for product name search
- `description` - Text index for description search

### Payload Structure
```json
{
  "id": "unique_product_id",
  "name": "Product Name",
  "description": "Product description...",
  "price": 99.99,
  "category": "electronics",
  "brand": "BrandName",
  "image_url": "https://example.com/image.jpg"
}
```

## 🛠️ Configuration

### Environment Variables (.env)
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key_here
```

### Database Settings
- Default collection: `products`
- Vector size: 512
- Distance metric: Cosine
- Batch size: 100 (for bulk operations)

## 🔒 Error Handling

The scripts include comprehensive error handling for:
- Docker connection issues
- Qdrant service unavailability
- Collection creation failures
- Index setup problems
- Network timeouts
- Invalid data formats

## 📊 Performance Features

- **Batch Processing**: Efficient bulk operations
- **Connection Pooling**: Optimized client connections
- **Retry Logic**: Automatic retry for transient failures
- **Indexing**: Pre-configured indexes for fast filtering
- **Memory Optimization**: Proper resource management

## 🔧 Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   sudo systemctl start docker  # Linux
   # or start Docker Desktop on Windows/Mac
   ```

2. **Port conflicts**
   - Change ports in docker-compose.yml
   - Update QDRANT_URL in .env file

3. **Permission issues**
   ```bash
   sudo chown -R $USER:$USER qdrant_storage/
   ```

4. **Memory issues**
   - Reduce batch_size in bulk operations
   - Monitor Docker container memory usage

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Next Steps

After running the setup:

1. **Backend Integration**: Update your FastAPI vector service to use the configured database
2. **CLIP Integration**: Generate embeddings for your product catalog
3. **Data Import**: Use the bulk insert methods to populate your database
4. **Performance Tuning**: Monitor and optimize based on your data size

## 📞 Support

For issues with the Qdrant setup, check:
- Docker container logs: `docker logs qdrant-ecommerce`
- Qdrant health endpoint: `http://localhost:6333/health`
- Script logs for detailed error information
