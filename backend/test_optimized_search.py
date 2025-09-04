"""
Comprehensive test suite for optimized search service functionality.
Tests indexing, filtering, hybrid search, ranking, and analytics.
"""

import pytest
import asyncio
import time
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import the classes we're testing
from app.services.optimized_search_service import (
    OptimizedSearchService, SearchFilter, RankingConfig, RankingFactor,
    SearchType, SearchMetrics, QueryAnalytics
)
from app.models.schemas import Product, SearchResponse

class TestSearchFilter:
    """Test the SearchFilter class"""
    
    def test_search_filter_creation(self):
        """Test creating search filters with various parameters"""
        filter_obj = SearchFilter(
            categories=["electronics", "clothing"],
            brands=["Apple", "Nike"],
            min_price=10.0,
            max_price=100.0,
            price_ranges=[(10, 50), (100, 200)],
            min_rating=4.0,
            in_stock=True,
            tags=["new", "sale"]
        )
        
        assert filter_obj.categories == ["electronics", "clothing"]
        assert filter_obj.brands == ["Apple", "Nike"]
        assert filter_obj.min_price == 10.0
        assert filter_obj.max_price == 100.0
        assert filter_obj.price_ranges == [(10, 50), (100, 200)]
        assert filter_obj.min_rating == 4.0
        assert filter_obj.in_stock is True
        assert filter_obj.tags == ["new", "sale"]
    
    def test_empty_search_filter(self):
        """Test creating an empty search filter"""
        filter_obj = SearchFilter()
        
        assert filter_obj.categories is None
        assert filter_obj.brands is None
        assert filter_obj.min_price is None
        assert filter_obj.max_price is None

class TestRankingConfig:
    """Test the RankingConfig class"""
    
    def test_default_ranking_config(self):
        """Test default ranking configuration"""
        config = RankingConfig()
        
        assert RankingFactor.SIMILARITY in config.factors
        assert RankingFactor.POPULARITY in config.factors
        assert config.price_preference == "balanced"
        assert config.boost_categories is None
    
    def test_custom_ranking_config(self):
        """Test custom ranking configuration"""
        custom_factors = {
            RankingFactor.SIMILARITY: 0.5,
            RankingFactor.PRICE: 0.3,
            RankingFactor.POPULARITY: 0.2
        }
        
        config = RankingConfig(
            factors=custom_factors,
            price_preference="low",
            boost_categories=["electronics"],
            boost_brands=["Apple", "Samsung"]
        )
        
        assert config.factors == custom_factors
        assert config.price_preference == "low"
        assert config.boost_categories == ["electronics"]
        assert config.boost_brands == ["Apple", "Samsung"]

class TestQueryAnalytics:
    """Test the QueryAnalytics class"""
    
    def test_analytics_initialization(self):
        """Test analytics initialization"""
        analytics = QueryAnalytics(max_history=100)
        
        assert len(analytics.search_history) == 0
        assert len(analytics.performance_stats) == 0
        assert len(analytics.popular_queries) == 0
        assert analytics.max_history == 100
    
    def test_log_search(self):
        """Test logging search metrics"""
        analytics = QueryAnalytics()
        
        metrics = SearchMetrics(
            search_id="test_123",
            search_type=SearchType.TEXT,
            query="test query",
            filters_applied={},
            results_count=10,
            search_time=0.5,
            encoding_time=0.1,
            vector_search_time=0.3,
            ranking_time=0.1,
            timestamp=datetime.now()
        )
        
        analytics.log_search(metrics)
        
        assert len(analytics.search_history) == 1
        assert analytics.popular_queries["test query"] == 1
        assert SearchType.TEXT in analytics.performance_stats
        assert len(analytics.performance_stats[SearchType.TEXT]) == 1
    
    def test_log_failed_search(self):
        """Test logging failed searches"""
        analytics = QueryAnalytics()
        
        analytics.log_failed_search("failed query", "connection error")
        
        assert analytics.failed_queries["failed query:connection error"] == 1
    
    def test_performance_summary(self):
        """Test getting performance summary"""
        analytics = QueryAnalytics()
        
        # Add some test data
        for i in range(5):
            metrics = SearchMetrics(
                search_id=f"test_{i}",
                search_type=SearchType.TEXT,
                query=f"query {i}",
                filters_applied={},
                results_count=10,
                search_time=0.1 * (i + 1),
                encoding_time=0.01,
                vector_search_time=0.08,
                ranking_time=0.01,
                timestamp=datetime.now()
            )
            analytics.log_search(metrics)
        
        summary = analytics.get_performance_summary(hours=24)
        
        assert summary["total_searches"] == 5
        assert "average_search_time" in summary
        assert "search_types" in summary
        assert "popular_queries" in summary

class TestOptimizedSearchService:
    """Test the OptimizedSearchService class"""
    
    @pytest.fixture
    def mock_search_service(self):
        """Create a mock search service for testing"""
        with patch('app.services.optimized_search_service.CLIPService') as mock_clip, \
             patch('app.services.optimized_search_service.VectorService') as mock_vector:
            
            # Setup mocks
            mock_clip_instance = Mock()
            mock_clip.return_value = mock_clip_instance
            
            mock_vector_instance = Mock()
            mock_vector_instance.client = Mock()
            mock_vector.return_value = mock_vector_instance
            
            service = OptimizedSearchService()
            service.clip_service = mock_clip_instance
            service.vector_service = mock_vector_instance
            service.client = mock_vector_instance.client
            
            return service
    
    def test_service_initialization(self, mock_search_service):
        """Test service initialization"""
        service = mock_search_service
        
        assert service.collection_name == "products"
        assert service.default_limit == 20
        assert service.max_limit == 100
        assert service.similarity_threshold == 0.1
        assert isinstance(service.analytics, QueryAnalytics)
    
    @pytest.mark.asyncio
    async def test_build_search_filter(self, mock_search_service):
        """Test building Qdrant filters from SearchFilter objects"""
        service = mock_search_service
        
        # Test with various filter combinations
        search_filter = SearchFilter(
            categories=["electronics"],
            brands=["Apple"],
            min_price=100.0,
            max_price=500.0,
            in_stock=True
        )
        
        qdrant_filter = service._build_search_filter(search_filter)
        
        assert qdrant_filter is not None
        assert hasattr(qdrant_filter, 'must')
        assert len(qdrant_filter.must) > 0  # Should have multiple conditions
    
    @pytest.mark.asyncio
    async def test_build_search_filter_empty(self, mock_search_service):
        """Test building filter with empty SearchFilter"""
        service = mock_search_service
        
        empty_filter = SearchFilter()
        qdrant_filter = service._build_search_filter(empty_filter)
        
        assert qdrant_filter is None
    
    def test_calculate_ranking_score(self, mock_search_service):
        """Test ranking score calculation"""
        service = mock_search_service
        
        product = {
            "id": "test_product",
            "name": "Test Product",
            "price": 100.0,
            "category": "electronics",
            "brand": "Apple",
            "popularity_score": 0.8,
            "created_at": datetime.now().isoformat()
        }
        
        ranking_config = RankingConfig()
        similarity_score = 0.9
        
        final_score = service._calculate_ranking_score(
            product, similarity_score, ranking_config
        )
        
        assert 0.0 <= final_score <= 1.0
        assert isinstance(final_score, float)
    
    def test_calculate_ranking_score_price_preferences(self, mock_search_service):
        """Test ranking score with different price preferences"""
        service = mock_search_service
        
        product = {
            "id": "test_product",
            "price": 100.0,
            "category": "electronics",
            "brand": "Apple",
            "popularity_score": 0.5,
            "created_at": datetime.now().isoformat()
        }
        
        similarity_score = 0.8
        
        # Test low price preference
        low_price_config = RankingConfig(price_preference="low")
        low_score = service._calculate_ranking_score(
            product, similarity_score, low_price_config
        )
        
        # Test high price preference
        high_price_config = RankingConfig(price_preference="high")
        high_score = service._calculate_ranking_score(
            product, similarity_score, high_price_config
        )
        
        # Test balanced preference
        balanced_config = RankingConfig(price_preference="balanced")
        balanced_score = service._calculate_ranking_score(
            product, similarity_score, balanced_config
        )
        
        # All scores should be valid
        assert 0.0 <= low_score <= 1.0
        assert 0.0 <= high_score <= 1.0
        assert 0.0 <= balanced_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_setup_optimized_indexes(self, mock_search_service):
        """Test setting up optimized indexes"""
        service = mock_search_service
        
        # Mock the client methods
        service.client.get_collections.return_value = Mock(collections=[])
        service.client.create_collection = Mock()
        service.client.create_payload_index = Mock()
        
        result = await service.setup_optimized_indexes()
        
        assert result is True
        service.client.create_collection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_hybrid_search_text_only(self, mock_search_service):
        """Test hybrid search with text only"""
        service = mock_search_service
        
        # Mock the dependencies
        service.clip_service.encode_text = AsyncMock(return_value=np.random.rand(512))
        
        # Mock search results
        mock_result = Mock()
        mock_result.score = 0.8
        mock_result.payload = {
            "id": "test_1",
            "name": "Test Product",
            "description": "Test description",
            "price": 99.99,
            "category": "electronics",
            "brand": "TestBrand",
            "image_url": "test.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        service.client.search.return_value = [mock_result]
        
        # Perform search
        result = await service.hybrid_search(
            text_query="test query",
            limit=10
        )
        
        assert isinstance(result, SearchResponse)
        assert len(result.products) == 1
        assert result.products[0].name == "Test Product"
        assert result.query_time > 0
        
        # Verify analytics were logged
        assert len(service.analytics.search_history) == 1
        assert service.analytics.popular_queries["test query"] == 1
    
    @pytest.mark.asyncio
    async def test_hybrid_search_with_filters(self, mock_search_service):
        """Test hybrid search with filters"""
        service = mock_search_service
        
        # Mock the dependencies
        service.clip_service.encode_text = AsyncMock(return_value=np.random.rand(512))
        service.client.search.return_value = []
        
        search_filter = SearchFilter(
            categories=["electronics"],
            min_price=50.0,
            max_price=200.0
        )
        
        result = await service.hybrid_search(
            text_query="laptop",
            search_filter=search_filter,
            limit=20
        )
        
        assert isinstance(result, SearchResponse)
        assert len(result.products) == 0  # Empty mock result
        
        # Verify search was called with filter
        service.client.search.assert_called_once()
        call_args = service.client.search.call_args
        assert call_args[1]['query_filter'] is not None
    
    @pytest.mark.asyncio
    async def test_hybrid_search_invalid_input(self, mock_search_service):
        """Test hybrid search with invalid input"""
        service = mock_search_service
        
        # Test with no query or image
        with pytest.raises(ValueError, match="Either text query or image data must be provided"):
            await service.hybrid_search()
        
        # Test with empty text query
        with pytest.raises(ValueError):
            await service.hybrid_search(text_query="")
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_search_service):
        """Test filtered search without vector similarity"""
        service = mock_search_service
        
        # Mock scroll results
        mock_result = Mock()
        mock_result.payload = {
            "id": "test_1",
            "name": "Filtered Product",
            "description": "Test description",
            "price": 150.0,
            "category": "electronics",
            "brand": "TestBrand",
            "image_url": "test.jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        service.client.scroll.return_value = ([mock_result], None)
        
        search_filter = SearchFilter(categories=["electronics"])
        
        result = await service.search_with_filters(
            search_filter=search_filter,
            limit=10
        )
        
        assert isinstance(result, SearchResponse)
        assert len(result.products) == 1
        assert result.products[0].name == "Filtered Product"
        
        # Verify analytics were logged
        assert len(service.analytics.search_history) == 1
        logged_search = service.analytics.search_history[0]
        assert logged_search.search_type == SearchType.FILTERED
    
    @pytest.mark.asyncio
    async def test_search_with_filters_no_filter(self, mock_search_service):
        """Test filtered search with no filter criteria"""
        service = mock_search_service
        
        empty_filter = SearchFilter()
        
        with pytest.raises(ValueError, match="At least one filter criterion must be specified"):
            await service.search_with_filters(search_filter=empty_filter)
    
    @pytest.mark.asyncio
    async def test_get_search_analytics(self, mock_search_service):
        """Test getting search analytics"""
        service = mock_search_service
        
        # Mock collection info
        mock_collection_info = Mock()
        mock_collection_info.points_count = 1000
        mock_collection_info.config.params.vectors.size = 512
        mock_collection_info.config.params.vectors.distance.value = "Cosine"
        
        service.client.get_collection.return_value = mock_collection_info
        
        # Add some test analytics data
        for i in range(3):
            metrics = SearchMetrics(
                search_id=f"test_{i}",
                search_type=SearchType.TEXT,
                query=f"query {i}",
                filters_applied={},
                results_count=10,
                search_time=0.5,
                encoding_time=0.1,
                vector_search_time=0.3,
                ranking_time=0.1,
                timestamp=datetime.now()
            )
            service.analytics.log_search(metrics)
        
        analytics = await service.get_search_analytics(hours=24)
        
        assert "performance" in analytics
        assert "collection_stats" in analytics
        assert "indexes" in analytics
        assert "search_trends" in analytics
        
        # Check collection stats
        assert analytics["collection_stats"]["total_points"] == 1000
        assert analytics["collection_stats"]["vector_size"] == 512
    
    @pytest.mark.asyncio
    async def test_optimize_collection(self, mock_search_service):
        """Test collection optimization"""
        service = mock_search_service
        
        service.client.update_collection.return_value = {"status": "ok"}
        
        result = await service.optimize_collection()
        
        assert result["status"] == "completed"
        assert "timestamp" in result
        service.client.update_collection.assert_called_once()
    
    def test_get_service_health(self, mock_search_service):
        """Test service health check"""
        service = mock_search_service
        
        # Mock collection info
        mock_collection_info = Mock()
        mock_collection_info.points_count = 500
        
        service.client.get_collection.return_value = mock_collection_info
        
        health = service.get_service_health()
        
        assert health["status"] == "healthy"
        assert health["collection_name"] == "products"
        assert health["total_products"] == 500
        assert "indexes_configured" in health
        assert "clip_model_loaded" in health
        assert "qdrant_connected" in health

class TestIntegration:
    """Integration tests for the complete search pipeline"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_search_flow(self):
        """Test complete search flow from query to results"""
        # This would be a more comprehensive test with real dependencies
        # For now, we'll test the workflow with mocks
        
        with patch('app.services.optimized_search_service.CLIPService') as mock_clip, \
             patch('app.services.optimized_search_service.VectorService') as mock_vector:
            
            # Setup mocks
            mock_clip_instance = Mock()
            mock_clip_instance.encode_text = AsyncMock(return_value=np.random.rand(512))
            mock_clip.return_value = mock_clip_instance
            
            mock_vector_instance = Mock()
            mock_vector_instance.client = Mock()
            mock_vector_instance.client.search.return_value = []
            mock_vector.return_value = mock_vector_instance
            
            # Create service
            service = OptimizedSearchService()
            service.clip_service = mock_clip_instance
            service.vector_service = mock_vector_instance
            service.client = mock_vector_instance.client
            
            # Perform search
            result = await service.hybrid_search(
                text_query="test product",
                limit=10
            )
            
            # Verify the flow
            assert isinstance(result, SearchResponse)
            mock_clip_instance.encode_text.assert_called_once_with("test product")
            mock_vector_instance.client.search.assert_called_once()
    
    def test_search_performance_requirements(self):
        """Test that search meets performance requirements"""
        # This would test actual performance metrics
        # For unit tests, we'll verify the structure supports performance monitoring
        
        analytics = QueryAnalytics()
        
        # Simulate some searches with timing
        search_times = [0.1, 0.15, 0.08, 0.12, 0.09]
        
        for i, search_time in enumerate(search_times):
            metrics = SearchMetrics(
                search_id=f"perf_test_{i}",
                search_type=SearchType.HYBRID,
                query=f"perf query {i}",
                filters_applied={},
                results_count=20,
                search_time=search_time,
                encoding_time=0.02,
                vector_search_time=search_time - 0.02,
                ranking_time=0.01,
                timestamp=datetime.now()
            )
            analytics.log_search(metrics)
        
        summary = analytics.get_performance_summary(hours=1)
        avg_time = summary["average_search_time"]
        
        # Verify average search time is reasonable (< 200ms)
        assert avg_time < 0.2
        assert summary["total_searches"] == 5

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
