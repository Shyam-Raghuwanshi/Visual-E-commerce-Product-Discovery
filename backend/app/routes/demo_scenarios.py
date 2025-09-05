"""
Demo Scenarios API Routes

This module provides API endpoints for specific demo scenarios:
- Celebrity outfit recreation
- Budget-conscious shopping
- Sustainable fashion alternatives
- Size-inclusive search
- Trend forecasting
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
import logging

from app.services.demo_scenarios_service import DemoScenariosService
from app.models.business_schemas import UserPreferences
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()
demo_service = DemoScenariosService()

# Request Models for Demo Scenarios

class CelebrityOutfitRequest(BaseModel):
    """Request for celebrity outfit recreation"""
    celebrity_name: Optional[str] = Field(None, description="Specific celebrity name")
    event: Optional[str] = Field(None, description="Specific event")
    budget_range: Optional[Dict[str, float]] = Field(None, description="Budget constraints")
    user_id: Optional[str] = Field(None, description="User ID for personalization")

class BudgetShoppingRequest(BaseModel):
    """Request for budget-conscious shopping"""
    target_look: str = Field(..., description="Desired look or style")
    max_budget: float = Field(..., gt=0, description="Maximum budget")
    style_preferences: Optional[List[str]] = Field(None, description="Style preferences")
    must_have_pieces: Optional[List[str]] = Field(None, description="Must-have pieces")
    user_id: Optional[str] = Field(None, description="User ID for personalization")

class SustainableFashionRequest(BaseModel):
    """Request for sustainable fashion alternatives"""
    search_query: str = Field(..., description="Product search query")
    sustainability_criteria: Optional[List[str]] = Field(None, description="Specific sustainability criteria")
    max_price_premium: Optional[float] = Field(0.3, description="Maximum price premium for sustainability")
    user_id: Optional[str] = Field(None, description="User ID for personalization")

class SizeInclusiveRequest(BaseModel):
    """Request for size-inclusive search"""
    search_query: str = Field(..., description="Product search query")
    target_size: str = Field(..., description="Target clothing size")
    size_range: Optional[List[str]] = Field(None, description="Acceptable size range")
    body_type_preferences: Optional[Dict[str, Any]] = Field(None, description="Body type preferences")
    user_id: Optional[str] = Field(None, description="User ID for personalization")

class TrendForecastRequest(BaseModel):
    """Request for trend forecasting"""
    season: Optional[str] = Field(None, description="Target season")
    year: Optional[int] = Field(None, description="Target year")
    style_category: Optional[str] = Field(None, description="Style category")
    demographic: Optional[str] = Field(None, description="Target demographic")
    user_id: Optional[str] = Field(None, description="User ID for personalization")

@router.post("/celebrity-outfit-recreation")
async def celebrity_outfit_recreation(request: CelebrityOutfitRequest):
    """
    Recreate celebrity outfits with similar products from the catalog
    
    This endpoint helps users recreate red carpet and celebrity looks using
    available products, with options for budget constraints and personalization.
    """
    try:
        logger.info(f"Celebrity outfit recreation request: {request.celebrity_name}")
        
        result = await demo_service.celebrity_outfit_recreation(
            celebrity_name=request.celebrity_name,
            event=request.event,
            budget_range=request.budget_range,
            user_preferences=None  # TODO: Fetch user preferences if user_id provided
        )
        
        return {
            "status": "success",
            "demo_type": "celebrity_outfit_recreation",
            "data": result,
            "message": f"Successfully generated celebrity outfit recreation for {result['celebrity_inspiration']['name']}"
        }
        
    except Exception as e:
        logger.error(f"Error in celebrity outfit recreation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget-conscious-shopping")
async def budget_conscious_shopping(request: BudgetShoppingRequest):
    """
    Find luxury-inspired looks within budget constraints
    
    This endpoint helps users achieve high-end looks on a budget by finding
    affordable alternatives and creating cost-effective outfit combinations.
    """
    try:
        logger.info(f"Budget shopping request: {request.target_look}, budget: ${request.max_budget}")
        
        result = await demo_service.budget_conscious_shopping(
            target_look=request.target_look,
            max_budget=request.max_budget,
            style_preferences=request.style_preferences,
            must_have_pieces=request.must_have_pieces
        )
        
        return {
            "status": "success",
            "demo_type": "budget_conscious_shopping",
            "data": result,
            "message": f"Found budget-friendly options for '{request.target_look}' under ${request.max_budget}"
        }
        
    except Exception as e:
        logger.error(f"Error in budget-conscious shopping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sustainable-fashion-alternatives")
async def sustainable_fashion_alternatives(request: SustainableFashionRequest):
    """
    Find eco-friendly alternatives to fashion items
    
    This endpoint helps users find sustainable and eco-friendly alternatives
    to regular fashion items, with detailed environmental impact analysis.
    """
    try:
        logger.info(f"Sustainable fashion request: {request.search_query}")
        
        result = await demo_service.sustainable_fashion_alternatives(
            search_query=request.search_query,
            sustainability_criteria=request.sustainability_criteria,
            max_price_premium=request.max_price_premium
        )
        
        return {
            "status": "success",
            "demo_type": "sustainable_fashion_alternatives",
            "data": result,
            "message": f"Found {len(result['sustainable_alternatives'])} sustainable alternatives for '{request.search_query}'"
        }
        
    except Exception as e:
        logger.error(f"Error in sustainable fashion alternatives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/size-inclusive-search")
async def size_inclusive_search(request: SizeInclusiveRequest):
    """
    Find products available in specific sizes with inclusive options
    
    This endpoint provides size-inclusive search functionality, helping users
    find products in their size with fit recommendations and alternatives.
    """
    try:
        logger.info(f"Size-inclusive search: {request.search_query}, size: {request.target_size}")
        
        result = await demo_service.size_inclusive_search(
            search_query=request.search_query,
            target_size=request.target_size,
            size_range=request.size_range,
            body_type_preferences=request.body_type_preferences
        )
        
        return {
            "status": "success",
            "demo_type": "size_inclusive_search",
            "data": result,
            "message": f"Found {len(result['available_products'])} products available in size {request.target_size}"
        }
        
    except Exception as e:
        logger.error(f"Error in size-inclusive search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trend-forecasting")
async def trend_forecasting(request: TrendForecastRequest):
    """
    Predict upcoming fashion trends and recommend products
    
    This endpoint provides fashion trend forecasting with product recommendations
    aligned to predicted trends and seasonal patterns.
    """
    try:
        logger.info(f"Trend forecasting request: {request.season} {request.year}")
        
        result = await demo_service.trend_forecasting(
            season=request.season,
            year=request.year,
            style_category=request.style_category,
            demographic=request.demographic
        )
        
        return {
            "status": "success",
            "demo_type": "trend_forecasting",
            "data": result,
            "message": f"Generated trend forecast for {result['forecast_period']} with {len(result['predicted_trends'])} trends"
        }
        
    except Exception as e:
        logger.error(f"Error in trend forecasting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional utility endpoints for demo scenarios

@router.get("/demo-scenarios/available")
async def get_available_demo_scenarios():
    """
    Get list of available demo scenarios with descriptions
    """
    scenarios = {
        "celebrity_outfit_recreation": {
            "name": "Celebrity Outfit Recreation",
            "description": "Recreate red carpet and celebrity looks with available products",
            "use_case": "Get this red carpet look",
            "features": ["Celebrity outfit matching", "Budget adaptation", "Alternative suggestions"]
        },
        "budget_conscious_shopping": {
            "name": "Budget-Conscious Shopping",
            "description": "Find luxury-inspired looks within budget constraints",
            "use_case": "Luxury look for less",
            "features": ["Price optimization", "Quality alternatives", "Value comparison"]
        },
        "sustainable_fashion_alternatives": {
            "name": "Sustainable Fashion",
            "description": "Find eco-friendly alternatives to fashion items",
            "use_case": "Eco-friendly alternatives",
            "features": ["Sustainability scoring", "Environmental impact", "Ethical brands"]
        },
        "size_inclusive_search": {
            "name": "Size-Inclusive Options",
            "description": "Find products available in specific sizes",
            "use_case": "Find this in my size",
            "features": ["Size availability", "Fit recommendations", "Inclusive brands"]
        },
        "trend_forecasting": {
            "name": "Trend Forecasting",
            "description": "Predict upcoming fashion trends and recommend products",
            "use_case": "What's coming next season",
            "features": ["Trend prediction", "Seasonal analysis", "Investment pieces"]
        }
    }
    
    return {
        "status": "success",
        "available_scenarios": scenarios,
        "total_scenarios": len(scenarios)
    }

@router.get("/demo-scenarios/celebrity-outfits")
async def get_available_celebrity_outfits():
    """
    Get list of available celebrity outfits for recreation
    """
    try:
        outfits = [
            {
                "celebrity_name": outfit.celebrity_name,
                "event": outfit.event,
                "description": outfit.description,
                "style_tags": outfit.style_tags,
                "color_palette": outfit.color_palette,
                "price_range": outfit.price_range
            }
            for outfit in demo_service.celebrity_outfits
        ]
        
        return {
            "status": "success",
            "available_outfits": outfits,
            "total_outfits": len(outfits)
        }
        
    except Exception as e:
        logger.error(f"Error getting celebrity outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-scenarios/trend-forecasts")
async def get_available_trend_forecasts():
    """
    Get list of available trend forecasts
    """
    try:
        forecasts = [
            {
                "trend_name": forecast.trend_name,
                "season": forecast.season,
                "year": forecast.year,
                "confidence_score": forecast.confidence_score,
                "key_elements": forecast.key_elements,
                "color_trends": forecast.color_trends,
                "target_demographics": forecast.target_demographics
            }
            for forecast in demo_service.trend_forecasts
        ]
        
        return {
            "status": "success",
            "available_forecasts": forecasts,
            "total_forecasts": len(forecasts)
        }
        
    except Exception as e:
        logger.error(f"Error getting trend forecasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-scenarios/sustainability-info")
async def get_sustainability_information():
    """
    Get information about sustainability criteria and eco-friendly options
    """
    try:
        return {
            "status": "success",
            "sustainability_info": {
                "sustainable_brands": demo_service.sustainable_brands,
                "eco_criteria": demo_service.eco_criteria,
                "sustainability_tips": demo_service._generate_sustainability_tips(),
                "environmental_benefits": [
                    "Reduced water consumption",
                    "Lower carbon footprint",
                    "Decreased chemical usage",
                    "Support for ethical labor",
                    "Reduced textile waste"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting sustainability info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Quick demo endpoints for testing

@router.get("/demo-scenarios/quick-celebrity-demo")
async def quick_celebrity_demo(
    celebrity: Optional[str] = Query(None, description="Celebrity name (optional)")
):
    """
    Quick demo of celebrity outfit recreation
    """
    try:
        request = CelebrityOutfitRequest(celebrity_name=celebrity)
        return await celebrity_outfit_recreation(request)
    except Exception as e:
        logger.error(f"Error in quick celebrity demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-scenarios/quick-budget-demo")
async def quick_budget_demo(
    look: str = Query("elegant evening wear", description="Target look"),
    budget: float = Query(200.0, description="Maximum budget")
):
    """
    Quick demo of budget-conscious shopping
    """
    try:
        request = BudgetShoppingRequest(target_look=look, max_budget=budget)
        return await budget_conscious_shopping(request)
    except Exception as e:
        logger.error(f"Error in quick budget demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-scenarios/quick-sustainable-demo")
async def quick_sustainable_demo(
    query: str = Query("dress", description="Search query")
):
    """
    Quick demo of sustainable fashion alternatives
    """
    try:
        request = SustainableFashionRequest(search_query=query)
        return await sustainable_fashion_alternatives(request)
    except Exception as e:
        logger.error(f"Error in quick sustainable demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-scenarios/quick-size-demo")
async def quick_size_demo(
    query: str = Query("dress", description="Search query"),
    size: str = Query("M", description="Target size")
):
    """
    Quick demo of size-inclusive search
    """
    try:
        request = SizeInclusiveRequest(search_query=query, target_size=size)
        return await size_inclusive_search(request)
    except Exception as e:
        logger.error(f"Error in quick size demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo-scenarios/quick-trend-demo")
async def quick_trend_demo(
    season: Optional[str] = Query(None, description="Season (Spring/Summer/Fall/Winter)")
):
    """
    Quick demo of trend forecasting
    """
    try:
        request = TrendForecastRequest(season=season)
        return await trend_forecasting(request)
    except Exception as e:
        logger.error(f"Error in quick trend demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))
