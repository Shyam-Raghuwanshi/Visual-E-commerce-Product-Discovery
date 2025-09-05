"""
Enhanced Search Service that integrates with the improved CLIP service.
This service provides comprehensive search functionality with proper error handling,
performance optimization, and production-ready features.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from PIL import Image
import io
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.clip_service import CLIPService
from app.services.vector_service import VectorService
from app.models.schemas import SearchResponse, Product, SearchRequest, CombinedSearchRequest
from app.utils.clip_config import VALIDATED_CONFIG

logger = logging.getLogger(__name__)

class EnhancedSearchService:
    """
    Enhanced search service with CLIP integration for text and image search.
    Provides high-performance search capabilities with proper error handling.
    """
    
    def __init__(self):
        """Initialize the enhanced search service"""
        self.clip_service = CLIPService(**VALIDATED_CONFIG)
        self.vector_service = VectorService()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Search configuration
        self.similarity_threshold = 0.1
        self.max_results = 100
        self.default_limit = 20
        
        logger.info("Enhanced Search Service initialized")
    
    async def search_by_text(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        min_similarity: float = 0.1
    ) -> SearchResponse:
        """
        Search for products using text query with enhanced features.
        
        Args:
            query: Text search query
            category: Optional category filter
            limit: Maximum number of results
            offset: Pagination offset
            min_similarity: Minimum similarity threshold
            
        Returns:
            SearchResponse with matching products
            
        Raises:
            ValueError: If query is invalid
            RuntimeError: If search fails
        """
        try:
            if not query or not query.strip():
                raise ValueError("Search query cannot be empty")
            
            logger.info(f"Searching by text: '{query}' (category: {category})")
            
            # Encode text query
            start_time = asyncio.get_event_loop().time()
            query_embedding = await self.clip_service.encode_text(query.strip())
            encoding_time = asyncio.get_event_loop().time() - start_time
            
            logger.debug(f"Text encoding took {encoding_time:.3f} seconds")
            
            # Search in vector database
            search_results = await self.vector_service.search_similar(
                query_vector=query_embedding,
                collection_name="products",
                limit=limit + offset,  # Get extra for pagination
                score_threshold=min_similarity,
                filter_conditions={"category": category} if category else None
            )
            
            # Apply pagination
            paginated_results = search_results[offset:offset + limit]
            
            # Convert to Product objects
            products = []
            for result in paginated_results:
                try:
                    product = Product(
                        id=result.get("id"),
                        name=result.get("name", ""),
                        description=result.get("description", ""),
                        category=result.get("category", ""),
                        price=result.get("price", 0.0),
                        image_url=result.get("image_url", ""),
                        similarity_score=result.get("score", 0.0)
                    )
                    products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            total_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Text search completed in {total_time:.3f} seconds, found {len(products)} products")
            
            return SearchResponse(
                query=query,
                products=products,
                total_count=len(search_results),
                limit=limit,
                offset=offset,
                search_time=total_time
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")
    
    async def search_by_image(
        self,
        file: "UploadFile",
        request: "ImageSearchRequest"
    ) -> Dict[str, Any]:
        """
        Search for products using an uploaded image file.
        
        Args:
            file: Uploaded image file
            request: Image search request parameters
            
        Returns:
            Dictionary with search results
            
        Raises:
            ValueError: If image is invalid
            RuntimeError: If search fails
        """
        try:
            logger.info(f"Searching by image: {file.filename} (category: {request.category})")
            
            start_time = asyncio.get_event_loop().time()
            
            # Read and process image
            image_data = await file.read()
            if not image_data:
                raise ValueError("Image file is empty")
            
            try:
                image = Image.open(io.BytesIO(image_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                raise ValueError(f"Invalid image format: {e}")
            
            # Encode image
            image_embedding = await self.clip_service.encode_image(image)
            encoding_time = asyncio.get_event_loop().time() - start_time
            
            logger.debug(f"Image encoding took {encoding_time:.3f} seconds")
            
            # Search in vector database
            search_results = await self.vector_service.search_similar(
                query_vector=image_embedding,
                collection_name="products",
                limit=request.limit + request.offset,
                score_threshold=request.similarity_threshold,
                filter_conditions={"category": request.category} if request.category else None
            )
            
            # Apply pagination
            paginated_results = search_results[request.offset:request.offset + request.limit]
            
            # Convert to Product objects
            products = []
            similarity_scores = []
            for result in paginated_results:
                try:
                    product_data = {
                        "id": result.get("id"),
                        "name": result.get("name", ""),
                        "description": result.get("description", ""),
                        "category": result.get("category", ""),
                        "price": result.get("price", 0.0),
                        "image_url": result.get("image_url", ""),
                        "created_at": result.get("created_at", "2024-01-01T00:00:00"),
                        "updated_at": result.get("updated_at", "2024-01-01T00:00:00"),
                    }
                    products.append(product_data)
                    similarity_scores.append(result.get("score", 0.0))
                except Exception as e:
                    logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            total_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Image search completed in {total_time:.3f} seconds, found {len(products)} products")
            
            return {
                "products": products,
                "total": len(search_results),
                "similarity_scores": similarity_scores,
                "query_time": total_time
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")
    
    async def search_combined(
        self,
        file: "UploadFile",
        request: "CombinedSearchRequest"
    ) -> Dict[str, Any]:
        """
        Search using both text and image with weighted combination.
        
        Args:
            file: Uploaded image file
            request: Combined search request parameters
            
        Returns:
            Dictionary with search results
            
        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If search fails
        """
        try:
            if not request.query or not request.query.strip():
                raise ValueError("Text query is required for combined search")
            
            logger.info(f"Combined search: '{request.query}' with image={file.filename}")
            
            start_time = asyncio.get_event_loop().time()
            
            # Encode text (always required)
            text_embedding = await self.clip_service.encode_text(request.query.strip())
            
            # Encode image
            image_data = await file.read()
            image_embedding = None
            if image_data:
                try:
                    image = Image.open(io.BytesIO(image_data))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image_embedding = await self.clip_service.encode_image(image)
                except Exception as e:
                    logger.warning(f"Failed to process image for combined search: {e}")
                    # Continue with text-only search
                    image_embedding = None
            
            # Create combined embedding
            if image_embedding is not None:
                # Weighted combination of text and image embeddings
                combined_embedding = (request.text_weight * text_embedding + 
                                    request.image_weight * image_embedding)
                # Normalize the combined embedding
                combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
            else:
                # Use only text embedding if image processing failed
                combined_embedding = text_embedding
                logger.info("Using text-only search due to image processing failure")
            
            encoding_time = asyncio.get_event_loop().time() - start_time
            logger.debug(f"Combined encoding took {encoding_time:.3f} seconds")
            
            # Search in vector database
            search_results = await self.vector_service.search_similar(
                query_vector=combined_embedding,
                collection_name="products",
                limit=request.limit + request.offset,
                score_threshold=0.1,  # Use default threshold for combined search
                filter_conditions={"category": request.category} if request.category else None
            )
            
            # Apply pagination
            paginated_results = search_results[request.offset:request.offset + request.limit]
            
            # Convert to Product objects
            products = []
            similarity_scores = []
            for result in paginated_results:
                try:
                    product_data = {
                        "id": result.get("id"),
                        "name": result.get("name", ""),
                        "description": result.get("description", ""),
                        "category": result.get("category", ""),
                        "price": result.get("price", 0.0),
                        "image_url": result.get("image_url", ""),
                        "created_at": result.get("created_at", "2024-01-01T00:00:00"),
                        "updated_at": result.get("updated_at", "2024-01-01T00:00:00"),
                    }
                    products.append(product_data)
                    similarity_scores.append(result.get("score", 0.0))
                except Exception as e:
                    logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            total_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Combined search completed in {total_time:.3f} seconds, found {len(products)} products")
            
            return {
                "products": products,
                "total": len(search_results),
                "similarity_scores": similarity_scores,
                "query_time": total_time
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Combined search failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")
    
    async def get_similar_products(
        self,
        product_id: str,
        limit: int = 10,
        min_similarity: float = 0.2
    ) -> SearchResponse:
        """
        Find products similar to a given product ID.
        
        Args:
            product_id: ID of the reference product
            limit: Maximum number of similar products
            min_similarity: Minimum similarity threshold
            
        Returns:
            SearchResponse with similar products
            
        Raises:
            ValueError: If product_id is invalid
            RuntimeError: If search fails
        """
        try:
            if not product_id:
                raise ValueError("Product ID cannot be empty")
            
            logger.info(f"Finding similar products for ID: {product_id}")
            
            start_time = asyncio.get_event_loop().time()
            
            # Get the reference product's embedding
            product_embedding = await self.vector_service.get_product_embedding(product_id)
            if product_embedding is None:
                raise ValueError(f"Product not found: {product_id}")
            
            # Search for similar products (exclude the reference product)
            search_results = await self.vector_service.search_similar(
                query_vector=product_embedding,
                collection_name="products",
                limit=limit + 1,  # Get one extra to exclude the reference
                score_threshold=min_similarity,
                exclude_ids=[product_id]
            )
            
            # Convert to Product objects
            products = []
            for result in search_results[:limit]:  # Take only the requested limit
                try:
                    product = Product(
                        id=result.get("id"),
                        name=result.get("name", ""),
                        description=result.get("description", ""),
                        category=result.get("category", ""),
                        price=result.get("price", 0.0),
                        image_url=result.get("image_url", ""),
                        similarity_score=result.get("score", 0.0)
                    )
                    products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            total_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Similar products search completed in {total_time:.3f} seconds, found {len(products)} products")
            
            return SearchResponse(
                query=f"similar_to:{product_id}",
                products=products,
                total_count=len(search_results),
                limit=limit,
                offset=0,
                search_time=total_time
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Similar products search failed: {e}")
            raise RuntimeError(f"Search failed: {str(e)}")
    
    async def get_categories(self) -> List[str]:
        """
        Get all available product categories.
        
        Returns:
            List of category names
        """
        try:
            categories = await self.vector_service.get_categories()
            return categories
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    async def index_product(
        self,
        product_id: str,
        name: str,
        description: str,
        category: str,
        price: float,
        image_url: str,
        image_data: Optional[bytes] = None
    ) -> bool:
        """
        Index a product for search.
        
        Args:
            product_id: Unique product identifier
            name: Product name
            description: Product description
            category: Product category
            price: Product price
            image_url: URL to product image
            image_data: Optional raw image data
            
        Returns:
            True if indexing succeeded
            
        Raises:
            ValueError: If required fields are missing
            RuntimeError: If indexing fails
        """
        try:
            if not all([product_id, name, category]):
                raise ValueError("Product ID, name, and category are required")
            
            logger.info(f"Indexing product: {product_id}")
            
            # Create combined text for encoding
            combined_text = f"{name} {description} {category}"
            
            # Encode text
            text_embedding = await self.clip_service.encode_text(combined_text)
            
            # Encode image if available
            image_embedding = None
            if image_data:
                try:
                    image = Image.open(io.BytesIO(image_data))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    image_embedding = await self.clip_service.encode_image(image)
                except Exception as e:
                    logger.warning(f"Failed to encode image for product {product_id}: {e}")
            
            # Combine embeddings if both are available
            if image_embedding is not None:
                # Weight text and image embeddings
                combined_embedding = 0.7 * text_embedding + 0.3 * image_embedding
                combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
            else:
                combined_embedding = text_embedding
            
            # Store in vector database
            success = await self.vector_service.add_product(
                product_id=product_id,
                embedding=combined_embedding,
                metadata={
                    "name": name,
                    "description": description,
                    "category": category,
                    "price": price,
                    "image_url": image_url
                }
            )
            
            if success:
                logger.info(f"Successfully indexed product: {product_id}")
            else:
                logger.error(f"Failed to index product: {product_id}")
            
            return success
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Product indexing failed: {e}")
            raise RuntimeError(f"Indexing failed: {str(e)}")
    
    async def batch_index_products(self, products: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Index multiple products in batch for efficiency.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        successful = 0
        failed = 0
        
        logger.info(f"Batch indexing {len(products)} products")
        
        # Process in smaller batches to manage memory
        batch_size = 10
        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            
            # Process batch
            tasks = []
            for product in batch:
                try:
                    task = self.index_product(
                        product_id=product["id"],
                        name=product.get("name", ""),
                        description=product.get("description", ""),
                        category=product.get("category", ""),
                        price=product.get("price", 0.0),
                        image_url=product.get("image_url", ""),
                        image_data=product.get("image_data")
                    )
                    tasks.append(task)
                except Exception as e:
                    logger.error(f"Failed to create indexing task for product {product.get('id')}: {e}")
                    failed += 1
            
            # Wait for batch to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                    elif result:
                        successful += 1
                    else:
                        failed += 1
        
        logger.info(f"Batch indexing completed: {successful} successful, {failed} failed")
        return successful, failed
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics and health information"""
        return {
            "clip_model_info": self.clip_service.get_model_info(),
            "similarity_threshold": self.similarity_threshold,
            "max_results": self.max_results,
            "default_limit": self.default_limit
        }
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            self.clip_service.cleanup()
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            logger.info("Enhanced Search Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during search service cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            asyncio.create_task(self.cleanup())
        except Exception:
            pass  # Ignore errors during destruction
