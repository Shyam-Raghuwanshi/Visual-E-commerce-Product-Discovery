from fastapi import APIRouter, Query, HTTPException, Request, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from app.models.schemas import (
    SearchRequest, SearchResponse, CombinedSearchRequest, ImageSearchRequest,
    FilterRequest, HybridSearchRequest, Product, ProductDetailResponse,
    ErrorResponse, SearchType, SortBy
)
from app.services.search_service import SearchService
from app.services.enhanced_search_service import EnhancedSearchService
from app.services.simple_search_service import SimpleSearchService
from app.services.advanced_search_integration import AdvancedSearchIntegration
from app.services.vector_service import VectorService
from app.middleware.authentication import get_current_user, AuthLevel
from app.middleware.rate_limiting import check_rate_limit, get_identifier
from typing import Optional, List, Dict, Any
import time
import uuid
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
search_service = SearchService()
enhanced_search_service = EnhancedSearchService()
simple_search_service = SimpleSearchService()
vector_service = VectorService()

# Initialize advanced search integration
advanced_search = AdvancedSearchIntegration(enhanced_search_service, vector_service)

@router.post("/search/text", response_model=SearchResponse, responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}})
async def search_by_text(
    request: SearchRequest,
    http_request: Request,
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for products using text query
    
    - **query**: Search text (required)
    - **category**: Filter by category (optional)
    - **limit**: Maximum results (1-100, default: 20)
    - **offset**: Results to skip for pagination (default: 0)
    
    Free tier endpoint - no authentication required
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Validate request
        if not request.query or request.query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Query parameter is required and cannot be empty",
                    "request_id": request_id
                }
            )
        
        # Check rate limits
        identifier = get_identifier(http_request)
        rate_info = check_rate_limit(identifier, "search")
        
        logger.info(f"Text search request: {request_id}, user: {current_user.get('level', 'none')}, query: {request.query[:50]}")
        
        # Check if user wants advanced search (users with premium+ get advanced search)
        user_level = current_user.get("level", "none")
        use_advanced = user_level in ["premium", "enterprise", "jwt"]
        
        if use_advanced:
            # Use advanced search with personalization and business logic
            user_context = await _extract_user_context(http_request, current_user)
            geographic_context = await _extract_geographic_context(http_request)
            session_id = _get_session_id(http_request)
            
            results = await advanced_search.advanced_text_search(
                request=request,
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id
            )
            
            # Convert advanced search response to standard response
            if results.get("success", False):
                query_time = time.time() - start_time
                response = SearchResponse(
                    products=results.get("products", []),
                    total=results.get("total_found", 0),
                    query_time=query_time,
                    search_type=SearchType.TEXT,
                    filters_applied={
                        "category": request.category,
                        "limit": request.limit,
                        "offset": request.offset,
                        "advanced_search": True,
                        "algorithm": results.get("search_metadata", {}).get("algorithm_used")
                    },
                    page_info={
                        "current_page": (request.offset // request.limit) + 1,
                        "has_next": (request.offset + request.limit) < results.get("total_found", 0),
                        "total_pages": ((results.get("total_found", 0) - 1) // request.limit) + 1 if results.get("total_found", 0) > 0 else 0
                    },
                    search_metadata=results.get("search_metadata")
                )
                
                logger.info(f"Advanced text search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
                return response
            else:
                # Fall back to basic search if advanced search fails
                logger.warning(f"Advanced search failed, falling back to basic search: {request_id}")
        
        # Perform basic search
        results = await search_service.search_by_text(
            query=request.query.strip(),
            category=request.category,
            limit=request.limit,
            offset=request.offset
        )
        
        query_time = time.time() - start_time
        
        # Enhanced response
        response = SearchResponse(
            products=results.get("products", []),
            total=results.get("total", 0),
            query_time=query_time,
            search_type=SearchType.TEXT,
            filters_applied={
                "category": request.category,
                "limit": request.limit,
                "offset": request.offset
            },
            page_info={
                "current_page": (request.offset // request.limit) + 1,
                "has_next": (request.offset + request.limit) < results.get("total", 0),
                "total_pages": ((results.get("total", 0) - 1) // request.limit) + 1 if results.get("total", 0) > 0 else 0
            }
        )
        
        logger.info(f"Text search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text search error: {request_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while processing your search",
                "request_id": request_id
            }
        )

@router.post("/search/image", response_model=SearchResponse, responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
async def search_by_image(
    file: UploadFile = File(...),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results to skip"),
    similarity_threshold: float = Query(0.7, ge=0, le=1, description="Minimum similarity score"),
    http_request: Request = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for products using an uploaded image
    
    - **file**: Image file (required) - supports JPEG, PNG, WebP
    - **category**: Filter by category (optional)
    - **limit**: Maximum results (1-100, default: 20)
    - **similarity_threshold**: Minimum similarity score (0-1, default: 0.7)
    
    Requires: Basic API key or higher
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Check authentication (Basic level required)
        if current_user.get("level") == "none":
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "authentication_required",
                    "message": "Image search requires Basic API key or higher",
                    "request_id": request_id
                }
            )
        
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_file_type",
                    "message": "File must be an image (JPEG, PNG, WebP)",
                    "request_id": request_id
                }
            )
        
        # Check file size (10MB limit)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "file_too_large",
                    "message": "Image file must be smaller than 10MB",
                    "request_id": request_id
                }
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Check rate limits
        identifier = get_identifier(http_request)
        rate_info = check_rate_limit(identifier, "search")
        
        logger.info(f"Image search request: {request_id}, user: {current_user.get('level')}, file: {file.filename}")
        
        # Check if user has premium+ for advanced search
        user_level = current_user.get("level", "none")
        use_advanced = user_level in ["premium", "enterprise", "jwt"]
        
        if use_advanced:
            # Use advanced image search
            content = await file.read()
            user_context = await _extract_user_context(http_request, current_user)
            geographic_context = await _extract_geographic_context(http_request)
            session_id = _get_session_id(http_request)
            
            # Convert filters
            filters = {}
            if category:
                filters["category"] = category
            
            results = await advanced_search.advanced_image_search(
                image_data=content,
                limit=limit,
                filters=filters,
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id
            )
            
            if results.get("success", False):
                query_time = time.time() - start_time
                response = SearchResponse(
                    products=results.get("products", []),
                    total=results.get("total_found", 0),
                    query_time=query_time,
                    search_type=SearchType.IMAGE,
                    filters_applied={
                        "category": category,
                        "similarity_threshold": similarity_threshold,
                        "limit": limit,
                        "offset": offset,
                        "advanced_search": True,
                        "algorithm": results.get("search_metadata", {}).get("algorithm_used")
                    },
                    page_info={
                        "current_page": (offset // limit) + 1,
                        "has_next": (offset + limit) < results.get("total_found", 0),
                        "total_pages": ((results.get("total_found", 0) - 1) // limit) + 1 if results.get("total_found", 0) > 0 else 0
                    },
                    search_metadata=results.get("search_metadata")
                )
                
                logger.info(f"Advanced image search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
                return response
            else:
                # Fall back to basic search
                logger.warning(f"Advanced image search failed, falling back to basic search: {request_id}")
                # Reset file pointer for fallback
                await file.seek(0)
        
        # Create search request for basic search
        search_request = ImageSearchRequest(
            category=category,
            limit=limit,
            offset=offset,
            similarity_threshold=similarity_threshold
        )
        
        # Perform basic search
        results = await enhanced_search_service.search_by_image(file, search_request)
        
        query_time = time.time() - start_time
        
        response = SearchResponse(
            products=results.get("products", []),
            total=results.get("total", 0),
            query_time=query_time,
            similarity_scores=results.get("similarity_scores"),
            search_type=SearchType.IMAGE,
            filters_applied={
                "category": category,
                "similarity_threshold": similarity_threshold,
                "limit": limit,
                "offset": offset
            },
            page_info={
                "current_page": (offset // limit) + 1,
                "has_next": (offset + limit) < results.get("total", 0),
                "total_pages": ((results.get("total", 0) - 1) // limit) + 1 if results.get("total", 0) > 0 else 0
            }
        )
        
        logger.info(f"Image search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image search error: {request_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while processing your image search",
                "request_id": request_id
            }
        )

@router.post("/search/combined", response_model=SearchResponse, responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
async def search_combined(
    file: UploadFile = File(...),
    query: str = Query(..., min_length=1, max_length=500, description="Text search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    image_weight: float = Query(0.7, ge=0, le=1, description="Weight for image similarity"),
    text_weight: float = Query(0.3, ge=0, le=1, description="Weight for text similarity"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results to skip"),
    http_request: Request = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for products using both image and text
    
    - **file**: Image file (required)
    - **query**: Text search query (required)
    - **image_weight**: Weight for image similarity (0-1, default: 0.7)
    - **text_weight**: Weight for text similarity (0-1, default: 0.3)
    - **category**: Filter by category (optional)
    
    Requires: Premium API key or higher
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Check authentication (Premium level required)
        user_level = current_user.get("level", "none")
        if user_level not in ["premium", "enterprise", "jwt"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": "Combined search requires Premium API key or higher",
                    "current_level": user_level,
                    "required_level": "premium",
                    "request_id": request_id
                }
            )
        
        # Validate weights
        if abs(image_weight + text_weight - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_weights",
                    "message": "image_weight + text_weight must equal 1.0",
                    "request_id": request_id
                }
            )
        
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_file_type",
                    "message": "File must be an image",
                    "request_id": request_id
                }
            )
        
        # Check rate limits
        identifier = get_identifier(http_request)
        rate_info = check_rate_limit(identifier, "search")
        
        logger.info(f"Combined search request: {request_id}, user: {user_level}, query: {query[:50]}")
        
        # Use advanced combined search for premium+ users
        content = await file.read()
        user_context = await _extract_user_context(http_request, current_user)
        geographic_context = await _extract_geographic_context(http_request)
        session_id = _get_session_id(http_request)
        
        # Convert filters
        filters = {}
        if category:
            filters["category"] = category
        
        results = await advanced_search.advanced_combined_search(
            query=query.strip(),
            image_data=content,
            text_weight=text_weight,
            image_weight=image_weight,
            limit=limit,
            filters=filters,
            user_context=user_context,
            geographic_context=geographic_context,
            session_id=session_id
        )
        
        query_time = time.time() - start_time
        
        if results.get("success", False):
            response = SearchResponse(
                products=results.get("products", []),
                total=results.get("total_found", 0),
                query_time=query_time,
                search_type=SearchType.COMBINED,
                filters_applied={
                    "query": query,
                    "category": category,
                    "image_weight": image_weight,
                    "text_weight": text_weight,
                    "limit": limit,
                    "offset": offset,
                    "advanced_search": True,
                    "algorithm": results.get("search_metadata", {}).get("algorithm_used")
                },
                search_metadata=results.get("search_metadata")
            )
            
            logger.info(f"Advanced combined search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
            return response
        else:
            # Fall back to basic combined search
            logger.warning(f"Advanced combined search failed, falling back to basic search: {request_id}")
            # Reset file pointer and create request object
            await file.seek(0)
            
            search_request = CombinedSearchRequest(
                query=query.strip(),
                category=category,
                image_weight=image_weight,
                text_weight=text_weight,
                limit=limit,
                offset=offset
            )
            
            # Perform basic combined search
            results = await enhanced_search_service.search_combined(file, search_request)
        
        query_time = time.time() - start_time
        
        response = SearchResponse(
            products=results.get("products", []),
            total=results.get("total", 0),
            query_time=query_time,
            similarity_scores=results.get("similarity_scores"),
            search_type=SearchType.COMBINED,
            filters_applied={
                "query": query,
                "category": category,
                "image_weight": image_weight,
                "text_weight": text_weight,
                "limit": limit,
                "offset": offset
            }
        )
        
        logger.info(f"Combined search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Combined search error: {request_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while processing your combined search",
                "request_id": request_id
            }
        )

@router.post("/search/filters", response_model=SearchResponse, responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}})
async def search_with_filters(
    request: FilterRequest,
    http_request: Request,
    current_user: Dict = Depends(get_current_user)
):
    """
    Advanced filtering with vector search
    
    - **text_query**: Optional text search
    - **categories**: List of categories to filter by
    - **brands**: List of brands to filter by
    - **price range**: Min/max price filters
    - **rating filter**: Minimum rating filter
    - **sorting**: Multiple sort options
    
    Requires: Premium API key or higher
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Check authentication (Premium level required)
        user_level = current_user.get("level", "none")
        if user_level not in ["premium", "enterprise", "jwt"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": "Advanced filtering requires Premium API key or higher",
                    "current_level": user_level,
                    "required_level": "premium",
                    "request_id": request_id
                }
            )
        
        # Check rate limits
        identifier = get_identifier(http_request)
        rate_info = check_rate_limit(identifier, "search")
        
        logger.info(f"Filter search request: {request_id}, user: {user_level}")
        
        # Use advanced filter search for premium+ users
        user_context = await _extract_user_context(http_request, current_user)
        geographic_context = await _extract_geographic_context(http_request)
        session_id = _get_session_id(http_request)
        
        results = await advanced_search.advanced_filter_search(
            request=request,
            user_context=user_context,
            geographic_context=geographic_context,
            session_id=session_id
        )
        
        query_time = time.time() - start_time
        
        if results.get("success", False):
            response = SearchResponse(
                products=results.get("products", []),
                total=results.get("total_found", 0),
                query_time=query_time,
                search_type=SearchType.ADVANCED,
                filters_applied=results.get("filters_applied", {}),
                aggregations=results.get("aggregations", {}),
                page_info={
                    "current_page": (request.offset // request.limit) + 1,
                    "has_next": (request.offset + request.limit) < results.get("total_found", 0),
                    "total_pages": ((results.get("total_found", 0) - 1) // request.limit) + 1 if results.get("total_found", 0) > 0 else 0
                },
                search_metadata=results.get("search_metadata")
            )
            
            logger.info(f"Advanced filter search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
            return response
        else:
            # Fall back to basic optimized search
            logger.warning(f"Advanced filter search failed, falling back to optimized search: {request_id}")
            
            # Perform optimized search
            results = await simple_search_service.search_by_text(
                query=request.query,
                limit=request.limit,
                filters=request.filters
            )
        
        query_time = time.time() - start_time
        
        response = SearchResponse(
            products=results.get("products", []),
            total=results.get("total", 0),
            query_time=query_time,
            search_type=SearchType.ADVANCED,
            filters_applied=results.get("filters_applied", {}),
            aggregations=results.get("aggregations", {}),
            page_info={
                "current_page": (request.offset // request.limit) + 1,
                "has_next": (request.offset + request.limit) < results.get("total", 0),
                "total_pages": ((results.get("total", 0) - 1) // request.limit) + 1 if results.get("total", 0) > 0 else 0
            }
        )
        
        logger.info(f"Filter search completed: {request_id}, results: {len(results.get('products', []))}, time: {query_time:.3f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Filter search error: {request_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while processing your filtered search",
                "request_id": request_id
            }
        )

@router.get("/products/{product_id}", response_model=ProductDetailResponse, responses={404: {"model": ErrorResponse}})
async def get_product_details(
    product_id: str,
    include_similar: bool = Query(True, description="Include similar products"),
    include_recommendations: bool = Query(True, description="Include recommendations"),
    similar_count: int = Query(5, ge=1, le=20, description="Number of similar products"),
    http_request: Request = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get detailed product information
    
    - **product_id**: Unique product identifier
    - **include_similar**: Include similar products (default: true)
    - **include_recommendations**: Include recommendations (default: true)
    - **similar_count**: Number of similar products (1-20, default: 5)
    
    Free tier endpoint
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Check rate limits
        identifier = get_identifier(http_request)
        rate_info = check_rate_limit(identifier, "product")
        
        logger.info(f"Product details request: {request_id}, product_id: {product_id}")
        
        # Get product details
        product = await search_service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "product_not_found",
                    "message": f"Product with ID '{product_id}' not found",
                    "request_id": request_id
                }
            )
        
        response_data = {"product": product}
        
        # Get similar products if requested
        if include_similar:
            similar_products = await search_service.get_similar_products(product_id, similar_count)
            response_data["similar_products"] = similar_products.get("products", [])
        
        # Get recommendations if requested
        if include_recommendations:
            recommendations = await search_service.get_recommendations(product_id, similar_count)
            response_data["recommendations"] = recommendations.get("products", [])
        
        query_time = time.time() - start_time
        response_data["metadata"] = {
            "query_time": query_time,
            "request_id": request_id
        }
        
        response = ProductDetailResponse(**response_data)
        
        logger.info(f"Product details completed: {request_id}, time: {query_time:.3f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Product details error: {request_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while retrieving product details",
                "request_id": request_id
            }
        )

@router.get("/search/similar/{product_id}", response_model=SearchResponse)
async def get_similar_products(
    product_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    category: Optional[str] = Query(None, description="Filter by category"),
    http_request: Request = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get similar products based on a product ID"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Check rate limits
        identifier = get_identifier(http_request)
        rate_info = check_rate_limit(identifier, "search")
        
        # Check if user has premium+ for advanced similar products
        user_level = current_user.get("level", "none")
        use_advanced = user_level in ["premium", "enterprise", "jwt"]
        
        if use_advanced:
            # Use advanced similar products search
            user_context = await _extract_user_context(http_request, current_user)
            geographic_context = await _extract_geographic_context(http_request)
            session_id = _get_session_id(http_request)
            
            results = await advanced_search.get_similar_products_advanced(
                product_id=product_id,
                limit=limit,
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id
            )
            
            query_time = time.time() - start_time
            
            if results.get("success", False):
                return SearchResponse(
                    products=results.get("products", []),
                    total=results.get("total_found", 0),
                    query_time=query_time,
                    search_type=SearchType.IMAGE,
                    filters_applied={
                        "product_id": product_id, 
                        "category": category,
                        "advanced_search": True,
                        "algorithm": results.get("search_metadata", {}).get("algorithm_used")
                    },
                    search_metadata=results.get("search_metadata")
                )
            else:
                # Fall back to basic similar products
                logger.warning(f"Advanced similar products failed, falling back to basic search: {request_id}")
        
        # Basic similar products search
        results = await search_service.get_similar_products(
            product_id, 
            limit, 
            category=category
        )
        
        query_time = time.time() - start_time
        
        return SearchResponse(
            products=results.get("products", []),
            total=results.get("total", 0),
            query_time=query_time,
            similarity_scores=results.get("similarity_scores"),
            search_type=SearchType.IMAGE,
            filters_applied={"product_id": product_id, "category": category}
        )
        
    except Exception as e:
        logger.error(f"Similar products error: {request_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while finding similar products",
                "request_id": request_id
            }
        )

@router.get("/categories", response_model=Dict[str, List[str]])
async def get_categories():
    """Get all available product categories and brands"""
    try:
        categories = await search_service.get_categories()
        brands = await search_service.get_brands()
        
        return {
            "categories": categories,
            "brands": brands,
            "total_categories": len(categories),
            "total_brands": len(brands)
        }
        
    except Exception as e:
        logger.error(f"Categories error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while retrieving categories"
            }
        )

@router.get("/products/categories", response_model=Dict[str, List[str]])
async def get_product_categories():
    """Get all available product categories and brands (alternative endpoint for frontend compatibility)"""
    try:
        categories = await search_service.get_categories()
        brands = await search_service.get_brands()
        
        return {
            "categories": categories,
            "brands": brands,
            "total_categories": len(categories),
            "total_brands": len(brands)
        }
        
    except Exception as e:
        logger.error(f"Product categories error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while retrieving product categories"
            }
        )

# Helper functions for advanced search integration

async def _extract_user_context(request: Request, current_user: Dict) -> Optional[Dict[str, Any]]:
    """Extract user context for personalized search"""
    try:
        user_context = {
            "user_id": current_user.get("user_id", "anonymous"),
            "level": current_user.get("level", "none")
        }
        
        # Extract from headers if available
        user_agent = request.headers.get("user-agent", "")
        if "mobile" in user_agent.lower():
            user_context["device_type"] = "mobile"
        elif "tablet" in user_agent.lower():
            user_context["device_type"] = "tablet"
        else:
            user_context["device_type"] = "desktop"
        
        # Extract preferences from request if available (could be from cookies, headers, etc.)
        preferences = {}
        
        # Price sensitivity from previous searches (simplified example)
        if current_user.get("price_sensitivity"):
            preferences["price_sensitivity"] = current_user["price_sensitivity"]
        
        # Category preferences (could be tracked from user history)
        if current_user.get("category_preferences"):
            preferences["category_preferences"] = current_user["category_preferences"]
        
        user_context["preferences"] = preferences
        
        return user_context
        
    except Exception as e:
        logger.warning(f"Error extracting user context: {e}")
        return None

async def _extract_geographic_context(request: Request) -> Optional[Dict[str, Any]]:
    """Extract geographic context from request"""
    try:
        geo_context = {}
        
        # Extract from headers
        country = request.headers.get("cf-ipcountry") or request.headers.get("x-country", "US")
        geo_context["country"] = country
        
        # Extract language preference
        accept_language = request.headers.get("accept-language", "en")
        primary_language = accept_language.split(",")[0].split("-")[0]
        geo_context["language"] = primary_language
        
        # Extract timezone (simplified)
        timezone = request.headers.get("x-timezone")
        if timezone:
            geo_context["timezone"] = timezone
        
        # Extract currency (could be based on country)
        currency_map = {
            "US": "USD", "CA": "CAD", "GB": "GBP", "DE": "EUR", 
            "FR": "EUR", "JP": "JPY", "AU": "AUD", "IN": "INR"
        }
        geo_context["currency"] = currency_map.get(country, "USD")
        
        # Shipping zones (simplified)
        shipping_zone_map = {
            "US": ["domestic"], "CA": ["international"], 
            "GB": ["eu"], "DE": ["eu"], "FR": ["eu"]
        }
        geo_context["shipping_zones"] = shipping_zone_map.get(country, ["international"])
        
        return geo_context
        
    except Exception as e:
        logger.warning(f"Error extracting geographic context: {e}")
        return None

def _get_session_id(request: Request) -> str:
    """Get or generate session ID"""
    try:
        # Try to get from cookie first
        session_id = request.cookies.get("session_id")
        
        # Try to get from header
        if not session_id:
            session_id = request.headers.get("x-session-id")
        
        # Generate new session ID if not found
        if not session_id:
            session_id = f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        return session_id
        
    except Exception as e:
        logger.warning(f"Error getting session ID: {e}")
        return f"session_{int(time.time())}_{uuid.uuid4().hex[:8]}"

# New endpoints for advanced search features

@router.post("/search/interaction")
async def record_search_interaction(
    session_id: str = Query(..., description="Session ID"),
    product_id: str = Query(..., description="Product ID"),
    interaction_type: str = Query(..., description="Type of interaction (view, click, purchase, etc.)"),
    position: int = Query(..., ge=1, description="Position in search results"),
    query: Optional[str] = Query(None, description="Search query"),
    algorithm: Optional[str] = Query(None, description="Algorithm used"),
    timestamp: Optional[str] = Query(None, description="Interaction timestamp"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Record user interaction for analytics and A/B testing
    
    - **session_id**: Unique session identifier
    - **product_id**: Product that was interacted with
    - **interaction_type**: Type of interaction (view, click, purchase, add_to_cart, etc.)
    - **position**: Position of product in search results (1-based)
    - **query**: Original search query (optional)
    - **algorithm**: Algorithm used for search (optional)
    
    Free tier endpoint for analytics
    """
    try:
        # Record interaction
        additional_data = {
            "query": query,
            "algorithm": algorithm,
            "timestamp": timestamp,
            "user_level": current_user.get("level", "none")
        }
        
        advanced_search.record_user_interaction(
            session_id=session_id,
            product_id=product_id,
            interaction_type=interaction_type,
            position=position,
            additional_data=additional_data
        )
        
        return {
            "success": True,
            "message": "Interaction recorded successfully",
            "session_id": session_id,
            "product_id": product_id,
            "interaction_type": interaction_type
        }
        
    except Exception as e:
        logger.error(f"Error recording interaction: {str(e)}")
        return {
            "success": False,
            "error": "Failed to record interaction",
            "message": str(e)
        }

@router.get("/search/analytics/performance")
async def get_algorithm_performance(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get A/B testing performance analytics
    
    Requires: Enterprise API key
    """
    try:
        # Check authentication (Enterprise level required for analytics)
        user_level = current_user.get("level", "none")
        if user_level != "enterprise":
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_permissions",
                    "message": "Performance analytics requires Enterprise API key",
                    "current_level": user_level,
                    "required_level": "enterprise"
                }
            )
        
        # Get performance report
        performance_report = advanced_search.get_algorithm_performance_report()
        
        return {
            "success": True,
            "performance_report": performance_report,
            "generated_at": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "message": "An error occurred while retrieving performance analytics"
            }
        )

@router.get("/search/test/{session_id}")
async def get_ab_test_assignment(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get A/B test assignment for a session
    
    - **session_id**: Session identifier
    
    Free tier endpoint
    """
    try:
        # This would typically check the assignment from the A/B testing framework
        # For now, return a simple response
        return {
            "session_id": session_id,
            "algorithm_assigned": "balanced",  # This would come from the actual assignment
            "features_enabled": {
                "advanced_ranking": current_user.get("level") in ["premium", "enterprise", "jwt"],
                "personalization": current_user.get("level") in ["premium", "enterprise", "jwt"],
                "geographic_optimization": True,
                "business_rules": True
            },
            "user_level": current_user.get("level", "none")
        }
        
    except Exception as e:
        logger.error(f"Error getting A/B test assignment: {str(e)}")
        return {
            "session_id": session_id,
            "algorithm_assigned": "similarity_first",
            "features_enabled": {
                "advanced_ranking": False,
                "personalization": False,
                "geographic_optimization": False,
                "business_rules": False
            },
            "error": str(e)
        }
