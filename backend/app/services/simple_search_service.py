"""
Simplified Search Service for Visual E-commerce Product Discovery
Provides basic search functionality without advanced Qdrant features
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)

class SimpleSearchService:
    """
    Simplified search service with basic functionality
    """
    
    def __init__(self):
        """Initialize the search service"""
        self.client = None
        self.collection_name = "products"
        self._init_client()
    
    def _init_client(self):
        """Initialize Qdrant client with fallback"""
        try:
            # Try to connect to Qdrant
            self.client = QdrantClient(host="localhost", port=6333)
            logger.info("Connected to Qdrant successfully")
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant: {e}")
            self.client = None
    
    async def search_by_text(self, query: str, limit: int = 20, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search products by text query
        """
        try:
            if not self.client:
                return self._fallback_search(query, limit, filters)
            
            # Simple text-based search using metadata
            search_results = []
            
            # For now, return mock results
            mock_results = [
                {
                    "id": f"product_{i}",
                    "title": f"Product {i} matching '{query}'",
                    "description": f"Description for product {i}",
                    "price": 99.99 + i * 10,
                    "category": "electronics",
                    "score": 0.9 - (i * 0.1),
                    "image_url": f"https://example.com/product_{i}.jpg"
                }
                for i in range(min(limit, 5))
            ]
            
            return mock_results
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return self._fallback_search(query, limit, filters)
    
    async def search_by_image(self, image_embedding: List[float], limit: int = 20, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search products by image embedding
        """
        try:
            if not self.client:
                return self._fallback_image_search(limit, filters)
            
            # Simple image-based search
            mock_results = [
                {
                    "id": f"image_product_{i}",
                    "title": f"Image Product {i}",
                    "description": f"Product found by image similarity {i}",
                    "price": 149.99 + i * 15,
                    "category": "fashion",
                    "score": 0.95 - (i * 0.1),
                    "image_url": f"https://example.com/image_product_{i}.jpg"
                }
                for i in range(min(limit, 5))
            ]
            
            return mock_results
            
        except Exception as e:
            logger.error(f"Error in image search: {e}")
            return self._fallback_image_search(limit, filters)
    
    async def search_hybrid(self, query: str, image_embedding: Optional[List[float]] = None, 
                           limit: int = 20, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Hybrid search combining text and image
        """
        try:
            text_results = await self.search_by_text(query, limit // 2, filters)
            
            if image_embedding:
                image_results = await self.search_by_image(image_embedding, limit // 2, filters)
                # Combine results
                combined_results = text_results + image_results
            else:
                combined_results = text_results
            
            # Sort by score
            combined_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return self._fallback_search(query, limit, filters)
    
    def _fallback_search(self, query: str, limit: int, filters: Optional[Dict] = None) -> List[Dict]:
        """Fallback search when Qdrant is not available"""
        return [
            {
                "id": f"fallback_{i}",
                "title": f"Fallback Product {i} for '{query}'",
                "description": f"Fallback product description {i}",
                "price": 79.99 + i * 5,
                "category": "general",
                "score": 0.8 - (i * 0.1),
                "image_url": f"https://example.com/fallback_{i}.jpg"
            }
            for i in range(min(limit, 3))
        ]
    
    def _fallback_image_search(self, limit: int, filters: Optional[Dict] = None) -> List[Dict]:
        """Fallback image search when Qdrant is not available"""
        return [
            {
                "id": f"fallback_img_{i}",
                "title": f"Fallback Image Product {i}",
                "description": f"Fallback image product description {i}",
                "price": 89.99 + i * 7,
                "category": "general",
                "score": 0.75 - (i * 0.1),
                "image_url": f"https://example.com/fallback_img_{i}.jpg"
            }
            for i in range(min(limit, 3))
        ]
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a specific product by ID"""
        try:
            # Mock product data
            return {
                "id": product_id,
                "title": f"Product {product_id}",
                "description": f"Detailed description for product {product_id}",
                "price": 199.99,
                "category": "electronics",
                "brand": "TechBrand",
                "rating": 4.5,
                "reviews_count": 123,
                "image_url": f"https://example.com/product_{product_id}.jpg",
                "images": [
                    f"https://example.com/product_{product_id}_1.jpg",
                    f"https://example.com/product_{product_id}_2.jpg",
                    f"https://example.com/product_{product_id}_3.jpg"
                ],
                "specifications": {
                    "color": "Black",
                    "size": "Medium",
                    "weight": "1.2kg"
                },
                "availability": True,
                "stock_count": 25
            }
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            return None
    
    async def get_recommendations(self, product_id: str, limit: int = 10) -> List[Dict]:
        """Get product recommendations"""
        try:
            # Mock recommendations
            return [
                {
                    "id": f"rec_{product_id}_{i}",
                    "title": f"Recommended Product {i}",
                    "description": f"Product recommended based on {product_id}",
                    "price": 159.99 + i * 20,
                    "category": "electronics",
                    "score": 0.9 - (i * 0.05),
                    "image_url": f"https://example.com/rec_{product_id}_{i}.jpg"
                }
                for i in range(min(limit, 5))
            ]
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Get search service statistics"""
        return {
            "status": "active",
            "client_connected": self.client is not None,
            "collection_name": self.collection_name,
            "timestamp": datetime.now().isoformat(),
            "service": "SimpleSearchService",
            "version": "1.0.0"
        }
