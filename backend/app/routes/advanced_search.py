"""
Advanced search routes with optimized indexing, hybrid search, and analytics.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from typing import List, Optional, Dict, Any
import logging
import asyncio
from datetime import datetime

from app.models.schemas import (
    SearchResponse, AdvancedSearchRequest, HybridSearchRequest,
    Product, UploadResponse
)
from app.services.optimized_search_service import (
    OptimizedSearchService, SearchFilter, RankingConfig, RankingFactor
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search/advanced", tags=["Advanced Search"])

# Global service instance
search_service = None

async def get_search_service() -> OptimizedSearchService:
    """Dependency to get the search service instance"""
    global search_service
    if search_service is None:
        search_service = OptimizedSearchService()
        # Setup indexes on first use
        await search_service.setup_optimized_indexes()
    return search_service

@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Perform hybrid search combining text query with advanced filtering and ranking.
    """
    try:
        # Build search filter
        search_filter = SearchFilter(
            categories=request.categories,
            brands=request.brands,
            min_price=request.min_price,
            max_price=request.max_price,
            min_rating=request.min_rating,
            in_stock=request.in_stock
        )
        
        # Build ranking config
        ranking_config = RankingConfig()
        if request.ranking_factors:
            # Map string keys to enum values
            factor_mapping = {
                "similarity": RankingFactor.SIMILARITY,
                "price": RankingFactor.PRICE,
                "popularity": RankingFactor.POPULARITY,
                "recency": RankingFactor.RECENCY,
                "brand_score": RankingFactor.BRAND_SCORE,
                "category_boost": RankingFactor.CATEGORY_BOOST
            }
            
            for factor_name, weight in request.ranking_factors.items():
                if factor_name in factor_mapping:
                    ranking_config.factors[factor_mapping[factor_name]] = weight
        
        # Perform hybrid search
        result = await service.hybrid_search(
            text_query=request.text_query,
            image_data=None,  # No image in this endpoint
            search_filter=search_filter,
            ranking_config=ranking_config,
            limit=request.limit,
            offset=request.offset,
            text_weight=request.text_weight,
            image_weight=request.image_weight
        )
        
        # Add metadata
        result.filters_applied = search_filter.__dict__
        result.search_type = "hybrid_text"
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.post("/hybrid-with-image", response_model=SearchResponse)
async def hybrid_search_with_image(
    text_query: Optional[str] = None,
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    brands: Optional[str] = Query(None, description="Comma-separated brands"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock: Optional[bool] = None,
    text_weight: float = 0.7,
    image_weight: float = 0.3,
    limit: int = 20,
    offset: int = 0,
    image: UploadFile = File(...),
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Perform hybrid search combining text query and image with advanced filtering.
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Parse comma-separated values
        category_list = categories.split(",") if categories else None
        brand_list = brands.split(",") if brands else None
        
        # Build search filter
        search_filter = SearchFilter(
            categories=category_list,
            brands=brand_list,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            in_stock=in_stock
        )
        
        # Use default ranking config
        ranking_config = RankingConfig()
        
        # Perform hybrid search
        result = await service.hybrid_search(
            text_query=text_query,
            image_data=image_data,
            search_filter=search_filter,
            ranking_config=ranking_config,
            limit=limit,
            offset=offset,
            text_weight=text_weight,
            image_weight=image_weight
        )
        
        # Add metadata
        result.filters_applied = search_filter.__dict__
        result.search_type = "hybrid_text_image"
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Hybrid search with image failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.post("/filtered", response_model=SearchResponse)
async def filtered_search(
    request: AdvancedSearchRequest,
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Perform filtered search without vector similarity.
    Useful for browsing by categories, price ranges, etc.
    """
    try:
        # Build search filter
        search_filter = SearchFilter(
            categories=[request.categories] if isinstance(request.categories, str) else request.categories,
            brands=[request.brands] if isinstance(request.brands, str) else request.brands,
            min_price=request.min_price,
            max_price=request.max_price,
            price_ranges=request.price_ranges,
            min_rating=request.min_rating,
            in_stock=request.in_stock,
            tags=request.tags
        )
        
        # Build ranking config based on sort_by
        ranking_config = None
        if request.sort_by and request.sort_by != "relevance":
            ranking_config = RankingConfig()
            
            if request.sort_by == "price_asc":
                ranking_config.price_preference = "low"
                ranking_config.factors[RankingFactor.PRICE] = 0.8
                ranking_config.factors[RankingFactor.SIMILARITY] = 0.1
            elif request.sort_by == "price_desc":
                ranking_config.price_preference = "high"
                ranking_config.factors[RankingFactor.PRICE] = 0.8
                ranking_config.factors[RankingFactor.SIMILARITY] = 0.1
            elif request.sort_by == "popularity":
                ranking_config.factors[RankingFactor.POPULARITY] = 0.6
                ranking_config.factors[RankingFactor.SIMILARITY] = 0.2
            elif request.sort_by == "rating":
                # This would need custom handling as rating isn't in RankingFactor
                pass
        
        # Perform filtered search
        result = await service.search_with_filters(
            search_filter=search_filter,
            ranking_config=ranking_config,
            limit=request.limit,
            offset=request.offset
        )
        
        # Add metadata
        result.filters_applied = search_filter.__dict__
        result.search_type = "filtered"
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Filtered search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/recommendations/{user_id}", response_model=List[Product])
async def get_search_recommendations(
    user_id: str,
    recent_searches: Optional[str] = Query(None, description="Comma-separated recent search queries"),
    viewed_products: Optional[str] = Query(None, description="Comma-separated product IDs"),
    limit: int = 10,
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Get personalized search recommendations based on user behavior.
    """
    try:
        # Parse comma-separated values
        search_list = recent_searches.split(",") if recent_searches else []
        viewed_list = viewed_products.split(",") if viewed_products else []
        
        # Get recommendations
        recommendations = await service.create_search_recommendations(
            user_id=user_id,
            recent_searches=search_list,
            viewed_products=viewed_list,
            limit=limit
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Failed to get recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.get("/analytics", response_model=Dict[str, Any])
async def get_search_analytics(
    hours: int = Query(24, description="Hours of history to analyze"),
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Get comprehensive search analytics and performance metrics.
    """
    try:
        analytics = await service.get_search_analytics(hours=hours)
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get search analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_search_collection(
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Trigger search collection optimization for better performance.
    This may take some time to complete.
    """
    try:
        result = await service.optimize_collection()
        return result
        
    except Exception as e:
        logger.error(f"Collection optimization failed: {e}")
        raise HTTPException(status_code=500, detail="Optimization failed")

@router.get("/health", response_model=Dict[str, Any])
async def get_search_health(
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Get comprehensive search service health information.
    """
    try:
        health_info = service.get_service_health()
        return health_info
        
    except Exception as e:
        logger.error(f"Failed to get search health: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.post("/indexes/setup", response_model=Dict[str, Any])
async def setup_search_indexes(
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Set up optimized search indexes. Call this after adding new data.
    """
    try:
        success = await service.setup_optimized_indexes()
        
        return {
            "status": "success" if success else "failed",
            "message": "Indexes setup completed" if success else "Indexes setup failed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Index setup failed: {e}")
        raise HTTPException(status_code=500, detail="Index setup failed")

@router.get("/categories", response_model=List[str])
async def get_search_categories(
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Get all available product categories for filtering.
    """
    try:
        categories = await service.vector_service.get_categories()
        return categories
        
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")

@router.get("/brands", response_model=List[str])
async def get_search_brands(
    limit: int = Query(50, description="Maximum number of brands to return"),
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Get all available product brands for filtering.
    """
    try:
        # This would need to be implemented in vector_service
        # For now, return a placeholder
        brands = [
            "Apple", "Samsung", "Nike", "Adidas", "Sony", "Microsoft",
            "Google", "Amazon", "Dell", "HP", "Canon", "Nikon",
            "LG", "Panasonic", "Philips", "Bosch", "GE", "Whirlpool"
        ]
        
        return brands[:limit]
        
    except Exception as e:
        logger.error(f"Failed to get brands: {e}")
        raise HTTPException(status_code=500, detail="Failed to get brands")

@router.get("/price-ranges", response_model=Dict[str, Any])
async def get_price_ranges(
    service: OptimizedSearchService = Depends(get_search_service)
):
    """
    Get price range statistics for the product catalog.
    """
    try:
        # This would need to be implemented to get actual price statistics
        # For now, return common price ranges
        return {
            "ranges": [
                {"label": "Under $25", "min": 0, "max": 25},
                {"label": "$25 - $50", "min": 25, "max": 50},
                {"label": "$50 - $100", "min": 50, "max": 100},
                {"label": "$100 - $250", "min": 100, "max": 250},
                {"label": "$250 - $500", "min": 250, "max": 500},
                {"label": "$500 - $1000", "min": 500, "max": 1000},
                {"label": "Over $1000", "min": 1000, "max": None}
            ],
            "statistics": {
                "min_price": 5.99,
                "max_price": 2999.99,
                "avg_price": 156.78,
                "median_price": 89.99
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get price ranges: {e}")
        raise HTTPException(status_code=500, detail="Failed to get price ranges")
