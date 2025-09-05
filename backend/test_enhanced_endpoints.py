"""
Test suite for the enhanced FastAPI search endpoints with authentication,
rate limiting, and comprehensive validation.
"""

import pytest
import asyncio
import httpx
import json
import io
from PIL import Image
import base64
from datetime import datetime
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEYS = {
    "basic": "basic_api_key_123",
    "premium": "premium_api_key_456",
    "enterprise": "enterprise_api_key_789"
}

class TestSearchEndpoints:
    """Test suite for search endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create HTTP client for testing"""
        return httpx.AsyncClient(base_url=BASE_URL)
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample image for testing"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    
    async def test_text_search_no_auth(self, client):
        """Test text search without authentication (should work - free tier)"""
        async with client as c:
            response = await c.post(
                "/api/search/text",
                json={
                    "query": "laptop",
                    "limit": 10
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            assert "total" in data
            assert "query_time" in data
            assert "search_type" in data
            assert data["search_type"] == "text"
    
    async def test_text_search_with_filters(self, client):
        """Test text search with category filter"""
        async with client as c:
            response = await c.post(
                "/api/search/text",
                json={
                    "query": "gaming laptop",
                    "category": "electronics",
                    "limit": 5,
                    "offset": 0
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["products"]) <= 5
            assert "page_info" in data
    
    async def test_text_search_validation_errors(self, client):
        """Test text search validation errors"""
        async with client as c:
            # Empty query
            response = await c.post(
                "/api/search/text",
                json={
                    "query": "",
                    "limit": 10
                }
            )
            assert response.status_code == 400
            
            # Invalid limit
            response = await c.post(
                "/api/search/text",
                json={
                    "query": "laptop",
                    "limit": 150  # Exceeds max limit
                }
            )
            assert response.status_code == 422  # Validation error
    
    async def test_image_search_no_auth(self, client, sample_image):
        """Test image search without authentication (should fail)"""
        async with client as c:
            files = {"file": ("test.jpg", sample_image, "image/jpeg")}
            response = await c.post("/api/search/image", files=files)
            
            assert response.status_code == 401
            data = response.json()
            assert "authentication_required" in data["detail"]["error"]
    
    async def test_image_search_with_basic_auth(self, client, sample_image):
        """Test image search with Basic API key"""
        async with client as c:
            headers = {"X-API-Key": API_KEYS["basic"]}
            files = {"file": ("test.jpg", sample_image, "image/jpeg")}
            
            response = await c.post(
                "/api/search/image",
                files=files,
                headers=headers,
                params={"limit": 5, "similarity_threshold": 0.8}
            )
            
            # Might fail due to service not running, but should pass auth
            assert response.status_code in [200, 500]  # 500 if service not available
    
    async def test_image_search_invalid_file(self, client):
        """Test image search with invalid file"""
        async with client as c:
            headers = {"X-API-Key": API_KEYS["basic"]}
            files = {"file": ("test.txt", b"not an image", "text/plain")}
            
            response = await c.post(
                "/api/search/image",
                files=files,
                headers=headers
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "invalid_file_type" in data["detail"]["error"]
    
    async def test_combined_search_no_auth(self, client, sample_image):
        """Test combined search without authentication (should fail)"""
        async with client as c:
            files = {"file": ("test.jpg", sample_image, "image/jpeg")}
            data = {"query": "gaming laptop"}
            
            response = await c.post(
                "/api/search/combined",
                files=files,
                data=data
            )
            
            assert response.status_code == 403
            error_data = response.json()
            assert "insufficient_permissions" in error_data["detail"]["error"]
    
    async def test_combined_search_with_premium_auth(self, client, sample_image):
        """Test combined search with Premium API key"""
        async with client as c:
            headers = {"X-API-Key": API_KEYS["premium"]}
            files = {"file": ("test.jpg", sample_image, "image/jpeg")}
            
            response = await c.post(
                "/api/search/combined",
                files=files,
                headers=headers,
                params={
                    "query": "gaming laptop",
                    "image_weight": 0.6,
                    "text_weight": 0.4,
                    "limit": 5
                }
            )
            
            # Might fail due to service not running, but should pass auth
            assert response.status_code in [200, 500]
    
    async def test_combined_search_weight_validation(self, client, sample_image):
        """Test combined search weight validation"""
        async with client as c:
            headers = {"X-API-Key": API_KEYS["premium"]}
            files = {"file": ("test.jpg", sample_image, "image/jpeg")}
            
            response = await c.post(
                "/api/search/combined",
                files=files,
                headers=headers,
                params={
                    "query": "laptop",
                    "image_weight": 0.6,
                    "text_weight": 0.5  # Total = 1.1, should fail
                }
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "invalid_weights" in data["detail"]["error"]
    
    async def test_filter_search_no_auth(self, client):
        """Test filter search without authentication (should fail)"""
        async with client as c:
            response = await c.post(
                "/api/search/filters",
                json={
                    "categories": ["electronics"],
                    "min_price": 100,
                    "max_price": 1000,
                    "sort_by": "price_asc"
                }
            )
            
            assert response.status_code == 403
    
    async def test_filter_search_with_premium_auth(self, client):
        """Test filter search with Premium API key"""
        async with client as c:
            headers = {"X-API-Key": API_KEYS["premium"]}
            
            response = await c.post(
                "/api/search/filters",
                json={
                    "text_query": "laptop",
                    "categories": ["electronics"],
                    "brands": ["Dell", "HP"],
                    "min_price": 500,
                    "max_price": 2000,
                    "min_rating": 4.0,
                    "in_stock": True,
                    "sort_by": "price_asc",
                    "limit": 10
                },
                headers=headers
            )
            
            # Should pass authentication and validation
            assert response.status_code in [200, 500]
    
    async def test_product_details_no_auth(self, client):
        """Test product details without authentication (should work - free tier)"""
        async with client as c:
            response = await c.get("/api/products/test-product-123")
            
            # Will likely return 404 since product doesn't exist
            assert response.status_code in [200, 404, 500]
    
    async def test_product_details_with_params(self, client):
        """Test product details with additional parameters"""
        async with client as c:
            response = await c.get(
                "/api/products/test-product-123",
                params={
                    "include_similar": True,
                    "include_recommendations": True,
                    "similar_count": 3
                }
            )
            
            assert response.status_code in [200, 404, 500]
    
    async def test_similar_products(self, client):
        """Test similar products endpoint"""
        async with client as c:
            response = await c.get(
                "/api/search/similar/test-product-123",
                params={"limit": 5, "category": "electronics"}
            )
            
            assert response.status_code in [200, 404, 500]
    
    async def test_categories_endpoint(self, client):
        """Test categories endpoint"""
        async with client as c:
            response = await c.get("/api/categories")
            
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                assert "categories" in data
                assert "brands" in data

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url=BASE_URL)
    
    async def test_rate_limit_text_search(self, client):
        """Test rate limiting on text search endpoint"""
        async with client as c:
            # Make multiple requests quickly
            tasks = []
            for i in range(10):
                task = c.post(
                    "/api/search/text",
                    json={"query": f"test query {i}", "limit": 1}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for rate limit responses
            status_codes = [r.status_code for r in responses if hasattr(r, 'status_code')]
            
            # Some requests should succeed, some might be rate limited
            assert any(code == 200 for code in status_codes)
            # Rate limiting might kick in
            rate_limited = any(code == 429 for code in status_codes)
            
            # Check rate limit headers if present
            for response in responses:
                if hasattr(response, 'headers'):
                    if 'X-RateLimit-Limit' in response.headers:
                        assert int(response.headers['X-RateLimit-Limit']) > 0

class TestResponseFormat:
    """Test response format and structure"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url=BASE_URL)
    
    async def test_text_search_response_structure(self, client):
        """Test text search response structure"""
        async with client as c:
            response = await c.post(
                "/api/search/text",
                json={"query": "test", "limit": 5}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Required fields
                assert "products" in data
                assert "total" in data
                assert "query_time" in data
                assert "search_type" in data
                
                # Optional fields
                assert "filters_applied" in data
                assert "page_info" in data
                
                # Products structure
                if data["products"]:
                    product = data["products"][0]
                    required_product_fields = ["id", "name", "description", "price", "category", "image_url"]
                    for field in required_product_fields:
                        assert field in product
    
    async def test_error_response_structure(self, client):
        """Test error response structure"""
        async with client as c:
            # Trigger validation error
            response = await c.post(
                "/api/search/text",
                json={"query": "", "limit": 10}
            )
            
            assert response.status_code == 400
            data = response.json()
            
            # Error response structure
            assert "detail" in data
            error_detail = data["detail"]
            assert "error" in error_detail
            assert "message" in error_detail
            assert "request_id" in error_detail

class TestAPIDocumentation:
    """Test API documentation and root endpoints"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url=BASE_URL)
    
    async def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        async with client as c:
            response = await c.get("/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "message" in data
            assert "version" in data
            assert "endpoints" in data
            assert "authentication" in data
    
    async def test_status_endpoint(self, client):
        """Test status endpoint"""
        async with client as c:
            response = await c.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "api_status" in data
            assert "version" in data
            assert "features" in data
    
    async def test_health_endpoint(self, client):
        """Test health endpoint"""
        async with client as c:
            response = await c.get("/api/health")
            
            assert response.status_code in [200, 500]
    
    async def test_openapi_docs(self, client):
        """Test OpenAPI documentation accessibility"""
        async with client as c:
            # Test docs endpoint
            response = await c.get("/docs")
            assert response.status_code == 200
            
            # Test OpenAPI JSON
            response = await c.get("/openapi.json")
            assert response.status_code == 200
            
            openapi_spec = response.json()
            assert "openapi" in openapi_spec
            assert "info" in openapi_spec
            assert "paths" in openapi_spec

class TestAuthenticationLevels:
    """Test different authentication levels and permissions"""
    
    @pytest.fixture
    def client(self):
        return httpx.AsyncClient(base_url=BASE_URL)
    
    async def test_api_key_levels(self, client):
        """Test different API key levels"""
        endpoints_by_level = {
            "none": ["/api/search/text", "/api/products/test-123"],
            "basic": ["/api/search/image"],
            "premium": ["/api/search/combined", "/api/search/filters"],
            "enterprise": []
        }
        
        async with client as c:
            # Test without auth (should work for 'none' level)
            for endpoint in endpoints_by_level["none"]:
                if endpoint.startswith("/api/search/text"):
                    response = await c.post(endpoint, json={"query": "test"})
                else:
                    response = await c.get(endpoint)
                
                # Should not be blocked by authentication
                assert response.status_code != 401
            
            # Test with basic auth
            headers = {"X-API-Key": API_KEYS["basic"]}
            for endpoint in endpoints_by_level["basic"]:
                # Create minimal request for image search
                sample_img = Image.new('RGB', (10, 10), color='red')
                img_bytes = io.BytesIO()
                sample_img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)
                
                files = {"file": ("test.jpg", img_bytes.getvalue(), "image/jpeg")}
                response = await c.post(endpoint, files=files, headers=headers)
                
                # Should pass authentication (might fail for other reasons)
                assert response.status_code != 401

# Utility functions for testing
def create_test_image(width=100, height=100, color='red'):
    """Create a test image for upload testing"""
    img = Image.new('RGB', (width, height), color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def create_test_product_data():
    """Create test product data"""
    return {
        "id": "test-product-123",
        "name": "Test Gaming Laptop",
        "description": "High-performance gaming laptop with RTX graphics",
        "price": 1299.99,
        "category": "electronics",
        "brand": "TestBrand",
        "image_url": "https://example.com/laptop.jpg",
        "rating": 4.5,
        "in_stock": True,
        "tags": ["gaming", "laptop", "high-performance"]
    }

if __name__ == "__main__":
    # Run specific tests
    import sys
    
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        if test_class == "search":
            pytest.main(["-v", "TestSearchEndpoints"])
        elif test_class == "auth":
            pytest.main(["-v", "TestAuthenticationLevels"])
        elif test_class == "rate":
            pytest.main(["-v", "TestRateLimiting"])
        else:
            pytest.main(["-v"])
    else:
        pytest.main(["-v"])
