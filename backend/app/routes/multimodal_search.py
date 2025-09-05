"""
Multi-Modal Search Enhancement Routes

Advanced search endpoints that showcase vector search capabilities:
- Find items that match this outfit but in a different color
- Show me cheaper alternatives to this luxury item
- Find accessories that go with this dress
- Seasonal recommendations based on current trends
- Style evolution ("make this more casual/formal")
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import asyncio

from app.services.multimodal_search_service import MultiModalSearchService
from app.models.schemas import (
    ColorVariationRequest, ColorVariationResponse,
    CheaperAlternativesRequest, CheaperAlternativesResponse,
    AccessoryMatchingRequest, AccessoryMatchingResponse,
    SeasonalRecommendationsRequest, SeasonalRecommendationsResponse,
    StyleEvolutionRequest, StyleEvolutionResponse,
    MultiModalSearchResponse, ErrorResponse
)
from app.middleware.rate_limiting import RateLimit
from app.middleware.authentication import get_api_key

logger = logging.getLogger(__name__)

# Create router for multi-modal search
router = APIRouter(prefix="/api/v1/multimodal", tags=["Multi-Modal Search"])

# Initialize the multi-modal search service
multimodal_service = MultiModalSearchService()

@router.post("/color-variations", 
             response_model=ColorVariationResponse,
             summary="Find Color Variations",
             description="Find items similar to a product but in different colors")
@RateLimit(max_requests=20, window_seconds=60)
async def find_color_variations(
    request: ColorVariationRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Find items that match a product's style but in different colors.
    
    This endpoint uses vector similarity to find products with similar style
    characteristics but in the specified target colors.
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Color variation search for product {request.product_id}")
        
        result = await multimodal_service.find_color_variations(
            product_id=request.product_id,
            target_colors=request.target_colors,
            limit=request.limit
        )
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return ColorVariationResponse(
            reference_product=result["reference_product"],
            target_colors=result["target_colors"],
            color_variations=result["color_variations"],
            total_found=result["total_found"],
            search_strategy=result["search_strategy"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid color variation request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Color variation search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/cheaper-alternatives",
             response_model=CheaperAlternativesResponse,
             summary="Find Cheaper Alternatives",
             description="Find budget-friendly alternatives to luxury items")
@RateLimit(max_requests=15, window_seconds=60)
async def find_cheaper_alternatives(
    request: CheaperAlternativesRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Find cheaper alternatives to luxury items while maintaining style similarity.
    
    Uses vector search to find products with similar aesthetic characteristics
    but at lower price points.
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Cheaper alternatives search for product {request.product_id}")
        
        result = await multimodal_service.find_cheaper_alternatives(
            product_id=request.product_id,
            max_price_ratio=request.max_price_ratio,
            limit=request.limit
        )
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return CheaperAlternativesResponse(
            reference_product=result["reference_product"],
            reference_price=result["reference_price"],
            max_target_price=result["max_target_price"],
            cheaper_alternatives=result["cheaper_alternatives"],
            total_found=result["total_found"],
            average_savings=result["average_savings"],
            search_strategy=result["search_strategy"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid cheaper alternatives request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cheaper alternatives search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/accessory-matching",
             response_model=AccessoryMatchingResponse,
             summary="Find Matching Accessories",
             description="Find accessories that complement a clothing item")
@RateLimit(max_requests=25, window_seconds=60)
async def find_matching_accessories(
    request: AccessoryMatchingRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Find accessories that go well with a specific clothing item.
    
    Analyzes style, color, season, and other attributes to suggest
    complementary accessories like bags, shoes, jewelry, etc.
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Accessory matching for clothing item {request.clothing_product_id}")
        
        result = await multimodal_service.find_matching_accessories(
            clothing_product_id=request.clothing_product_id,
            accessory_types=request.accessory_types,
            limit=request.limit
        )
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return AccessoryMatchingResponse(
            clothing_item=result["clothing_item"],
            matching_accessories=result["matching_accessories"],
            total_accessories_found=result["total_accessories_found"],
            accessory_types_searched=result["accessory_types_searched"],
            search_strategy=result["search_strategy"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid accessory matching request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Accessory matching search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/seasonal-recommendations",
             response_model=SeasonalRecommendationsResponse,
             summary="Get Seasonal Recommendations",
             description="Get product recommendations based on seasonal trends")
@RateLimit(max_requests=30, window_seconds=60)
async def get_seasonal_recommendations(
    request: SeasonalRecommendationsRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Get seasonal product recommendations based on current trends.
    
    Analyzes seasonal keywords, trends, and user preferences to suggest
    products that are appropriate and fashionable for the specified season.
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Seasonal recommendations for {request.season}")
        
        result = await multimodal_service.get_seasonal_recommendations(
            season=request.season,
            user_preferences=request.user_preferences,
            limit=request.limit
        )
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return SeasonalRecommendationsResponse(
            season=result["season"],
            seasonal_keywords=result["seasonal_keywords"],
            user_preferences=result["user_preferences"],
            top_recommendations=result["top_recommendations"],
            categorized_recommendations=result["categorized_recommendations"],
            total_found=result["total_found"],
            average_trend_score=result["average_trend_score"],
            search_strategy=result["search_strategy"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid seasonal recommendations request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Seasonal recommendations failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/style-evolution",
             response_model=StyleEvolutionResponse,
             summary="Style Evolution Search",
             description="Transform a product's style (make it more casual/formal/etc.)")
@RateLimit(max_requests=20, window_seconds=60)
async def style_evolution_search(
    request: StyleEvolutionRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Transform a product's style to a different aesthetic.
    
    Uses vector space manipulation to find products that represent
    a style evolution from the original (e.g., casual to formal,
    sporty to elegant, etc.).
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Style evolution search: {request.product_id} -> {request.target_style}")
        
        result = await multimodal_service.style_evolution_search(
            product_id=request.product_id,
            target_style=request.target_style,
            intensity=request.intensity,
            limit=request.limit
        )
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return StyleEvolutionResponse(
            original_product=result["original_product"],
            target_style=result["target_style"],
            transformation_intensity=result["transformation_intensity"],
            style_evolved_products=result["style_evolved_products"],
            total_found=result["total_found"],
            average_style_score=result["average_style_score"],
            search_strategy=result["search_strategy"]
        )
        
    except ValueError as e:
        logger.warning(f"Invalid style evolution request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Style evolution search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/outfit-suggestions/{product_id}",
            summary="Get Outfit Suggestions",
            description="Get complete outfit suggestions based on a single item")
@RateLimit(max_requests=25, window_seconds=60)
async def get_outfit_suggestions(
    product_id: str,
    style: Optional[str] = Query(None, description="Preferred style (casual, formal, etc.)"),
    occasion: Optional[str] = Query(None, description="Occasion (work, party, date, etc.)"),
    budget: Optional[float] = Query(None, description="Budget limit for additional items"),
    limit: int = Query(15, ge=1, le=30, description="Maximum suggestions"),
    api_key: str = Depends(get_api_key)
):
    """
    Get complete outfit suggestions based on a single clothing item.
    
    Analyzes the base item and suggests complementary pieces to create
    a cohesive outfit for the specified style and occasion.
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Outfit suggestions for product {product_id}")
        
        # Determine what accessories are needed based on the base item
        base_product = await multimodal_service.enhanced_search.vector_service.get_product_by_id(product_id)
        if not base_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        base_category = base_product.get("category", "").lower()
        
        # Determine complementary categories
        if base_category == "clothing":
            accessory_types = ["shoes", "bags", "jewelry", "scarves"]
        else:
            # If starting with accessories, suggest clothing
            accessory_types = ["clothing"]
        
        # Find matching accessories
        accessories_result = await multimodal_service.find_matching_accessories(
            clothing_product_id=product_id,
            accessory_types=accessory_types,
            limit=limit
        )
        
        # If style is specified, filter for style consistency
        if style:
            style_filter_tasks = []
            for category, items in accessories_result["matching_accessories"].items():
                filtered_items = []
                for item in items:
                    item_text = f"{item.get('name', '')} {item.get('description', '')}".lower()
                    if style.lower() in item_text:
                        filtered_items.append(item)
                
                if filtered_items:
                    accessories_result["matching_accessories"][category] = filtered_items[:limit//len(accessory_types)]
        
        # Apply budget filter if specified
        if budget:
            total_cost = base_product.get("price", 0)
            remaining_budget = budget - total_cost
            
            if remaining_budget > 0:
                for category, items in accessories_result["matching_accessories"].items():
                    affordable_items = [
                        item for item in items 
                        if item.get("price", 0) <= remaining_budget
                    ]
                    accessories_result["matching_accessories"][category] = affordable_items
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "base_item": base_product,
            "style_preference": style,
            "occasion": occasion,
            "budget_limit": budget,
            "outfit_suggestions": accessories_result["matching_accessories"],
            "total_suggestions": sum(len(items) for items in accessories_result["matching_accessories"].values()),
            "query_time": query_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Outfit suggestions failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/trending-now",
            summary="Get Trending Items",
            description="Get currently trending products across categories")
@RateLimit(max_requests=30, window_seconds=60)
async def get_trending_items(
    categories: Optional[List[str]] = Query(None, description="Categories to focus on"),
    season: Optional[str] = Query(None, description="Season filter"),
    limit: int = Query(30, ge=1, le=100, description="Maximum trending items"),
    api_key: str = Depends(get_api_key)
):
    """
    Get currently trending products based on various signals.
    
    Analyzes product popularity, seasonal relevance, and current fashion
    trends to identify items that are currently popular or emerging.
    """
    try:
        start_time = datetime.now()
        
        logger.info("Getting trending items")
        
        # Use seasonal recommendations as a proxy for trending items
        current_season = season or _get_current_season()
        
        trending_result = await multimodal_service.get_seasonal_recommendations(
            season=current_season,
            user_preferences={"preferred_styles": ["trending", "popular", "fashionable"]},
            limit=limit
        )
        
        # Filter by categories if specified
        if categories:
            filtered_recommendations = {}
            for category in categories:
                if category in trending_result["categorized_recommendations"]:
                    filtered_recommendations[category] = trending_result["categorized_recommendations"][category]
            trending_result["categorized_recommendations"] = filtered_recommendations
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "trending_items": trending_result["top_recommendations"],
            "trending_by_category": trending_result["categorized_recommendations"],
            "season": current_season,
            "categories_analyzed": categories or list(trending_result["categorized_recommendations"].keys()),
            "total_trending": trending_result["total_found"],
            "trend_analysis_time": query_time
        }
        
    except Exception as e:
        logger.error(f"Trending items failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/style-inspiration/{style}",
            summary="Get Style Inspiration",
            description="Get product collections for specific style inspirations")
@RateLimit(max_requests=25, window_seconds=60)
async def get_style_inspiration(
    style: str,
    categories: Optional[List[str]] = Query(None, description="Categories to include"),
    price_range: Optional[str] = Query(None, description="Price range (budget, mid, luxury)"),
    limit: int = Query(25, ge=1, le=50, description="Maximum items per category"),
    api_key: str = Depends(get_api_key)
):
    """
    Get curated product collections for specific style inspirations.
    
    Creates themed collections based on style aesthetics like 
    "minimalist chic", "bohemian summer", "urban streetwear", etc.
    """
    try:
        start_time = datetime.now()
        
        logger.info(f"Style inspiration for: {style}")
        
        # Create a dummy product ID for style-based search
        # In a real implementation, you would have style reference products
        dummy_product_id = "STYLE_REFERENCE"
        
        # Use the enhanced search with style-specific queries
        style_keywords = {
            "minimalist": ["clean", "simple", "sleek", "understated", "modern"],
            "bohemian": ["boho", "flowy", "artistic", "free-spirited", "eclectic"],
            "vintage": ["retro", "classic", "timeless", "nostalgic", "heritage"],
            "urban": ["streetwear", "contemporary", "edgy", "metropolitan"],
            "elegant": ["sophisticated", "refined", "polished", "graceful"],
            "casual": ["relaxed", "comfortable", "everyday", "laid-back"],
            "sporty": ["athletic", "active", "performance", "dynamic"]
        }
        
        style_terms = style_keywords.get(style.lower(), [style])
        search_query = " ".join(style_terms + ["fashion", "style"])
        
        # Search using text query
        search_results = await multimodal_service.enhanced_search.search_by_text(
            query=search_query,
            limit=limit * 2
        )
        
        # Group by categories
        style_collections = {}
        for product in search_results.products:
            category = product.category
            if categories is None or category in categories:
                if category not in style_collections:
                    style_collections[category] = []
                
                # Apply price range filter
                if price_range:
                    product_price = product.price
                    if price_range.lower() == "budget" and product_price > 100:
                        continue
                    elif price_range.lower() == "mid" and (product_price < 50 or product_price > 300):
                        continue
                    elif price_range.lower() == "luxury" and product_price < 200:
                        continue
                
                style_collections[category].append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "category": product.category,
                    "image_url": product.image_url,
                    "style_score": product.similarity_score
                })
        
        # Limit items per category
        for category in style_collections:
            style_collections[category] = style_collections[category][:limit]
        
        query_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "style": style,
            "style_keywords": style_terms,
            "collections": style_collections,
            "total_items": sum(len(items) for items in style_collections.values()),
            "categories_found": list(style_collections.keys()),
            "price_range": price_range,
            "query_time": query_time
        }
        
    except Exception as e:
        logger.error(f"Style inspiration failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def _get_current_season() -> str:
    """Determine current season based on date"""
    from datetime import datetime
    
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"

@router.get("/health",
            summary="Multi-Modal Search Health Check",
            description="Check the health of multi-modal search services")
async def health_check():
    """Health check endpoint for multi-modal search services"""
    try:
        # Test the service by getting some basic stats
        service_stats = multimodal_service.enhanced_search.get_service_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "service": "multi-modal-search",
            "version": "1.0.0",
            "clip_service": service_stats.get("clip_model_info", {}),
            "capabilities": [
                "color_variations",
                "cheaper_alternatives", 
                "accessory_matching",
                "seasonal_recommendations",
                "style_evolution",
                "outfit_suggestions",
                "trending_analysis",
                "style_inspiration"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )
