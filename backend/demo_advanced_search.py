#!/usr/bin/env python3
"""
Advanced Search Algorithms Demo
Demonstrates the capabilities of the sophisticated search algorithms
including similarity metrics, business logic, personalization, and A/B testing
"""

import asyncio
import json
import time
import random
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

# Import our advanced search components
try:
    from app.services.advanced_search_algorithms import (
        AdvancedSearchEngine,
        SearchContext,
        UserProfile,
        GeographicContext,
        SimilarityMetric,
        RankingAlgorithm
    )
    print("✅ Successfully imported advanced search components")
except ImportError as e:
    print(f"❌ Failed to import components: {e}")
    print("Please ensure you're running from the backend directory")
    exit(1)

class AdvancedSearchDemo:
    """Demo class showcasing advanced search capabilities"""
    
    def __init__(self):
        self.engine = AdvancedSearchEngine()
        self.demo_data = self._create_demo_data()
        print("🚀 Advanced Search Demo initialized")
    
    def _create_demo_data(self) -> Dict[str, Any]:
        """Create comprehensive demo data"""
        
        # Demo products with rich metadata
        products = [
            {
                "id": "nike_air_max_1",
                "name": "Nike Air Max 90 Running Shoes",
                "description": "Classic running shoes with air cushioning technology",
                "category": "footwear",
                "subcategory": "running_shoes",
                "brand": "Nike",
                "price": 120,
                "original_price": 150,
                "rating": 4.5,
                "review_count": 1250,
                "popularity_score": 0.85,
                "view_count": 15000,
                "purchase_count": 850,
                "conversion_rate": 0.12,
                "add_to_cart_rate": 0.25,
                "return_rate": 0.08,
                "in_stock": True,
                "stock_level": 75,
                "tags": ["running", "athletic", "cushioned", "breathable"],
                "available_regions": ["US", "CA", "EU"],
                "shipping_zones": {
                    "domestic": {"cost": 0, "days": 2},
                    "international": {"cost": 15, "days": 7}
                },
                "regional_popularity": {"US": 0.9, "CA": 0.8, "EU": 0.7},
                "is_trending": True,
                "image_embedding": np.random.rand(512).tolist()
            },
            {
                "id": "adidas_ultraboost_1",
                "name": "Adidas UltraBoost 22 Running Shoes",
                "description": "Energy-returning running shoes with Boost midsole",
                "category": "footwear",
                "subcategory": "running_shoes",
                "brand": "Adidas",
                "price": 180,
                "original_price": 180,
                "rating": 4.7,
                "review_count": 890,
                "popularity_score": 0.78,
                "view_count": 12000,
                "purchase_count": 720,
                "conversion_rate": 0.15,
                "add_to_cart_rate": 0.28,
                "return_rate": 0.06,
                "in_stock": True,
                "stock_level": 45,
                "tags": ["running", "performance", "energy-return", "premium"],
                "available_regions": ["US", "CA", "EU", "AU"],
                "shipping_zones": {
                    "domestic": {"cost": 0, "days": 1},
                    "international": {"cost": 20, "days": 5}
                },
                "regional_popularity": {"US": 0.85, "CA": 0.9, "EU": 0.95},
                "is_trending": False,
                "image_embedding": np.random.rand(512).tolist()
            },
            {
                "id": "generic_runner_1",
                "name": "Generic Sport Running Shoes",
                "description": "Affordable running shoes for casual runners",
                "category": "footwear",
                "subcategory": "running_shoes",
                "brand": "SportMax",
                "price": 60,
                "original_price": 80,
                "rating": 3.2,
                "review_count": 150,
                "popularity_score": 0.35,
                "view_count": 3000,
                "purchase_count": 180,
                "conversion_rate": 0.06,
                "add_to_cart_rate": 0.15,
                "return_rate": 0.18,
                "in_stock": False,
                "stock_level": 0,
                "tags": ["running", "budget", "basic"],
                "available_regions": ["US"],
                "shipping_zones": {
                    "domestic": {"cost": 8, "days": 5},
                    "international": {"cost": 25, "days": 14}
                },
                "regional_popularity": {"US": 0.4},
                "is_trending": False,
                "image_embedding": np.random.rand(512).tolist()
            },
            {
                "id": "premium_lifestyle_1",
                "name": "Premium Lifestyle Sneakers",
                "description": "Luxury sneakers for style and comfort",
                "category": "footwear",
                "subcategory": "lifestyle",
                "brand": "LuxeFoot",
                "price": 350,
                "original_price": 350,
                "rating": 4.3,
                "review_count": 95,
                "popularity_score": 0.65,
                "view_count": 8000,
                "purchase_count": 120,
                "conversion_rate": 0.18,
                "add_to_cart_rate": 0.22,
                "return_rate": 0.05,
                "in_stock": True,
                "stock_level": 15,
                "tags": ["lifestyle", "luxury", "comfort", "style"],
                "available_regions": ["US", "EU"],
                "shipping_zones": {
                    "domestic": {"cost": 0, "days": 1},
                    "international": {"cost": 30, "days": 3}
                },
                "regional_popularity": {"US": 0.7, "EU": 0.8},
                "is_trending": False,
                "image_embedding": np.random.rand(512).tolist()
            }
        ]
        
        # Demo user profiles
        user_profiles = {
            "runner_enthusiast": UserProfile(
                user_id="user_runner_123",
                category_preferences={"footwear": 0.9, "athletic_wear": 0.8},
                brand_loyalty={"Nike": 0.8, "Adidas": 0.9, "Asics": 0.7},
                price_sensitivity=0.3,  # Not very price sensitive
                preferences={"avg_purchase_price": 160, "purchase_hours": [18, 19, 20]},
                purchase_history=["nike_air_max_prev", "adidas_ultraboost_prev"],
                search_history=["running shoes", "marathon gear", "athletic wear"]
            ),
            "budget_shopper": UserProfile(
                user_id="user_budget_456",
                category_preferences={"footwear": 0.6, "accessories": 0.4},
                brand_loyalty={"SportMax": 0.7, "BudgetBrand": 0.8},
                price_sensitivity=0.9,  # Very price sensitive
                preferences={"avg_purchase_price": 45, "purchase_hours": [12, 13, 14]},
                purchase_history=["budget_shoes_1", "discount_apparel"],
                search_history=["cheap shoes", "discount running gear", "sale items"]
            ),
            "luxury_customer": UserProfile(
                user_id="user_luxury_789",
                category_preferences={"footwear": 0.7, "luxury": 0.9},
                brand_loyalty={"LuxeFoot": 0.9, "PremiumBrand": 0.8},
                price_sensitivity=0.1,  # Price insensitive
                preferences={"avg_purchase_price": 320, "purchase_hours": [10, 11, 15, 16]},
                purchase_history=["luxury_sneakers_1", "premium_accessories"],
                search_history=["luxury sneakers", "designer shoes", "premium footwear"]
            )
        }
        
        # Demo geographic contexts
        geo_contexts = {
            "us_domestic": GeographicContext(
                country="US",
                state="CA",
                city="San Francisco",
                currency="USD",
                language="en",
                shipping_zones=["domestic"]
            ),
            "eu_customer": GeographicContext(
                country="DE",
                city="Berlin",
                currency="EUR",
                language="de",
                shipping_zones=["eu"]
            ),
            "international": GeographicContext(
                country="AU",
                city="Sydney",
                currency="AUD",
                language="en",
                shipping_zones=["international"]
            )
        }
        
        return {
            "products": products,
            "user_profiles": user_profiles,
            "geo_contexts": geo_contexts
        }
    
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_subsection(self, title: str):
        """Print a formatted subsection header"""
        print(f"\n{'-'*40}")
        print(f"📊 {title}")
        print(f"{'-'*40}")
    
    async def demo_similarity_metrics(self):
        """Demonstrate different similarity calculation methods"""
        self.print_section("SIMILARITY METRICS DEMONSTRATION")
        
        query = "running shoes nike"
        
        print(f"🔍 Query: '{query}'")
        print(f"📦 Analyzing {len(self.demo_data['products'])} products...\n")
        
        calculator = self.engine.similarity_calculator
        
        for product in self.demo_data['products']:
            print(f"Product: {product['name']}")
            print(f"Brand: {product['brand']} | Price: ${product['price']} | Rating: {product['rating']}")
            
            # Textual similarity
            product_text = f"{product['name']} {product['description']}"
            textual_sim = calculator.calculate_textual_similarity(query, product_text, product)
            print(f"📝 Textual Similarity: {textual_sim:.3f}")
            
            # Categorical similarity
            context = SearchContext(query=query)
            categorical_sim = calculator.calculate_categorical_similarity(context, product)
            print(f"🏷️  Categorical Similarity: {categorical_sim:.3f}")
            
            # Visual similarity (simulated)
            query_embedding = np.random.rand(512)
            product_embedding = np.array(product['image_embedding'])
            visual_sim = calculator.calculate_visual_similarity(query_embedding, product_embedding)
            print(f"👁️  Visual Similarity: {visual_sim:.3f}")
            
            print()
    
    async def demo_business_logic(self):
        """Demonstrate business logic application"""
        self.print_section("BUSINESS LOGIC DEMONSTRATION")
        
        business_engine = self.engine.business_engine
        context = SearchContext()
        
        for product in self.demo_data['products']:
            print(f"📦 Product: {product['name']}")
            print(f"💰 Price: ${product['price']} | Stock: {product['stock_level']} | Rating: {product['rating']}")
            
            # Apply different business rules
            popularity = business_engine.apply_popularity_boost(product, context)
            stock = business_engine.apply_stock_availability(product, context)
            price_comp = business_engine.apply_price_competitiveness(product, context)
            conversion = business_engine.apply_conversion_rate_boost(product, context)
            
            print(f"🔥 Popularity Boost: {popularity:.3f}")
            print(f"📦 Stock Score: {stock:.3f}")
            print(f"💲 Price Competitiveness: {price_comp:.3f}")
            print(f"📈 Conversion Boost: {conversion:.3f}")
            
            # Overall business score
            weights = business_engine.rule_weights
            overall_business = (
                popularity * weights['popularity_boost'] +
                stock * weights['stock_availability'] +
                price_comp * weights['price_competitiveness'] +
                conversion * weights['conversion_rate']
            )
            print(f"🎯 Overall Business Score: {overall_business:.3f}")
            print()
    
    async def demo_personalization(self):
        """Demonstrate personalization for different user types"""
        self.print_section("PERSONALIZATION DEMONSTRATION")
        
        personalization_engine = self.engine.personalization_engine
        
        for user_type, user_profile in self.demo_data['user_profiles'].items():
            self.print_subsection(f"User Profile: {user_type.replace('_', ' ').title()}")
            
            print(f"👤 User ID: {user_profile.user_id}")
            print(f"💰 Price Sensitivity: {user_profile.price_sensitivity:.1f}")
            print(f"🏷️  Category Preferences: {user_profile.category_preferences}")
            print(f"🏭 Brand Loyalty: {user_profile.brand_loyalty}")
            print()
            
            context = SearchContext(user_profile=user_profile)
            
            for product in self.demo_data['products']:
                personalization_score = personalization_engine.calculate_personalization_score(
                    product, user_profile, context
                )
                
                print(f"  📦 {product['name'][:30]:<30} | Score: {personalization_score:.3f}")
            
            print()
    
    async def demo_geographic_relevance(self):
        """Demonstrate geographic context impact"""
        self.print_section("GEOGRAPHIC RELEVANCE DEMONSTRATION")
        
        business_engine = self.engine.business_engine
        
        for geo_type, geo_context in self.demo_data['geo_contexts'].items():
            self.print_subsection(f"Geographic Context: {geo_type.replace('_', ' ').title()}")
            
            print(f"🌍 Country: {geo_context.country}")
            print(f"💱 Currency: {geo_context.currency}")
            print(f"🚚 Shipping Zones: {geo_context.shipping_zones}")
            print()
            
            context = SearchContext(geographic_context=geo_context)
            
            for product in self.demo_data['products']:
                geo_score = business_engine.apply_geographic_relevance(product, context)
                
                print(f"  📦 {product['name'][:30]:<30} | Geo Score: {geo_score:.3f}")
            
            print()
    
    async def demo_ab_testing(self):
        """Demonstrate A/B testing framework"""
        self.print_section("A/B TESTING FRAMEWORK DEMONSTRATION")
        
        ab_framework = self.engine.ab_testing
        
        # Simulate user assignments
        users = [f"user_{i}" for i in range(1, 11)]
        
        print("👥 User Test Group Assignments:")
        assignments = {}
        for user in users:
            algorithm = ab_framework.assign_test_group(user, f"session_{user}")
            assignments[user] = algorithm
            print(f"  {user}: {algorithm.value}")
        
        print("\n🎯 Algorithm Weight Configurations:")
        for algorithm in RankingAlgorithm:
            weights = ab_framework.get_algorithm_weights(algorithm, SearchContext())
            print(f"  {algorithm.value}:")
            for weight_type, weight_value in weights.items():
                print(f"    {weight_type}: {weight_value:.2f}")
        
        # Simulate interactions and performance tracking
        print("\n📊 Simulating User Interactions:")
        for i, (user, algorithm) in enumerate(assignments.items()):
            session_id = f"session_{user}"
            
            # Simulate different interaction patterns
            if i % 3 == 0:  # User clicks and purchases
                ab_framework.record_interaction(session_id, "product_1", "view", 1)
                ab_framework.record_interaction(session_id, "product_1", "click", 1)
                ab_framework.record_interaction(session_id, "product_1", "purchase", 1)
            elif i % 3 == 1:  # User clicks but doesn't purchase
                ab_framework.record_interaction(session_id, "product_2", "view", 2)
                ab_framework.record_interaction(session_id, "product_2", "click", 2)
            else:  # User only views
                ab_framework.record_interaction(session_id, "product_3", "view", 3)
        
        print("\n📈 Performance Metrics:")
        for algorithm in RankingAlgorithm:
            ctr_data = ab_framework.get_test_performance(algorithm, "ctr")
            conversion_data = ab_framework.get_test_performance(algorithm, "conversion")
            
            print(f"  {algorithm.value}:")
            print(f"    CTR: {ctr_data['ctr']:.3f} (sample: {ctr_data['sample_size']})")
            print(f"    Conversion: {conversion_data['conversion_rate']:.3f} (sample: {conversion_data['sample_size']})")
    
    async def demo_complete_search_ranking(self):
        """Demonstrate complete search and ranking process"""
        self.print_section("COMPLETE SEARCH & RANKING DEMONSTRATION")
        
        # Test different scenarios
        scenarios = [
            {
                "name": "Runner Enthusiast in US",
                "query": {"query_text": "running shoes", "search_type": "text"},
                "user": "runner_enthusiast",
                "geo": "us_domestic"
            },
            {
                "name": "Budget Shopper Searching",
                "query": {"query_text": "cheap athletic shoes", "search_type": "text"},
                "user": "budget_shopper",
                "geo": "us_domestic"
            },
            {
                "name": "Luxury Customer in Europe",
                "query": {"query_text": "premium sneakers", "search_type": "text"},
                "user": "luxury_customer",
                "geo": "eu_customer"
            }
        ]
        
        for scenario in scenarios:
            self.print_subsection(scenario["name"])
            
            # Create search context
            context = SearchContext(
                query=scenario["query"]["query_text"],
                user_profile=self.demo_data["user_profiles"][scenario["user"]],
                geographic_context=self.demo_data["geo_contexts"][scenario["geo"]],
                session_id=f"demo_session_{scenario['name'].replace(' ', '_').lower()}"
            )
            
            print(f"🔍 Query: '{scenario['query']['query_text']}'")
            print(f"👤 User: {scenario['user'].replace('_', ' ').title()}")
            print(f"🌍 Location: {scenario['geo'].replace('_', ' ').title()}")
            print()
            
            # Perform search and ranking
            start_time = time.time()
            results = await self.engine.search_and_rank(
                query_data=scenario["query"],
                candidate_products=self.demo_data["products"],
                context=context
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️  Processing Time: {processing_time:.3f}s")
            print(f"🎯 Algorithm Used: {context.ab_test_group}")
            print(f"📊 Results Count: {len(results)}")
            print()
            
            print("🏆 Ranking Results:")
            for i, score in enumerate(results[:3], 1):  # Show top 3
                product = next(p for p in self.demo_data["products"] if p["id"] == score.product_id)
                print(f"  {i}. {product['name']}")
                print(f"     💰 Price: ${product['price']} | ⭐ Rating: {product['rating']}")
                print(f"     🎯 Final Score: {score.final_score:.3f}")
                print(f"     📊 Breakdown:")
                print(f"       - Similarity: {score.base_similarity:.3f}")
                print(f"       - Business: {score.business_score:.3f}")
                print(f"       - Personalization: {score.personalization_score:.3f}")
                print(f"       - Geographic: {score.geographic_score:.3f}")
                print()
    
    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🚀 Starting Advanced Search Algorithms Demo")
        print("=" * 80)
        
        try:
            await self.demo_similarity_metrics()
            await self.demo_business_logic()
            await self.demo_personalization()
            await self.demo_geographic_relevance()
            await self.demo_ab_testing()
            await self.demo_complete_search_ranking()
            
            print("\n" + "=" * 80)
            print("✅ Advanced Search Demo Completed Successfully!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Demo encountered an error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Main demo function"""
    demo = AdvancedSearchDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    # Run the demo
    print("🎯 Advanced Search Algorithms Demo")
    print("This demo showcases the sophisticated search capabilities including:")
    print("• Multiple similarity metrics (visual, textual, categorical, behavioral)")
    print("• Business logic (popularity, stock, price, conversion optimization)")
    print("• Personalization (user preferences, behavior patterns, context)")
    print("• Geographic relevance (shipping, regional preferences)")
    print("• A/B testing framework (algorithm variants, performance tracking)")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()
