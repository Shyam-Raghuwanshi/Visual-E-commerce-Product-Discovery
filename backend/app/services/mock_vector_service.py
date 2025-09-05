"""
Mock Vector Service for Advanced Search Demo
Provides a simple implementation for demonstration purposes
"""

import logging
import time
import numpy as np
from typing import List, Optional, Dict, Any, Union
import io

logger = logging.getLogger(__name__)

class MockVectorService:
    """
    Mock vector service for demonstration purposes.
    Generates random embeddings and provides basic similarity search.
    """
    
    def __init__(self):
        self.vector_size = 512
        self.mock_database = {}  # Simple in-memory storage
        logger.info("Mock Vector Service initialized")
    
    async def generate_image_embedding(self, image_data: Union[bytes, str]) -> np.ndarray:
        """
        Generate a mock image embedding
        
        Args:
            image_data: Image data as bytes or base64 string
            
        Returns:
            Mock embedding as numpy array
        """
        try:
            # Simulate processing time
            import time
            time.sleep(0.1)
            
            # Generate a deterministic but seemingly random embedding
            if isinstance(image_data, bytes):
                # Use hash of image data for consistency
                seed = hash(image_data) % (2**32)
            else:
                seed = hash(str(image_data)) % (2**32)
            
            np.random.seed(seed)
            embedding = np.random.rand(self.vector_size)
            
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.debug(f"Generated mock image embedding with seed {seed}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating mock image embedding: {e}")
            # Return a random embedding as fallback
            return np.random.rand(self.vector_size)
    
    async def generate_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate a mock text embedding
        
        Args:
            text: Input text
            
        Returns:
            Mock embedding as numpy array
        """
        try:
            # Generate deterministic embedding based on text content
            seed = hash(text) % (2**32)
            np.random.seed(seed)
            embedding = np.random.rand(self.vector_size)
            
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            logger.debug(f"Generated mock text embedding for: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating mock text embedding: {e}")
            return np.random.rand(self.vector_size)
    
    async def store_product_embedding(
        self,
        product_id: str,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a product embedding in mock database
        
        Args:
            product_id: Unique product identifier
            embedding: Product embedding vector
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            self.mock_database[product_id] = {
                "embedding": embedding,
                "metadata": metadata or {}
            }
            logger.debug(f"Stored embedding for product {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing product embedding: {e}")
            return False
    
    async def search_similar_products(
        self,
        query_embedding: np.ndarray,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar products using mock similarity
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            filters: Optional filters
            
        Returns:
            List of similar products with scores
        """
        try:
            results = []
            
            for product_id, data in self.mock_database.items():
                product_embedding = data["embedding"]
                metadata = data["metadata"]
                
                # Apply basic filters
                if filters:
                    skip_product = False
                    for filter_key, filter_value in filters.items():
                        if filter_key in metadata and metadata[filter_key] != filter_value:
                            skip_product = True
                            break
                    if skip_product:
                        continue
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, product_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding)
                )
                
                results.append({
                    "product_id": product_id,
                    "similarity_score": float(similarity),
                    "metadata": metadata
                })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.debug(f"Found {len(results[:limit])} similar products")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching similar products: {e}")
            return []
    
    async def get_product_embedding(self, product_id: str) -> Optional[np.ndarray]:
        """
        Get embedding for a specific product
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product embedding or None if not found
        """
        try:
            if product_id in self.mock_database:
                return self.mock_database[product_id]["embedding"]
            else:
                logger.warning(f"Product embedding not found for {product_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting product embedding: {e}")
            return None
    
    async def batch_search_similar_products(
        self,
        query_embeddings: List[np.ndarray],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Batch search for multiple query embeddings
        
        Args:
            query_embeddings: List of query embeddings
            limit: Maximum results per query
            filters: Optional filters
            
        Returns:
            List of result lists
        """
        try:
            results = []
            for embedding in query_embeddings:
                result = await self.search_similar_products(embedding, limit, filters)
                results.append(result)
            
            logger.debug(f"Completed batch search for {len(query_embeddings)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch search: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the mock collection
        
        Returns:
            Collection information
        """
        return {
            "name": "mock_products",
            "vector_size": self.vector_size,
            "total_products": len(self.mock_database),
            "status": "active"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the service
        
        Returns:
            Health status information
        """
        try:
            return {
                "status": "healthy",
                "service": "mock_vector_service",
                "total_embeddings": len(self.mock_database),
                "vector_size": self.vector_size,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

# For backward compatibility, create an alias
VectorService = MockVectorService
