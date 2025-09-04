from typing import List, Optional
import time
from app.models.schemas import SearchResponse, Product
from app.services.vector_service import VectorService
from app.services.clip_service import CLIPService

class SearchService:
    def __init__(self):
        self.vector_service = VectorService()
        self.clip_service = CLIPService()
    
    async def search_by_text(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResponse:
        """Search products using text query"""
        
        start_time = time.time()
        
        # Generate text embedding
        text_embedding = await self.clip_service.encode_text(query)
        
        # Search in vector database
        results = await self.vector_service.search_similar(
            embedding=text_embedding,
            category=category,
            limit=limit,
            offset=offset
        )
        
        query_time = time.time() - start_time
        
        return SearchResponse(
            products=results["products"],
            total=results["total"],
            query_time=query_time,
            similarity_scores=results["scores"]
        )
    
    async def search_combined(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResponse:
        """Search products using combined text and image embeddings"""
        
        start_time = time.time()
        
        # This will be implemented when we have image upload capability
        # For now, fallback to text search
        results = await self.search_by_text(query, category, limit, offset)
        
        return results
    
    async def get_similar_products(self, product_id: str, limit: int = 10):
        """Get products similar to a specific product"""
        
        start_time = time.time()
        
        # Get product embedding and find similar
        results = await self.vector_service.get_similar_by_id(product_id, limit)
        
        query_time = time.time() - start_time
        
        return SearchResponse(
            products=results["products"],
            total=results["total"],
            query_time=query_time,
            similarity_scores=results["scores"]
        )
    
    async def get_categories(self) -> List[str]:
        """Get all available product categories"""
        
        return await self.vector_service.get_categories()
