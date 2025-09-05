#!/usr/bin/env python3
"""
Test Script for Demo Scenarios

Quick test to verify all demo scenarios are working correctly.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_demo_scenarios():
    """Test all demo scenarios"""
    print("🧪 Testing Demo Scenarios...")
    
    try:
        from app.services.demo_scenarios_service import DemoScenariosService
        
        demo_service = DemoScenariosService()
        print("✅ Demo service initialized successfully")
        
        # Test 1: Celebrity outfit recreation
        print("\n1. Testing celebrity outfit recreation...")
        celebrity_result = await demo_service.celebrity_outfit_recreation()
        print(f"   ✅ Celebrity: {celebrity_result['celebrity_inspiration']['name']}")
        print(f"   ✅ Found {len(celebrity_result['recreated_outfit'])} pieces")
        
        # Test 2: Budget shopping
        print("\n2. Testing budget-conscious shopping...")
        budget_result = await demo_service.budget_conscious_shopping(
            target_look="casual dress",
            max_budget=100.0
        )
        print(f"   ✅ Found {len(budget_result['budget_products'])} budget options")
        print(f"   ✅ Created {len(budget_result['outfit_combinations'])} combinations")
        
        # Test 3: Sustainable fashion
        print("\n3. Testing sustainable fashion...")
        sustainable_result = await demo_service.sustainable_fashion_alternatives(
            search_query="shirt"
        )
        print(f"   ✅ Found {len(sustainable_result['sustainable_alternatives'])} sustainable options")
        print(f"   ✅ Featured {len(sustainable_result['sustainable_brands_featured'])} sustainable brands")
        
        # Test 4: Size-inclusive search
        print("\n4. Testing size-inclusive search...")
        size_result = await demo_service.size_inclusive_search(
            search_query="dress",
            target_size="L"
        )
        print(f"   ✅ Found {len(size_result['available_products'])} products in size L")
        print(f"   ✅ Size availability: {size_result['size_availability_rate']*100:.1f}%")
        
        # Test 5: Trend forecasting
        print("\n5. Testing trend forecasting...")
        trend_result = await demo_service.trend_forecasting()
        print(f"   ✅ Predicted {len(trend_result['predicted_trends'])} trends")
        print(f"   ✅ Forecast confidence: {trend_result['confidence_level']*100:.1f}%")
        
        print("\n🎉 All demo scenarios tested successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure the backend services are properly set up")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n🌐 Testing API endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API server is running")
            
            # Test demo endpoints
            endpoints = [
                "/api/demo/demo-scenarios/available",
                "/api/demo/demo-scenarios/celebrity-outfits",
                "/api/demo/demo-scenarios/trend-forecasts"
            ]
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"{base_url}{endpoint}", timeout=5)
                    if resp.status_code == 200:
                        print(f"   ✅ {endpoint}")
                    else:
                        print(f"   ⚠️  {endpoint} returned {resp.status_code}")
                except Exception as e:
                    print(f"   ❌ {endpoint} failed: {e}")
        else:
            print("   ❌ API server not responding")
            
    except ImportError:
        print("   ⚠️  requests library not available")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")

def main():
    """Main test function"""
    print("🔍 Demo Scenarios Test Suite")
    print("=" * 50)
    
    # Test demo scenarios
    success = asyncio.run(test_demo_scenarios())
    
    # Test API endpoints
    asyncio.run(test_api_endpoints())
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Demo scenarios are ready!")
        print("\n📋 Next steps:")
        print("1. Start the backend server: cd backend && python main.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Run full demo: python demo_scenarios_showcase.py")
    else:
        print("❌ Demo scenarios need attention")
        print("\n🔧 Troubleshooting:")
        print("1. Check that all backend dependencies are installed")
        print("2. Verify the services are properly configured")
        print("3. Run: cd backend && pip install -r requirements.txt")

if __name__ == "__main__":
    main()
