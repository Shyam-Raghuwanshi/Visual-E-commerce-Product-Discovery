"""
Comprehensive test suite for Advanced Search Algorithms
Tests all components including similarity metrics, business logic, personalization, and A/B testing
"""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import time

# Import our advanced search components
from app.services.advanced_search_algorithms import (
    AdvancedSearchEngine,
    SimilarityCalculator,
    BusinessLogicEngine,
    PersonalizationEngine,
    ABTestingFramework,
    SearchContext,
    UserProfile,
    GeographicContext,
    ProductScore,
    SimilarityMetric,
    BusinessRule,
    RankingAlgorithm
)
from app.services.advanced_search_integration import AdvancedSearchIntegration

class TestSimilarityCalculator:
    """Test similarity calculation algorithms"""
    
    def setup_method(self):
        self.calculator = SimilarityCalculator()
    
    def test_visual_similarity_calculation(self):
        """Test visual similarity calculation with embeddings"""
        # Create test embeddings
        query_embedding = np.random.rand(512)
        product_embedding = np.random.rand(512)
        
        # Calculate similarity
        similarity = self.calculator.calculate_visual_similarity(
            query_embedding, product_embedding
        )
        
        assert 0 <= similarity <= 1, "Similarity should be between 0 and 1"
        assert isinstance(similarity, float), "Similarity should be a float"
    
    def test_visual_similarity_identical_embeddings(self):
        """Test that identical embeddings give high similarity"""
        embedding = np.random.rand(512)
        
        similarity = self.calculator.calculate_visual_similarity(embedding, embedding)
        
        assert similarity > 0.9, "Identical embeddings should have very high similarity"
    
    def test_textual_similarity_exact_match(self):
        """Test textual similarity with exact matches"""
        query = "red running shoes"
        product_text = "red running shoes for athletes"
        product_metadata = {
            "name": "Red Running Shoes Premium",
            "brand": "Nike",
            "category": "footwear"
        }
        
        similarity = self.calculator.calculate_textual_similarity(
            query, product_text, product_metadata
        )
        
        assert similarity > 0.7, "Exact match should have high similarity"
    
    def test_textual_similarity_brand_boost(self):
        """Test brand matching boost in textual similarity"""
        query = "nike shoes"
        product_text = "athletic footwear"
        product_metadata = {
            "name": "Athletic Shoes",
            "brand": "Nike",
            "category": "footwear"
        }
        
        similarity = self.calculator.calculate_textual_similarity(
            query, product_text, product_metadata
        )
        
        assert similarity > 0.5, "Brand match should boost similarity"
    
    def test_categorical_similarity(self):
        """Test categorical similarity calculation"""
        context = SearchContext(query="running shoes")
        product_metadata = {
            "category": "footwear",
            "subcategory": "running",
            "tags": ["athletic", "outdoor", "sport"]
        }
        
        similarity = self.calculator.calculate_categorical_similarity(
            context, product_metadata
        )
        
        assert 0 <= similarity <= 1, "Categorical similarity should be between 0 and 1"
    
    def test_behavioral_similarity_with_user_profile(self):
        """Test behavioral similarity with user preferences"""
        user_profile = UserProfile(
            user_id="test_user",
            category_preferences={"footwear": 0.8, "electronics": 0.2},
            brand_loyalty={"Nike": 0.9, "Adidas": 0.7},
            preferences={"avg_price": 150}
        )
        
        product_metadata = {
            "category": "footwear",
            "brand": "Nike",
            "price": 160
        }
        
        similarity = self.calculator.calculate_behavioral_similarity(
            user_profile, product_metadata
        )
        
        assert similarity > 0.5, "Good user-product match should have high behavioral similarity"
    
    def test_behavioral_similarity_anonymous_user(self):
        """Test behavioral similarity for anonymous users"""
        product_metadata = {"category": "footwear", "brand": "Nike", "price": 100}
        
        similarity = self.calculator.calculate_behavioral_similarity(
            None, product_metadata
        )
        
        assert similarity == 0.5, "Anonymous users should get neutral similarity"

class TestBusinessLogicEngine:
    """Test business logic and rules"""
    
    def setup_method(self):
        self.engine = BusinessLogicEngine()
        self.context = SearchContext()
    
    def test_popularity_boost_high_rating(self):
        """Test popularity boost for highly rated products"""
        product_metadata = {
            "popularity_score": 0.8,
            "view_count": 5000,
            "purchase_count": 500,
            "rating": 4.5,
            "review_count": 200
        }
        
        boost = self.engine.apply_popularity_boost(product_metadata, self.context)
        
        assert boost > 0.7, "High-quality products should get significant popularity boost"
    
    def test_popularity_boost_low_rating(self):
        """Test popularity boost for low-rated products"""
        product_metadata = {
            "popularity_score": 0.3,
            "view_count": 100,
            "purchase_count": 5,
            "rating": 2.0,
            "review_count": 10
        }
        
        boost = self.engine.apply_popularity_boost(product_metadata, self.context)
        
        assert boost < 0.5, "Low-quality products should get lower popularity boost"
    
    def test_stock_availability_in_stock(self):
        """Test stock availability for in-stock products"""
        product_metadata = {"in_stock": True, "stock_level": 100}
        
        score = self.engine.apply_stock_availability(product_metadata, self.context)
        
        assert score == 1.0, "High stock items should get maximum score"
    
    def test_stock_availability_out_of_stock(self):
        """Test stock availability for out-of-stock products"""
        product_metadata = {"in_stock": False, "stock_level": 0}
        
        score = self.engine.apply_stock_availability(product_metadata, self.context)
        
        assert score == 0.1, "Out-of-stock items should get very low score"
    
    def test_price_competitiveness_discounted(self):
        """Test price competitiveness for discounted products"""
        product_metadata = {
            "price": 80,
            "original_price": 100,
            "category_avg_price": 90
        }
        
        score = self.engine.apply_price_competitiveness(product_metadata, self.context)
        
        assert score > 0.7, "Discounted products should get high price competitiveness score"
    
    def test_conversion_rate_boost_high_conversion(self):
        """Test conversion rate boost for high-converting products"""
        product_metadata = {
            "conversion_rate": 0.15,  # 15% conversion rate
            "add_to_cart_rate": 0.25,
            "return_rate": 0.05
        }
        
        score = self.engine.apply_conversion_rate_boost(product_metadata, self.context)
        
        assert score > 0.7, "High-converting products should get good boost"
    
    def test_geographic_relevance_domestic_shipping(self):
        """Test geographic relevance for domestic shipping"""
        geo_context = GeographicContext(
            country="US",
            shipping_zones=["domestic"]
        )
        context = SearchContext(geographic_context=geo_context)
        
        product_metadata = {
            "available_regions": ["US", "CA"],
            "shipping_zones": {
                "domestic": {"cost": 5, "days": 2}
            }
        }
        
        score = self.engine.apply_geographic_relevance(product_metadata, context)
        
        assert score > 0.7, "Products with good domestic shipping should score well"

class TestPersonalizationEngine:
    """Test personalization algorithms"""
    
    def setup_method(self):
        self.engine = PersonalizationEngine()
        self.user_profile = UserProfile(
            user_id="test_user",
            category_preferences={"electronics": 0.8, "books": 0.6},
            brand_loyalty={"Apple": 0.9, "Samsung": 0.7},
            price_sensitivity=0.3,  # Not very price sensitive
            preferences={"avg_purchase_price": 200}
        )
        self.context = SearchContext(
            user_profile=self.user_profile,
            search_intent="purchase"
        )
    
    def test_personalization_score_good_match(self):
        """Test personalization score for well-matching product"""
        product_metadata = {
            "category": "electronics",
            "brand": "Apple",
            "price": 250,
            "id": "test_product"
        }
        
        score = self.engine.calculate_personalization_score(
            product_metadata, self.user_profile, self.context
        )
        
        assert score > 0.6, "Well-matching products should get high personalization score"
    
    def test_personalization_score_poor_match(self):
        """Test personalization score for poorly matching product"""
        product_metadata = {
            "category": "clothing",  # User prefers electronics
            "brand": "Unknown Brand",
            "price": 50,
            "id": "test_product_2"
        }
        
        score = self.engine.calculate_personalization_score(
            product_metadata, self.user_profile, self.context
        )
        
        assert score < 0.6, "Poorly matching products should get lower personalization score"
    
    def test_personalization_score_anonymous_user(self):
        """Test personalization score for anonymous users"""
        product_metadata = {
            "category": "electronics",
            "brand": "Apple",
            "price": 200
        }
        
        score = self.engine.calculate_personalization_score(
            product_metadata, None, self.context
        )
        
        assert score == 0.5, "Anonymous users should get neutral personalization score"
    
    def test_preference_alignment(self):
        """Test preference alignment calculation"""
        product_metadata = {
            "category": "electronics",  # User likes electronics (0.8)
            "brand": "Apple",  # User loyal to Apple (0.9)
            "price": 180  # Close to user's average ($200)
        }
        
        alignment = self.engine._calculate_preference_alignment(
            product_metadata, self.user_profile
        )
        
        assert alignment > 0.7, "Good preference alignment should score high"

class TestABTestingFramework:
    """Test A/B testing framework"""
    
    def setup_method(self):
        self.framework = ABTestingFramework()
    
    def test_test_group_assignment_consistency(self):
        """Test that same user gets same test group"""
        user_id = "test_user_123"
        session_id = "session_123"
        
        # Get assignment twice
        assignment1 = self.framework.assign_test_group(user_id, session_id)
        assignment2 = self.framework.assign_test_group(user_id, session_id)
        
        assert assignment1 == assignment2, "Same user should get consistent test group assignment"
    
    def test_algorithm_weights_retrieval(self):
        """Test algorithm weights retrieval"""
        context = SearchContext()
        
        weights = self.framework.get_algorithm_weights(
            RankingAlgorithm.BALANCED, context
        )
        
        assert "similarity_weight" in weights, "Weights should include similarity weight"
        assert "business_weight" in weights, "Weights should include business weight"
        assert "personalization_weight" in weights, "Weights should include personalization weight"
        
        # Check weights sum approximately to 1
        weight_sum = sum(weights.values())
        assert 0.9 <= weight_sum <= 1.1, "Weights should sum to approximately 1"
    
    def test_interaction_recording(self):
        """Test interaction recording for A/B testing"""
        session_id = "test_session"
        user_id = "test_user"
        
        # Assign test group first
        algorithm = self.framework.assign_test_group(user_id, session_id)
        
        # Record interaction
        self.framework.record_interaction(
            session_id=session_id,
            product_id="product_123",
            interaction_type="click",
            position=1
        )
        
        # Check that interaction was recorded
        performance = self.framework.get_test_performance(algorithm, "ctr")
        assert performance["sample_size"] > 0, "Interaction should be recorded"
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation"""
        algorithm = RankingAlgorithm.BALANCED
        session_id = "test_session"
        
        # Assign test group
        self.framework.assign_test_group("test_user", session_id)
        
        # Record some interactions
        interactions = [
            ("product_1", "view", 1),
            ("product_1", "click", 1),
            ("product_2", "view", 2),
            ("product_3", "view", 3),
            ("product_3", "click", 3),
            ("product_3", "purchase", 3)
        ]
        
        for product_id, interaction_type, position in interactions:
            self.framework.record_interaction(session_id, product_id, interaction_type, position)
        
        # Calculate CTR
        ctr_performance = self.framework.get_test_performance(algorithm, "ctr")
        expected_ctr = 2 / 4  # 2 clicks out of 4 views
        
        assert abs(ctr_performance["ctr"] - expected_ctr) < 0.01, f"CTR calculation incorrect: expected {expected_ctr}, got {ctr_performance['ctr']}"
        
        # Calculate conversion rate
        conversion_performance = self.framework.get_test_performance(algorithm, "conversion")
        expected_conversion = 1 / 2  # 1 purchase out of 2 clicks
        
        assert abs(conversion_performance["conversion_rate"] - expected_conversion) < 0.01, "Conversion rate calculation incorrect"

class TestAdvancedSearchEngine:
    """Test the main advanced search engine"""
    
    def setup_method(self):
        self.engine = AdvancedSearchEngine()
        
        # Create test data
        self.query_data = {
            "query_text": "running shoes",
            "search_type": "text"
        }
        
        self.candidate_products = [
            {
                "id": "product_1",
                "name": "Nike Air Max Running Shoes",
                "category": "footwear",
                "brand": "Nike",
                "price": 150,
                "rating": 4.5,
                "popularity_score": 0.8,
                "in_stock": True,
                "stock_level": 50
            },
            {
                "id": "product_2",
                "name": "Adidas UltraBoost Running Shoes",
                "category": "footwear",
                "brand": "Adidas",
                "price": 180,
                "rating": 4.7,
                "popularity_score": 0.9,
                "in_stock": True,
                "stock_level": 30
            },
            {
                "id": "product_3",
                "name": "Generic Running Shoes",
                "category": "footwear",
                "brand": "NoName",
                "price": 80,
                "rating": 3.0,
                "popularity_score": 0.3,
                "in_stock": False,
                "stock_level": 0
            }
        ]
        
        self.context = SearchContext(
            query="running shoes",
            user_profile=UserProfile(
                user_id="test_user",
                category_preferences={"footwear": 0.8},
                brand_loyalty={"Nike": 0.7, "Adidas": 0.8}
            ),
            session_id="test_session"
        )
    
    @pytest.mark.asyncio
    async def test_search_and_rank(self):
        """Test complete search and ranking process"""
        results = await self.engine.search_and_rank(
            self.query_data,
            self.candidate_products,
            self.context
        )
        
        assert len(results) == 3, "Should return all candidate products"
        assert all(isinstance(score, ProductScore) for score in results), "Results should be ProductScore objects"
        
        # Check that results are sorted by final score
        scores = [score.final_score for score in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by final score descending"
        
        # Check that ranks are assigned correctly
        for i, score in enumerate(results):
            assert score.rank == i + 1, f"Rank should be {i + 1}, got {score.rank}"
    
    @pytest.mark.asyncio
    async def test_search_ranking_quality(self):
        """Test that search ranking produces reasonable results"""
        results = await self.engine.search_and_rank(
            self.query_data,
            self.candidate_products,
            self.context
        )
        
        # The out-of-stock product should rank lower
        out_of_stock_score = next(score for score in results if score.product_id == "product_3")
        in_stock_scores = [score for score in results if score.product_id != "product_3"]
        
        assert all(out_of_stock_score.final_score <= score.final_score for score in in_stock_scores), \
            "Out-of-stock products should generally rank lower"
        
        # Higher rated products should generally rank higher (all else being equal)
        adidas_score = next(score for score in results if score.product_id == "product_2")
        nike_score = next(score for score in results if score.product_id == "product_1")
        
        # Adidas has higher rating (4.7 vs 4.5) and popularity (0.9 vs 0.8)
        assert adidas_score.final_score >= nike_score.final_score, \
            "Higher rated and more popular products should rank higher"
    
    def test_interaction_recording(self):
        """Test interaction recording"""
        self.engine.record_search_interaction(
            session_id="test_session",
            product_id="product_1",
            interaction_type="click",
            position=1
        )
        
        # This should not raise an exception
        assert True, "Interaction recording should complete without error"
    
    def test_algorithm_performance_retrieval(self):
        """Test algorithm performance report"""
        performance = self.engine.get_algorithm_performance()
        
        assert isinstance(performance, dict), "Performance should be a dictionary"
        assert len(performance) > 0, "Performance should include algorithm data"

# Integration tests
class TestAdvancedSearchIntegration:
    """Test the integration service"""
    
    def setup_method(self):
        # Mock services
        self.mock_enhanced_search = MockEnhancedSearchService()
        self.mock_vector_service = MockVectorService()
        
        self.integration = AdvancedSearchIntegration(
            self.mock_enhanced_search,
            self.mock_vector_service
        )
    
    @pytest.mark.asyncio
    async def test_advanced_text_search_integration(self):
        """Test advanced text search integration"""
        request = MockSearchRequest(query="test query", limit=10)
        
        result = await self.integration.advanced_text_search(
            request=request,
            user_context={"user_id": "test_user"},
            session_id="test_session"
        )
        
        assert result["success"] == True, "Advanced text search should succeed"
        assert "products" in result, "Result should contain products"
        assert "search_metadata" in result, "Result should contain search metadata"

# Mock classes for testing
class MockSearchRequest:
    def __init__(self, query: str, limit: int = 20, offset: int = 0, category: str = None, filters: Dict = None):
        self.query = query
        self.limit = limit
        self.offset = offset
        self.category = category
        self.filters = filters or {}

class MockEnhancedSearchService:
    async def search_by_text(self, query: str, limit: int, filters: Dict = None):
        return {
            "products": [
                {
                    "id": "mock_product_1",
                    "name": f"Mock Product for {query}",
                    "category": "test_category",
                    "price": 100,
                    "rating": 4.0
                }
            ],
            "total": 1
        }

class MockVectorService:
    async def generate_image_embedding(self, image_data: bytes):
        return np.random.rand(512)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
