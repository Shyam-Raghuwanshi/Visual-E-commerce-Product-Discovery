from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import numpy as np
from typing import List, Optional, Dict, Any
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.client = None
        self.collection_name = "products"
        self.vector_size = 512  # CLIP embedding size
        self.distance_metric = Distance.COSINE
        self._connect()
    
    def _connect(self, max_retries: int = 3, retry_delay: int = 2):
        """Connect to Qdrant database with retry logic"""
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Qdrant at {qdrant_url} (attempt {attempt + 1}/{max_retries})")
                
                self.client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                    timeout=10.0
                )
                
                # Test connection
                collections = self.client.get_collections()
                logger.info(f"Successfully connected to Qdrant. Found {len(collections.collections)} collections.")
                
                # Create collection if it doesn't exist
                self._create_collection_if_not_exists()
                return
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to connect to Qdrant after all attempts")
                    logger.error("Make sure Qdrant is running. You can start it with: cd docker && docker-compose up -d qdrant")
    
    def _create_collection_if_not_exists(self):
        """Create products collection if it doesn't exist"""
        try:
            if not self.client:
                logger.error("No client connection available")
                return
                
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=self.distance_metric
                    )
                )
                logger.info(f"Successfully created collection: {self.collection_name}")
                
                # Set up basic indexes
                self._setup_basic_indexes()
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
        
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
    
    def _setup_basic_indexes(self):
        """Set up basic payload indexes for filtering"""
        try:
            from qdrant_client.models import PayloadIndexParams
            
            # Index for category filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="category",
                field_schema=PayloadIndexParams(type="keyword")
            )
            
            # Index for brand filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="brand",
                field_schema=PayloadIndexParams(type="keyword")
            )
            
            # Index for price filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="price",
                field_schema=PayloadIndexParams(type="float")
            )
            
            logger.info("Basic indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes (this is not critical): {e}")
    
    async def search_similar(
        self,
        embedding: np.ndarray,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20,
        offset: int = 0,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Search for similar products using vector similarity with advanced filtering"""
        
        try:
            if not self.client:
                logger.error("No client connection available")
                return {"products": [], "total": 0, "scores": []}
            
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
                        range={"gte": min_price}
                    )
                )
            
            if max_price is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="price",
                        range={"lte": max_price}
                    )
                )
            
            # Create filter
            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)
            
            # Perform vector search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding.tolist(),
                query_filter=search_filter,
                limit=limit,
                offset=offset,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Process results
            products = []
            scores = []
            
            for result in search_results:
                # Ensure we have all required fields
                payload = result.payload
                product = {
                    "id": payload.get("id", str(result.id)),
                    "name": payload.get("name", "Unknown Product"),
                    "description": payload.get("description", ""),
                    "price": payload.get("price", 0.0),
                    "category": payload.get("category", "uncategorized"),
                    "brand": payload.get("brand"),
                    "image_url": payload.get("image_url", ""),
                    "created_at": payload.get("created_at", "2024-01-01T00:00:00"),
                    "updated_at": payload.get("updated_at", "2024-01-01T00:00:00")
                }
                
                products.append(product)
                scores.append(result.score)
            
            logger.info(f"Found {len(products)} similar products")
            
            return {
                "products": products,
                "total": len(products),
                "scores": scores
            }
        
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return {
                "products": [],
                "total": 0,
                "scores": []
            }
    
    async def get_similar_by_id(self, product_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get similar products by product ID"""
        
        try:
            if not self.client:
                logger.error("No client connection available")
                return {"products": [], "total": 0, "scores": []}
            
            # First, get the product by ID to get its vector
            try:
                product_points = self.client.retrieve(
                    collection_name=self.collection_name,
                    ids=[product_id],
                    with_vectors=True,
                    with_payload=True
                )
                
                if not product_points:
                    logger.warning(f"Product with ID {product_id} not found")
                    return {"products": [], "total": 0, "scores": []}
                
                product_point = product_points[0]
                
                # Use the product's vector to find similar products
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=product_point.vector,
                    limit=limit + 1,  # +1 to exclude the original product
                    with_payload=True,
                    with_vectors=False
                )
                
                # Process results and exclude the original product
                products = []
                scores = []
                
                for result in search_results:
                    if str(result.id) != str(product_id):  # Exclude the original product
                        payload = result.payload
                        product = {
                            "id": payload.get("id", str(result.id)),
                            "name": payload.get("name", "Unknown Product"),
                            "description": payload.get("description", ""),
                            "price": payload.get("price", 0.0),
                            "category": payload.get("category", "uncategorized"),
                            "brand": payload.get("brand"),
                            "image_url": payload.get("image_url", ""),
                            "created_at": payload.get("created_at", "2024-01-01T00:00:00"),
                            "updated_at": payload.get("updated_at", "2024-01-01T00:00:00")
                        }
                        
                        products.append(product)
                        scores.append(result.score)
                        
                        # Stop when we have enough results
                        if len(products) >= limit:
                            break
                
                logger.info(f"Found {len(products)} similar products for product {product_id}")
                
                return {
                    "products": products,
                    "total": len(products),
                    "scores": scores
                }
                
            except Exception as e:
                logger.error(f"Error retrieving product {product_id}: {e}")
                return {"products": [], "total": 0, "scores": []}
        
        except Exception as e:
            logger.error(f"Error getting similar products: {e}")
            return {
                "products": [],
                "total": 0,
                "scores": []
            }
    
    async def get_categories(self) -> List[str]:
        """Get all available product categories from the database"""
        
        try:
            if not self.client:
                logger.error("No client connection available")
                # Return default categories as fallback
                return [
                    "electronics", "clothing", "home", "sports", 
                    "books", "beauty", "automotive"
                ]
            
            # Get unique categories by scrolling through all points
            categories = set()
            offset = None
            limit = 1000
            
            while True:
                try:
                    batch = self.client.scroll(
                        collection_name=self.collection_name,
                        limit=limit,
                        offset=offset,
                        with_payload=True,
                        with_vectors=False
                    )
                    
                    if not batch[0]:  # No more points
                        break
                    
                    for point in batch[0]:
                        category = point.payload.get("category")
                        if category:
                            categories.add(category)
                    
                    offset = batch[1]  # Next offset
                    
                    # Prevent infinite loops
                    if offset is None:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error during category aggregation: {e}")
                    break
            
            category_list = sorted(list(categories))
            
            # If no categories found, return defaults
            if not category_list:
                logger.info("No categories found in database, returning defaults")
                return [
                    "electronics", "clothing", "home", "sports", 
                    "books", "beauty", "automotive"
                ]
            
            logger.info(f"Found {len(category_list)} categories: {category_list}")
            return category_list
        
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            # Return default categories as fallback
            return [
                "electronics", "clothing", "home", "sports", 
                "books", "beauty", "automotive"
            ]
    
    async def add_product(self, product_id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Add a product to the vector database"""
        
        try:
            point = PointStruct(
                id=product_id,
                vector=embedding.tolist(),
                payload=metadata
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
        except Exception as e:
            print(f"Error adding product: {e}")
