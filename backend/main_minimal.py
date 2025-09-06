#!/usr/bin/env python3
"""
Minimal FastAPI server for testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request models
class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    category: Optional[str] = None

class VisualSearchRequest(BaseModel):
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    limit: Optional[int] = 10

# Create FastAPI app
app = FastAPI(
    title="Visual E-commerce Product Discovery API - Test",
    description="Minimal API for testing connectivity",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Visual E-commerce API is running!", "status": "OK"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "visual-ecommerce-api",
        "version": "1.0.0"
    }

@app.get("/api/categories")
async def get_categories():
    """Get product categories"""
    return {
        "categories": [
            {"id": "electronics", "name": "Electronics", "count": 150},
            {"id": "clothing", "name": "Clothing", "count": 230},
            {"id": "footwear", "name": "Footwear", "count": 180},
            {"id": "accessories", "name": "Accessories", "count": 95}
        ]
    }

@app.get("/api/products/categories")
async def get_product_categories():
    """Get product categories - alternate endpoint"""
    return {
        "categories": ["electronics", "clothing", "footwear", "accessories"]
    }

@app.get("/api/products")
async def get_products():
    """Get products"""
    return {
        "products": [
            {
                "id": "1",
                "name": "Sample Product 1",
                "description": "This is a sample product for testing",
                "price": 29.99,
                "category": "electronics",
                "image_url": "https://example.com/image1.jpg"
            },
            {
                "id": "2", 
                "name": "Sample Product 2",
                "description": "Another sample product for testing",
                "price": 49.99,
                "category": "clothing",
                "image_url": "https://example.com/image2.jpg"
            }
        ],
        "total": 2
    }

@app.post("/api/search/text")
async def search_text(request: SearchRequest):
    """Text search endpoint"""
    query = request.query.lower()
    limit = request.limit or 10
    
    # Define comprehensive product database
    all_products = [
        # Footwear products
        {
            "id": "nike_air_1",
            "name": "Nike Air Max 90 Running Shoes",
            "description": "Classic Nike running shoes with air cushioning technology. Perfect for daily runs and casual wear.",
            "price": 129.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "score": 0.98,
            "brand": "Nike",
            "tags": ["running", "athletic", "casual", "footwear"]
        },
        {
            "id": "adidas_ultra_1",
            "name": "Adidas UltraBoost 22 Sneakers",
            "description": "Premium Adidas sneakers with Boost technology for maximum comfort and energy return.",
            "price": 189.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400",
            "score": 0.96,
            "brand": "Adidas",
            "tags": ["sneakers", "boost", "comfort", "footwear"]
        },
        {
            "id": "converse_chuck_1",
            "name": "Converse Chuck Taylor All Star",
            "description": "Classic canvas sneakers that never go out of style. Perfect for casual everyday wear.",
            "price": 65.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=400",
            "score": 0.94,
            "brand": "Converse",
            "tags": ["canvas", "classic", "casual", "footwear"]
        },
        {
            "id": "boots_hiking_1",
            "name": "Waterproof Hiking Boots",
            "description": "Durable waterproof hiking boots designed for outdoor adventures and tough terrains.",
            "price": 159.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=400",
            "score": 0.92,
            "brand": "OutdoorGear",
            "tags": ["hiking", "waterproof", "outdoor", "footwear"]
        },
        {
            "id": "sandals_summer_1",
            "name": "Comfortable Summer Sandals",
            "description": "Lightweight and comfortable sandals perfect for summer days and beach walks.",
            "price": 45.99,
            "category": "footwear",
            "image_url": "https://images.unsplash.com/photo-1603487742131-4160ec999306?w=400",
            "score": 0.90,
            "brand": "SummerStyle",
            "tags": ["sandals", "summer", "beach", "footwear"]
        },
        # Electronics
        {
            "id": "iphone_15",
            "name": "iPhone 15 Pro Max",
            "description": "Latest iPhone with advanced camera system and A17 Pro chip.",
            "price": 1199.99,
            "category": "electronics",
            "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400",
            "score": 0.85,
            "brand": "Apple",
            "tags": ["smartphone", "iPhone", "camera", "electronics"]
        },
        # Clothing
        {
            "id": "jacket_winter_1",
            "name": "Winter Jacket",
            "description": "Warm and stylish winter jacket for cold weather protection.",
            "price": 89.99,
            "category": "clothing",
            "image_url": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400",
            "score": 0.83,
            "brand": "WinterWear",
            "tags": ["jacket", "winter", "warm", "clothing"]
        },
        # Accessories
        {
            "id": "watch_sport_1",
            "name": "Sports Watch",
            "description": "Digital sports watch with fitness tracking features.",
            "price": 199.99,
            "category": "accessories",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
            "score": 0.81,
            "brand": "SportsTech",
            "tags": ["watch", "sports", "fitness", "accessories"]
        }
    ]
    
    # Filter products based on query
    matching_products = []
    
    for product in all_products:
        # Check if query matches product name, description, category, brand, or tags
        searchable_text = f"{product['name']} {product['description']} {product['category']} {product['brand']} {' '.join(product['tags'])}".lower()
        
        if query in searchable_text:
            # Calculate relevance score based on match quality
            relevance_score = 0.5  # Base score
            
            # Higher score for name matches
            if query in product['name'].lower():
                relevance_score += 0.3
            
            # Higher score for category matches
            if query in product['category'].lower():
                relevance_score += 0.2
            
            # Higher score for exact tag matches
            if query in [tag.lower() for tag in product['tags']]:
                relevance_score += 0.4
            
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
        "query_time": 0.15,
        "processing_time": 0.15
    }

@app.post("/api/search/visual")
async def search_visual(request: VisualSearchRequest):
    """Visual search endpoint"""
    # Mock visual search results
    mock_products = [
        {
            "id": "visual_1",
            "name": "Visually Similar Product 1",
            "description": "Product found through visual similarity",
            "price": 45.99,
            "category": "footwear",
            "image_url": "https://example.com/visual1.jpg",
            "score": 0.92
        },
        {
            "id": "visual_2",
            "name": "Visually Similar Product 2",
            "description": "Another visually similar match",
            "price": 67.99,
            "category": "clothing",
            "image_url": "https://example.com/visual2.jpg",
            "score": 0.84
        }
    ]
    
    return {
        "products": mock_products,
        "similarity_scores": [product.get('score', 0.0) for product in mock_products],
        "total": len(mock_products),
        "search_type": "visual",
        "query_time": 0.23,
        "processing_time": 0.23
    }

@app.post("/api/search/multimodal")
async def search_multimodal(request: SearchRequest):
    """Multimodal search endpoint"""
    query = request.query
    
    # Mock multimodal search results
    mock_products = [
        {
            "id": "multi_1",
            "name": f"Multimodal Result for '{query}' - Premium Item",
            "description": f"Advanced search result combining text and visual for '{query}'",
            "price": 89.99,
            "category": "electronics",
            "image_url": "https://example.com/multi1.jpg",
            "score": 0.96
        },
        {
            "id": "multi_2",
            "name": f"Smart Match for '{query}'",
            "description": f"AI-powered recommendation based on '{query}'",
            "price": 129.99,
            "category": "electronics",
            "image_url": "https://example.com/multi2.jpg",
            "score": 0.91
        }
    ]
    
    return {
        "products": mock_products,
        "similarity_scores": [product.get('score', 0.0) for product in mock_products],
        "total": len(mock_products),
        "query": query,
        "search_type": "multimodal",
        "query_time": 0.31,
        "processing_time": 0.31
    }

if __name__ == "__main__":
    logger.info("Starting minimal Visual E-commerce API server...")
    
    config = {
        "host": "0.0.0.0",
        "port": 8001,
        "reload": False,
        "log_level": "info",
        "access_log": True
    }
    
    logger.info(f"Server config: {config}")
    uvicorn.run("main_minimal:app", **config)
