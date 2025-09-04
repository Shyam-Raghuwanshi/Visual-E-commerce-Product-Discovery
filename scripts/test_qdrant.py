#!/usr/bin/env python3
"""
Test script to verify Qdrant database setup and functionality
Run this after setting up the database to ensure everything works correctly
"""

import asyncio
import sys
import os
import numpy as np
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from setup_qdrant import QdrantDatabaseManager, ProductData
from qdrant_utils import QdrantUtilities

async def test_database_setup():
    """
    Comprehensive test of database setup and functionality
    """
    print("🧪 Visual E-commerce Product Discovery - Database Test")
    print("=" * 60)
    
    # Test results tracking
    tests_passed = 0
    tests_total = 0
    
    def test_result(test_name: str, success: bool, details: str = ""):
        nonlocal tests_passed, tests_total
        tests_total += 1
        if success:
            tests_passed += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
    
    # Initialize database manager
    db_manager = QdrantDatabaseManager()
    
    # Test 1: Database Connection
    print("\n🔌 Testing Database Connection...")
    connection_success = await db_manager.connect()
    test_result(
        "Database Connection", 
        connection_success,
        f"Connected to {db_manager.url}" if connection_success else "Failed to connect"
    )
    
    if not connection_success:
        print("\n❌ Cannot proceed without database connection")
        print("💡 Make sure Qdrant is running: cd docker && docker-compose up -d qdrant")
        return False
    
    # Test 2: Collection Creation
    print("\n📊 Testing Collection Creation...")
    collection_success = await db_manager.create_collection(recreate=False)
    test_result(
        "Collection Creation", 
        collection_success,
        f"Collection '{db_manager.collection_name}' ready"
    )
    
    # Test 3: Index Setup
    print("\n🔍 Testing Index Setup...")
    index_success = await db_manager.setup_indexes()
    test_result(
        "Index Setup", 
        index_success,
        "Payload indexes configured"
    )
    
    # Test 4: Health Check
    print("\n🏥 Testing Health Check...")
    health_info = await db_manager.health_check()
    health_success = health_info.get("status") == "healthy"
    test_result(
        "Health Check", 
        health_success,
        f"Status: {health_info.get('status', 'unknown')}"
    )
    
    # Test 5: Sample Data Insertion
    print("\n💾 Testing Data Insertion...")
    
    sample_products = [
        ProductData(
            id="test_001",
            name="Test iPhone 15 Pro",
            description="High-end smartphone with advanced features and camera",
            price=999.99,
            category="electronics",
            brand="Apple",
            image_url="https://example.com/iphone15.jpg",
            embedding=np.random.rand(512).astype(np.float32)
        ),
        ProductData(
            id="test_002",
            name="Test Nike Air Max 270",
            description="Comfortable running shoes with excellent cushioning",
            price=150.00,
            category="sports",
            brand="Nike",
            image_url="https://example.com/airmax270.jpg",
            embedding=np.random.rand(512).astype(np.float32)
        ),
        ProductData(
            id="test_003",
            name="Test Laptop ThinkPad",
            description="Professional business laptop with high performance",
            price=1299.99,
            category="electronics",
            brand="Lenovo",
            image_url="https://example.com/thinkpad.jpg",
            embedding=np.random.rand(512).astype(np.float32)
        ),
        ProductData(
            id="test_004",
            name="Test Organic Cotton T-Shirt",
            description="Comfortable and sustainable cotton t-shirt",
            price=29.99,
            category="clothing",
            brand="EcoWear",
            image_url="https://example.com/tshirt.jpg",
            embedding=np.random.rand(512).astype(np.float32)
        )
    ]
    
    insert_success = await db_manager.bulk_insert_products(sample_products)
    test_result(
        "Data Insertion", 
        insert_success,
        f"Inserted {len(sample_products)} test products"
    )
    
    # Test 6: Vector Search
    print("\n🔎 Testing Vector Search...")
    
    # Test basic search
    query_vector = np.random.rand(512).astype(np.float32)
    search_results = await db_manager.search_similar_products(
        query_vector=query_vector,
        limit=10
    )
    
    basic_search_success = len(search_results) > 0
    test_result(
        "Basic Vector Search", 
        basic_search_success,
        f"Found {len(search_results)} results"
    )
    
    # Test category filtering
    electronics_results = await db_manager.search_similar_products(
        query_vector=query_vector,
        category="electronics",
        limit=10
    )
    
    category_filter_success = all(
        result["payload"]["category"] == "electronics" 
        for result in electronics_results
    ) if electronics_results else True
    
    test_result(
        "Category Filtering", 
        category_filter_success,
        f"Found {len(electronics_results)} electronics products"
    )
    
    # Test price filtering
    budget_results = await db_manager.search_similar_products(
        query_vector=query_vector,
        max_price=100.0,
        limit=10
    )
    
    price_filter_success = all(
        result["payload"]["price"] <= 100.0 
        for result in budget_results
    ) if budget_results else True
    
    test_result(
        "Price Filtering", 
        price_filter_success,
        f"Found {len(budget_results)} products under $100"
    )
    
    # Test 7: Similar Products by ID
    print("\n🔗 Testing Similar Products by ID...")
    
    if search_results:
        first_product_id = search_results[0]["id"]
        similar_results = await db_manager.get_similar_by_id(first_product_id, limit=5)
        
        similar_search_success = len(similar_results) > 0
        test_result(
            "Similar Products by ID", 
            similar_search_success,
            f"Found {len(similar_results)} similar products"
        )
    else:
        test_result("Similar Products by ID", False, "No products available for test")
    
    # Test 8: Collection Information
    print("\n📈 Testing Collection Information...")
    
    collection_info = await db_manager.get_collection_info()
    info_success = bool(collection_info) and collection_info.get("points_count", 0) > 0
    test_result(
        "Collection Information", 
        info_success,
        f"Collection has {collection_info.get('points_count', 0)} points"
    )
    
    # Test 9: Utility Functions
    print("\n🔧 Testing Utility Functions...")
    
    utils = QdrantUtilities(db_manager)
    stats = await utils.get_collection_stats()
    
    stats_success = bool(stats) and stats.get("total_points", 0) > 0
    test_result(
        "Collection Statistics", 
        stats_success,
        f"Stats collected for {stats.get('total_points', 0)} points"
    )
    
    # Test 10: Performance Check
    print("\n⚡ Testing Performance...")
    
    import time
    start_time = time.time()
    
    # Perform multiple searches to test performance
    for _ in range(5):
        await db_manager.search_similar_products(
            query_vector=np.random.rand(512).astype(np.float32),
            limit=20
        )
    
    end_time = time.time()
    avg_search_time = (end_time - start_time) / 5
    
    performance_success = avg_search_time < 1.0  # Should be under 1 second
    test_result(
        "Search Performance", 
        performance_success,
        f"Average search time: {avg_search_time:.3f}s"
    )
    
    # Test Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! Your Qdrant database is ready for production.")
        print("\n✅ Next Steps:")
        print("   1. Start your FastAPI backend: cd ../backend && python main.py")
        print("   2. Start your React frontend: cd ../frontend && npm start")
        print("   3. Begin uploading real product data")
        return True
    else:
        print(f"⚠️ {tests_total - tests_passed} tests failed. Please review the issues above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure Qdrant is running: docker-compose up -d qdrant")
        print("   2. Check network connectivity")
        print("   3. Verify environment variables in .env file")
        return False

async def cleanup_test_data():
    """
    Clean up test data after running tests
    """
    print("\n🧹 Cleaning up test data...")
    
    try:
        db_manager = QdrantDatabaseManager()
        if await db_manager.connect():
            # Delete test products
            test_ids = ["test_001", "test_002", "test_003", "test_004"]
            
            for test_id in test_ids:
                try:
                    db_manager.client.delete(
                        collection_name=db_manager.collection_name,
                        points_selector={"ids": [test_id]}
                    )
                except:
                    pass  # Ignore if already deleted
            
            print("✅ Test data cleaned up")
        else:
            print("⚠️ Could not connect to clean up test data")
    
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import qdrant_client
        import numpy as np
        from dotenv import load_dotenv
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Please install required packages:")
        print("cd scripts && pip install -r requirements.txt")
        sys.exit(1)
    
    # Run the tests
    async def main():
        success = await test_database_setup()
        
        # Ask user if they want to clean up test data
        if success:
            try:
                response = input("\n🗑️ Clean up test data? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    await cleanup_test_data()
            except KeyboardInterrupt:
                print("\n👋 Test completed.")
    
    asyncio.run(main())
