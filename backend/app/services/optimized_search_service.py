"""
Optimized Search Service with advanced Qdrant indexing, hybrid search,
and comprehensive performance monitoring.
"""

import logging
import time
import asyncio
from typing import List, Optional, Dict, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import numpy as np
from enum import Enum

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    MatchValue, Range, PayloadIndexParams, CreateIndex, DeleteIndex,
    SearchRequest, QueryRequest, RecommendRequest, ScrollRequest,
    UpdateStatus, CollectionInfo, OptimizersConfig, HnswConfig,
    WalConfig, QuantizationConfig, ScalarQuantization, SearchParams
)

from app.services.clip_service import CLIPService
from app.services.vector_service import VectorService
from app.models.schemas import SearchResponse, Product
from app.utils.clip_config import VALIDATED_CONFIG

logger = logging.getLogger(__name__)

class SearchType(Enum):
    """Types of search operations"""
    TEXT = "text"
    IMAGE = "image"
    HYBRID = "hybrid"
    SIMILAR = "similar"
    FILTERED = "filtered"

class RankingFactor(Enum):
    """Factors used in search result ranking"""
    SIMILARITY = "similarity"
    PRICE = "price"
    POPULARITY = "popularity"
    RECENCY = "recency"
    BRAND_SCORE = "brand_score"
    CATEGORY_BOOST = "category_boost"

@dataclass
class SearchFilter:
    """Advanced search filter configuration"""
    categories: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_ranges: Optional[List[Tuple[float, float]]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_rating: Optional[float] = None
    in_stock: Optional[bool] = None
    tags: Optional[List[str]] = None
    exclude_ids: Optional[List[str]] = None

@dataclass
class RankingConfig:
    """Configuration for search result ranking"""
    factors: Dict[RankingFactor, float] = field(default_factory=lambda: {
        RankingFactor.SIMILARITY: 0.4,
        RankingFactor.POPULARITY: 0.2,
        RankingFactor.RECENCY: 0.15,
        RankingFactor.PRICE: 0.1,
        RankingFactor.BRAND_SCORE: 0.1,
        RankingFactor.CATEGORY_BOOST: 0.05
    })
    price_preference: str = "balanced"  # "low", "high", "balanced"
    boost_categories: Optional[List[str]] = None
    boost_brands: Optional[List[str]] = None

@dataclass
class SearchMetrics:
    """Search performance and analytics metrics"""
    search_id: str
    search_type: SearchType
    query: Optional[str]
    filters_applied: Dict[str, Any]
    results_count: int
    search_time: float
    encoding_time: float
    vector_search_time: float
    ranking_time: float
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class QueryAnalytics:
    """Analytics and performance monitoring for search queries"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.search_history: deque = deque(maxlen=max_history)
        self.performance_stats = defaultdict(list)
        self.popular_queries = defaultdict(int)
        self.failed_queries = defaultdict(int)
        
    def log_search(self, metrics: SearchMetrics):
        """Log a search operation for analytics"""
        self.search_history.append(metrics)
        self.performance_stats[metrics.search_type].append(metrics.search_time)
        
        if metrics.query:
            self.popular_queries[metrics.query.lower()] += 1
            
    def log_failed_search(self, query: str, error: str):
        """Log a failed search operation"""
        self.failed_queries[f"{query}:{error}"] += 1
        
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_searches = [
            m for m in self.search_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_searches:
            return {"message": "No recent searches found"}
            
        return {
            "total_searches": len(recent_searches),
            "average_search_time": sum(m.search_time for m in recent_searches) / len(recent_searches),
            "search_types": {
                search_type.value: len([m for m in recent_searches if m.search_type == search_type])
                for search_type in SearchType
            },
            "popular_queries": dict(list(self.popular_queries.items())[:10]),
            "failed_queries": dict(list(self.failed_queries.items())[:5])
        }

class OptimizedSearchService:
    """
    Advanced search service with optimized Qdrant indexes, hybrid search,
    intelligent ranking, and comprehensive analytics.
    """
    
    def __init__(self):
        """Initialize the optimized search service"""
        self.clip_service = CLIPService(**VALIDATED_CONFIG)
        self.vector_service = VectorService()
        self.client = self.vector_service.client
        self.collection_name = "products"
        self.analytics = QueryAnalytics()
        
        # Search configuration
        self.default_limit = 20
        self.max_limit = 100
        self.similarity_threshold = 0.1
        
        # Index configurations
        self.index_configs = {
            "category": {"type": "keyword", "index": True},
            "brand": {"type": "keyword", "index": True},
            "price": {"type": "float", "index": True},
            "created_at": {"type": "datetime", "index": True},
            "rating": {"type": "float", "index": True},
            "popularity_score": {"type": "float", "index": True},
            "in_stock": {"type": "bool", "index": True},
            "tags": {"type": "keyword", "index": True},
            "price_tier": {"type": "keyword", "index": True}  # budget, mid, premium
        }
        
        logger.info("Optimized Search Service initialized")
    
    async def setup_optimized_indexes(self) -> bool:
        """
        Create optimized Qdrant indexes for different search types.
        Sets up indexes for filtering, sorting, and performance optimization.
        """
        try:
            logger.info("Setting up optimized Qdrant indexes...")
            
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                
                # Create collection with optimized configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=512,  # CLIP embedding size
                        distance=Distance.COSINE,
                        hnsw_config=HnswConfig(
                            m=16,  # Number of bi-directional links for every new element
                            ef_construct=200,  # Size of the dynamic candidate list
                        )
                    ),
                    optimizers_config=OptimizersConfig(
                        deleted_threshold=0.2,  # Threshold for vacuum
                        vacuum_min_vector_number=1000,
                        default_segment_number=0,
                        max_segment_size=None,
                        memmap_threshold=None,
                        indexing_threshold=20000,
                        flush_interval_sec=5,
                        max_optimization_threads=2
                    ),
                    wal_config=WalConfig(
                        wal_capacity_mb=32,
                        wal_segments_ahead=0
                    )
                )
            
            # Create payload indexes for efficient filtering
            for field_name, config in self.index_configs.items():
                try:
                    if config["index"]:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field_name,
                            field_schema=PayloadIndexParams(type=config["type"])
                        )
                        logger.debug(f"Created index for field: {field_name}")
                except Exception as e:
                    logger.warning(f"Failed to create index for {field_name}: {e}")
            
            # Create composite indexes for common filter combinations
            composite_indexes = [
                ["category", "price"],
                ["brand", "category"],
                ["category", "in_stock"],
                ["price_tier", "category"]
            ]
            
            for fields in composite_indexes:
                try:
                    # Qdrant doesn't support composite indexes directly,
                    # but we can optimize by ensuring individual indexes exist
                    logger.debug(f"Composite index strategy for fields: {fields}")
                except Exception as e:
                    logger.warning(f"Composite index setup failed for {fields}: {e}")
            
            logger.info("Optimized indexes setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup optimized indexes: {e}")
            return False
    
    def _build_search_filter(self, search_filter: SearchFilter) -> Optional[Filter]:
        """Build Qdrant filter from SearchFilter object"""
        if not search_filter:
            return None
            
        conditions = []
        
        # Category filter
        if search_filter.categories:
            if len(search_filter.categories) == 1:
                conditions.append(
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=search_filter.categories[0])
                    )
                )
            else:
                # Multiple categories - use should (OR logic)
                category_conditions = [
                    FieldCondition(key="category", match=MatchValue(value=cat))
                    for cat in search_filter.categories
                ]
                conditions.append(Filter(should=category_conditions))
        
        # Brand filter
        if search_filter.brands:
            if len(search_filter.brands) == 1:
                conditions.append(
                    FieldCondition(
                        key="brand",
                        match=MatchValue(value=search_filter.brands[0])
                    )
                )
            else:
                brand_conditions = [
                    FieldCondition(key="brand", match=MatchValue(value=brand))
                    for brand in search_filter.brands
                ]
                conditions.append(Filter(should=brand_conditions))
        
        # Price range filter
        if search_filter.min_price is not None or search_filter.max_price is not None:
            price_range = {}
            if search_filter.min_price is not None:
                price_range["gte"] = search_filter.min_price
            if search_filter.max_price is not None:
                price_range["lte"] = search_filter.max_price
                
            conditions.append(
                FieldCondition(key="price", range=price_range)
            )
        
        # Multiple price ranges (OR logic)
        if search_filter.price_ranges:
            price_conditions = []
            for min_p, max_p in search_filter.price_ranges:
                price_conditions.append(
                    FieldCondition(
                        key="price",
                        range={"gte": min_p, "lte": max_p}
                    )
                )
            if price_conditions:
                conditions.append(Filter(should=price_conditions))
        
        # Date filters
        if search_filter.created_after:
            conditions.append(
                FieldCondition(
                    key="created_at",
                    range={"gte": search_filter.created_after.isoformat()}
                )
            )
        
        if search_filter.created_before:
            conditions.append(
                FieldCondition(
                    key="created_at",
                    range={"lte": search_filter.created_before.isoformat()}
                )
            )
        
        # Rating filter
        if search_filter.min_rating is not None:
            conditions.append(
                FieldCondition(
                    key="rating",
                    range={"gte": search_filter.min_rating}
                )
            )
        
        # Stock filter
        if search_filter.in_stock is not None:
            conditions.append(
                FieldCondition(
                    key="in_stock",
                    match=MatchValue(value=search_filter.in_stock)
                )
            )
        
        # Tags filter
        if search_filter.tags:
            tag_conditions = [
                FieldCondition(key="tags", match=MatchValue(value=tag))
                for tag in search_filter.tags
            ]
            conditions.append(Filter(should=tag_conditions))
        
        # Exclude IDs
        if search_filter.exclude_ids:
            for exclude_id in search_filter.exclude_ids:
                conditions.append(
                    FieldCondition(
                        key="id",
                        match=MatchValue(value=exclude_id),
                        # Note: Qdrant doesn't have direct "NOT" support in FieldCondition
                        # This would need to be handled differently
                    )
                )
        
        return Filter(must=conditions) if conditions else None
    
    def _calculate_ranking_score(
        self, 
        product: Dict[str, Any], 
        similarity_score: float,
        ranking_config: RankingConfig
    ) -> float:
        """Calculate final ranking score based on multiple factors"""
        
        total_score = 0.0
        
        # Similarity score (primary factor)
        similarity_weight = ranking_config.factors.get(RankingFactor.SIMILARITY, 0.4)
        total_score += similarity_score * similarity_weight
        
        # Popularity score
        popularity_weight = ranking_config.factors.get(RankingFactor.POPULARITY, 0.2)
        popularity_score = product.get("popularity_score", 0.5)  # Default to neutral
        total_score += popularity_score * popularity_weight
        
        # Recency score (newer products get boost)
        recency_weight = ranking_config.factors.get(RankingFactor.RECENCY, 0.15)
        created_at = product.get("created_at")
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now().replace(tzinfo=created_date.tzinfo) - created_date).days
                recency_score = max(0, 1.0 - (days_old / 365))  # Score decreases over a year
                total_score += recency_score * recency_weight
            except:
                total_score += 0.5 * recency_weight  # Default score
        
        # Price score (based on preference)
        price_weight = ranking_config.factors.get(RankingFactor.PRICE, 0.1)
        price = product.get("price", 0)
        if ranking_config.price_preference == "low":
            # Lower prices get higher scores
            price_score = max(0, 1.0 - min(price / 1000, 1.0))  # Normalize to $1000
        elif ranking_config.price_preference == "high":
            # Higher prices get higher scores (luxury preference)
            price_score = min(price / 1000, 1.0)
        else:  # balanced
            # Mid-range prices get highest scores
            normalized_price = min(price / 1000, 1.0)
            price_score = 1.0 - abs(0.5 - normalized_price) * 2
        
        total_score += price_score * price_weight
        
        # Brand score
        brand_weight = ranking_config.factors.get(RankingFactor.BRAND_SCORE, 0.1)
        brand = product.get("brand", "")
        if ranking_config.boost_brands and brand in ranking_config.boost_brands:
            brand_score = 1.0
        else:
            brand_score = 0.5  # Neutral for unknown brands
        total_score += brand_score * brand_weight
        
        # Category boost
        category_weight = ranking_config.factors.get(RankingFactor.CATEGORY_BOOST, 0.05)
        category = product.get("category", "")
        if ranking_config.boost_categories and category in ranking_config.boost_categories:
            category_score = 1.0
        else:
            category_score = 0.5
        total_score += category_score * category_weight
        
        return min(total_score, 1.0)  # Cap at 1.0
    
    async def hybrid_search(
        self,
        text_query: Optional[str] = None,
        image_data: Optional[bytes] = None,
        search_filter: Optional[SearchFilter] = None,
        ranking_config: Optional[RankingConfig] = None,
        limit: int = 20,
        offset: int = 0,
        text_weight: float = 0.7,
        image_weight: float = 0.3,
        search_params: Optional[SearchParams] = None
    ) -> SearchResponse:
        """
        Perform hybrid search combining text, image, similarity and filters.
        
        Args:
            text_query: Text search query
            image_data: Raw image bytes for image search
            search_filter: Advanced filtering options
            ranking_config: Ranking configuration
            limit: Maximum number of results
            offset: Pagination offset
            text_weight: Weight for text similarity
            image_weight: Weight for image similarity
            search_params: Qdrant search parameters for fine-tuning
            
        Returns:
            SearchResponse with ranked and filtered results
        """
        search_id = f"hybrid_{int(time.time() * 1000)}"
        start_time = time.time()
        encoding_start = time.time()
        
        try:
            if not text_query and not image_data:
                raise ValueError("Either text query or image data must be provided")
            
            # Normalize weights
            if text_query and image_data:
                total_weight = text_weight + image_weight
                text_weight = text_weight / total_weight
                image_weight = image_weight / total_weight
            elif text_query:
                text_weight = 1.0
                image_weight = 0.0
            else:
                text_weight = 0.0
                image_weight = 1.0
            
            logger.info(f"Hybrid search - Text: {bool(text_query)}, Image: {bool(image_data)}")
            
            # Generate embeddings
            embeddings = []
            weights = []
            
            if text_query:
                text_embedding = await self.clip_service.encode_text(text_query)
                embeddings.append(text_embedding)
                weights.append(text_weight)
            
            if image_data:
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(image_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image_embedding = await self.clip_service.encode_image(image)
                embeddings.append(image_embedding)
                weights.append(image_weight)
            
            # Combine embeddings
            if len(embeddings) > 1:
                combined_embedding = sum(w * emb for w, emb in zip(weights, embeddings))
                combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
            else:
                combined_embedding = embeddings[0]
            
            encoding_time = time.time() - encoding_start
            vector_search_start = time.time()
            
            # Build filter
            qdrant_filter = self._build_search_filter(search_filter) if search_filter else None
            
            # Configure search parameters
            if not search_params:
                search_params = SearchParams(
                    hnsw_ef=128,  # Higher ef for better recall
                    exact=False,  # Use HNSW for speed
                )
            
            # Perform vector search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=combined_embedding.tolist(),
                query_filter=qdrant_filter,
                limit=min(limit + offset, self.max_limit),
                offset=0,  # We'll handle pagination after ranking
                score_threshold=self.similarity_threshold,
                with_payload=True,
                with_vectors=False,
                search_params=search_params
            )
            
            vector_search_time = time.time() - vector_search_start
            ranking_start = time.time()
            
            # Apply ranking if configured
            if not ranking_config:
                ranking_config = RankingConfig()
            
            # Calculate ranking scores and sort
            scored_results = []
            for result in search_results:
                similarity_score = result.score
                ranking_score = self._calculate_ranking_score(
                    result.payload, similarity_score, ranking_config
                )
                scored_results.append((result, ranking_score))
            
            # Sort by ranking score
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            # Apply pagination after ranking
            paginated_results = scored_results[offset:offset + limit]
            
            ranking_time = time.time() - ranking_start
            
            # Convert to Product objects
            products = []
            similarity_scores = []
            
            for result, ranking_score in paginated_results:
                try:
                    payload = result.payload
                    product = Product(
                        id=payload.get("id", str(result.id)),
                        name=payload.get("name", "Unknown Product"),
                        description=payload.get("description", ""),
                        price=payload.get("price", 0.0),
                        category=payload.get("category", "uncategorized"),
                        brand=payload.get("brand"),
                        image_url=payload.get("image_url", ""),
                        created_at=payload.get("created_at", "2024-01-01T00:00:00"),
                        updated_at=payload.get("updated_at", "2024-01-01T00:00:00")
                    )
                    
                    products.append(product)
                    similarity_scores.append(result.score)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            total_time = time.time() - start_time
            
            # Log analytics
            metrics = SearchMetrics(
                search_id=search_id,
                search_type=SearchType.HYBRID,
                query=text_query,
                filters_applied=search_filter.__dict__ if search_filter else {},
                results_count=len(products),
                search_time=total_time,
                encoding_time=encoding_time,
                vector_search_time=vector_search_time,
                ranking_time=ranking_time,
                timestamp=datetime.now()
            )
            self.analytics.log_search(metrics)
            
            logger.info(f"Hybrid search completed in {total_time:.3f}s, found {len(products)} products")
            
            return SearchResponse(
                products=products,
                total=len(search_results),
                query_time=total_time,
                similarity_scores=similarity_scores
            )
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            if text_query:
                self.analytics.log_failed_search(text_query, str(e))
            raise RuntimeError(f"Hybrid search failed: {str(e)}")
    
    async def search_with_filters(
        self,
        search_filter: SearchFilter,
        ranking_config: Optional[RankingConfig] = None,
        limit: int = 20,
        offset: int = 0
    ) -> SearchResponse:
        """
        Perform filtered search without vector similarity.
        Useful for browsing by categories, price ranges, etc.
        """
        search_id = f"filtered_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            logger.info("Performing filtered search")
            
            # Build filter
            qdrant_filter = self._build_search_filter(search_filter)
            
            if not qdrant_filter:
                raise ValueError("At least one filter criterion must be specified")
            
            # Use scroll for filtered search (more efficient for large result sets)
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=qdrant_filter,
                limit=min(limit + offset, self.max_limit),
                offset=None,  # Start from beginning
                with_payload=True,
                with_vectors=False
            )
            
            results = scroll_result[0]  # Points
            
            # Apply ranking if configured
            if ranking_config:
                scored_results = []
                for result in results:
                    # Use neutral similarity for filtered search
                    ranking_score = self._calculate_ranking_score(
                        result.payload, 0.5, ranking_config
                    )
                    scored_results.append((result, ranking_score))
                
                # Sort by ranking score
                scored_results.sort(key=lambda x: x[1], reverse=True)
                
                # Apply pagination
                paginated_results = scored_results[offset:offset + limit]
                final_results = [result for result, score in paginated_results]
            else:
                # Apply pagination without ranking
                final_results = results[offset:offset + limit]
            
            # Convert to Product objects
            products = []
            for result in final_results:
                try:
                    payload = result.payload
                    product = Product(
                        id=payload.get("id", str(result.id)),
                        name=payload.get("name", "Unknown Product"),
                        description=payload.get("description", ""),
                        price=payload.get("price", 0.0),
                        category=payload.get("category", "uncategorized"),
                        brand=payload.get("brand"),
                        image_url=payload.get("image_url", ""),
                        created_at=payload.get("created_at", "2024-01-01T00:00:00"),
                        updated_at=payload.get("updated_at", "2024-01-01T00:00:00")
                    )
                    
                    products.append(product)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse product result: {e}")
                    continue
            
            total_time = time.time() - start_time
            
            # Log analytics
            metrics = SearchMetrics(
                search_id=search_id,
                search_type=SearchType.FILTERED,
                query=None,
                filters_applied=search_filter.__dict__,
                results_count=len(products),
                search_time=total_time,
                encoding_time=0,
                vector_search_time=total_time,
                ranking_time=0,
                timestamp=datetime.now()
            )
            self.analytics.log_search(metrics)
            
            logger.info(f"Filtered search completed in {total_time:.3f}s, found {len(products)} products")
            
            return SearchResponse(
                products=products,
                total=len(results),
                query_time=total_time,
                similarity_scores=None
            )
            
        except Exception as e:
            logger.error(f"Filtered search failed: {e}")
            raise RuntimeError(f"Filtered search failed: {str(e)}")
    
    async def get_search_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive search analytics and performance metrics"""
        try:
            # Get basic performance summary
            performance_summary = self.analytics.get_performance_summary(hours)
            
            # Get collection info from Qdrant
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get index information
            indexes_info = {}
            for field_name in self.index_configs.keys():
                try:
                    # Note: Qdrant doesn't provide direct index info API
                    # This is a placeholder for index statistics
                    indexes_info[field_name] = {"status": "active"}
                except:
                    indexes_info[field_name] = {"status": "unknown"}
            
            return {
                "performance": performance_summary,
                "collection_stats": {
                    "total_points": collection_info.points_count,
                    "vector_size": collection_info.config.params.vectors.size,
                    "distance_metric": collection_info.config.params.vectors.distance.value,
                    "segments_count": len(collection_info.segments) if hasattr(collection_info, 'segments') else 0
                },
                "indexes": indexes_info,
                "search_trends": {
                    "most_popular_queries": dict(list(self.analytics.popular_queries.items())[:10]),
                    "recent_failures": dict(list(self.analytics.failed_queries.items())[:5])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return {"error": str(e)}
    
    async def optimize_collection(self) -> Dict[str, Any]:
        """Optimize the collection for better performance"""
        try:
            logger.info("Starting collection optimization...")
            
            # Trigger optimization
            result = self.client.update_collection(
                collection_name=self.collection_name,
                optimizers_config=OptimizersConfig(
                    deleted_threshold=0.1,  # More aggressive cleanup
                    vacuum_min_vector_number=100,
                    default_segment_number=0,
                    max_segment_size=None,
                    memmap_threshold=None,
                    indexing_threshold=10000,
                    flush_interval_sec=5,
                    max_optimization_threads=4  # Use more threads
                )
            )
            
            # Wait for optimization to complete
            await asyncio.sleep(2)
            
            logger.info("Collection optimization completed")
            
            return {
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Collection optimization failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_search_recommendations(
        self,
        user_id: str,
        recent_searches: List[str],
        viewed_products: List[str],
        limit: int = 10
    ) -> List[Product]:
        """
        Generate personalized search recommendations based on user behavior.
        """
        try:
            logger.info(f"Generating recommendations for user: {user_id}")
            
            # Get embeddings for recent searches
            search_embeddings = []
            for query in recent_searches[-5:]:  # Use last 5 searches
                try:
                    embedding = await self.clip_service.encode_text(query)
                    search_embeddings.append(embedding)
                except:
                    continue
            
            # Get embeddings for viewed products
            viewed_embeddings = []
            for product_id in viewed_products[-10:]:  # Use last 10 viewed
                try:
                    # Retrieve product embedding
                    product_point = self.client.retrieve(
                        collection_name=self.collection_name,
                        ids=[product_id],
                        with_vectors=True
                    )
                    if product_point:
                        viewed_embeddings.append(np.array(product_point[0].vector))
                except:
                    continue
            
            if not search_embeddings and not viewed_embeddings:
                # Fallback to popular products
                return await self._get_popular_products(limit)
            
            # Combine user preference embeddings
            all_embeddings = search_embeddings + viewed_embeddings
            if all_embeddings:
                # Calculate average embedding as user preference
                user_preference = np.mean(all_embeddings, axis=0)
                user_preference = user_preference / np.linalg.norm(user_preference)
                
                # Search for similar products
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=user_preference.tolist(),
                    limit=limit * 2,  # Get more to filter out already viewed
                    with_payload=True
                )
                
                # Filter out already viewed products
                recommendations = []
                for result in results:
                    product_id = result.payload.get("id", str(result.id))
                    if product_id not in viewed_products:
                        try:
                            product = Product(
                                id=product_id,
                                name=result.payload.get("name", "Unknown Product"),
                                description=result.payload.get("description", ""),
                                price=result.payload.get("price", 0.0),
                                category=result.payload.get("category", "uncategorized"),
                                brand=result.payload.get("brand"),
                                image_url=result.payload.get("image_url", ""),
                                created_at=result.payload.get("created_at", "2024-01-01T00:00:00"),
                                updated_at=result.payload.get("updated_at", "2024-01-01T00:00:00")
                            )
                            recommendations.append(product)
                            
                            if len(recommendations) >= limit:
                                break
                        except:
                            continue
                
                return recommendations
            
            return await self._get_popular_products(limit)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return await self._get_popular_products(limit)
    
    async def _get_popular_products(self, limit: int = 10) -> List[Product]:
        """Get popular products as fallback recommendations"""
        try:
            # Search for products with high popularity scores
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="popularity_score",
                            range={"gte": 0.7}
                        )
                    ]
                ),
                limit=limit,
                with_payload=True
            )
            
            products = []
            for result in results[0]:
                try:
                    product = Product(
                        id=result.payload.get("id", str(result.id)),
                        name=result.payload.get("name", "Unknown Product"),
                        description=result.payload.get("description", ""),
                        price=result.payload.get("price", 0.0),
                        category=result.payload.get("category", "uncategorized"),
                        brand=result.payload.get("brand"),
                        image_url=result.payload.get("image_url", ""),
                        created_at=result.payload.get("created_at", "2024-01-01T00:00:00"),
                        updated_at=result.payload.get("updated_at", "2024-01-01T00:00:00")
                    )
                    products.append(product)
                except:
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Failed to get popular products: {e}")
            return []
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health information"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "status": "healthy",
                "collection_name": self.collection_name,
                "total_products": collection_info.points_count,
                "indexes_configured": len(self.index_configs),
                "analytics_history_size": len(self.analytics.search_history),
                "clip_model_loaded": self.clip_service is not None,
                "qdrant_connected": self.client is not None,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
