#!/usr/bin/env python3
"""
Comprehensive Demo Script for Visual E-commerce Product Discovery

This script demonstrates all five demo scenarios:
1. Celebrity outfit recreation
2. Budget-conscious shopping
3. Sustainable fashion alternatives
4. Size-inclusive search
5. Trend forecasting
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.append('/home/shyam/Desktop/code/Visual-E-commerce-Product-Discovery/backend')

from app.services.demo_scenarios_service import DemoScenariosService

class DemoRunner:
    """Comprehensive demo runner for all scenarios"""
    
    def __init__(self):
        self.demo_service = DemoScenariosService()
        self.results = {}
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
    
    def print_subheader(self, title: str):
        """Print a formatted subheader"""
        print(f"\n--- {title} ---")
    
    def print_results(self, results: Dict[str, Any], scenario_name: str):
        """Print formatted results"""
        print(f"\n✅ {scenario_name} completed successfully!")
        print(f"📊 Results summary:")
        
        # Print key metrics based on scenario type
        if 'celebrity_inspiration' in results:
            print(f"   Celebrity: {results['celebrity_inspiration']['name']}")
            print(f"   Event: {results['celebrity_inspiration']['event']}")
            print(f"   Total Cost: ${results['total_cost']:.2f}")
            print(f"   Pieces Found: {len(results['recreated_outfit'])}")
            print(f"   Completion Rate: {results['completion_rate']*100:.1f}%")
            
        elif 'budget_limit' in results:
            print(f"   Budget Limit: ${results['budget_limit']}")
            print(f"   Options Found: {len(results['budget_products'])}")
            print(f"   Money Saved: ${results['money_saved']:.2f}")
            print(f"   Outfit Combinations: {len(results['outfit_combinations'])}")
            
        elif 'sustainable_alternatives' in results:
            print(f"   Sustainable Options: {len(results['sustainable_alternatives'])}")
            print(f"   Water Saved: {results['eco_impact_summary']['estimated_water_savings_liters']}L")
            print(f"   CO2 Reduced: {results['eco_impact_summary']['estimated_co2_reduction_kg']}kg")
            print(f"   Sustainable Brands: {len(results['sustainable_brands_featured'])}")
            
        elif 'size_availability_rate' in results:
            print(f"   Size Availability: {results['size_availability_rate']*100:.1f}%")
            print(f"   Products Available: {len(results['available_products'])}")
            print(f"   Inclusive Brands: {len(results['inclusive_brands'])}")
            
        elif 'predicted_trends' in results:
            print(f"   Forecast Period: {results['forecast_period']}")
            print(f"   Trends Predicted: {len(results['predicted_trends'])}")
            print(f"   Confidence Level: {results['confidence_level']*100:.1f}%")
    
    async def demo_celebrity_outfit_recreation(self):
        """Demo celebrity outfit recreation"""
        self.print_subheader("Celebrity Outfit Recreation Demo")
        print("🎭 Recreating celebrity red carpet looks...")
        
        # Demo 1: Random celebrity outfit
        print("\n1. Random Celebrity Outfit:")
        result1 = await self.demo_service.celebrity_outfit_recreation()
        self.print_results(result1, "Random Celebrity Outfit")
        
        # Demo 2: Specific celebrity with budget
        print("\n2. Emma Stone with $800 budget:")
        result2 = await self.demo_service.celebrity_outfit_recreation(
            celebrity_name="Emma Stone",
            budget_range={"min": 0, "max": 800}
        )
        self.print_results(result2, "Emma Stone Look")
        
        # Demo 3: Zendaya's futuristic style
        print("\n3. Zendaya's avant-garde style:")
        result3 = await self.demo_service.celebrity_outfit_recreation(
            celebrity_name="Zendaya"
        )
        self.print_results(result3, "Zendaya Look")
        
        return {
            "random_celebrity": result1,
            "emma_stone_budget": result2,
            "zendaya_style": result3
        }
    
    async def demo_budget_conscious_shopping(self):
        """Demo budget-conscious shopping"""
        self.print_subheader("Budget-Conscious Shopping Demo")
        print("💰 Finding luxury looks for less...")
        
        # Demo 1: Elegant evening wear on budget
        print("\n1. Elegant evening wear under $200:")
        result1 = await self.demo_service.budget_conscious_shopping(
            target_look="elegant evening wear",
            max_budget=200.0
        )
        self.print_results(result1, "Evening Wear Budget")
        
        # Demo 2: Professional business attire
        print("\n2. Professional business attire under $300:")
        result2 = await self.demo_service.budget_conscious_shopping(
            target_look="professional business attire",
            max_budget=300.0,
            must_have_pieces=["blazer", "dress pants"]
        )
        self.print_results(result2, "Business Attire Budget")
        
        # Demo 3: Casual weekend style
        print("\n3. Casual weekend style under $150:")
        result3 = await self.demo_service.budget_conscious_shopping(
            target_look="casual weekend style",
            max_budget=150.0,
            style_preferences=["comfortable", "trendy", "versatile"]
        )
        self.print_results(result3, "Weekend Style Budget")
        
        return {
            "evening_wear": result1,
            "business_attire": result2,
            "weekend_style": result3
        }
    
    async def demo_sustainable_fashion(self):
        """Demo sustainable fashion alternatives"""
        self.print_subheader("Sustainable Fashion Demo")
        print("🌱 Finding eco-friendly fashion alternatives...")
        
        # Demo 1: Sustainable dresses
        print("\n1. Sustainable dress alternatives:")
        result1 = await self.demo_service.sustainable_fashion_alternatives(
            search_query="dress",
            sustainability_criteria=["organic", "recycled", "fair trade"]
        )
        self.print_results(result1, "Sustainable Dresses")
        
        # Demo 2: Eco-friendly jeans
        print("\n2. Eco-friendly jeans:")
        result2 = await self.demo_service.sustainable_fashion_alternatives(
            search_query="jeans",
            sustainability_criteria=["organic cotton", "low water usage"]
        )
        self.print_results(result2, "Sustainable Jeans")
        
        # Demo 3: Sustainable accessories
        print("\n3. Sustainable accessories:")
        result3 = await self.demo_service.sustainable_fashion_alternatives(
            search_query="accessories",
            max_price_premium=0.2  # 20% premium acceptable
        )
        self.print_results(result3, "Sustainable Accessories")
        
        return {
            "dresses": result1,
            "jeans": result2,
            "accessories": result3
        }
    
    async def demo_size_inclusive_search(self):
        """Demo size-inclusive search"""
        self.print_subheader("Size-Inclusive Search Demo")
        print("👥 Finding inclusive sizing options...")
        
        # Demo 1: Plus size dresses
        print("\n1. Dresses in size XXL:")
        result1 = await self.demo_service.size_inclusive_search(
            search_query="dress",
            target_size="XXL"
        )
        self.print_results(result1, "XXL Dresses")
        
        # Demo 2: Petite sizing
        print("\n2. Blazers in size XS:")
        result2 = await self.demo_service.size_inclusive_search(
            search_query="blazer",
            target_size="XS",
            body_type_preferences={"preference": "petite_friendly"}
        )
        self.print_results(result2, "XS Blazers")
        
        # Demo 3: Mid-range sizing with alternatives
        print("\n3. Sweaters in size L with alternatives:")
        result3 = await self.demo_service.size_inclusive_search(
            search_query="sweater",
            target_size="L",
            size_range=["M", "L", "XL"]
        )
        self.print_results(result3, "L Sweaters")
        
        return {
            "xxl_dresses": result1,
            "xs_blazers": result2,
            "l_sweaters": result3
        }
    
    async def demo_trend_forecasting(self):
        """Demo trend forecasting"""
        self.print_subheader("Trend Forecasting Demo")
        print("📈 Predicting upcoming fashion trends...")
        
        # Demo 1: Next season trends
        print("\n1. Upcoming season trends:")
        result1 = await self.demo_service.trend_forecasting()
        self.print_results(result1, "Next Season Trends")
        
        # Demo 2: Spring 2025 trends
        print("\n2. Spring 2025 specific trends:")
        result2 = await self.demo_service.trend_forecasting(
            season="Spring",
            year=2025
        )
        self.print_results(result2, "Spring 2025 Trends")
        
        # Demo 3: Fall trends with demographic focus
        print("\n3. Fall trends for young professionals:")
        result3 = await self.demo_service.trend_forecasting(
            season="Fall",
            demographic="young professionals"
        )
        self.print_results(result3, "Fall Professional Trends")
        
        return {
            "next_season": result1,
            "spring_2025": result2,
            "fall_professional": result3
        }
    
    async def run_all_demos(self):
        """Run all demo scenarios"""
        self.print_header("Visual E-commerce Product Discovery - Demo Scenarios")
        print("🚀 Starting comprehensive demo of all scenarios...")
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        try:
            # Run all demos
            print("\n🎯 Running all demo scenarios...")
            
            self.results['celebrity_outfits'] = await self.demo_celebrity_outfit_recreation()
            self.results['budget_shopping'] = await self.demo_budget_conscious_shopping()
            self.results['sustainable_fashion'] = await self.demo_sustainable_fashion()
            self.results['size_inclusive'] = await self.demo_size_inclusive_search()
            self.results['trend_forecasting'] = await self.demo_trend_forecasting()
            
            # Summary
            end_time = time.time()
            total_time = end_time - start_time
            
            self.print_header("Demo Summary")
            print(f"✅ All demos completed successfully!")
            print(f"⏱️  Total execution time: {total_time:.2f} seconds")
            print(f"📊 Scenarios tested: 5")
            print(f"🔍 Individual demos: 15")
            print(f"📁 Results saved to: demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            # Save results to file
            filename = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n🎉 Demo showcase completed! Check the results file for detailed output.")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    async def run_interactive_demo(self):
        """Run interactive demo where user can choose scenarios"""
        self.print_header("Interactive Demo Mode")
        print("Choose demo scenarios to run:")
        print("1. Celebrity Outfit Recreation")
        print("2. Budget-Conscious Shopping")
        print("3. Sustainable Fashion Alternatives")
        print("4. Size-Inclusive Search")
        print("5. Trend Forecasting")
        print("6. Run All Demos")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (0-6): ").strip()
                
                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    await self.demo_celebrity_outfit_recreation()
                elif choice == '2':
                    await self.demo_budget_conscious_shopping()
                elif choice == '3':
                    await self.demo_sustainable_fashion()
                elif choice == '4':
                    await self.demo_size_inclusive_search()
                elif choice == '5':
                    await self.demo_trend_forecasting()
                elif choice == '6':
                    await self.run_all_demos()
                    break
                else:
                    print("❌ Invalid choice. Please enter 0-6.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function"""
    demo_runner = DemoRunner()
    
    # Check if interactive mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        await demo_runner.run_interactive_demo()
    else:
        # Run all demos
        success = await demo_runner.run_all_demos()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    print("🎬 Visual E-commerce Product Discovery - Demo Scenarios")
    print("=" * 60)
    print("This script demonstrates AI-powered fashion discovery scenarios:")
    print("• Celebrity outfit recreation")
    print("• Budget-conscious shopping")
    print("• Sustainable fashion alternatives")
    print("• Size-inclusive search")
    print("• Trend forecasting")
    print("=" * 60)
    
    # Run the demo
    asyncio.run(main())
