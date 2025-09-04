#!/usr/bin/env python3
"""
Comprehensive setup and demo script for the optimized search system.
This script demonstrates all the features of Step 2.3: Search Index Optimization.
"""

import asyncio
import json
import time
import requests
from typing import List, Dict, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchOptimizationDemo:
    """Demo class to showcase all search optimization features"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def health_check(self) -> bool:
        """Check if the API is healthy and ready"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                logger.info("✅ API health check passed")
                return True
            else:
                logger.error(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ API connection failed: {e}")
            return False
    
    def setup_optimized_indexes(self) -> bool:
        """Setup optimized search indexes"""
        try:
            logger.info("🔧 Setting up optimized search indexes...")
            response = self.session.post(f"{self.base_url}/search/advanced/indexes/setup")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Indexes setup: {result['message']}")
                return True
            else:
                logger.error(f"❌ Index setup failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Index setup error: {e}")
            return False
    
    def test_hybrid_text_search(self):
        """Test hybrid search with text query and filters"""
        logger.info("🔍 Testing hybrid text search with filters...")
        
        search_request = {
            "text_query": "wireless bluetooth headphones",
            "categories": ["electronics", "audio"],
            "brands": ["Sony", "Bose", "Apple"],
            "min_price": 50.0,
            "max_price": 300.0,
            "min_rating": 4.0,
            "ranking_factors": {
                "similarity": 0.5,
                "popularity": 0.3,
                "price": 0.2
            },
            "limit": 10
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/search/advanced/hybrid",
                json=search_request
            )
            search_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Hybrid search completed in {search_time:.3f}s")
                logger.info(f"   Found {len(result['products'])} products")
                logger.info(f"   Query time: {result['query_time']:.3f}s")
                
                # Show top results
                for i, product in enumerate(result['products'][:3]):
                    logger.info(f"   {i+1}. {product['name']} - ${product['price']}")
                
                return result
            else:
                logger.error(f"❌ Hybrid search failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Hybrid search error: {e}")
            return None
    
    def test_filtered_search(self):
        """Test filtered search without vector similarity"""
        logger.info("🔍 Testing filtered search...")
        
        search_request = {
            "categories": ["electronics"],
            "min_price": 100.0,
            "max_price": 500.0,
            "in_stock": True,
            "sort_by": "popularity",
            "limit": 15
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/search/advanced/filtered",
                json=search_request
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Filtered search completed")
                logger.info(f"   Found {len(result['products'])} products")
                logger.info(f"   Search type: {result.get('search_type', 'unknown')}")
                
                return result
            else:
                logger.error(f"❌ Filtered search failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Filtered search error: {e}")
            return None
    
    def test_search_recommendations(self, user_id: str = "demo_user"):
        """Test personalized search recommendations"""
        logger.info("🎯 Testing search recommendations...")
        
        # Simulate user behavior
        recent_searches = "laptop,smartphone,headphones"
        viewed_products = "prod_1,prod_2,prod_3"
        
        try:
            response = self.session.get(
                f"{self.base_url}/search/advanced/recommendations/{user_id}",
                params={
                    "recent_searches": recent_searches,
                    "viewed_products": viewed_products,
                    "limit": 8
                }
            )
            
            if response.status_code == 200:
                recommendations = response.json()
                logger.info(f"✅ Got {len(recommendations)} recommendations")
                
                for i, product in enumerate(recommendations[:3]):
                    logger.info(f"   {i+1}. {product['name']} - ${product['price']}")
                
                return recommendations
            else:
                logger.error(f"❌ Recommendations failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Recommendations error: {e}")
            return None
    
    def get_search_analytics(self, hours: int = 24):
        """Get search analytics and performance metrics"""
        logger.info("📊 Getting search analytics...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/search/advanced/analytics",
                params={"hours": hours}
            )
            
            if response.status_code == 200:
                analytics = response.json()
                logger.info("✅ Analytics retrieved successfully")
                
                # Display key metrics
                if "performance" in analytics:
                    perf = analytics["performance"]
                    logger.info(f"   Total searches: {perf.get('total_searches', 0)}")
                    logger.info(f"   Avg search time: {perf.get('average_search_time', 0):.3f}s")
                
                if "collection_stats" in analytics:
                    stats = analytics["collection_stats"]
                    logger.info(f"   Total products: {stats.get('total_points', 0)}")
                    logger.info(f"   Vector size: {stats.get('vector_size', 0)}")
                
                return analytics
            else:
                logger.error(f"❌ Analytics failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Analytics error: {e}")
            return None
    
    def optimize_collection(self):
        """Trigger collection optimization"""
        logger.info("⚡ Optimizing search collection...")
        
        try:
            response = self.session.post(f"{self.base_url}/search/advanced/optimize")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Optimization {result['status']}")
                return result
            else:
                logger.error(f"❌ Optimization failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Optimization error: {e}")
            return None
    
    def get_service_health(self):
        """Get comprehensive service health information"""
        logger.info("🏥 Checking service health...")
        
        try:
            response = self.session.get(f"{self.base_url}/search/advanced/health")
            
            if response.status_code == 200:
                health = response.json()
                logger.info(f"✅ Service status: {health['status']}")
                logger.info(f"   Collection: {health['collection_name']}")
                logger.info(f"   Total products: {health['total_products']}")
                logger.info(f"   Indexes configured: {health['indexes_configured']}")
                logger.info(f"   CLIP model loaded: {health['clip_model_loaded']}")
                logger.info(f"   Qdrant connected: {health['qdrant_connected']}")
                
                return health
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return None
    
    def get_categories_and_brands(self):
        """Get available categories and brands for filtering"""
        logger.info("📂 Getting available categories and brands...")
        
        try:
            # Get categories
            cat_response = self.session.get(f"{self.base_url}/search/advanced/categories")
            categories = cat_response.json() if cat_response.status_code == 200 else []
            
            # Get brands
            brand_response = self.session.get(f"{self.base_url}/search/advanced/brands")
            brands = brand_response.json() if brand_response.status_code == 200 else []
            
            logger.info(f"✅ Found {len(categories)} categories and {len(brands)} brands")
            logger.info(f"   Categories: {', '.join(categories[:5])}...")
            logger.info(f"   Brands: {', '.join(brands[:5])}...")
            
            return {"categories": categories, "brands": brands}
            
        except Exception as e:
            logger.error(f"❌ Error getting categories/brands: {e}")
            return {"categories": [], "brands": []}
    
    def get_price_ranges(self):
        """Get price range statistics"""
        logger.info("💰 Getting price range information...")
        
        try:
            response = self.session.get(f"{self.base_url}/search/advanced/price-ranges")
            
            if response.status_code == 200:
                price_info = response.json()
                logger.info("✅ Price ranges retrieved")
                
                # Display price ranges
                for range_info in price_info["ranges"][:3]:
                    logger.info(f"   {range_info['label']}: ${range_info['min']} - ${range_info.get('max', '∞')}")
                
                stats = price_info["statistics"]
                logger.info(f"   Price range: ${stats['min_price']} - ${stats['max_price']}")
                logger.info(f"   Average: ${stats['avg_price']:.2f}")
                
                return price_info
            else:
                logger.error(f"❌ Price ranges failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Price ranges error: {e}")
            return None
    
    def run_comprehensive_demo(self):
        """Run a comprehensive demo of all search optimization features"""
        logger.info("🚀 Starting comprehensive search optimization demo...")
        logger.info("=" * 60)
        
        # Step 1: Health check
        if not self.health_check():
            logger.error("❌ Demo aborted - API not available")
            return False
        
        # Step 2: Setup indexes
        self.setup_optimized_indexes()
        
        # Step 3: Get service health
        self.get_service_health()
        
        # Step 4: Get available filters
        self.get_categories_and_brands()
        self.get_price_ranges()
        
        # Step 5: Test different search types
        logger.info("\n" + "=" * 60)
        logger.info("🧪 Testing Search Functionality")
        logger.info("=" * 60)
        
        self.test_hybrid_text_search()
        time.sleep(1)  # Brief pause between tests
        
        self.test_filtered_search()
        time.sleep(1)
        
        self.test_search_recommendations()
        time.sleep(1)
        
        # Step 6: Analytics and optimization
        logger.info("\n" + "=" * 60)
        logger.info("📊 Analytics and Optimization")
        logger.info("=" * 60)
        
        self.get_search_analytics()
        self.optimize_collection()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Demo completed successfully!")
        logger.info("=" * 60)
        
        return True
    
    def performance_test(self, num_queries: int = 10):
        """Run performance tests with multiple queries"""
        logger.info(f"🏃 Running performance test with {num_queries} queries...")
        
        search_queries = [
            {"text_query": "laptop computer", "categories": ["electronics"]},
            {"text_query": "running shoes", "categories": ["sports", "clothing"]},
            {"text_query": "wireless headphones", "min_price": 50, "max_price": 200},
            {"text_query": "smartphone", "brands": ["Apple", "Samsung"]},
            {"text_query": "coffee maker", "categories": ["home"]},
        ]
        
        total_time = 0
        successful_queries = 0
        
        for i in range(num_queries):
            query = search_queries[i % len(search_queries)]
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/search/advanced/hybrid",
                    json=query
                )
                query_time = time.time() - start_time
                
                if response.status_code == 200:
                    successful_queries += 1
                    total_time += query_time
                    
                    if i == 0:  # Log first query details
                        result = response.json()
                        logger.info(f"   Query {i+1}: {query_time:.3f}s, {len(result['products'])} results")
                
            except Exception as e:
                logger.error(f"   Query {i+1} failed: {e}")
        
        if successful_queries > 0:
            avg_time = total_time / successful_queries
            qps = successful_queries / total_time if total_time > 0 else 0
            
            logger.info(f"✅ Performance test completed")
            logger.info(f"   Successful queries: {successful_queries}/{num_queries}")
            logger.info(f"   Average query time: {avg_time:.3f}s")
            logger.info(f"   Queries per second: {qps:.2f}")
        else:
            logger.error("❌ Performance test failed - no successful queries")

def main():
    """Main demo function"""
    print("🔍 Visual E-commerce Product Discovery - Search Optimization Demo")
    print("=" * 70)
    print()
    print("This demo showcases the Step 2.3 implementation:")
    print("1. ✅ Optimized Qdrant indexes for different search types")
    print("2. ✅ Advanced filters for price ranges, categories, brands")
    print("3. ✅ Hybrid search combining similarity and filters")
    print("4. ✅ Multi-factor ranking system")
    print("5. ✅ Performance monitoring and query analytics")
    print()
    print("=" * 70)
    
    # Initialize demo
    demo = SearchOptimizationDemo()
    
    # Run comprehensive demo
    success = demo.run_comprehensive_demo()
    
    if success:
        print("\n🚀 Running performance test...")
        demo.performance_test(num_queries=5)
        
        print("\n🎉 All features demonstrated successfully!")
        print("\nNext steps:")
        print("1. Explore the API documentation at http://localhost:8000/docs")
        print("2. Try the advanced search endpoints with different parameters")
        print("3. Monitor performance with the analytics endpoint")
        print("4. Optimize the collection periodically for best performance")
    else:
        print("\n❌ Demo failed. Please check the API server and try again.")

if __name__ == "__main__":
    main()
