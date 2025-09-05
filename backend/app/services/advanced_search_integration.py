"""
Advanced Search Integration Service
Integrates the advanced search algorithms with the existing search infrastructure.
Provides high-level interface for advanced search functionality.
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import time

from ..services.advanced_search_algorithms import (
    AdvancedSearchEngine,
    SearchContext,
    UserProfile,
    GeographicContext,
    ProductScore,
    RankingAlgorithm
)
from ..services.enhanced_search_service import EnhancedSearchService
from ..services.vector_service import VectorService
from ..models.schemas import SearchRequest, FilterRequest, SearchResponse

logger = logging.getLogger(__name__)

class AdvancedSearchIntegration:
    """
    Integration service that combines advanced search algorithms
    with existing search infrastructure
    """
    
    def __init__(self, enhanced_search: EnhancedSearchService, vector_service: VectorService):
        self.enhanced_search = enhanced_search
        self.vector_service = vector_service
        self.advanced_engine = AdvancedSearchEngine()
        
        # Performance tracking
        self.search_stats = {
            "total_searches": 0,
            "avg_response_time": 0.0,
            "algorithm_usage": {},
            "user_satisfaction": {}
        }
        
        logger.info("Advanced Search Integration initialized")
    
    async def advanced_text_search(
        self,
        request: SearchRequest,
        user_context: Optional[Dict[str, Any]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced text-based search with personalization and business logic
        """
        try:
            start_time = time.time()
            
            # Create search context
            context = self._create_search_context(
                query=request.query,
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id,
                search_intent="text_search"
            )
            
            # Get initial candidates using existing search
            initial_results = await self.enhanced_search.search_by_text(
                request.query,
                request.limit * 3,  # Get more candidates for re-ranking
                request.filters
            )
            
            if not initial_results or "products" not in initial_results:
                return self._create_empty_response("No products found")
            
            # Prepare query data for advanced ranking
            query_data = {
                "query_text": request.query,
                "search_type": "text"
            }
            
            # Apply advanced ranking
            ranked_scores = await self.advanced_engine.search_and_rank(
                query_data=query_data,
                candidate_products=initial_results["products"],
                context=context
            )
            
            # Convert to response format
            response = self._create_advanced_response(
                ranked_scores[:request.limit],
                context,
                time.time() - start_time
            )
            
            # Update statistics
            self._update_search_stats(context, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced text search: {e}")
            return self._create_error_response(str(e))
    
    async def advanced_image_search(
        self,
        image_data: bytes,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced image-based search with visual similarity and business logic
        """
        try:
            start_time = time.time()
            
            # Create search context
            context = self._create_search_context(
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id,
                search_intent="image_search"
            )
            
            # Get initial candidates using existing image search
            initial_results = await self.enhanced_search.search_by_image_data(
                image_data,
                limit * 3,  # Get more candidates for re-ranking
                filters
            )
            
            if not initial_results or "products" not in initial_results:
                return self._create_empty_response("No similar products found")
            
            # Get image embedding for advanced ranking
            try:
                image_embedding = await self.vector_service.generate_image_embedding(image_data)
            except Exception as e:
                logger.warning(f"Could not generate image embedding: {e}")
                image_embedding = None
            
            # Prepare query data for advanced ranking
            query_data = {
                "search_type": "image",
                "query_image_embedding": image_embedding
            }
            
            # Apply advanced ranking
            ranked_scores = await self.advanced_engine.search_and_rank(
                query_data=query_data,
                candidate_products=initial_results["products"],
                context=context
            )
            
            # Convert to response format
            response = self._create_advanced_response(
                ranked_scores[:limit],
                context,
                time.time() - start_time
            )
            
            # Update statistics
            self._update_search_stats(context, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced image search: {e}")
            return self._create_error_response(str(e))
    
    async def advanced_combined_search(
        self,
        query: str,
        image_data: bytes,
        text_weight: float = 0.5,
        image_weight: float = 0.5,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced combined text and image search
        """
        try:
            start_time = time.time()
            
            # Create search context
            context = self._create_search_context(
                query=query,
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id,
                search_intent="combined_search"
            )
            
            # Get initial candidates using existing combined search
            initial_results = await self.enhanced_search.search_combined(
                query,
                image_data,
                text_weight,
                image_weight,
                limit * 3,  # Get more candidates for re-ranking
                filters
            )
            
            if not initial_results or "products" not in initial_results:
                return self._create_empty_response("No matching products found")
            
            # Get embeddings for advanced ranking
            try:
                image_embedding = await self.vector_service.generate_image_embedding(image_data)
            except Exception as e:
                logger.warning(f"Could not generate image embedding: {e}")
                image_embedding = None
            
            # Prepare query data for advanced ranking
            query_data = {
                "query_text": query,
                "query_image_embedding": image_embedding,
                "search_type": "combined",
                "text_weight": text_weight,
                "image_weight": image_weight
            }
            
            # Apply advanced ranking
            ranked_scores = await self.advanced_engine.search_and_rank(
                query_data=query_data,
                candidate_products=initial_results["products"],
                context=context
            )
            
            # Convert to response format
            response = self._create_advanced_response(
                ranked_scores[:limit],
                context,
                time.time() - start_time
            )
            
            # Update statistics
            self._update_search_stats(context, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced combined search: {e}")
            return self._create_error_response(str(e))
    
    async def advanced_filter_search(
        self,
        request: FilterRequest,
        user_context: Optional[Dict[str, Any]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced filtered search with business logic
        """
        try:
            start_time = time.time()
            
            # Create search context
            context = self._create_search_context(
                query=request.query,
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id,
                search_intent="filter_search"
            )
            
            # Convert FilterRequest to basic filters for existing search
            basic_filters = self._convert_filter_request(request)
            
            # Get initial candidates using existing search
            if request.query:
                initial_results = await self.enhanced_search.search_by_text(
                    request.query,
                    request.limit * 3,
                    basic_filters
                )
            else:
                # Pure filter search without text query
                initial_results = await self._get_filtered_products(basic_filters, request.limit * 3)
            
            if not initial_results or "products" not in initial_results:
                return self._create_empty_response("No products match the filters")
            
            # Prepare query data for advanced ranking
            query_data = {
                "query_text": request.query,
                "search_type": "filter",
                "filters": basic_filters,
                "advanced_filters": {
                    "price_range": request.price_range,
                    "brands": request.brands,
                    "categories": request.categories,
                    "rating_min": request.rating_min,
                    "in_stock_only": request.in_stock_only
                }
            }
            
            # Apply advanced ranking with filter-specific logic
            ranked_scores = await self.advanced_engine.search_and_rank(
                query_data=query_data,
                candidate_products=initial_results["products"],
                context=context
            )
            
            # Convert to response format with aggregations
            response = self._create_advanced_response(
                ranked_scores[:request.limit],
                context,
                time.time() - start_time,
                include_aggregations=True,
                all_products=initial_results["products"]
            )
            
            # Update statistics
            self._update_search_stats(context, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced filter search: {e}")
            return self._create_error_response(str(e))
    
    async def get_similar_products_advanced(
        self,
        product_id: str,
        limit: int = 10,
        user_context: Optional[Dict[str, Any]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get similar products using advanced algorithms
        """
        try:
            start_time = time.time()
            
            # Create search context
            context = self._create_search_context(
                user_context=user_context,
                geographic_context=geographic_context,
                session_id=session_id,
                search_intent="similar_products"
            )
            
            # Get the base product
            base_product = await self._get_product_by_id(product_id)
            if not base_product:
                return self._create_error_response("Product not found")
            
            # Get initial similar products
            initial_results = await self.enhanced_search.find_similar_products(
                product_id,
                limit * 2  # Get more candidates for re-ranking
            )
            
            if not initial_results or "products" not in initial_results:
                return self._create_empty_response("No similar products found")
            
            # Prepare query data for advanced ranking
            query_data = {
                "search_type": "similar",
                "base_product": base_product,
                "base_product_embedding": base_product.get("image_embedding")
            }
            
            # Apply advanced ranking
            ranked_scores = await self.advanced_engine.search_and_rank(
                query_data=query_data,
                candidate_products=initial_results["products"],
                context=context
            )
            
            # Convert to response format
            response = self._create_advanced_response(
                ranked_scores[:limit],
                context,
                time.time() - start_time
            )
            
            # Update statistics
            self._update_search_stats(context, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced similar products search: {e}")
            return self._create_error_response(str(e))
    
    def record_user_interaction(
        self,
        session_id: str,
        product_id: str,
        interaction_type: str,
        position: int,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """
        Record user interaction for A/B testing and analytics
        """
        try:
            self.advanced_engine.record_search_interaction(
                session_id, product_id, interaction_type, position
            )
            
            # Store additional analytics data
            if additional_data:
                self._store_interaction_data(
                    session_id, product_id, interaction_type, position, additional_data
                )
                
        except Exception as e:
            logger.error(f"Error recording user interaction: {e}")
    
    def get_algorithm_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report for all algorithms
        """
        try:
            performance = self.advanced_engine.get_algorithm_performance()
            
            return {
                "algorithm_performance": performance,
                "overall_stats": self.search_stats,
                "generated_at": datetime.now().isoformat(),
                "recommendations": self._generate_algorithm_recommendations(performance)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance report: {e}")
            return {"error": str(e)}
    
    def _create_search_context(
        self,
        query: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        geographic_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        search_intent: Optional[str] = None
    ) -> SearchContext:
        """Create search context from request data"""
        
        # Create user profile
        user_profile = None
        if user_context:
            user_profile = UserProfile(
                user_id=user_context.get("user_id", "anonymous"),
                age_group=user_context.get("age_group"),
                gender=user_context.get("gender"),
                preferences=user_context.get("preferences", {}),
                purchase_history=user_context.get("purchase_history", []),
                search_history=user_context.get("search_history", []),
                viewed_products=user_context.get("viewed_products", []),
                price_sensitivity=user_context.get("price_sensitivity", 0.5),
                brand_loyalty=user_context.get("brand_loyalty", {}),
                category_preferences=user_context.get("category_preferences", {})
            )
        
        # Create geographic context
        geo_context = None
        if geographic_context:
            geo_context = GeographicContext(
                country=geographic_context.get("country", "US"),
                state=geographic_context.get("state"),
                city=geographic_context.get("city"),
                postal_code=geographic_context.get("postal_code"),
                latitude=geographic_context.get("latitude"),
                longitude=geographic_context.get("longitude"),
                timezone=geographic_context.get("timezone"),
                currency=geographic_context.get("currency", "USD"),
                language=geographic_context.get("language", "en"),
                shipping_zones=geographic_context.get("shipping_zones", [])
            )
        
        return SearchContext(
            query=query,
            user_profile=user_profile,
            geographic_context=geo_context,
            session_id=session_id or f"session_{int(time.time())}",
            search_intent=search_intent,
            timestamp=datetime.now()
        )
    
    def _create_advanced_response(
        self,
        product_scores: List[ProductScore],
        context: SearchContext,
        processing_time: float,
        include_aggregations: bool = False,
        all_products: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create response with advanced search results"""
        
        # Convert product scores to response format
        products = []
        for score in product_scores:
            # Find the original product data
            product_data = self._find_product_data(score.product_id, all_products or [])
            if product_data:
                product_response = product_data.copy()
                product_response.update({
                    "similarity_score": score.base_similarity,
                    "business_score": score.business_score,
                    "personalization_score": score.personalization_score,
                    "final_score": score.final_score,
                    "rank": score.rank,
                    "explanation": score.explanation if logger.level <= logging.DEBUG else None
                })
                products.append(product_response)
        
        response = {
            "products": products,
            "total_found": len(products),
            "search_metadata": {
                "algorithm_used": context.ab_test_group,
                "processing_time_ms": round(processing_time * 1000, 2),
                "search_intent": context.search_intent,
                "personalized": context.user_profile is not None,
                "geographic_context": context.geographic_context is not None,
                "timestamp": context.timestamp.isoformat()
            },
            "success": True
        }
        
        # Add aggregations for filter searches
        if include_aggregations and all_products:
            response["aggregations"] = self._generate_aggregations(all_products)
        
        return response
    
    def _create_empty_response(self, message: str) -> Dict[str, Any]:
        """Create empty response"""
        return {
            "products": [],
            "total_found": 0,
            "message": message,
            "success": True
        }
    
    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "products": [],
            "total_found": 0,
            "error": error,
            "success": False
        }
    
    def _convert_filter_request(self, request: FilterRequest) -> Dict[str, Any]:
        """Convert FilterRequest to basic filters"""
        filters = {}
        
        if request.price_range:
            filters["price_min"] = request.price_range.get("min")
            filters["price_max"] = request.price_range.get("max")
        
        if request.brands:
            filters["brands"] = request.brands
        
        if request.categories:
            filters["categories"] = request.categories
        
        if request.rating_min:
            filters["rating_min"] = request.rating_min
        
        if request.in_stock_only:
            filters["in_stock"] = True
        
        return filters
    
    async def _get_filtered_products(
        self,
        filters: Dict[str, Any],
        limit: int
    ) -> Dict[str, Any]:
        """Get products by filters only (no text query)"""
        # This would typically query the database or vector store directly
        # For now, return empty result indicating this needs implementation
        return {"products": []}
    
    async def _get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        # This would typically query the database
        # For now, return None indicating this needs implementation
        return None
    
    def _find_product_data(
        self,
        product_id: str,
        products: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find product data by ID in product list"""
        for product in products:
            if product.get("id") == product_id:
                return product
        return None
    
    def _generate_aggregations(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate aggregations for filter results"""
        aggregations = {
            "brands": {},
            "categories": {},
            "price_ranges": {
                "0-25": 0,
                "25-50": 0,
                "50-100": 0,
                "100-200": 0,
                "200+": 0
            },
            "ratings": {
                "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
            }
        }
        
        for product in products:
            # Brand aggregation
            brand = product.get("brand", "Unknown")
            aggregations["brands"][brand] = aggregations["brands"].get(brand, 0) + 1
            
            # Category aggregation
            category = product.get("category", "Unknown")
            aggregations["categories"][category] = aggregations["categories"].get(category, 0) + 1
            
            # Price range aggregation
            price = product.get("price", 0)
            if price <= 25:
                aggregations["price_ranges"]["0-25"] += 1
            elif price <= 50:
                aggregations["price_ranges"]["25-50"] += 1
            elif price <= 100:
                aggregations["price_ranges"]["50-100"] += 1
            elif price <= 200:
                aggregations["price_ranges"]["100-200"] += 1
            else:
                aggregations["price_ranges"]["200+"] += 1
            
            # Rating aggregation
            rating = int(product.get("rating", 3))
            aggregations["ratings"][str(rating)] += 1
        
        return aggregations
    
    def _update_search_stats(self, context: SearchContext, processing_time: float):
        """Update search statistics"""
        self.search_stats["total_searches"] += 1
        
        # Update average response time
        current_avg = self.search_stats["avg_response_time"]
        total_searches = self.search_stats["total_searches"]
        self.search_stats["avg_response_time"] = (
            (current_avg * (total_searches - 1) + processing_time) / total_searches
        )
        
        # Update algorithm usage
        algorithm = context.ab_test_group or "unknown"
        self.search_stats["algorithm_usage"][algorithm] = (
            self.search_stats["algorithm_usage"].get(algorithm, 0) + 1
        )
    
    def _store_interaction_data(
        self,
        session_id: str,
        product_id: str,
        interaction_type: str,
        position: int,
        additional_data: Dict[str, Any]
    ):
        """Store interaction data for analytics"""
        # This would typically store in a database or analytics service
        logger.debug(f"Interaction: {session_id}, {product_id}, {interaction_type}, pos: {position}")
    
    def _generate_algorithm_recommendations(
        self,
        performance: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on algorithm performance"""
        recommendations = []
        
        # Analyze CTR performance
        best_ctr_algorithm = None
        best_ctr = 0.0
        
        for algorithm, metrics in performance.items():
            ctr_data = metrics.get("ctr", {})
            ctr = ctr_data.get("ctr", 0.0)
            
            if ctr > best_ctr and ctr_data.get("sample_size", 0) > 100:  # Require minimum sample size
                best_ctr = ctr
                best_ctr_algorithm = algorithm
        
        if best_ctr_algorithm:
            recommendations.append(
                f"Algorithm '{best_ctr_algorithm}' shows best CTR performance ({best_ctr:.3f})"
            )
        
        # Analyze conversion performance
        best_conversion_algorithm = None
        best_conversion = 0.0
        
        for algorithm, metrics in performance.items():
            conv_data = metrics.get("conversion", {})
            conv_rate = conv_data.get("conversion_rate", 0.0)
            
            if conv_rate > best_conversion and conv_data.get("sample_size", 0) > 50:
                best_conversion = conv_rate
                best_conversion_algorithm = algorithm
        
        if best_conversion_algorithm:
            recommendations.append(
                f"Algorithm '{best_conversion_algorithm}' shows best conversion rate ({best_conversion:.3f})"
            )
        
        if not recommendations:
            recommendations.append("Insufficient data for performance recommendations")
        
        return recommendations
