"""
Analytics and Recommendation Engine Service

Provides comprehensive analytics tracking, user behavior analysis,
and personalized product recommendations for e-commerce optimization.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter
import statistics
import random

from app.models.business_schemas import (
    SearchAnalytics, UserBehaviorAnalytics, RecommendationRequest,
    RecommendationResponse, AnalyticsQuery
)
from app.services.database_service import db_manager
from app.services.cache_service import CacheService
from app.services.user_behavior_service import user_behavior_service
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

class AnalyticsRecommendationService:
    """Analytics tracking and recommendation engine service"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.vector_service = VectorService()
        self.analytics_cache_ttl = 3600  # 1 hour cache for analytics
        self.recommendation_cache_ttl = 1800  # 30 minutes cache for recommendations
        
        # Recommendation algorithm weights
        self.collaborative_weight = 0.4
        self.content_weight = 0.3
        self.popularity_weight = 0.2
        self.trend_weight = 0.1
        
        logger.info("Analytics and Recommendation Service initialized")
    
    async def track_search_pattern(
        self,
        user_id: str,
        search_query: str,
        search_type: str,
        results_count: int,
        clicked_products: List[str],
        session_id: Optional[str] = None
    ):
        """
        Track search patterns for analytics
        
        Args:
            user_id: User identifier
            search_query: Search query text
            search_type: Type of search
            results_count: Number of results returned
            clicked_products: Products clicked from results
            session_id: User session identifier
        """
        try:
            # Track in user behavior service
            await user_behavior_service.track_search_activity(
                user_id=user_id,
                search_query=search_query,
                search_type=search_type,
                filters_applied={},
                results_count=results_count,
                session_id=session_id
            )
            
            # Track global search analytics
            await self._update_global_search_analytics(
                search_query, search_type, results_count, len(clicked_products) > 0
            )
            
            logger.debug(f"Search pattern tracked for user {user_id}: {search_query}")
            
        except Exception as e:
            logger.error(f"Search pattern tracking failed: {e}")
    
    async def generate_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Generate personalized product recommendations
        
        Args:
            request: Recommendation request details
            
        Returns:
            Personalized recommendations
        """
        try:
            # Check cache first
            cache_key = f"recommendations:{request.user_id}:{request.recommendation_type}:{hash(str(request.dict()))}"
            cached_recommendations = await self.cache_service.get(cache_key)
            
            if cached_recommendations:
                return RecommendationResponse(**json.loads(cached_recommendations))
            
            # Generate recommendations based on type
            if request.recommendation_type == "similar_users":
                recommendations = await self._collaborative_filtering_recommendations(request)
            elif request.recommendation_type == "similar_products":
                recommendations = await self._content_based_recommendations(request)
            elif request.recommendation_type == "trending":
                recommendations = await self._trending_recommendations(request)
            elif request.recommendation_type == "personalized":
                recommendations = await self._hybrid_recommendations(request)
            elif request.recommendation_type == "category_based":
                recommendations = await self._category_based_recommendations(request)
            elif request.recommendation_type == "price_based":
                recommendations = await self._price_based_recommendations(request)
            else:
                # Default to hybrid recommendations
                recommendations = await self._hybrid_recommendations(request)
            
            # Filter out excluded products
            if request.exclude_products:
                recommendations = [
                    rec for rec in recommendations 
                    if rec.get("id") not in request.exclude_products
                ]
            
            # Apply category filter
            if request.include_categories:
                recommendations = [
                    rec for rec in recommendations 
                    if rec.get("category") in request.include_categories
                ]
            
            # Apply price filter
            if request.price_range:
                min_price = request.price_range.get("min", 0)
                max_price = request.price_range.get("max", float('inf'))
                recommendations = [
                    rec for rec in recommendations 
                    if min_price <= rec.get("price", 0) <= max_price
                ]
            
            # Limit results
            recommendations = recommendations[:request.limit]
            
            # Generate reasons and confidence scores
            recommendation_reasons = await self._generate_recommendation_reasons(
                request, recommendations
            )
            confidence_scores = await self._calculate_confidence_scores(
                request, recommendations
            )
            
            response = RecommendationResponse(
                user_id=request.user_id,
                recommendations=recommendations,
                recommendation_reasons=recommendation_reasons,
                confidence_scores=confidence_scores,
                algorithm_used=request.recommendation_type,
                expires_at=datetime.now() + timedelta(hours=2)
            )
            
            # Cache the result
            await self.cache_service.set(
                cache_key, 
                response.json(), 
                self.recommendation_cache_ttl
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise RuntimeError(f"Recommendation generation failed: {str(e)}")
    
    async def get_search_analytics(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """
        Get search analytics for specified period
        
        Args:
            query: Analytics query parameters
            
        Returns:
            Search analytics data
        """
        try:
            if query.metric_type != "search":
                raise ValueError("This method only handles search analytics")
            
            # Check cache
            cache_key = f"search_analytics:{query.start_date.date()}:{query.end_date.date()}:{query.aggregation}"
            cached_analytics = await self.cache_service.get(cache_key)
            
            if cached_analytics:
                return json.loads(cached_analytics)
            
            # Get search data from database
            search_data = await self._get_search_data(query.start_date, query.end_date)
            
            if not search_data:
                return {
                    "period": {
                        "start_date": query.start_date.isoformat(),
                        "end_date": query.end_date.isoformat()
                    },
                    "error": "No search data available for this period"
                }
            
            # Aggregate data
            analytics = await self._aggregate_search_analytics(search_data, query.aggregation)
            
            # Add insights
            analytics["insights"] = await self._generate_search_insights(search_data)
            analytics["generated_at"] = datetime.now().isoformat()
            
            # Cache result
            await self.cache_service.set(
                cache_key, 
                json.dumps(analytics, default=str), 
                self.analytics_cache_ttl
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Search analytics failed: {e}")
            raise RuntimeError(f"Search analytics failed: {str(e)}")
    
    async def get_user_analytics(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """
        Get user behavior analytics
        
        Args:
            query: Analytics query parameters
            
        Returns:
            User analytics data
        """
        try:
            if query.metric_type != "user_behavior":
                raise ValueError("This method only handles user behavior analytics")
            
            # Get user activity data
            user_data = await self._get_user_activity_data(query.start_date, query.end_date)
            
            if not user_data:
                return {
                    "period": {
                        "start_date": query.start_date.isoformat(),
                        "end_date": query.end_date.isoformat()
                    },
                    "error": "No user activity data available"
                }
            
            # Aggregate and analyze
            analytics = await self._aggregate_user_analytics(user_data, query.aggregation)
            
            # Add segmentation analysis
            analytics["user_segments"] = await self._analyze_user_segments(user_data)
            
            # Add conversion funnel
            analytics["conversion_funnel"] = await self._analyze_conversion_funnel(user_data)
            
            analytics["generated_at"] = datetime.now().isoformat()
            
            return analytics
            
        except Exception as e:
            logger.error(f"User analytics failed: {e}")
            raise RuntimeError(f"User analytics failed: {str(e)}")
    
    async def get_product_analytics(
        self,
        query: AnalyticsQuery
    ) -> Dict[str, Any]:
        """
        Get product performance analytics
        
        Args:
            query: Analytics query parameters
            
        Returns:
            Product analytics data
        """
        try:
            if query.metric_type != "product_performance":
                raise ValueError("This method only handles product performance analytics")
            
            # Get product interaction data
            product_data = await self._get_product_interaction_data(query.start_date, query.end_date)
            
            if not product_data:
                return {
                    "period": {
                        "start_date": query.start_date.isoformat(),
                        "end_date": query.end_date.isoformat()
                    },
                    "error": "No product interaction data available"
                }
            
            # Analyze product performance
            analytics = {
                "period": {
                    "start_date": query.start_date.isoformat(),
                    "end_date": query.end_date.isoformat()
                },
                "top_performing_products": await self._get_top_performing_products(product_data),
                "category_performance": await self._analyze_category_performance(product_data),
                "product_discovery_patterns": await self._analyze_product_discovery(product_data),
                "recommendation_effectiveness": await self._analyze_recommendation_effectiveness(product_data)
            }
            
            analytics["generated_at"] = datetime.now().isoformat()
            
            return analytics
            
        except Exception as e:
            logger.error(f"Product analytics failed: {e}")
            raise RuntimeError(f"Product analytics failed: {str(e)}")
    
    async def get_recommendation_performance(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze recommendation system performance
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Recommendation performance metrics
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get recommendation interaction data
            rec_data = await self._get_recommendation_interaction_data(start_date)
            
            if not rec_data:
                return {
                    "error": "No recommendation data available",
                    "analysis_period_days": days
                }
            
            # Calculate performance metrics
            total_recommendations = len(rec_data)
            clicked_recommendations = len([r for r in rec_data if r.get("clicked")])
            purchased_recommendations = len([r for r in rec_data if r.get("purchased")])
            
            click_through_rate = clicked_recommendations / total_recommendations if total_recommendations > 0 else 0
            conversion_rate = purchased_recommendations / total_recommendations if total_recommendations > 0 else 0
            
            # Algorithm performance breakdown
            algorithm_performance = defaultdict(lambda: {"total": 0, "clicked": 0, "purchased": 0})
            
            for rec in rec_data:
                algorithm = rec.get("algorithm", "unknown")
                algorithm_performance[algorithm]["total"] += 1
                if rec.get("clicked"):
                    algorithm_performance[algorithm]["clicked"] += 1
                if rec.get("purchased"):
                    algorithm_performance[algorithm]["purchased"] += 1
            
            # Calculate rates for each algorithm
            for algorithm in algorithm_performance:
                perf = algorithm_performance[algorithm]
                perf["click_rate"] = perf["clicked"] / perf["total"] if perf["total"] > 0 else 0
                perf["conversion_rate"] = perf["purchased"] / perf["total"] if perf["total"] > 0 else 0
            
            return {
                "analysis_period_days": days,
                "overall_performance": {
                    "total_recommendations_served": total_recommendations,
                    "click_through_rate": click_through_rate,
                    "conversion_rate": conversion_rate,
                    "effectiveness_score": (click_through_rate * 0.3 + conversion_rate * 0.7)
                },
                "algorithm_performance": dict(algorithm_performance),
                "top_performing_algorithms": sorted(
                    algorithm_performance.items(),
                    key=lambda x: x[1]["conversion_rate"],
                    reverse=True
                )[:5],
                "recommendations": await self._generate_performance_recommendations(algorithm_performance),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Recommendation performance analysis failed: {e}")
            return {"error": "Performance analysis failed"}
    
    async def get_trending_insights(
        self,
        category: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get trending products and search insights
        
        Args:
            category: Product category to focus on
            days: Number of days for trend analysis
            
        Returns:
            Trending insights data
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get trending search terms
            trending_searches = await self._get_trending_searches(start_date, category)
            
            # Get trending products
            trending_products = await self._get_trending_products(start_date, category)
            
            # Get emerging trends
            emerging_trends = await self._identify_emerging_trends(start_date, category)
            
            return {
                "analysis_period_days": days,
                "category": category or "all_categories",
                "trending_searches": trending_searches,
                "trending_products": trending_products,
                "emerging_trends": emerging_trends,
                "trend_insights": await self._generate_trend_insights(
                    trending_searches, trending_products, emerging_trends
                ),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trending insights analysis failed: {e}")
            return {"error": "Trending insights analysis failed"}
    
    # Private recommendation methods
    
    async def _collaborative_filtering_recommendations(
        self,
        request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on similar users"""
        try:
            # Get similar users
            similar_users = await user_behavior_service.get_similar_users(
                request.user_id, 
                limit=20
            )
            
            if not similar_users:
                # Fallback to popular products
                return await self._get_popular_products(request.limit)
            
            # Get products that similar users liked/purchased
            similar_user_ids = [user["user_id"] for user in similar_users]
            
            # Get their purchase/view history
            user_product_scores = defaultdict(float)
            
            for similar_user in similar_users:
                similarity_score = similar_user["similarity_score"]
                user_id = similar_user["user_id"]
                
                # Get user's interactions (simplified - would normally use more sophisticated scoring)
                user_interactions = await self._get_user_product_interactions(user_id)
                
                for interaction in user_interactions:
                    product_id = interaction["product_id"]
                    interaction_score = self._calculate_interaction_score(interaction)
                    user_product_scores[product_id] += similarity_score * interaction_score
            
            # Sort by score and get product details
            top_products = sorted(
                user_product_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:request.limit * 2]
            
            # Get product details
            product_ids = [product_id for product_id, _ in top_products]
            products = await self._get_products_by_ids(product_ids)
            
            return products[:request.limit]
            
        except Exception as e:
            logger.error(f"Collaborative filtering failed: {e}")
            return await self._get_popular_products(request.limit)
    
    async def _content_based_recommendations(
        self,
        request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on product content similarity"""
        try:
            # Get user's interaction history to understand preferences
            user_interactions = await self._get_user_product_interactions(request.user_id)
            
            if not user_interactions:
                return await self._get_popular_products(request.limit)
            
            # Get recently interacted products
            recent_products = [
                interaction["product_id"] 
                for interaction in user_interactions[-10:]  # Last 10 interactions
            ]
            
            all_similar_products = []
            
            # Find products similar to each recently interacted product
            for product_id in recent_products:
                try:
                    # Use vector similarity if available
                    product_embedding = await self.vector_service.get_product_embedding(product_id)
                    
                    if product_embedding:
                        similar_products = await self.vector_service.search_similar(
                            query_vector=product_embedding,
                            collection_name="products",
                            limit=10,
                            score_threshold=0.5,
                            exclude_ids=[product_id] + request.exclude_products
                        )
                        all_similar_products.extend(similar_products)
                    else:
                        # Fallback to category-based similarity
                        category_similar = await self._get_category_similar_products(
                            product_id, 10
                        )
                        all_similar_products.extend(category_similar)
                        
                except Exception as ve:
                    logger.warning(f"Vector similarity failed for {product_id}: {ve}")
                    # Fallback to category-based
                    category_similar = await self._get_category_similar_products(
                        product_id, 10
                    )
                    all_similar_products.extend(category_similar)
            
            # Remove duplicates and score
            product_scores = defaultdict(float)
            for product in all_similar_products:
                product_id = product.get("id")
                similarity_score = product.get("score", 0.5)
                product_scores[product_id] += similarity_score
            
            # Sort by score
            top_products = sorted(
                product_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:request.limit]
            
            # Get full product details
            product_ids = [product_id for product_id, _ in top_products]
            return await self._get_products_by_ids(product_ids)
            
        except Exception as e:
            logger.error(f"Content-based recommendations failed: {e}")
            return await self._get_popular_products(request.limit)
    
    async def _trending_recommendations(
        self,
        request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on trending products"""
        try:
            # Get trending products from recent activity
            trending_data = await self._get_trending_products(
                datetime.now() - timedelta(days=7)
            )
            
            if not trending_data:
                return await self._get_popular_products(request.limit)
            
            # Filter by user's preferred categories if available
            user_preferences = await user_behavior_service.get_user_preferences(request.user_id)
            
            if user_preferences and user_preferences.preferred_categories:
                trending_data = [
                    product for product in trending_data
                    if product.get("category") in user_preferences.preferred_categories
                ]
            
            return trending_data[:request.limit]
            
        except Exception as e:
            logger.error(f"Trending recommendations failed: {e}")
            return await self._get_popular_products(request.limit)
    
    async def _hybrid_recommendations(
        self,
        request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Generate hybrid recommendations combining multiple approaches"""
        try:
            # Get recommendations from different algorithms
            collaborative_recs = await self._collaborative_filtering_recommendations(request)
            content_recs = await self._content_based_recommendations(request)
            trending_recs = await self._trending_recommendations(request)
            popular_recs = await self._get_popular_products(request.limit)
            
            # Combine and weight recommendations
            all_recommendations = []
            
            # Add collaborative filtering recommendations
            for rec in collaborative_recs[:int(request.limit * self.collaborative_weight)]:
                rec["recommendation_source"] = "collaborative"
                rec["source_weight"] = self.collaborative_weight
                all_recommendations.append(rec)
            
            # Add content-based recommendations
            for rec in content_recs[:int(request.limit * self.content_weight)]:
                rec["recommendation_source"] = "content"
                rec["source_weight"] = self.content_weight
                all_recommendations.append(rec)
            
            # Add trending recommendations
            for rec in trending_recs[:int(request.limit * self.trend_weight)]:
                rec["recommendation_source"] = "trending"
                rec["source_weight"] = self.trend_weight
                all_recommendations.append(rec)
            
            # Add popular recommendations
            for rec in popular_recs[:int(request.limit * self.popularity_weight)]:
                rec["recommendation_source"] = "popular"
                rec["source_weight"] = self.popularity_weight
                all_recommendations.append(rec)
            
            # Remove duplicates (keep highest weighted)
            seen_products = set()
            final_recommendations = []
            
            # Sort by source weight to prioritize higher-weighted sources
            all_recommendations.sort(key=lambda x: x.get("source_weight", 0), reverse=True)
            
            for rec in all_recommendations:
                product_id = rec.get("id")
                if product_id not in seen_products:
                    seen_products.add(product_id)
                    final_recommendations.append(rec)
                    
                    if len(final_recommendations) >= request.limit:
                        break
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Hybrid recommendations failed: {e}")
            return await self._get_popular_products(request.limit)
    
    async def _category_based_recommendations(
        self,
        request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on category preferences"""
        try:
            # Get user's preferred categories
            categories = request.include_categories
            
            if not categories:
                # Get from user preferences
                user_preferences = await user_behavior_service.get_user_preferences(request.user_id)
                if user_preferences:
                    categories = user_preferences.preferred_categories[:3]  # Top 3 categories
            
            if not categories:
                # Fallback to popular products
                return await self._get_popular_products(request.limit)
            
            # Get top products from preferred categories
            category_products = []
            products_per_category = max(1, request.limit // len(categories))
            
            for category in categories:
                products = await self._get_top_products_in_category(category, products_per_category)
                category_products.extend(products)
            
            return category_products[:request.limit]
            
        except Exception as e:
            logger.error(f"Category-based recommendations failed: {e}")
            return await self._get_popular_products(request.limit)
    
    async def _price_based_recommendations(
        self,
        request: RecommendationRequest
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on user's price preferences"""
        try:
            # Get user's price preferences
            user_preferences = await user_behavior_service.get_user_preferences(request.user_id)
            
            price_range = request.price_range
            if not price_range and user_preferences:
                # Use user's general price preferences
                general_range = user_preferences.price_ranges.get("general")
                if general_range:
                    price_range = general_range
            
            if not price_range:
                # Analyze user's purchase history to infer price preferences
                price_range = await self._infer_price_preferences(request.user_id)
            
            # Get products in the price range
            if price_range:
                products = await self._get_products_in_price_range(
                    price_range.get("min", 0),
                    price_range.get("max", 1000),
                    request.limit
                )
                return products
            else:
                return await self._get_popular_products(request.limit)
            
        except Exception as e:
            logger.error(f"Price-based recommendations failed: {e}")
            return await self._get_popular_products(request.limit)
    
    # Private helper methods
    
    async def _update_global_search_analytics(
        self,
        search_query: str,
        search_type: str,
        results_count: int,
        had_clicks: bool
    ):
        """Update global search analytics"""
        try:
            # This would typically update daily aggregated analytics
            # For now, we'll just log the search
            logger.debug(f"Global search analytics: {search_query} ({search_type}) -> {results_count} results, clicked: {had_clicks}")
        except Exception as e:
            logger.error(f"Global search analytics update failed: {e}")
    
    async def _get_search_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get search data from database"""
        try:
            query = """
                SELECT * FROM search_history 
                WHERE search_timestamp BETWEEN %s AND %s
                ORDER BY search_timestamp
            """
            
            return await db_manager.execute_query(query, [start_date, end_date])
            
        except Exception as e:
            logger.error(f"Search data retrieval failed: {e}")
            return []
    
    async def _aggregate_search_analytics(
        self,
        search_data: List[Dict[str, Any]],
        aggregation: str
    ) -> Dict[str, Any]:
        """Aggregate search analytics data"""
        try:
            total_searches = len(search_data)
            unique_users = len(set(item["user_id"] for item in search_data))
            
            # Analyze search terms
            search_terms = [item["search_query"] for item in search_data if item["search_query"]]
            term_counts = Counter(search_terms)
            top_search_terms = [
                {"term": term, "count": count} 
                for term, count in term_counts.most_common(20)
            ]
            
            # Analyze search types
            type_counts = Counter(item["search_type"] for item in search_data)
            
            # Calculate click-through rates
            searches_with_clicks = len([
                item for item in search_data 
                if item.get("clicked_products") and len(json.loads(item["clicked_products"])) > 0
            ])
            
            click_through_rate = searches_with_clicks / total_searches if total_searches > 0 else 0
            
            # Zero result searches
            zero_result_searches = len([
                item for item in search_data 
                if item["results_count"] == 0
            ])
            
            return {
                "total_searches": total_searches,
                "unique_users": unique_users,
                "top_search_terms": top_search_terms,
                "search_type_distribution": dict(type_counts),
                "click_through_rate": click_through_rate,
                "zero_result_searches": zero_result_searches,
                "zero_result_rate": zero_result_searches / total_searches if total_searches > 0 else 0,
                "average_results_per_search": statistics.mean([item["results_count"] for item in search_data]) if search_data else 0
            }
            
        except Exception as e:
            logger.error(f"Search analytics aggregation failed: {e}")
            return {}
    
    async def _generate_search_insights(self, search_data: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from search data"""
        try:
            insights = []
            
            if not search_data:
                return insights
            
            # Analyze search patterns
            zero_results = len([item for item in search_data if item["results_count"] == 0])
            zero_rate = zero_results / len(search_data)
            
            if zero_rate > 0.1:
                insights.append(f"High zero-result rate ({zero_rate:.1%}) indicates potential gaps in product catalog")
            
            # Analyze search terms
            search_terms = [item["search_query"] for item in search_data if item["search_query"]]
            if search_terms:
                term_lengths = [len(term.split()) for term in search_terms]
                avg_length = statistics.mean(term_lengths)
                
                if avg_length > 3:
                    insights.append("Users are using detailed search queries - consider improving auto-suggestions")
            
            return insights
            
        except Exception as e:
            logger.error(f"Search insights generation failed: {e}")
            return []
    
    async def _get_user_activity_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get user activity data"""
        try:
            query = """
                SELECT * FROM user_activity 
                WHERE timestamp BETWEEN %s AND %s
                ORDER BY timestamp
            """
            
            return await db_manager.execute_query(query, [start_date, end_date])
            
        except Exception as e:
            logger.error(f"User activity data retrieval failed: {e}")
            return []
    
    async def _aggregate_user_analytics(
        self,
        user_data: List[Dict[str, Any]],
        aggregation: str
    ) -> Dict[str, Any]:
        """Aggregate user analytics data"""
        try:
            total_activities = len(user_data)
            unique_users = len(set(item["user_id"] for item in user_data))
            
            # Activity type distribution
            activity_types = Counter(item["activity_type"] for item in user_data)
            
            # User engagement metrics
            page_views = len([item for item in user_data if item["activity_type"] == "view_product"])
            purchases = len([item for item in user_data if item["activity_type"] == "purchase"])
            
            conversion_rate = purchases / page_views if page_views > 0 else 0
            
            return {
                "total_activities": total_activities,
                "unique_active_users": unique_users,
                "activity_distribution": dict(activity_types),
                "engagement_metrics": {
                    "page_views": page_views,
                    "purchases": purchases,
                    "conversion_rate": conversion_rate
                },
                "average_activities_per_user": total_activities / unique_users if unique_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"User analytics aggregation failed: {e}")
            return {}
    
    async def _get_popular_products(self, limit: int) -> List[Dict[str, Any]]:
        """Get popular products as fallback recommendations"""
        try:
            query = """
                SELECT p.*, COUNT(ua.product_id) as interaction_count
                FROM products p
                LEFT JOIN user_activity ua ON p.id = ua.product_id
                WHERE ua.timestamp >= %s
                GROUP BY p.id
                ORDER BY interaction_count DESC, p.rating DESC
                LIMIT %s
            """
            
            start_date = datetime.now() - timedelta(days=30)
            results = await db_manager.execute_query(query, [start_date, limit])
            
            return results
            
        except Exception as e:
            logger.error(f"Popular products retrieval failed: {e}")
            return []
    
    async def _get_user_product_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's product interactions"""
        try:
            query = """
                SELECT * FROM user_activity 
                WHERE user_id = %s 
                AND product_id IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 100
            """
            
            return await db_manager.execute_query(query, [user_id])
            
        except Exception as e:
            logger.error(f"User product interactions retrieval failed: {e}")
            return []
    
    def _calculate_interaction_score(self, interaction: Dict[str, Any]) -> float:
        """Calculate score for user interaction"""
        activity_type = interaction.get("activity_type", "")
        
        # Different weights for different activities
        scores = {
            "purchase": 1.0,
            "add_to_cart": 0.8,
            "add_to_wishlist": 0.6,
            "view_product": 0.3,
            "search": 0.1
        }
        
        return scores.get(activity_type, 0.1)
    
    async def _get_products_by_ids(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Get product details by IDs"""
        try:
            if not product_ids:
                return []
            
            placeholders = ",".join(["%s"] * len(product_ids))
            query = f"SELECT * FROM products WHERE id IN ({placeholders})"
            
            return await db_manager.execute_query(query, product_ids)
            
        except Exception as e:
            logger.error(f"Products by IDs retrieval failed: {e}")
            return []
    
    async def _generate_recommendation_reasons(
        self,
        request: RecommendationRequest,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate reasons for each recommendation"""
        try:
            reasons = []
            
            for rec in recommendations:
                reason_data = {
                    "product_id": rec.get("id"),
                    "reasons": []
                }
                
                # Check recommendation source
                source = rec.get("recommendation_source", "unknown")
                
                if source == "collaborative":
                    reason_data["reasons"].append("Users with similar tastes also liked this")
                elif source == "content":
                    reason_data["reasons"].append("Similar to products you've viewed")
                elif source == "trending":
                    reason_data["reasons"].append("Trending now")
                elif source == "popular":
                    reason_data["reasons"].append("Popular choice among customers")
                
                # Add category-based reason
                if rec.get("category"):
                    reason_data["reasons"].append(f"From your preferred {rec['category']} category")
                
                # Add price-based reason
                if request.price_range:
                    reason_data["reasons"].append("Within your price range")
                
                reasons.append(reason_data)
            
            return reasons
            
        except Exception as e:
            logger.error(f"Recommendation reasons generation failed: {e}")
            return []
    
    async def _calculate_confidence_scores(
        self,
        request: RecommendationRequest,
        recommendations: List[Dict[str, Any]]
    ) -> List[float]:
        """Calculate confidence scores for recommendations"""
        try:
            scores = []
            
            for rec in recommendations:
                confidence = 0.5  # Base confidence
                
                # Boost confidence based on various factors
                if rec.get("rating", 0) > 4.0:
                    confidence += 0.1
                
                if rec.get("recommendation_source") == "collaborative":
                    confidence += 0.2
                elif rec.get("recommendation_source") == "content":
                    confidence += 0.15
                
                # Boost for user's preferred categories
                # (would check user preferences here)
                
                scores.append(min(confidence, 1.0))
            
            return scores
            
        except Exception as e:
            logger.error(f"Confidence scores calculation failed: {e}")
            return [0.5] * len(recommendations)
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            logger.info("Analytics and Recommendation Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during analytics service cleanup: {e}")

# Global analytics and recommendation service instance
analytics_recommendation_service = AnalyticsRecommendationService()
