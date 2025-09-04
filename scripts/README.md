# Qdrant Database Scripts

This directory contains scripts for setting up and managing the Qdrant vector database for the Visual E-commerce Product Discovery platform.

## 📁 Files

- `setup_qdrant.py` - Main setup script for initializing Qdrant with Docker
- `qdrant_utils.py` - Utility functions for database maintenance
- `setup.sh` - Automated bash setup script
- `requirements.txt` - Python dependencies for the scripts

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
