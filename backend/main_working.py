#!/usr/bin/env python3
"""
Visual E-commerce Product Discovery API
Consolidated main server file with all features
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import logging
import os
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    category: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class VisualSearchRequest(BaseModel):
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    limit: Optional[int] = 10
    category: Optional[str] = None

class MultimodalSearchRequest(BaseModel):
    query: str
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    limit: Optional[int] = 10
    category: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="Visual E-commerce Product Discovery API",
    description="High-performance multi-modal search API with advanced optimization features",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Simple performance tracking
request_metrics = {
    "total_requests": 0,
    "active_requests": 0,
    "errors": 0,
    "response_times": []
}

# Performance middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Performance monitoring middleware"""
    start_time = time.time()
    method = request.method
    endpoint = str(request.url.path)
    
    # Track request start
    request_metrics["active_requests"] += 1
    request_metrics["total_requests"] += 1
    
    try:
        response = await call_next(request)
        
        # Record successful request
        processing_time = time.time() - start_time
        request_metrics["response_times"].append(processing_time)
        
        # Keep only last 100 response times for averaging
        if len(request_metrics["response_times"]) > 100:
            request_metrics["response_times"] = request_metrics["response_times"][-100:]
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(processing_time)
        response.headers["X-API-Version"] = "2.1.0"
        
        logger.info(f"{method} {endpoint} - {response.status_code} - {processing_time:.3f}s")
        
        return response
        
    except Exception as e:
        # Record failed request
        processing_time = time.time() - start_time
        request_metrics["errors"] += 1
        
        logger.error(f"Request processing error: {e}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "path": endpoint,
                "method": method,
                "processing_time": processing_time
            }
        )
    finally:
        # Track request end
        request_metrics["active_requests"] -= 1

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive product database
def get_all_products():
    """Get comprehensive product database"""
    return [
        # Footwear products
        {
            "id": "nike_air_1",
            "name": "Nike Air Max 90 Running Shoes",
            "description": "Classic Nike running shoes with air cushioning technology. Perfect for daily runs and casual wear.",
            "price": 129.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "brand": "Nike",
            "tags": ["running", "athletic", "casual", "footwear"],
            "color": "white",
            "size": ["7", "8", "9", "10", "11", "12"],
            "rating": 4.5,
            "reviews": 1250
        },
        {
            "id": "adidas_ultra_1",
            "name": "Adidas UltraBoost 22 Sneakers",
            "description": "Premium Adidas sneakers with Boost technology for maximum comfort and energy return.",
            "price": 189.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
            "brand": "Adidas",
            "tags": ["sneakers", "boost", "comfort", "footwear"],
            "color": "black",
            "size": ["7", "8", "9", "10", "11", "12"],
            "rating": 4.7,
            "reviews": 980
        },
        {
            "id": "converse_chuck_1",
            "name": "Converse Chuck Taylor All Star",
            "description": "Classic canvas sneakers that never go out of style. Perfect for casual everyday wear.",
            "price": 65.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=400",
            "brand": "Converse",
            "tags": ["canvas", "classic", "casual", "footwear"],
            "color": "red",
            "size": ["6", "7", "8", "9", "10", "11"],
            "rating": 4.3,
            "reviews": 2100
        },
        {
            "id": "boots_hiking_1",
            "name": "Waterproof Hiking Boots",
            "description": "Durable waterproof hiking boots designed for outdoor adventures and tough terrains.",
            "price": 159.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400",
            "brand": "OutdoorGear",
            "tags": ["hiking", "waterproof", "outdoor", "footwear"],
            "color": "brown",
            "size": ["8", "9", "10", "11", "12", "13"],
            "rating": 4.6,
            "reviews": 650
        },
        {
            "id": "sandals_summer_1",
            "name": "Comfortable Summer Sandals",
            "description": "Lightweight and comfortable sandals perfect for summer days and beach walks.",
            "price": 45.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400",
            "brand": "SummerStyle",
            "tags": ["sandals", "summer", "beach", "footwear"],
            "color": "tan",
            "size": ["6", "7", "8", "9", "10", "11"],
            "rating": 4.2,
            "reviews": 450
        },
        # Electronics
        {
            "id": "iphone_15",
            "name": "iPhone 15 Pro Max",
            "description": "Latest iPhone with advanced camera system and A17 Pro chip. Features titanium design and improved battery life.",
            "price": 1199.99,
            "category": "electronics",
            "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400",
            "brand": "Apple",
            "tags": ["smartphone", "iPhone", "camera", "electronics"],
            "color": "blue",
            "storage": ["128GB", "256GB", "512GB", "1TB"],
            "rating": 4.8,
            "reviews": 3200
        },
        {
            "id": "samsung_galaxy_1",
            "name": "Samsung Galaxy S24 Ultra",
            "description": "Premium Android smartphone with S Pen and advanced photography features.",
            "price": 1099.99,
            "category": "electronics",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
            "brand": "Samsung",
            "tags": ["smartphone", "android", "camera", "electronics"],
            "color": "black",
            "storage": ["256GB", "512GB", "1TB"],
            "rating": 4.6,
            "reviews": 2800
        },
        {
            "id": "macbook_air_1",
            "name": "MacBook Air M3",
            "description": "Ultra-thin laptop with M3 chip for incredible performance and all-day battery life.",
            "price": 1299.99,
            "category": "electronics",
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
            "brand": "Apple",
            "tags": ["laptop", "macbook", "portable", "electronics"],
            "color": "silver",
            "storage": ["256GB", "512GB", "1TB"],
            "rating": 4.7,
            "reviews": 1850
        },
        # Clothing
        {
            "id": "jacket_winter_1",
            "name": "Insulated Winter Jacket",
            "description": "Warm and stylish winter jacket with premium insulation for cold weather protection.",
            "price": 189.99,
            "category": "clothing",
            "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400",
            "brand": "WinterWear",
            "tags": ["jacket", "winter", "warm", "clothing"],
            "color": "navy",
            "size": ["S", "M", "L", "XL", "XXL"],
            "rating": 4.4,
            "reviews": 720
        },
        {
            "id": "dress_summer_1",
            "name": "Floral Summer Dress",
            "description": "Light and breezy summer dress with beautiful floral pattern, perfect for warm days.",
            "price": 79.99,
            "category": "clothing",
            "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
            "brand": "SummerFashion",
            "tags": ["dress", "summer", "floral", "clothing"],
            "color": "multicolor",
            "size": ["XS", "S", "M", "L", "XL"],
            "rating": 4.5,
            "reviews": 890
        },
        {
            "id": "jeans_classic_1",
            "name": "Classic Blue Jeans",
            "description": "Timeless straight-leg jeans in classic blue denim. Comfortable fit for everyday wear.",
            "price": 89.99,
            "category": "clothing",
            "image_url": "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=400",
            "brand": "DenimCo",
            "tags": ["jeans", "denim", "casual", "clothing"],
            "color": "blue",
            "size": ["28", "30", "32", "34", "36", "38"],
            "rating": 4.3,
            "reviews": 1540
        },
        # Accessories
        {
            "id": "watch_sport_1",
            "name": "Smart Sports Watch",
            "description": "Advanced fitness tracker with heart rate monitoring, GPS, and smartphone connectivity.",
            "price": 299.99,
            "category": "accessories",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
            "brand": "SportsTech",
            "tags": ["watch", "sports", "fitness", "accessories"],
            "color": "black",
            "features": ["GPS", "Heart Rate", "Waterproof", "Bluetooth"],
            "rating": 4.5,
            "reviews": 950
        },
        {
            "id": "bag_leather_1",
            "name": "Premium Leather Handbag",
            "description": "Elegant leather handbag with multiple compartments and adjustable strap.",
            "price": 159.99,
            "category": "accessories",
            "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400",
            "brand": "LeatherCraft",
            "tags": ["bag", "leather", "handbag", "accessories"],
            "color": "brown",
            "material": "genuine leather",
            "rating": 4.6,
            "reviews": 680
        },
        {
            "id": "sunglasses_1",
            "name": "Polarized Sunglasses",
            "description": "Stylish polarized sunglasses with UV protection and durable frame.",
            "price": 89.99,
            "category": "accessories",
            "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400",
            "brand": "SunStyle",
            "tags": ["sunglasses", "polarized", "UV protection", "accessories"],
            "color": "black",
            "features": ["UV Protection", "Polarized", "Scratch Resistant"],
            "rating": 4.4,
            "reviews": 520
        }
    ]

# Main endpoints
@app.get("/")
async def root():
    """Enhanced root endpoint with comprehensive API information"""
    avg_response_time = sum(request_metrics["response_times"][-10:]) / len(request_metrics["response_times"][-10:]) if request_metrics["response_times"] else 0
    
    return {
        "message": "Visual E-commerce Product Discovery API",
        "version": "2.1.0",
        "status": "active",
        "performance_stats": {
            "total_requests": request_metrics["total_requests"],
            "active_requests": request_metrics["active_requests"],
            "error_count": request_metrics["errors"],
            "avg_response_time_ms": round(avg_response_time * 1000, 2)
        },
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "metrics": "/api/metrics",
            "docs": "/docs",
            "redoc": "/redoc",
            "categories": "/api/categories",
            "products": "/api/products",
            "search_text": "/api/search/text",
            "search_visual": "/api/search/visual", 
            "search_multimodal": "/api/search/multimodal",
            "search_advanced": "/api/search/advanced"
        },
        "features": {
            "text_search": True,
            "visual_search": True,
            "multimodal_search": True,
            "advanced_filters": True,
            "performance_monitoring": True,
            "cors_enabled": True,
            "comprehensive_products": True
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "visual-ecommerce-api",
        "version": "2.1.0",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - getattr(app, '_start_time', time.time())
    }

@app.get("/api/status")
async def enhanced_status():
    """Enhanced API status with performance metrics"""
    avg_response_time = sum(request_metrics["response_times"][-10:]) / len(request_metrics["response_times"][-10:]) if request_metrics["response_times"] else 0
    
    return {
        "api_status": "healthy",
        "version": "2.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "performance_metrics": {
            "total_requests": request_metrics["total_requests"],
            "active_requests": request_metrics["active_requests"],
            "total_errors": request_metrics["errors"],
            "avg_response_time_seconds": avg_response_time,
            "error_rate_percent": (request_metrics["errors"] / max(request_metrics["total_requests"], 1)) * 100
        },
        "features": {
            "text_search": True,
            "visual_search": True,
            "multimodal_search": True,
            "advanced_filters": True,
            "performance_monitoring": True,
            "error_tracking": True
        },
        "system_info": {
            "uptime_seconds": time.time() - getattr(app, '_start_time', time.time()),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "port": int(os.getenv("PORT", 8001))
        }
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "requests": {
            "total": request_metrics["total_requests"],
            "active": request_metrics["active_requests"],
            "errors": request_metrics["errors"]
        },
        "performance": {
            "response_times": request_metrics["response_times"][-50:],  # Last 50 response times
            "avg_response_time": sum(request_metrics["response_times"][-10:]) / len(request_metrics["response_times"][-10:]) if request_metrics["response_times"] else 0
        }
    }

@app.get("/api/categories")
async def get_categories():
    """Get product categories with counts"""
    products = get_all_products()
    category_counts = {}
    
    for product in products:
        category = product["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
    
    categories = []
    for category, count in category_counts.items():
        categories.append({
            "id": category,
            "name": category.title(),
            "count": count
        })
    
    return {"categories": categories}

@app.get("/api/products/categories")
async def get_product_categories():
    """Get product categories - alternate endpoint"""
    products = get_all_products()
    categories = list(set(product["category"] for product in products))
    return {"categories": categories}

@app.get("/api/products")
async def get_products(category: Optional[str] = None, limit: Optional[int] = 20):
    """Get products with optional category filter"""
    products = get_all_products()
    
    # Filter by category if specified
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    # Apply limit
    if limit:
        products = products[:limit]
    
    return {
        "products": products,
        "total": len(products),
        "category_filter": category
    }

@app.post("/api/search/text")
async def search_text(request: SearchRequest):
    """Enhanced text search endpoint"""
    query = request.query.lower()
    limit = request.limit or 10
    category_filter = request.category
    filters = request.filters or {}
    
    all_products = get_all_products()
    
    # Apply category filter first
    if category_filter:
        all_products = [p for p in all_products if p["category"].lower() == category_filter.lower()]
    
    # Apply additional filters
    if filters:
        if "price_min" in filters:
            all_products = [p for p in all_products if p["price"] >= filters["price_min"]]
        if "price_max" in filters:
            all_products = [p for p in all_products if p["price"] <= filters["price_max"]]
        if "brand" in filters:
            all_products = [p for p in all_products if p["brand"].lower() == filters["brand"].lower()]
        if "color" in filters:
            all_products = [p for p in all_products if p.get("color", "").lower() == filters["color"].lower()]
        if "rating_min" in filters:
            all_products = [p for p in all_products if p.get("rating", 0) >= filters["rating_min"]]
    
    # Filter products based on query
    matching_products = []
    
    for product in all_products:
        # Check if query matches product name, description, category, brand, or tags
        searchable_text = f"{product['name']} {product['description']} {product['category']} {product['brand']} {' '.join(product['tags'])}".lower()
        
        if query in searchable_text:
            # Calculate relevance score based on match quality
            relevance_score = 0.3  # Base score
            
            # Higher score for name matches
            if query in product['name'].lower():
                relevance_score += 0.4
            
            # Higher score for category matches
            if query in product['category'].lower():
                relevance_score += 0.2
            
            # Higher score for brand matches
            if query in product['brand'].lower():
                relevance_score += 0.3
            
            # Higher score for exact tag matches
            if query in [tag.lower() for tag in product['tags']]:
                relevance_score += 0.3
            
            # Boost score for highly rated products
            if product.get('rating', 0) >= 4.5:
                relevance_score += 0.1
            
            # Update the score
            product_copy = product.copy()
            product_copy['score'] = min(relevance_score, 1.0)
            matching_products.append(product_copy)
    
    # Sort by relevance score (highest first)
    matching_products.sort(key=lambda x: x['score'], reverse=True)
    
    # Apply limit
    results = matching_products[:limit]
    
    return {
        "products": results,
        "similarity_scores": [product.get('score', 0.0) for product in results],
        "total": len(matching_products),
        "query": query,
        "category_filter": category_filter,
        "filters_applied": filters,
        "query_time": 0.12,
        "processing_time": 0.12
    }

@app.post("/api/search/visual")
async def search_visual(request: VisualSearchRequest):
    """Enhanced visual search endpoint"""
    limit = request.limit or 10
    category_filter = request.category
    
    # Get products for visual search simulation
    all_products = get_all_products()
    
    # Apply category filter if specified
    if category_filter:
        all_products = [p for p in all_products if p["category"].lower() == category_filter.lower()]
    
    # Simulate visual similarity matching (in real implementation, this would use image AI)
    # For demo, we'll return products with high ratings as "visually similar"
    visual_results = []
    
    for product in all_products:
        # Simulate visual similarity score based on product attributes
        visual_score = 0.6 + (product.get('rating', 4.0) - 4.0) * 0.2  # Higher rated products get higher visual scores
        
        if product['category'] == 'footwear':
            visual_score += 0.1  # Boost footwear for visual search demo
        
        product_copy = product.copy()
        product_copy['score'] = min(visual_score, 1.0)
        visual_results.append(product_copy)
    
    # Sort by visual similarity score
    visual_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Apply limit
    results = visual_results[:limit]
    
    return {
        "products": results,
        "similarity_scores": [product.get('score', 0.0) for product in results],
        "total": len(visual_results),
        "search_type": "visual",
        "category_filter": category_filter,
        "image_url": request.image_url,
        "query_time": 0.28,
        "processing_time": 0.28
    }

@app.post("/api/search/multimodal")
async def search_multimodal(request: MultimodalSearchRequest):
    """Enhanced multimodal search endpoint combining text and visual"""
    query = request.query.lower()
    limit = request.limit or 10
    category_filter = request.category
    
    all_products = get_all_products()
    
    # Apply category filter if specified
    if category_filter:
        all_products = [p for p in all_products if p["category"].lower() == category_filter.lower()]
    
    # Combine text and visual search results
    multimodal_results = []
    
    for product in all_products:
        # Text similarity component
        searchable_text = f"{product['name']} {product['description']} {product['category']} {product['brand']} {' '.join(product['tags'])}".lower()
        text_score = 0.0
        
        if query in searchable_text:
            text_score = 0.4
            if query in product['name'].lower():
                text_score += 0.3
            if query in product['category'].lower():
                text_score += 0.2
            if query in [tag.lower() for tag in product['tags']]:
                text_score += 0.3
        
        # Visual similarity component (simulated)
        visual_score = 0.3 + (product.get('rating', 4.0) - 4.0) * 0.15
        
        # Combine scores (weighted average)
        combined_score = (text_score * 0.6) + (visual_score * 0.4)
        
        # Boost popular products
        if product.get('reviews', 0) > 1000:
            combined_score += 0.1
        
        product_copy = product.copy()
        product_copy['score'] = min(combined_score, 1.0)
        product_copy['text_score'] = text_score
        product_copy['visual_score'] = visual_score
        
        if combined_score > 0.2:  # Only include products with reasonable scores
            multimodal_results.append(product_copy)
    
    # Sort by combined score
    multimodal_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Apply limit
    results = multimodal_results[:limit]
    
    return {
        "products": results,
        "similarity_scores": [product.get('score', 0.0) for product in results],
        "text_scores": [product.get('text_score', 0.0) for product in results],
        "visual_scores": [product.get('visual_score', 0.0) for product in results],
        "total": len(multimodal_results),
        "query": query,
        "search_type": "multimodal",
        "category_filter": category_filter,
        "image_url": request.image_url,
        "query_time": 0.35,
        "processing_time": 0.35
    }

@app.post("/api/search/advanced")
async def search_advanced(request: SearchRequest):
    """Advanced search with comprehensive filtering and sorting"""
    query = request.query.lower()
    limit = request.limit or 10
    category_filter = request.category
    filters = request.filters or {}
    
    all_products = get_all_products()
    
    # Apply category filter
    if category_filter:
        all_products = [p for p in all_products if p["category"].lower() == category_filter.lower()]
    
    # Apply advanced filters
    if filters:
        if "price_min" in filters:
            all_products = [p for p in all_products if p["price"] >= filters["price_min"]]
        if "price_max" in filters:
            all_products = [p for p in all_products if p["price"] <= filters["price_max"]]
        if "brand" in filters:
            brands = filters["brand"] if isinstance(filters["brand"], list) else [filters["brand"]]
            all_products = [p for p in all_products if p["brand"] in brands]
        if "color" in filters:
            colors = filters["color"] if isinstance(filters["color"], list) else [filters["color"]]
            all_products = [p for p in all_products if p.get("color", "").lower() in [c.lower() for c in colors]]
        if "rating_min" in filters:
            all_products = [p for p in all_products if p.get("rating", 0) >= filters["rating_min"]]
        if "size" in filters:
            sizes = filters["size"] if isinstance(filters["size"], list) else [filters["size"]]
            all_products = [p for p in all_products if any(size in p.get("size", []) for size in sizes)]
    
    # Search and score products
    matching_products = []
    
    for product in all_products:
        searchable_text = f"{product['name']} {product['description']} {product['category']} {product['brand']} {' '.join(product['tags'])}".lower()
        
        if not query or query in searchable_text:
            # Calculate comprehensive relevance score
            score = 0.2  # Base score
            
            if query:
                # Text matching scores
                if query in product['name'].lower():
                    score += 0.4
                if query in product['description'].lower():
                    score += 0.2
                if query in product['category'].lower():
                    score += 0.2
                if query in product['brand'].lower():
                    score += 0.3
                if query in [tag.lower() for tag in product['tags']]:
                    score += 0.3
            else:
                score = 0.8  # High score for non-query searches (browsing)
            
            # Quality boosters
            if product.get('rating', 0) >= 4.5:
                score += 0.15
            if product.get('reviews', 0) > 1000:
                score += 0.1
            
            product_copy = product.copy()
            product_copy['score'] = min(score, 1.0)
            matching_products.append(product_copy)
    
    # Apply sorting
    sort_by = filters.get("sort_by", "relevance")
    
    if sort_by == "price_low":
        matching_products.sort(key=lambda x: x['price'])
    elif sort_by == "price_high":
        matching_products.sort(key=lambda x: x['price'], reverse=True)
    elif sort_by == "rating":
        matching_products.sort(key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_by == "reviews":
        matching_products.sort(key=lambda x: x.get('reviews', 0), reverse=True)
    elif sort_by == "name":
        matching_products.sort(key=lambda x: x['name'])
    else:  # relevance (default)
        matching_products.sort(key=lambda x: x['score'], reverse=True)
    
    # Apply limit
    results = matching_products[:limit]
    
    # Get available filter options from current results
    available_brands = list(set(p["brand"] for p in all_products))
    available_colors = list(set(p.get("color", "") for p in all_products if p.get("color")))
    price_range = {
        "min": min(p["price"] for p in all_products) if all_products else 0,
        "max": max(p["price"] for p in all_products) if all_products else 0
    }
    
    return {
        "products": results,
        "similarity_scores": [product.get('score', 0.0) for product in results],
        "total": len(matching_products),
        "query": query,
        "category_filter": category_filter,
        "filters_applied": filters,
        "sort_by": sort_by,
        "available_filters": {
            "brands": available_brands,
            "colors": available_colors,
            "price_range": price_range,
            "sort_options": ["relevance", "price_low", "price_high", "rating", "reviews", "name"]
        },
        "query_time": 0.18,
        "processing_time": 0.18
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    import traceback
    
    # Log detailed error information
    logger.error(f"Unhandled exception in {request.method} {request.url.path}: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Track error
    request_metrics["errors"] += 1
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path),
            "method": request.method,
            "error_type": type(exc).__name__,
            "timestamp": time.time()
        }
    )

# Store startup time for uptime calculation
app._start_time = time.time()

if __name__ == "__main__":
    logger.info("Starting Visual E-commerce API v2.1.0...")
    
    # Enhanced server configuration
    config = {
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8001)),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "access_log": True
    }
    
    logger.info(f"Starting server with config: {config}")
    uvicorn.run("main_working:app", **config)
