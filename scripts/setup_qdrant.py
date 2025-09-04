#!/usr/bin/env python3
"""
Qdrant Database Setup and Management Script
Initializes vector database, creates collections, and provides utility methods
for the Visual E-commerce Product Discovery platform.
"""

import os
import sys
import time
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    MatchValue, SearchRequest, CreateIndex, PayloadIndexParams,
    TextIndexParams, IntegerIndexParams
)
from qdrant_client.http.exceptions import UnexpectedResponse
import docker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    """Data structure for product information"""
    id: str
    name: str
    description: str
    price: float
    category: str
    brand: Optional[str]
    image_url: str
    embedding: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None

class QdrantDatabaseManager:
    """
    Comprehensive Qdrant database manager for e-commerce product search
    """
    
    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        collection_name: str = "products",
        vector_size: int = 512,
        distance_metric: Distance = Distance.COSINE
    ):
        """
        Initialize Qdrant database manager
        
        Args:
            url: Qdrant server URL
            api_key: API key for authentication
            collection_name: Name of the collection
            vector_size: Dimension of embedding vectors
            distance_metric: Distance metric for similarity search
        """
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance_metric = distance_metric
        self.client = None
        
    async def connect(self, max_retries: int = 5, retry_delay: int = 2) -> bool:
        """
        Connect to Qdrant database with retry logic
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay between retry attempts in seconds
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to Qdrant at {self.url} (attempt {attempt + 1}/{max_retries})")
                
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key,
                    timeout=10.0
                )
                
                # Test connection
                collections = self.client.get_collections()
                logger.info(f"Successfully connected to Qdrant. Found {len(collections.collections)} collections.")
                return True
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to Qdrant after all attempts")
                    return False
        
        return False
    
    async def initialize_docker_qdrant(self) -> bool:
        """
        Initialize Qdrant using Docker if not already running
        
        Returns:
            bool: True if Qdrant is running, False otherwise
        """
        try:
            docker_client = docker.from_env()
            
            # Check if Qdrant container is already running
            containers = docker_client.containers.list(filters={"name": "qdrant-ecommerce"})
            
            if containers:
                container = containers[0]
                if container.status == "running":
                    logger.info("Qdrant container is already running")
                    return True
                else:
                    logger.info("Starting existing Qdrant container")
                    container.start()
                    time.sleep(5)  # Wait for container to fully start
                    return True
            
            # Start new Qdrant container
            logger.info("Starting new Qdrant container...")
            
            container = docker_client.containers.run(
                "qdrant/qdrant:latest",
                name="qdrant-ecommerce",
                ports={"6333/tcp": 6333, "6334/tcp": 6334},
                volumes={"qdrant_storage": {"bind": "/qdrant/storage", "mode": "rw"}},
                environment={
                    "QDRANT__SERVICE__HTTP_PORT": "6333",
                    "QDRANT__SERVICE__GRPC_PORT": "6334"
                },
                detach=True,
                remove=False
            )
            
            logger.info(f"Qdrant container started: {container.id}")
            
            # Wait for Qdrant to be ready
            for i in range(30):  # Wait up to 30 seconds
                try:
                    test_client = QdrantClient(url=self.url, timeout=5.0)
                    test_client.get_collections()
                    logger.info("Qdrant is ready!")
                    return True
                except:
                    logger.info(f"Waiting for Qdrant to be ready... ({i+1}/30)")
                    time.sleep(1)
            
            logger.error("Qdrant failed to start within timeout period")
            return False
            
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            logger.info("Please ensure Docker is installed and running")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant with Docker: {str(e)}")
            return False
    
    async def create_collection(self, recreate: bool = False) -> bool:
        """
        Create products collection with proper configuration
        
        Args:
            recreate: Whether to recreate collection if it exists
            
        Returns:
            bool: True if collection created/exists, False otherwise
        """
        try:
            if not self.client:
                raise Exception("Not connected to Qdrant. Call connect() first.")
            
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name in collection_names:
                if recreate:
                    logger.info(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"Collection '{self.collection_name}' already exists")
                    return True
            
            # Create collection with vector configuration
            logger.info(f"Creating collection: {self.collection_name}")
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance_metric
                )
            )
            
            logger.info(f"Successfully created collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {str(e)}")
            return False
    
    async def setup_indexes(self) -> bool:
        """
        Set up payload indexes for fast filtering
        
        Returns:
            bool: True if indexes created successfully, False otherwise
        """
        try:
            if not self.client:
                raise Exception("Not connected to Qdrant. Call connect() first.")
            
            logger.info("Setting up payload indexes...")
            
            # Index for category filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="category",
                field_schema=PayloadIndexParams(
                    type="keyword"
                )
            )
            logger.info("Created index for 'category' field")
            
            # Index for brand filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="brand",
                field_schema=PayloadIndexParams(
                    type="keyword"
                )
            )
            logger.info("Created index for 'brand' field")
            
            # Index for price range filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="price",
                field_schema=PayloadIndexParams(
                    type="float"
                )
            )
            logger.info("Created index for 'price' field")
            
            # Index for text search on name and description
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="name",
                field_schema=PayloadIndexParams(
                    type="text",
                    text_index_params=TextIndexParams(
                        type="text",
                        tokenizer="word",
                        min_token_len=2,
                        max_token_len=15,
                        lowercase=True
                    )
                )
            )
            logger.info("Created text index for 'name' field")
            
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="description",
                field_schema=PayloadIndexParams(
                    type="text",
                    text_index_params=TextIndexParams(
                        type="text",
                        tokenizer="word",
                        min_token_len=2,
                        max_token_len=15,
                        lowercase=True
                    )
                )
            )
            logger.info("Created text index for 'description' field")
            
            logger.info("All payload indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
            return False
    
    async def bulk_insert_products(
        self, 
        products: List[ProductData], 
        batch_size: int = 100
    ) -> bool:
        """
        Bulk insert products into the collection
        
        Args:
            products: List of ProductData objects
            batch_size: Number of products to insert per batch
            
        Returns:
            bool: True if all products inserted successfully, False otherwise
        """
        try:
            if not self.client:
                raise Exception("Not connected to Qdrant. Call connect() first.")
            
            if not products:
                logger.warning("No products to insert")
                return True
            
            logger.info(f"Starting bulk insert of {len(products)} products...")
            
            # Process products in batches
            for i in range(0, len(products), batch_size):
                batch = products[i:i + batch_size]
                points = []
                
                for product in batch:
                    if product.embedding is None:
                        logger.warning(f"Product {product.id} has no embedding, skipping")
                        continue
                    
                    # Prepare payload
                    payload = {
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "price": product.price,
                        "category": product.category,
                        "brand": product.brand,
                        "image_url": product.image_url
                    }
                    
                    # Add custom metadata if available
                    if product.metadata:
                        payload.update(product.metadata)
                    
                    # Create point
                    point = PointStruct(
                        id=product.id,
                        vector=product.embedding.tolist(),
                        payload=payload
                    )
                    points.append(point)
                
                # Insert batch
                if points:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    logger.info(f"Inserted batch {i//batch_size + 1}: {len(points)} products")
            
            logger.info(f"Successfully inserted {len(products)} products")
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk insert products: {str(e)}")
            return False
    
    async def search_similar_products(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar products using vector similarity
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results to return
            category: Filter by category
            brand: Filter by brand
            min_price: Minimum price filter
            max_price: Maximum price filter
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            if not self.client:
                raise Exception("Not connected to Qdrant. Call connect() first.")
            
            # Build filter conditions
            filter_conditions = []
            
            if category:
                filter_conditions.append(
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category)
                    )
                )
            
            if brand:
                filter_conditions.append(
                    FieldCondition(
                        key="brand",
                        match=MatchValue(value=brand)
                    )
                )
            
            if min_price is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="price",
                        range={
                            "gte": min_price
                        }
                    )
                )
            
            if max_price is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="price",
                        range={
                            "lte": max_price
                        }
                    )
                )
            
            # Create filter
            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                query_filter=search_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            logger.info(f"Found {len(results)} similar products")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection
        
        Returns:
            Dict with collection statistics and configuration
        """
        try:
            if not self.client:
                raise Exception("Not connected to Qdrant. Call connect() first.")
            
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get collection statistics
            points_count = collection_info.points_count
            vectors_count = collection_info.vectors_count
            indexed_vectors_count = collection_info.indexed_vectors_count
            
            info = {
                "collection_name": self.collection_name,
                "points_count": points_count,
                "vectors_count": vectors_count,
                "indexed_vectors_count": indexed_vectors_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "status": collection_info.status.value
            }
            
            logger.info(f"Collection info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the database
        
        Returns:
            Dict with health status information
        """
        try:
            if not self.client:
                return {"status": "disconnected", "error": "No client connection"}
            
            # Test basic operations
            collections = self.client.get_collections()
            
            health_info = {
                "status": "healthy",
                "url": self.url,
                "collections_count": len(collections.collections),
                "target_collection_exists": self.collection_name in [c.name for c in collections.collections]
            }
            
            # If target collection exists, get more details
            if health_info["target_collection_exists"]:
                collection_info = await self.get_collection_info()
                health_info.update(collection_info)
            
            return health_info
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "url": self.url
            }

async def main():
    """
    Main function to demonstrate database setup and usage
    """
    print("🚀 Visual E-commerce Product Discovery - Qdrant Setup")
    print("=" * 60)
    
    # Initialize database manager
    db_manager = QdrantDatabaseManager()
    
    # Step 1: Initialize Docker Qdrant (if needed)
    print("\n📦 Step 1: Initializing Qdrant with Docker...")
    docker_success = await db_manager.initialize_docker_qdrant()
    if not docker_success:
        print("❌ Failed to initialize Qdrant with Docker")
        print("💡 Please ensure Docker is running or start Qdrant manually")
        return
    
    # Step 2: Connect to Qdrant
    print("\n🔌 Step 2: Connecting to Qdrant...")
    connection_success = await db_manager.connect()
    if not connection_success:
        print("❌ Failed to connect to Qdrant")
        return
    
    # Step 3: Create collection
    print("\n📊 Step 3: Creating products collection...")
    collection_success = await db_manager.create_collection(recreate=False)
    if not collection_success:
        print("❌ Failed to create collection")
        return
    
    # Step 4: Setup indexes
    print("\n🔍 Step 4: Setting up indexes...")
    index_success = await db_manager.setup_indexes()
    if not index_success:
        print("❌ Failed to create indexes")
        return
    
    # Step 5: Health check
    print("\n🏥 Step 5: Performing health check...")
    health_info = await db_manager.health_check()
    print(f"Health Status: {health_info}")
    
    # Step 6: Demo data insertion (optional)
    print("\n💾 Step 6: Testing with sample data...")
    
    # Create sample products
    sample_products = [
        ProductData(
            id="1",
            name="iPhone 15 Pro",
            description="Latest Apple smartphone with advanced features",
            price=999.99,
            category="electronics",
            brand="Apple",
            image_url="https://example.com/iphone15.jpg",
            embedding=np.random.rand(512).astype(np.float32)
        ),
        ProductData(
            id="2",
            name="Nike Air Max 270",
            description="Comfortable running shoes with Air Max technology",
            price=150.00,
            category="sports",
            brand="Nike",
            image_url="https://example.com/airmax270.jpg",
            embedding=np.random.rand(512).astype(np.float32)
        )
    ]
    
    # Insert sample data
    insert_success = await db_manager.bulk_insert_products(sample_products)
    if insert_success:
        print("✅ Sample data inserted successfully")
    else:
        print("❌ Failed to insert sample data")
    
    # Step 7: Test search
    print("\n🔎 Step 7: Testing search functionality...")
    query_vector = np.random.rand(512).astype(np.float32)
    search_results = await db_manager.search_similar_products(
        query_vector=query_vector,
        limit=5
    )
    
    print(f"Search returned {len(search_results)} results")
    for i, result in enumerate(search_results):
        print(f"  {i+1}. {result['payload']['name']} (score: {result['score']:.3f})")
    
    # Final status
    print("\n✅ Qdrant database setup completed successfully!")
    print("🎯 Your Visual E-commerce Product Discovery database is ready!")

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import qdrant_client
        import docker
        import numpy as np
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Please install required packages:")
        print("pip install qdrant-client docker numpy python-dotenv")
        sys.exit(1)
    
    # Run the main setup
    asyncio.run(main())
