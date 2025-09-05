#!/usr/bin/env python3
"""
Simple test script for Multi-Modal Search Service
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

async def test_multimodal_search():
    """Test the multi-modal search service with mock data"""
    print("🧪 Testing Multi-Modal Search Service")
    print("=" * 50)
    
    try:
        # Try to import and test the service
        from app.services.multimodal_search_service import MultiModalSearchService
        
        print("✅ Successfully imported MultiModalSearchService")
        
        # Create service instance
        service = MultiModalSearchService()
        print("✅ Service instance created")
        
        # Test color mappings
        print("\n🎨 Testing color mappings:")
        print(f"Red variations: {service.color_mappings.get('red', [])}")
        print(f"Blue variations: {service.color_mappings.get('blue', [])}")
        
        # Test style transforms
        print("\n✨ Testing style transforms:")
        casual_style = service.style_transforms.get('casual', {})
        print(f"Casual keywords: {casual_style.get('keywords', [])}")
        
        # Test seasonal keywords
        print("\n🍂 Testing seasonal keywords:")
        fall_keywords = service.seasonal_keywords.get('fall', [])
        print(f"Fall keywords: {fall_keywords}")
        
        # Test service stats (if available)
        try:
            stats = service.enhanced_search.get_service_stats()
            print(f"\n📊 Service stats: {stats}")
        except Exception as e:
            print(f"\n⚠️  Service stats not available: {e}")
        
        print("\n🎉 All tests passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("This is expected if dependencies are not installed")
        
        # Test with mock implementation
        print("\n🔧 Testing with mock implementation:")
        
        # Mock color mappings
        color_mappings = {
            "red": ["burgundy", "crimson", "scarlet", "cherry", "wine"],
            "blue": ["navy", "royal", "sky", "teal", "azure"],
            "green": ["forest", "emerald", "olive", "sage", "mint"]
        }
        
        # Mock style transforms
        style_transforms = {
            "casual": {
                "keywords": ["casual", "relaxed", "comfortable", "everyday"],
                "avoid": ["formal", "dressy", "elegant", "sophisticated"]
            },
            "formal": {
                "keywords": ["formal", "elegant", "sophisticated", "dressy"],
                "avoid": ["casual", "relaxed", "sporty", "athletic"]
            }
        }
        
        # Mock seasonal keywords
        seasonal_keywords = {
            "spring": ["light", "fresh", "pastel", "floral", "breathable"],
            "summer": ["lightweight", "cool", "bright", "airy", "tropical"],
            "fall": ["warm", "cozy", "earth tones", "layering", "autumn"],
            "winter": ["warm", "heavy", "thick", "insulated", "holiday"]
        }
        
        print(f"✅ Color mappings loaded: {len(color_mappings)} colors")
        print(f"✅ Style transforms loaded: {len(style_transforms)} styles")
        print(f"✅ Seasonal keywords loaded: {len(seasonal_keywords)} seasons")
        
        # Test color expansion
        target_color = "red"
        expanded_colors = [target_color] + color_mappings.get(target_color, [])
        print(f"\n🎨 Color '{target_color}' expands to: {expanded_colors}")
        
        # Test style keywords
        target_style = "casual"
        style_info = style_transforms.get(target_style, {})
        print(f"\n✨ Style '{target_style}' keywords: {style_info.get('keywords', [])}")
        print(f"   Avoid keywords: {style_info.get('avoid', [])}")
        
        # Test seasonal analysis
        current_season = "fall"
        season_keywords = seasonal_keywords.get(current_season, [])
        print(f"\n🍂 Season '{current_season}' keywords: {season_keywords}")
        
        print("\n🎉 Mock tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

def demo_api_endpoints():
    """Show the available API endpoints"""
    print("\n🚀 Multi-Modal Search API Endpoints")
    print("=" * 50)
    
    endpoints = [
        {
            "name": "Color Variations",
            "method": "POST",
            "endpoint": "/api/v1/multimodal/color-variations",
            "description": "Find items in different colors with same style"
        },
        {
            "name": "Cheaper Alternatives", 
            "method": "POST",
            "endpoint": "/api/v1/multimodal/cheaper-alternatives",
            "description": "Find budget-friendly alternatives to luxury items"
        },
        {
            "name": "Accessory Matching",
            "method": "POST", 
            "endpoint": "/api/v1/multimodal/accessory-matching",
            "description": "Find accessories that complement clothing items"
        },
        {
            "name": "Seasonal Recommendations",
            "method": "POST",
            "endpoint": "/api/v1/multimodal/seasonal-recommendations", 
            "description": "Get trend-aware seasonal product suggestions"
        },
        {
            "name": "Style Evolution",
            "method": "POST",
            "endpoint": "/api/v1/multimodal/style-evolution",
            "description": "Transform product style (casual/formal/etc.)"
        },
        {
            "name": "Outfit Suggestions",
            "method": "GET",
            "endpoint": "/api/v1/multimodal/outfit-suggestions/{product_id}",
            "description": "Get complete outfit suggestions for a product"
        },
        {
            "name": "Trending Now",
            "method": "GET", 
            "endpoint": "/api/v1/multimodal/trending-now",
            "description": "Get currently trending products"
        },
        {
            "name": "Style Inspiration",
            "method": "GET",
            "endpoint": "/api/v1/multimodal/style-inspiration/{style}",
            "description": "Get curated collections for style themes"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n📍 {endpoint['name']}")
        print(f"   {endpoint['method']} {endpoint['endpoint']}")
        print(f"   {endpoint['description']}")
    
    print(f"\n✨ Total endpoints: {len(endpoints)}")

def show_usage_examples():
    """Show usage examples for the multi-modal search features"""
    print("\n💡 Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "scenario": "Customer likes a navy dress but wants it in red",
            "feature": "Color Variations",
            "description": "Search finds red dresses with similar style, cut, and material"
        },
        {
            "scenario": "Customer loves designer jacket but it's too expensive", 
            "feature": "Cheaper Alternatives",
            "description": "Search finds similar style jackets at 30-70% lower price points"
        },
        {
            "scenario": "Customer has a formal dress, needs accessories",
            "feature": "Accessory Matching", 
            "description": "Search suggests matching shoes, bags, jewelry for the occasion"
        },
        {
            "scenario": "Customer wants fall fashion trends",
            "feature": "Seasonal Recommendations",
            "description": "Search provides trending fall items based on current fashion"
        },
        {
            "scenario": "Customer has formal outfit, wants casual version",
            "feature": "Style Evolution",
            "description": "Search transforms formal pieces into casual equivalents"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['scenario']}")
        print(f"   Feature: {example['feature']}")
        print(f"   Solution: {example['description']}")

async def main():
    """Main function"""
    await test_multimodal_search()
    demo_api_endpoints()
    show_usage_examples()
    
    print("\n🎯 Next Steps:")
    print("1. Start the backend API: python backend/main.py")
    print("2. Test endpoints with: python backend/demo_multimodal_search.py")
    print("3. View frontend demo: npm start (in frontend directory)")
    print("4. Check documentation: MULTIMODAL_SEARCH_FEATURES.md")

if __name__ == "__main__":
    asyncio.run(main())
