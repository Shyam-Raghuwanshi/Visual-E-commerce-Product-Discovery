from fastapi import APIRouter, Query, HTTPException
from app.models.schemas import SearchRequest, SearchResponse, CombinedSearchRequest
from app.services.search_service import SearchService
from typing import Optional

router = APIRouter()
search_service = SearchService()

@router.post("/search/text", response_model=SearchResponse)
async def search_by_text(request: SearchRequest):
    """Search for products using text query"""
    
    if not request.query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    results = await search_service.search_by_text(
        query=request.query,
        category=request.category,
        limit=request.limit,
        offset=request.offset
    )
    return results

@router.post("/search/combined", response_model=SearchResponse)
async def search_combined(request: CombinedSearchRequest):
    """Search for products using both text and image"""
    
    if not request.query:
        raise HTTPException(status_code=400, detail="Query parameter is required for combined search")
    
    results = await search_service.search_combined(
        query=request.query,
        category=request.category,
        limit=request.limit,
        offset=request.offset
    )
    return results

@router.get("/search/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get similar products based on a product ID"""
    
    results = await search_service.get_similar_products(product_id, limit)
    return results

@router.get("/products/categories")
async def get_categories():
    """Get all available product categories"""
    
    categories = await search_service.get_categories()
    return {"categories": categories}
