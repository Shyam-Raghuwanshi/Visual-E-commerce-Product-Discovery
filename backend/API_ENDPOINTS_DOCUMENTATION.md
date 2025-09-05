# FastAPI Enhanced Search Endpoints Documentation

## Overview

This document describes the comprehensive FastAPI endpoints for the Visual E-commerce Product Discovery system, including authentication, rate limiting, and advanced search capabilities.

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Core Search Endpoints](#core-search-endpoints)
4. [Response Formats](#response-formats)
5. [Error Handling](#error-handling)
6. [Testing](#testing)

## Authentication

### Authentication Levels

The API supports multiple authentication levels:

- **None**: Free tier access for basic endpoints
- **Basic**: Required for image search capabilities
- **Premium**: Required for combined search and advanced filtering
- **Enterprise**: Full access to all features

### Authentication Methods

#### 1. API Key Authentication
```http
X-API-Key: your_api_key_here
```

#### 2. JWT Token Authentication
```http
Authorization: Bearer your_jwt_token_here
```

### API Keys by Level
- Basic: `basic_api_key_123`
- Premium: `premium_api_key_456`
- Enterprise: `enterprise_api_key_789`

## Rate Limiting

### Rate Limits by Endpoint Type

| Endpoint Type | Requests per Hour | Authentication Level |
|---------------|-------------------|----------------------|
| Search        | 100               | Basic+               |
| Upload        | 50                | Basic+               |
| Product       | 200               | None                 |
| Default       | 1000              | None                 |

### Rate Limit Headers

All responses include rate limiting headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

## Core Search Endpoints

### 1. POST /api/search/text - Text-based Product Search

**Authentication**: None (Free tier)

Search for products using text queries.

#### Request Body
```json
{
  "query": "gaming laptop",
  "category": "electronics",
  "limit": 20,
  "offset": 0
}
```

#### Parameters
- `query` (required): Search text (1-500 characters)
- `category` (optional): Product category filter
- `limit` (optional): Maximum results (1-100, default: 20)
- `offset` (optional): Pagination offset (default: 0)

#### Response
```json
{
  "products": [
    {
      "id": "product-123",
      "name": "Gaming Laptop Pro",
      "description": "High-performance gaming laptop...",
      "price": 1299.99,
      "category": "electronics",
      "brand": "TechBrand",
      "image_url": "https://example.com/image.jpg",
      "rating": 4.5,
      "in_stock": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 150,
  "query_time": 0.045,
  "search_type": "text",
  "filters_applied": {
    "category": "electronics",
    "limit": 20,
    "offset": 0
  },
  "page_info": {
    "current_page": 1,
    "has_next": true,
    "total_pages": 8
  }
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/api/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gaming laptop",
    "category": "electronics",
    "limit": 10
  }'
```

### 2. POST /api/search/image - Image-based Product Search

**Authentication**: Basic API key required

Search for products using uploaded images.

#### Request (Multipart Form)
- `file` (required): Image file (JPEG, PNG, WebP, max 10MB)
- `category` (optional): Category filter
- `limit` (optional): Maximum results (1-100, default: 20)
- `offset` (optional): Pagination offset (default: 0)
- `similarity_threshold` (optional): Minimum similarity score (0-1, default: 0.7)

#### Response
```json
{
  "products": [...],
  "total": 50,
  "query_time": 0.128,
  "similarity_scores": [0.95, 0.87, 0.82, ...],
  "search_type": "image",
  "filters_applied": {
    "category": "electronics",
    "similarity_threshold": 0.7
  }
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/api/search/image" \
  -H "X-API-Key: basic_api_key_123" \
  -F "file=@laptop_image.jpg" \
  -F "category=electronics" \
  -F "limit=10"
```

### 3. POST /api/search/combined - Multi-modal Search

**Authentication**: Premium API key required

Search using both text and image with weighted combination.

#### Request (Multipart Form)
- `file` (required): Image file
- `query` (required): Text search query
- `category` (optional): Category filter
- `image_weight` (optional): Weight for image similarity (0-1, default: 0.7)
- `text_weight` (optional): Weight for text similarity (0-1, default: 0.3)
- `limit` (optional): Maximum results (1-100, default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Note**: `image_weight + text_weight` must equal 1.0

#### Response
```json
{
  "products": [...],
  "total": 75,
  "query_time": 0.156,
  "similarity_scores": [0.91, 0.84, 0.79, ...],
  "search_type": "combined",
  "filters_applied": {
    "query": "gaming laptop",
    "image_weight": 0.7,
    "text_weight": 0.3
  }
}
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/api/search/combined" \
  -H "X-API-Key: premium_api_key_456" \
  -F "file=@laptop_image.jpg" \
  -F "query=gaming laptop RTX" \
  -F "image_weight=0.6" \
  -F "text_weight=0.4"
```

### 4. POST /api/search/filters - Advanced Filtering

**Authentication**: Premium API key required

Advanced filtering with vector search and multiple filter combinations.

#### Request Body
```json
{
  "text_query": "laptop",
  "categories": ["electronics", "computers"],
  "brands": ["Dell", "HP", "Lenovo"],
  "min_price": 500,
  "max_price": 2000,
  "min_rating": 4.0,
  "max_rating": 5.0,
  "in_stock": true,
  "tags": ["gaming", "high-performance"],
  "sort_by": "price_asc",
  "include_out_of_stock": false,
  "limit": 20,
  "offset": 0
}
```

#### Parameters
- `text_query` (optional): Text search query
- `categories` (optional): List of categories (max 10)
- `brands` (optional): List of brands (max 20)
- `min_price/max_price` (optional): Price range filters
- `min_rating/max_rating` (optional): Rating range filters (0-5)
- `in_stock` (optional): Stock availability filter
- `tags` (optional): Product tags filter (max 20)
- `sort_by` (optional): Sort order
  - `relevance` (default)
  - `price_asc`
  - `price_desc`
  - `rating`
  - `popularity`
  - `created_date`
  - `name`

#### Response
```json
{
  "products": [...],
  "total": 25,
  "query_time": 0.089,
  "search_type": "advanced",
  "filters_applied": {
    "categories": ["electronics"],
    "min_price": 500,
    "max_price": 2000,
    "sort_by": "price_asc"
  },
  "aggregations": {
    "categories": {
      "electronics": 20,
      "computers": 15
    },
    "brands": {
      "Dell": 10,
      "HP": 8
    },
    "price_ranges": {
      "500-1000": 12,
      "1000-1500": 8,
      "1500-2000": 5
    },
    "price_stats": {
      "min": 549.99,
      "max": 1899.99,
      "avg": 1124.50
    }
  }
}
```

### 5. GET /api/products/{product_id} - Product Details

**Authentication**: None (Free tier)

Get detailed information about a specific product.

#### Parameters
- `product_id` (required): Unique product identifier
- `include_similar` (optional): Include similar products (default: true)
- `include_recommendations` (optional): Include recommendations (default: true)
- `similar_count` (optional): Number of similar products (1-20, default: 5)

#### Response
```json
{
  "product": {
    "id": "product-123",
    "name": "Gaming Laptop Pro",
    "description": "High-performance gaming laptop...",
    "price": 1299.99,
    "category": "electronics",
    "brand": "TechBrand",
    "image_url": "https://example.com/image.jpg",
    "rating": 4.5,
    "in_stock": true,
    "tags": ["gaming", "laptop"],
    "specifications": {
      "cpu": "Intel i7",
      "gpu": "RTX 3080",
      "ram": "16GB"
    },
    "reviews_count": 150,
    "average_rating": 4.5
  },
  "similar_products": [...],
  "recommendations": [...],
  "metadata": {
    "query_time": 0.023,
    "request_id": "req-123"
  }
}
```

#### cURL Example
```bash
curl -X GET "http://localhost:8000/api/products/product-123" \
  -G \
  -d "include_similar=true" \
  -d "similar_count=3"
```

### 6. GET /api/search/similar/{product_id} - Similar Products

**Authentication**: None (Free tier)

Find products similar to a specific product.

#### Parameters
- `product_id` (required): Reference product ID
- `limit` (optional): Maximum results (1-50, default: 10)
- `category` (optional): Category filter

#### Response
```json
{
  "products": [...],
  "total": 15,
  "query_time": 0.034,
  "similarity_scores": [0.89, 0.85, 0.81],
  "search_type": "image",
  "filters_applied": {
    "product_id": "product-123",
    "category": "electronics"
  }
}
```

### 7. GET /api/categories - Available Categories and Brands

**Authentication**: None (Free tier)

Get all available product categories and brands.

#### Response
```json
{
  "categories": [
    "electronics",
    "fashion",
    "home",
    "sports"
  ],
  "brands": [
    "Dell",
    "HP",
    "Apple",
    "Samsung"
  ],
  "total_categories": 4,
  "total_brands": 4
}
```

## Response Formats

### Success Response Structure

All successful responses follow this structure:

```json
{
  "products": [...],        // Array of product objects
  "total": 100,            // Total number of matching products
  "query_time": 0.045,     // Query execution time in seconds
  "search_type": "text",   // Type of search performed
  "filters_applied": {...}, // Summary of applied filters
  "page_info": {           // Pagination information (optional)
    "current_page": 1,
    "has_next": true,
    "total_pages": 5
  },
  "aggregations": {...}    // Search result aggregations (optional)
}
```

### Product Object Structure

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": 0.0,
  "category": "string",
  "brand": "string",
  "image_url": "string",
  "rating": 4.5,
  "in_stock": true,
  "tags": ["tag1", "tag2"],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "specifications": {...},  // Optional
  "reviews_count": 100,     // Optional
  "average_rating": 4.5     // Optional
}
```

## Error Handling

### Error Response Structure

```json
{
  "detail": {
    "error": "error_type",
    "message": "Human-readable error message",
    "request_id": "req-123",
    "timestamp": "2024-01-01T00:00:00"
  }
}
```

### Common Error Types

#### 1. Authentication Errors (401)
```json
{
  "detail": {
    "error": "authentication_required",
    "message": "This endpoint requires authentication. Please provide a valid API key or JWT token.",
    "required_level": "basic"
  }
}
```

#### 2. Authorization Errors (403)
```json
{
  "detail": {
    "error": "insufficient_permissions",
    "message": "This endpoint requires Premium API key or higher",
    "current_level": "basic",
    "required_level": "premium"
  }
}
```

#### 3. Validation Errors (400)
```json
{
  "detail": {
    "error": "validation_error",
    "message": "Query parameter is required and cannot be empty",
    "field": "query"
  }
}
```

#### 4. Rate Limit Errors (429)
```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 100,
    "reset_time": 1234567890,
    "message": "Too many requests. Try again after 2024-01-01T01:00:00"
  }
}
```

#### 5. File Upload Errors (400)
```json
{
  "detail": {
    "error": "invalid_file_type",
    "message": "File must be an image (JPEG, PNG, WebP)",
    "supported_types": ["image/jpeg", "image/png", "image/webp"]
  }
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (validation errors, invalid files) |
| 401 | Unauthorized (authentication required) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found (product not found) |
| 429 | Too Many Requests (rate limit exceeded) |
| 500 | Internal Server Error |

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
python test_enhanced_endpoints.py

# Run specific test categories
python test_enhanced_endpoints.py search    # Search endpoint tests
python test_enhanced_endpoints.py auth      # Authentication tests
python test_enhanced_endpoints.py rate      # Rate limiting tests
```

### Test Categories

1. **Search Endpoints**: Test all search functionality
2. **Authentication**: Test different auth levels and permissions
3. **Rate Limiting**: Test rate limiting behavior
4. **Response Format**: Test response structure and validation
5. **Error Handling**: Test error scenarios and responses

### Sample Test Commands

```bash
# Test text search
curl -X POST "http://localhost:8000/api/search/text" \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop", "limit": 5}'

# Test with authentication
curl -X POST "http://localhost:8000/api/search/image" \
  -H "X-API-Key: basic_api_key_123" \
  -F "file=@test_image.jpg"

# Test rate limiting
for i in {1..20}; do
  curl -X POST "http://localhost:8000/api/search/text" \
    -H "Content-Type: application/json" \
    -d '{"query": "test '$i'"}' &
done
```

## API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Health Endpoints

- **API Status**: `GET /api/status`
- **Health Check**: `GET /api/health`
- **Root Info**: `GET /`

## Performance Considerations

### Optimization Tips

1. **Use appropriate limits**: Don't request more data than needed
2. **Implement pagination**: Use offset/limit for large result sets
3. **Cache responses**: Cache frequently accessed product details
4. **Optimize images**: Compress images before upload for faster processing
5. **Use filters**: Apply filters to reduce search scope
6. **Monitor rate limits**: Implement exponential backoff for rate limit handling

### Best Practices

1. **Authentication**: Store API keys securely, rotate regularly
2. **Error Handling**: Implement proper error handling and retry logic
3. **Logging**: Log all requests for monitoring and debugging
4. **Monitoring**: Monitor response times and error rates
5. **Testing**: Test all endpoints with various scenarios

## Deployment

### Environment Variables

```bash
# Authentication
SECRET_KEY=your-secret-key-here
BASIC_API_KEY=your-basic-api-key
PREMIUM_API_KEY=your-premium-api-key
ENTERPRISE_API_KEY=your-enterprise-api-key

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379

# Database
QDRANT_URL=http://localhost:6333

# Environment
ENVIRONMENT=production
```

### Docker Deployment

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Set strong secret keys
- [ ] Configure rate limiting with Redis
- [ ] Set up proper logging
- [ ] Configure CORS for your domain
- [ ] Set up monitoring and alerts
- [ ] Test all endpoints thoroughly
- [ ] Document API usage for your team
