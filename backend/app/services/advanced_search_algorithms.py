"""
Advanced Search Algorithms implementing sophisticated ranking and personalization.
This module provides comprehensive search logic with multiple similarity metrics,
business rules, personalization, and A/B testing capabilities.
"""

import logging
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import asyncio
from collections import defaultdict
import math
import random

logger = logging.getLogger(__name__)

class SimilarityMetric(Enum):
    """Types of similarity metrics available"""
    VISUAL = "visual"
    TEXTUAL = "textual"
    CATEGORICAL = "categorical"
    BEHAVIORAL = "behavioral"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"

class BusinessRule(Enum):
    """Business rules for search ranking"""
    POPULARITY_BOOST = "popularity_boost"
    STOCK_AVAILABILITY = "stock_availability"
    PRICE_COMPETITIVENESS = "price_competitiveness"
    BRAND_PREFERENCE = "brand_preference"
    SEASONAL_RELEVANCE = "seasonal_relevance"
    GEOGRAPHIC_PREFERENCE = "geographic_preference"
    CONVERSION_RATE = "conversion_rate"

class RankingAlgorithm(Enum):
    """Different ranking algorithms for A/B testing"""
    SIMILARITY_FIRST = "similarity_first"
    BUSINESS_FIRST = "business_first"
    BALANCED = "balanced"
    PERSONALIZED = "personalized"
    GEOGRAPHIC = "geographic"
    EXPERIMENTAL = "experimental"

@dataclass
class UserProfile:
    """User profile for personalized search"""
    user_id: str
    age_group: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    preferences: Dict[str, float] = field(default_factory=dict)
    purchase_history: List[str] = field(default_factory=list)
    search_history: List[str] = field(default_factory=list)
    viewed_products: List[str] = field(default_factory=list)
    price_sensitivity: float = 0.5  # 0=price-insensitive, 1=very price-sensitive
    brand_loyalty: Dict[str, float] = field(default_factory=dict)
    category_preferences: Dict[str, float] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeographicContext:
    """Geographic context for localized search"""
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    currency: str = "USD"
    language: str = "en"
    shipping_zones: List[str] = field(default_factory=list)

@dataclass
class SearchContext:
    """Complete search context including user, geography, and session data"""
    query: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    geographic_context: Optional[GeographicContext] = None
    session_id: Optional[str] = None
    device_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    ab_test_group: Optional[str] = None
    search_intent: Optional[str] = None  # "browse", "purchase", "research"

@dataclass
class ProductScore:
    """Comprehensive product scoring"""
    product_id: str
    base_similarity: float
    visual_similarity: float = 0.0
    textual_similarity: float = 0.0
    categorical_similarity: float = 0.0
    business_score: float = 0.0
    personalization_score: float = 0.0
    geographic_score: float = 0.0
    final_score: float = 0.0
    rank: int = 0
    explanation: Dict[str, Any] = field(default_factory=dict)

class SimilarityCalculator:
    """Advanced similarity calculation with multiple metrics"""
    
    def __init__(self):
        self.metric_weights = {
            SimilarityMetric.VISUAL: 0.4,
            SimilarityMetric.TEXTUAL: 0.3,
            SimilarityMetric.CATEGORICAL: 0.2,
            SimilarityMetric.BEHAVIORAL: 0.1
        }
    
    def calculate_visual_similarity(
        self,
        query_embedding: np.ndarray,
        product_embedding: np.ndarray
    ) -> float:
        """Calculate visual similarity using cosine similarity with improvements"""
        try:
            # Cosine similarity
            cosine_sim = np.dot(query_embedding, product_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(product_embedding)
            )
            
            # Apply non-linear transformation to spread scores
            enhanced_sim = 1 / (1 + np.exp(-10 * (cosine_sim - 0.5)))
            
            return float(np.clip(enhanced_sim, 0, 1))
        except Exception as e:
            logger.error(f"Error calculating visual similarity: {e}")
            return 0.0
    
    def calculate_textual_similarity(
        self,
        query_text: str,
        product_text: str,
        product_metadata: Dict[str, Any]
    ) -> float:
        """Calculate textual similarity with semantic understanding"""
        try:
            # Basic text similarity (would use actual embeddings in practice)
            query_tokens = set(query_text.lower().split())
            product_tokens = set(product_text.lower().split())
            
            # Jaccard similarity
            intersection = len(query_tokens.intersection(product_tokens))
            union = len(query_tokens.union(product_tokens))
            jaccard_sim = intersection / union if union > 0 else 0
            
            # Boost for exact matches in title
            title_boost = 0.0
            if query_text.lower() in product_metadata.get("name", "").lower():
                title_boost = 0.3
            
            # Boost for brand matches
            brand_boost = 0.0
            for token in query_tokens:
                if token in product_metadata.get("brand", "").lower():
                    brand_boost = 0.2
                    break
            
            # Boost for category matches
            category_boost = 0.0
            for token in query_tokens:
                if token in product_metadata.get("category", "").lower():
                    category_boost = 0.1
                    break
            
            final_sim = min(1.0, jaccard_sim + title_boost + brand_boost + category_boost)
            return final_sim
            
        except Exception as e:
            logger.error(f"Error calculating textual similarity: {e}")
            return 0.0
    
    def calculate_categorical_similarity(
        self,
        query_context: SearchContext,
        product_metadata: Dict[str, Any]
    ) -> float:
        """Calculate categorical similarity based on product attributes"""
        try:
            similarity_score = 0.0
            
            # Category hierarchy similarity
            if query_context.query:
                query_tokens = set(query_context.query.lower().split())
                product_category = product_metadata.get("category", "").lower()
                
                # Direct category match
                if any(token in product_category for token in query_tokens):
                    similarity_score += 0.4
                
                # Sub-category match
                product_subcategory = product_metadata.get("subcategory", "").lower()
                if any(token in product_subcategory for token in query_tokens):
                    similarity_score += 0.3
                
                # Tags similarity
                product_tags = [tag.lower() for tag in product_metadata.get("tags", [])]
                tag_matches = sum(1 for token in query_tokens if any(token in tag for tag in product_tags))
                similarity_score += min(0.3, tag_matches * 0.1)
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Error calculating categorical similarity: {e}")
            return 0.0
    
    def calculate_behavioral_similarity(
        self,
        user_profile: Optional[UserProfile],
        product_metadata: Dict[str, Any]
    ) -> float:
        """Calculate similarity based on user behavior patterns"""
        try:
            if not user_profile:
                return 0.5  # Neutral score for anonymous users
            
            similarity_score = 0.0
            
            # Purchase history similarity
            product_category = product_metadata.get("category", "")
            if product_category in user_profile.category_preferences:
                similarity_score += user_profile.category_preferences[product_category] * 0.4
            
            # Brand loyalty
            product_brand = product_metadata.get("brand", "")
            if product_brand in user_profile.brand_loyalty:
                similarity_score += user_profile.brand_loyalty[product_brand] * 0.3
            
            # Price range preference
            product_price = product_metadata.get("price", 0)
            user_avg_price = user_profile.preferences.get("avg_price", 100)
            price_diff = abs(product_price - user_avg_price) / max(user_avg_price, 1)
            price_similarity = 1 / (1 + price_diff)
            similarity_score += price_similarity * 0.3
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Error calculating behavioral similarity: {e}")
            return 0.5

class BusinessLogicEngine:
    """Engine for applying business rules and logic"""
    
    def __init__(self):
        self.rule_weights = {
            BusinessRule.POPULARITY_BOOST: 0.2,
            BusinessRule.STOCK_AVAILABILITY: 0.25,
            BusinessRule.PRICE_COMPETITIVENESS: 0.15,
            BusinessRule.BRAND_PREFERENCE: 0.1,
            BusinessRule.CONVERSION_RATE: 0.15,
            BusinessRule.GEOGRAPHIC_PREFERENCE: 0.1,
            BusinessRule.SEASONAL_RELEVANCE: 0.05
        }
    
    def apply_popularity_boost(
        self,
        product_metadata: Dict[str, Any],
        context: SearchContext
    ) -> float:
        """Apply popularity-based boost"""
        try:
            popularity_score = product_metadata.get("popularity_score", 0.5)
            view_count = product_metadata.get("view_count", 0)
            purchase_count = product_metadata.get("purchase_count", 0)
            rating = product_metadata.get("rating", 3.0)
            review_count = product_metadata.get("review_count", 0)
            
            # Normalize popularity metrics
            normalized_views = min(1.0, view_count / 10000)  # Assume 10k views is max
            normalized_purchases = min(1.0, purchase_count / 1000)  # Assume 1k purchases is max
            normalized_rating = (rating - 1) / 4  # Convert 1-5 to 0-1
            normalized_reviews = min(1.0, review_count / 500)  # Assume 500 reviews is good
            
            # Weighted combination
            boost = (
                popularity_score * 0.3 +
                normalized_views * 0.2 +
                normalized_purchases * 0.3 +
                normalized_rating * 0.15 +
                normalized_reviews * 0.05
            )
            
            return boost
            
        except Exception as e:
            logger.error(f"Error applying popularity boost: {e}")
            return 0.5
    
    def apply_stock_availability(
        self,
        product_metadata: Dict[str, Any],
        context: SearchContext
    ) -> float:
        """Apply stock availability logic"""
        try:
            in_stock = product_metadata.get("in_stock", True)
            stock_level = product_metadata.get("stock_level", 100)
            
            if not in_stock:
                return 0.1  # Heavy penalty for out-of-stock
            
            # Boost items with good stock levels
            if stock_level > 50:
                return 1.0
            elif stock_level > 10:
                return 0.8
            elif stock_level > 0:
                return 0.6
            else:
                return 0.2
                
        except Exception as e:
            logger.error(f"Error applying stock availability: {e}")
            return 0.5
    
    def apply_price_competitiveness(
        self,
        product_metadata: Dict[str, Any],
        context: SearchContext
    ) -> float:
        """Apply price competitiveness logic"""
        try:
            product_price = product_metadata.get("price", 0)
            original_price = product_metadata.get("original_price", product_price)
            category_avg_price = product_metadata.get("category_avg_price", product_price)
            
            # Discount factor
            discount_factor = 0.0
            if original_price > product_price:
                discount_factor = (original_price - product_price) / original_price
            
            # Price competitiveness vs category average
            price_competitiveness = 0.5
            if category_avg_price > 0:
                if product_price < category_avg_price:
                    price_competitiveness = 0.7 + (category_avg_price - product_price) / category_avg_price * 0.3
                else:
                    price_competitiveness = 0.7 - (product_price - category_avg_price) / category_avg_price * 0.3
            
            # Combine discount and competitiveness
            final_score = min(1.0, price_competitiveness + discount_factor * 0.3)
            
            return max(0.1, final_score)
            
        except Exception as e:
            logger.error(f"Error applying price competitiveness: {e}")
            return 0.5
    
    def apply_conversion_rate_boost(
        self,
        product_metadata: Dict[str, Any],
        context: SearchContext
    ) -> float:
        """Apply conversion rate boost"""
        try:
            conversion_rate = product_metadata.get("conversion_rate", 0.05)
            add_to_cart_rate = product_metadata.get("add_to_cart_rate", 0.1)
            return_rate = product_metadata.get("return_rate", 0.1)
            
            # Normalize rates
            normalized_conversion = min(1.0, conversion_rate / 0.2)  # 20% is excellent
            normalized_cart = min(1.0, add_to_cart_rate / 0.3)  # 30% is good
            penalty_returns = max(0.0, 1.0 - return_rate / 0.1)  # 10% return rate is acceptable
            
            boost = (normalized_conversion * 0.5 + normalized_cart * 0.3 + penalty_returns * 0.2)
            
            return boost
            
        except Exception as e:
            logger.error(f"Error applying conversion rate boost: {e}")
            return 0.5
    
    def apply_geographic_relevance(
        self,
        product_metadata: Dict[str, Any],
        context: SearchContext
    ) -> float:
        """Apply geographic relevance scoring"""
        try:
            if not context.geographic_context:
                return 0.5
            
            geo_context = context.geographic_context
            relevance_score = 0.5
            
            # Local availability
            available_regions = product_metadata.get("available_regions", [])
            if geo_context.country in available_regions:
                relevance_score += 0.3
            
            # Shipping cost and time
            shipping_zones = product_metadata.get("shipping_zones", {})
            user_zone = geo_context.shipping_zones[0] if geo_context.shipping_zones else "default"
            
            if user_zone in shipping_zones:
                shipping_info = shipping_zones[user_zone]
                shipping_cost = shipping_info.get("cost", 0)
                shipping_days = shipping_info.get("days", 7)
                
                # Lower cost and faster shipping = higher score
                cost_score = max(0, 1 - shipping_cost / 50)  # Assume $50 is expensive shipping
                speed_score = max(0, 1 - shipping_days / 14)  # Assume 14 days is slow
                
                relevance_score += (cost_score * 0.1 + speed_score * 0.1)
            
            # Local preferences (could be based on regional trends)
            local_popularity = product_metadata.get("regional_popularity", {}).get(geo_context.country, 0.5)
            relevance_score += local_popularity * 0.1
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            logger.error(f"Error applying geographic relevance: {e}")
            return 0.5

class PersonalizationEngine:
    """Advanced personalization engine"""
    
    def __init__(self):
        self.learning_rate = 0.1
        self.decay_factor = 0.95
    
    def calculate_personalization_score(
        self,
        product_metadata: Dict[str, Any],
        user_profile: Optional[UserProfile],
        context: SearchContext
    ) -> float:
        """Calculate comprehensive personalization score"""
        try:
            if not user_profile:
                return 0.5  # Neutral for anonymous users
            
            score = 0.0
            
            # Historical preference alignment
            score += self._calculate_preference_alignment(product_metadata, user_profile) * 0.3
            
            # Behavioral pattern matching
            score += self._calculate_behavioral_match(product_metadata, user_profile) * 0.25
            
            # Session context relevance
            score += self._calculate_session_relevance(product_metadata, user_profile, context) * 0.2
            
            # Collaborative filtering
            score += self._calculate_collaborative_score(product_metadata, user_profile) * 0.15
            
            # Temporal relevance
            score += self._calculate_temporal_relevance(product_metadata, user_profile) * 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating personalization score: {e}")
            return 0.5
    
    def _calculate_preference_alignment(
        self,
        product_metadata: Dict[str, Any],
        user_profile: UserProfile
    ) -> float:
        """Calculate how well product aligns with user preferences"""
        alignment_score = 0.0
        
        # Category preference
        product_category = product_metadata.get("category", "")
        if product_category in user_profile.category_preferences:
            alignment_score += user_profile.category_preferences[product_category] * 0.4
        
        # Brand preference
        product_brand = product_metadata.get("brand", "")
        if product_brand in user_profile.brand_loyalty:
            alignment_score += user_profile.brand_loyalty[product_brand] * 0.3
        
        # Price sensitivity alignment
        product_price = product_metadata.get("price", 0)
        user_avg_price = user_profile.preferences.get("avg_purchase_price", 100)
        
        price_ratio = product_price / max(user_avg_price, 1)
        if user_profile.price_sensitivity > 0.7:  # Price-sensitive user
            price_alignment = 1.0 if price_ratio <= 1.0 else 1.0 / price_ratio
        else:  # Price-insensitive user
            price_alignment = 0.8  # Neutral
        
        alignment_score += price_alignment * 0.3
        
        return alignment_score
    
    def _calculate_behavioral_match(
        self,
        product_metadata: Dict[str, Any],
        user_profile: UserProfile
    ) -> float:
        """Calculate behavioral pattern matching"""
        behavioral_score = 0.0
        
        # Purchase timing patterns
        current_hour = datetime.now().hour
        preferred_hours = user_profile.preferences.get("purchase_hours", [])
        if preferred_hours and current_hour in preferred_hours:
            behavioral_score += 0.2
        
        # Purchase frequency patterns
        product_id = product_metadata.get("id", "")
        if product_id in user_profile.viewed_products:
            behavioral_score += 0.3  # Previously viewed
        
        # Similar product interaction
        product_category = product_metadata.get("category", "")
        category_interaction_count = sum(
            1 for pid in user_profile.purchase_history
            if pid.startswith(product_category)  # Simplified category matching
        )
        
        if category_interaction_count > 0:
            behavioral_score += min(0.5, category_interaction_count * 0.1)
        
        return behavioral_score
    
    def _calculate_session_relevance(
        self,
        product_metadata: Dict[str, Any],
        user_profile: UserProfile,
        context: SearchContext
    ) -> float:
        """Calculate relevance based on current session"""
        session_score = 0.0
        
        # Query intent matching
        if context.search_intent:
            product_intent_score = self._match_search_intent(
                product_metadata, context.search_intent
            )
            session_score += product_intent_score * 0.4
        
        # Device type optimization
        if context.device_type:
            device_score = self._calculate_device_relevance(
                product_metadata, context.device_type
            )
            session_score += device_score * 0.3
        
        # Time-of-day relevance
        current_hour = datetime.now().hour
        time_score = self._calculate_time_relevance(
            product_metadata, current_hour
        )
        session_score += time_score * 0.3
        
        return session_score
    
    def _calculate_collaborative_score(
        self,
        product_metadata: Dict[str, Any],
        user_profile: UserProfile
    ) -> float:
        """Calculate collaborative filtering score"""
        # Simplified collaborative filtering
        # In practice, this would use a pre-computed similarity matrix
        
        product_category = product_metadata.get("category", "")
        product_price_tier = self._get_price_tier(product_metadata.get("price", 0))
        
        # Find similar users based on category preferences and price tier
        similarity_score = 0.5  # Default
        
        # Users who bought similar items also liked...
        if product_category in user_profile.category_preferences:
            category_strength = user_profile.category_preferences[product_category]
            similarity_score += category_strength * 0.3
        
        return similarity_score
    
    def _calculate_temporal_relevance(
        self,
        product_metadata: Dict[str, Any],
        user_profile: UserProfile
    ) -> float:
        """Calculate temporal relevance (seasonal, trending, etc.)"""
        temporal_score = 0.5
        
        # Seasonal relevance
        current_month = datetime.now().month
        seasonal_categories = {
            "winter_clothing": [11, 12, 1, 2],
            "summer_clothing": [5, 6, 7, 8],
            "electronics": list(range(1, 13)),  # Year-round
            "gifts": [11, 12, 2, 5],  # Holiday seasons
        }
        
        product_category = product_metadata.get("category", "")
        for season_cat, months in seasonal_categories.items():
            if season_cat in product_category.lower() and current_month in months:
                temporal_score += 0.3
                break
        
        # Trending boost
        if product_metadata.get("is_trending", False):
            temporal_score += 0.2
        
        return min(1.0, temporal_score)
    
    def _match_search_intent(self, product_metadata: Dict[str, Any], intent: str) -> float:
        """Match product to search intent"""
        intent_scores = {
            "purchase": 0.8 if product_metadata.get("in_stock", True) else 0.2,
            "browse": 0.7,
            "research": 0.6 if product_metadata.get("review_count", 0) > 10 else 0.4,
            "compare": 0.8 if product_metadata.get("specifications") else 0.5
        }
        return intent_scores.get(intent, 0.5)
    
    def _calculate_device_relevance(self, product_metadata: Dict[str, Any], device_type: str) -> float:
        """Calculate device-specific relevance"""
        if device_type == "mobile":
            # Mobile users might prefer quick purchases, lower prices
            price = product_metadata.get("price", 0)
            return 0.8 if price < 100 else 0.6
        elif device_type == "desktop":
            # Desktop users might be doing more research
            return 0.8 if product_metadata.get("specifications") else 0.6
        return 0.7
    
    def _calculate_time_relevance(self, product_metadata: Dict[str, Any], hour: int) -> float:
        """Calculate time-of-day relevance"""
        if 9 <= hour <= 17:  # Business hours
            return 0.8 if product_metadata.get("category") == "business" else 0.6
        elif 18 <= hour <= 22:  # Evening
            return 0.8 if product_metadata.get("category") in ["entertainment", "home"] else 0.6
        return 0.5
    
    def _get_price_tier(self, price: float) -> str:
        """Categorize price into tiers"""
        if price < 25:
            return "budget"
        elif price < 100:
            return "mid"
        elif price < 500:
            return "premium"
        else:
            return "luxury"

class ABTestingFramework:
    """A/B testing framework for ranking algorithms"""
    
    def __init__(self):
        self.test_configurations = {
            RankingAlgorithm.SIMILARITY_FIRST: {
                "similarity_weight": 0.7,
                "business_weight": 0.2,
                "personalization_weight": 0.1
            },
            RankingAlgorithm.BUSINESS_FIRST: {
                "similarity_weight": 0.3,
                "business_weight": 0.5,
                "personalization_weight": 0.2
            },
            RankingAlgorithm.BALANCED: {
                "similarity_weight": 0.4,
                "business_weight": 0.3,
                "personalization_weight": 0.3
            },
            RankingAlgorithm.PERSONALIZED: {
                "similarity_weight": 0.2,
                "business_weight": 0.3,
                "personalization_weight": 0.5
            },
            RankingAlgorithm.GEOGRAPHIC: {
                "similarity_weight": 0.4,
                "business_weight": 0.2,
                "personalization_weight": 0.2,
                "geographic_weight": 0.2
            },
            RankingAlgorithm.EXPERIMENTAL: {
                "similarity_weight": 0.3,
                "business_weight": 0.4,
                "personalization_weight": 0.2,
                "experimental_boost": 0.1
            }
        }
        
        self.active_tests = {}
        self.test_results = defaultdict(list)
    
    def assign_test_group(
        self,
        user_id: Optional[str],
        session_id: str,
        available_algorithms: List[RankingAlgorithm] = None
    ) -> RankingAlgorithm:
        """Assign user to A/B test group"""
        if available_algorithms is None:
            available_algorithms = list(RankingAlgorithm)
        
        # Consistent assignment based on user/session ID
        if user_id:
            hash_input = user_id
        else:
            hash_input = session_id
        
        # Simple hash-based assignment
        hash_value = hash(hash_input) % len(available_algorithms)
        assigned_algorithm = available_algorithms[hash_value]
        
        # Store assignment
        self.active_tests[session_id] = {
            "algorithm": assigned_algorithm,
            "assigned_at": datetime.now(),
            "user_id": user_id
        }
        
        return assigned_algorithm
    
    def get_algorithm_weights(
        self,
        algorithm: RankingAlgorithm,
        context: SearchContext
    ) -> Dict[str, float]:
        """Get weights for the assigned algorithm"""
        base_weights = self.test_configurations.get(algorithm, {})
        
        # Apply contextual modifications
        if context.device_type == "mobile":
            # Mobile users might prefer faster results (similarity-first)
            weights = base_weights.copy()
            weights["similarity_weight"] = weights.get("similarity_weight", 0.4) * 1.2
            weights = self._normalize_weights(weights)
            return weights
        
        return base_weights
    
    def record_interaction(
        self,
        session_id: str,
        product_id: str,
        interaction_type: str,
        position: int,
        timestamp: datetime = None
    ):
        """Record user interaction for A/B test analysis"""
        if session_id not in self.active_tests:
            return
        
        test_info = self.active_tests[session_id]
        interaction_data = {
            "session_id": session_id,
            "algorithm": test_info["algorithm"].value,
            "product_id": product_id,
            "interaction_type": interaction_type,  # "click", "view", "purchase", etc.
            "position": position,
            "timestamp": timestamp or datetime.now()
        }
        
        self.test_results[test_info["algorithm"]].append(interaction_data)
    
    def get_test_performance(
        self,
        algorithm: RankingAlgorithm,
        metric: str = "ctr"  # "ctr", "conversion", "engagement"
    ) -> Dict[str, float]:
        """Get performance metrics for A/B test"""
        results = self.test_results[algorithm]
        if not results:
            return {"metric": 0.0, "sample_size": 0}
        
        if metric == "ctr":
            clicks = sum(1 for r in results if r["interaction_type"] == "click")
            views = len(results)
            return {
                "ctr": clicks / max(views, 1),
                "sample_size": views
            }
        elif metric == "conversion":
            purchases = sum(1 for r in results if r["interaction_type"] == "purchase")
            clicks = sum(1 for r in results if r["interaction_type"] == "click")
            return {
                "conversion_rate": purchases / max(clicks, 1),
                "sample_size": clicks
            }
        
        return {"metric": 0.0, "sample_size": 0}
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1"""
        total = sum(weights.values())
        if total > 0:
            return {k: v / total for k, v in weights.items()}
        return weights

class AdvancedSearchEngine:
    """Main advanced search engine combining all components"""
    
    def __init__(self):
        self.similarity_calculator = SimilarityCalculator()
        self.business_engine = BusinessLogicEngine()
        self.personalization_engine = PersonalizationEngine()
        self.ab_testing = ABTestingFramework()
        
        logger.info("Advanced Search Engine initialized")
    
    async def search_and_rank(
        self,
        query_data: Dict[str, Any],
        candidate_products: List[Dict[str, Any]],
        context: SearchContext
    ) -> List[ProductScore]:
        """Main search and ranking method"""
        try:
            start_time = time.time()
            
            # Assign A/B test group
            if not context.ab_test_group:
                context.ab_test_group = self.ab_testing.assign_test_group(
                    context.user_profile.user_id if context.user_profile else None,
                    context.session_id or f"session_{int(time.time())}"
                ).value
            
            algorithm = RankingAlgorithm(context.ab_test_group)
            weights = self.ab_testing.get_algorithm_weights(algorithm, context)
            
            # Calculate scores for all products
            product_scores = []
            
            for product in candidate_products:
                score = await self._calculate_product_score(
                    query_data, product, context, weights
                )
                product_scores.append(score)
            
            # Sort by final score
            product_scores.sort(key=lambda x: x.final_score, reverse=True)
            
            # Assign ranks
            for i, score in enumerate(product_scores):
                score.rank = i + 1
            
            processing_time = time.time() - start_time
            logger.info(f"Advanced search completed in {processing_time:.3f}s for {len(product_scores)} products")
            
            return product_scores
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return []
    
    async def _calculate_product_score(
        self,
        query_data: Dict[str, Any],
        product: Dict[str, Any],
        context: SearchContext,
        weights: Dict[str, float]
    ) -> ProductScore:
        """Calculate comprehensive score for a single product"""
        try:
            product_id = product.get("id", "unknown")
            
            # Calculate individual scores
            similarity_scores = await self._calculate_similarity_scores(
                query_data, product, context
            )
            
            business_score = self._calculate_business_score(product, context)
            personalization_score = self.personalization_engine.calculate_personalization_score(
                product, context.user_profile, context
            )
            geographic_score = self.business_engine.apply_geographic_relevance(
                product, context
            )
            
            # Combine scores using algorithm weights
            final_score = (
                similarity_scores["overall"] * weights.get("similarity_weight", 0.4) +
                business_score * weights.get("business_weight", 0.3) +
                personalization_score * weights.get("personalization_weight", 0.2) +
                geographic_score * weights.get("geographic_weight", 0.1)
            )
            
            # Apply experimental boost if applicable
            if "experimental_boost" in weights:
                final_score += weights["experimental_boost"]
            
            # Create explanation
            explanation = {
                "algorithm": context.ab_test_group,
                "similarity_breakdown": similarity_scores,
                "business_score": business_score,
                "personalization_score": personalization_score,
                "geographic_score": geographic_score,
                "weights_used": weights,
                "final_calculation": f"({similarity_scores['overall']:.3f} * {weights.get('similarity_weight', 0.4):.3f}) + ({business_score:.3f} * {weights.get('business_weight', 0.3):.3f}) + ({personalization_score:.3f} * {weights.get('personalization_weight', 0.2):.3f}) + ({geographic_score:.3f} * {weights.get('geographic_weight', 0.1):.3f}) = {final_score:.3f}"
            }
            
            return ProductScore(
                product_id=product_id,
                base_similarity=similarity_scores["overall"],
                visual_similarity=similarity_scores["visual"],
                textual_similarity=similarity_scores["textual"],
                categorical_similarity=similarity_scores["categorical"],
                business_score=business_score,
                personalization_score=personalization_score,
                geographic_score=geographic_score,
                final_score=final_score,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Error calculating product score for {product.get('id', 'unknown')}: {e}")
            return ProductScore(
                product_id=product.get("id", "unknown"),
                base_similarity=0.0,
                final_score=0.0
            )
    
    async def _calculate_similarity_scores(
        self,
        query_data: Dict[str, Any],
        product: Dict[str, Any],
        context: SearchContext
    ) -> Dict[str, float]:
        """Calculate all similarity scores"""
        scores = {
            "visual": 0.0,
            "textual": 0.0,
            "categorical": 0.0,
            "behavioral": 0.0,
            "overall": 0.0
        }
        
        try:
            # Visual similarity
            if "query_image_embedding" in query_data and "image_embedding" in product:
                scores["visual"] = self.similarity_calculator.calculate_visual_similarity(
                    query_data["query_image_embedding"],
                    np.array(product["image_embedding"])
                )
            
            # Textual similarity
            if query_data.get("query_text") and product.get("name"):
                combined_text = f"{product.get('name', '')} {product.get('description', '')}"
                scores["textual"] = self.similarity_calculator.calculate_textual_similarity(
                    query_data["query_text"],
                    combined_text,
                    product
                )
            
            # Categorical similarity
            scores["categorical"] = self.similarity_calculator.calculate_categorical_similarity(
                context, product
            )
            
            # Behavioral similarity
            scores["behavioral"] = self.similarity_calculator.calculate_behavioral_similarity(
                context.user_profile, product
            )
            
            # Overall similarity (weighted combination)
            weights = self.similarity_calculator.metric_weights
            scores["overall"] = (
                scores["visual"] * weights[SimilarityMetric.VISUAL] +
                scores["textual"] * weights[SimilarityMetric.TEXTUAL] +
                scores["categorical"] * weights[SimilarityMetric.CATEGORICAL] +
                scores["behavioral"] * weights[SimilarityMetric.BEHAVIORAL]
            )
            
        except Exception as e:
            logger.error(f"Error calculating similarity scores: {e}")
        
        return scores
    
    def _calculate_business_score(
        self,
        product: Dict[str, Any],
        context: SearchContext
    ) -> float:
        """Calculate overall business logic score"""
        try:
            business_scores = {}
            weights = self.business_engine.rule_weights
            
            # Calculate individual business rule scores
            business_scores["popularity"] = self.business_engine.apply_popularity_boost(product, context)
            business_scores["stock"] = self.business_engine.apply_stock_availability(product, context)
            business_scores["price"] = self.business_engine.apply_price_competitiveness(product, context)
            business_scores["conversion"] = self.business_engine.apply_conversion_rate_boost(product, context)
            business_scores["geographic"] = self.business_engine.apply_geographic_relevance(product, context)
            
            # Weighted combination
            overall_score = (
                business_scores["popularity"] * weights[BusinessRule.POPULARITY_BOOST] +
                business_scores["stock"] * weights[BusinessRule.STOCK_AVAILABILITY] +
                business_scores["price"] * weights[BusinessRule.PRICE_COMPETITIVENESS] +
                business_scores["conversion"] * weights[BusinessRule.CONVERSION_RATE] +
                business_scores["geographic"] * weights[BusinessRule.GEOGRAPHIC_PREFERENCE]
            )
            
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating business score: {e}")
            return 0.5
    
    def record_search_interaction(
        self,
        session_id: str,
        product_id: str,
        interaction_type: str,
        position: int
    ):
        """Record user interaction for A/B testing"""
        self.ab_testing.record_interaction(
            session_id, product_id, interaction_type, position
        )
    
    def get_algorithm_performance(self) -> Dict[str, Any]:
        """Get A/B testing performance results"""
        performance = {}
        
        for algorithm in RankingAlgorithm:
            performance[algorithm.value] = {
                "ctr": self.ab_testing.get_test_performance(algorithm, "ctr"),
                "conversion": self.ab_testing.get_test_performance(algorithm, "conversion")
            }
        
        return performance
