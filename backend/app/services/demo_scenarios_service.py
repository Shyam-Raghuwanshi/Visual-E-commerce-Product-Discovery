"""
Demo Scenarios Service for Visual E-commerce Product Discovery

This service provides specific demo scenarios:
- Celebrity outfit recreation ("get this red carpet look")
- Budget-conscious shopping ("luxury look for less")
- Sustainable fashion ("eco-friendly alternatives")
- Size-inclusive options ("find this in my size")
- Trend forecasting ("what's coming next season")
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
import asyncio
from datetime import datetime, timedelta
import random
from dataclasses import dataclass

from app.services.enhanced_search_service import EnhancedSearchService
from app.services.analytics_recommendation_service import AnalyticsRecommendationService
from app.services.inventory_service import InventoryService
from app.models.schemas import Product, SearchResponse
from app.models.business_schemas import (
    UserPreferences, RecommendationRequest, RecommendationResponse,
    InventoryCheck, UserBehaviorAnalytics
)

logger = logging.getLogger(__name__)

@dataclass
class CelebrityOutfit:
    """Celebrity outfit data for recreation"""
    celebrity_name: str
    event: str
    description: str
    key_pieces: List[Dict[str, Any]]
    style_tags: List[str]
    color_palette: List[str]
    price_range: Dict[str, float]
    image_url: Optional[str] = None

@dataclass
class TrendForecast:
    """Fashion trend forecast data"""
    trend_name: str
    season: str
    year: int
    confidence_score: float
    key_elements: List[str]
    color_trends: List[str]
    material_trends: List[str]
    style_influences: List[str]
    target_demographics: List[str]

class DemoScenariosService:
    """Service for handling various demo scenarios"""
    
    def __init__(self):
        self.search_service = EnhancedSearchService()
        self.analytics_service = AnalyticsRecommendationService()
        self.inventory_service = InventoryService()
        
        # Demo data
        self._initialize_demo_data()
        
        logger.info("Demo Scenarios Service initialized")
    
    def _initialize_demo_data(self):
        """Initialize demo celebrity outfits and trend data"""
        self.celebrity_outfits = [
            CelebrityOutfit(
                celebrity_name="Emma Stone",
                event="Golden Globes 2024",
                description="Elegant black velvet gown with crystal embellishments",
                key_pieces=[
                    {"type": "dress", "description": "black velvet evening gown", "required": True},
                    {"type": "jewelry", "description": "crystal statement earrings", "required": False},
                    {"type": "shoes", "description": "black strappy heels", "required": True},
                    {"type": "clutch", "description": "silver beaded clutch", "required": False}
                ],
                style_tags=["elegant", "formal", "classic", "evening", "glamorous"],
                color_palette=["black", "silver", "crystal"],
                price_range={"min": 200, "max": 2000}
            ),
            CelebrityOutfit(
                celebrity_name="Zendaya",
                event="Met Gala 2024",
                description="Futuristic metallic ensemble with avant-garde accessories",
                key_pieces=[
                    {"type": "dress", "description": "metallic silver bodycon dress", "required": True},
                    {"type": "jacket", "description": "structured metallic blazer", "required": False},
                    {"type": "boots", "description": "metallic knee-high boots", "required": True},
                    {"type": "accessories", "description": "geometric statement jewelry", "required": False}
                ],
                style_tags=["futuristic", "metallic", "avant-garde", "bold", "modern"],
                color_palette=["silver", "metallic", "chrome", "gunmetal"],
                price_range={"min": 150, "max": 1500}
            ),
            CelebrityOutfit(
                celebrity_name="Taylor Swift",
                event="Grammy Awards 2024",
                description="Vintage-inspired sequined mini dress with retro accessories",
                key_pieces=[
                    {"type": "dress", "description": "gold sequined mini dress", "required": True},
                    {"type": "shoes", "description": "gold strappy sandals", "required": True},
                    {"type": "jewelry", "description": "vintage gold jewelry set", "required": False},
                    {"type": "clutch", "description": "vintage beaded purse", "required": False}
                ],
                style_tags=["vintage", "sequined", "retro", "glamorous", "sparkly"],
                color_palette=["gold", "champagne", "bronze", "cream"],
                price_range={"min": 100, "max": 1200}
            )
        ]
        
        self.trend_forecasts = [
            TrendForecast(
                trend_name="Neo-Victorian Romance",
                season="Spring",
                year=2025,
                confidence_score=0.85,
                key_elements=["corset tops", "puffed sleeves", "lace details", "high necklines", "midi skirts"],
                color_trends=["dusty rose", "sage green", "cream", "burgundy", "navy"],
                material_trends=["lace", "velvet", "silk", "cotton", "tulle"],
                style_influences=["Victorian era", "romantic", "feminine", "vintage"],
                target_demographics=["young professionals", "fashion enthusiasts", "romantic style lovers"]
            ),
            TrendForecast(
                trend_name="Sustainable Minimalism",
                season="Summer",
                year=2025,
                confidence_score=0.92,
                key_elements=["clean lines", "organic shapes", "multifunctional pieces", "neutral tones"],
                color_trends=["earth tones", "natural beige", "soft white", "sage", "terracotta"],
                material_trends=["organic cotton", "bamboo fiber", "recycled polyester", "hemp", "linen"],
                style_influences=["minimalism", "sustainability", "conscious fashion"],
                target_demographics=["eco-conscious consumers", "minimalists", "professionals"]
            ),
            TrendForecast(
                trend_name="Tech-Wear Fusion",
                season="Fall",
                year=2025,
                confidence_score=0.78,
                key_elements=["technical fabrics", "utility details", "modular design", "smart textiles"],
                color_trends=["neon accents", "black", "silver", "electric blue", "cyber green"],
                material_trends=["technical mesh", "waterproof fabrics", "smart textiles", "recycled materials"],
                style_influences=["cyberpunk", "techwear", "urban utility", "futurism"],
                target_demographics=["tech enthusiasts", "urban commuters", "early adopters"]
            )
        ]
        
        # Sustainable brands and eco-friendly criteria
        self.sustainable_brands = [
            "Patagonia", "Eileen Fisher", "Reformation", "Everlane", "Stella McCartney",
            "Veja", "Ganni", "Kotn", "Outerknown", "Amour Vert"
        ]
        
        self.eco_criteria = {
            "materials": ["organic cotton", "recycled polyester", "hemp", "bamboo", "tencel", "linen"],
            "certifications": ["GOTS", "OEKO-TEX", "Fair Trade", "B-Corp", "Cradle to Cradle"],
            "production": ["local production", "small batch", "zero waste", "renewable energy"],
            "packaging": ["minimal packaging", "recycled materials", "biodegradable"]
        }
    
    async def celebrity_outfit_recreation(
        self,
        celebrity_name: Optional[str] = None,
        event: Optional[str] = None,
        budget_range: Optional[Dict[str, float]] = None,
        user_preferences: Optional[UserPreferences] = None
    ) -> Dict[str, Any]:
        """
        Recreate celebrity outfits with similar products from the catalog
        """
        logger.info(f"Celebrity outfit recreation for: {celebrity_name or 'random'}")
        
        # Select celebrity outfit
        if celebrity_name:
            outfit = next((o for o in self.celebrity_outfits if o.celebrity_name.lower() == celebrity_name.lower()), None)
            if not outfit:
                outfit = random.choice(self.celebrity_outfits)
        else:
            outfit = random.choice(self.celebrity_outfits)
        
        # Adjust for budget if provided
        if budget_range:
            outfit.price_range = {
                "min": max(outfit.price_range["min"], budget_range.get("min", 0)),
                "max": min(outfit.price_range["max"], budget_range.get("max", float('inf')))
            }
        
        # Search for similar products for each key piece
        recreated_pieces = []
        total_cost = 0
        
        for piece in outfit.key_pieces:
            # Create search query combining style tags and piece description
            search_query = f"{piece['description']} {' '.join(outfit.style_tags[:3])}"
            
            try:
                # Search for similar products
                search_result = await self.search_service.search_by_text(
                    query=search_query,
                    limit=5,
                    min_similarity=0.3
                )
                
                # Filter by price range and preferences
                filtered_products = []
                for product in search_result.products:
                    if (outfit.price_range["min"] <= product.price <= outfit.price_range["max"]):
                        # Check color compatibility
                        if any(color.lower() in product.tags for color in outfit.color_palette):
                            filtered_products.append(product)
                
                if filtered_products:
                    selected_product = filtered_products[0]
                    recreated_pieces.append({
                        "original_piece": piece,
                        "suggested_product": selected_product.__dict__,
                        "similarity_score": search_result.similarity_scores[0] if search_result.similarity_scores else 0.5,
                        "price_difference": selected_product.price - (outfit.price_range["max"] / len(outfit.key_pieces))
                    })
                    total_cost += selected_product.price
                
            except Exception as e:
                logger.error(f"Error searching for piece {piece['type']}: {e}")
                continue
        
        # Calculate styling tips and alternatives
        styling_tips = self._generate_styling_tips(outfit, recreated_pieces)
        alternatives = await self._find_alternatives(recreated_pieces, budget_range)
        
        return {
            "celebrity_inspiration": {
                "name": outfit.celebrity_name,
                "event": outfit.event,
                "description": outfit.description,
                "style_tags": outfit.style_tags,
                "color_palette": outfit.color_palette
            },
            "recreated_outfit": recreated_pieces,
            "total_cost": total_cost,
            "original_price_range": outfit.price_range,
            "styling_tips": styling_tips,
            "alternatives": alternatives,
            "completion_rate": len(recreated_pieces) / len(outfit.key_pieces),
            "generated_at": datetime.now().isoformat()
        }
    
    async def budget_conscious_shopping(
        self,
        target_look: str,
        max_budget: float,
        style_preferences: Optional[List[str]] = None,
        must_have_pieces: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find luxury-inspired looks within budget constraints
        """
        logger.info(f"Budget-conscious shopping for: {target_look}, budget: ${max_budget}")
        
        # Define luxury keywords to search for and replace with budget alternatives
        luxury_keywords = {
            "designer": ["trendy", "stylish", "fashion-forward"],
            "premium": ["quality", "well-made", "durable"],
            "luxury": ["chic", "elegant", "sophisticated"],
            "haute couture": ["fashion", "stylish", "contemporary"],
            "exclusive": ["unique", "special", "distinctive"]
        }
        
        # Create budget-friendly search query
        budget_query = target_look.lower()
        for luxury_word, alternatives in luxury_keywords.items():
            if luxury_word in budget_query:
                budget_query = budget_query.replace(luxury_word, alternatives[0])
        
        # Search for products within budget
        search_result = await self.search_service.search_by_text(
            query=budget_query,
            limit=50,
            min_similarity=0.2
        )
        
        # Filter products by budget
        budget_products = [
            product for product in search_result.products 
            if product.price <= max_budget
        ]
        
        # Categorize products by type
        categorized_products = self._categorize_products_by_type(budget_products)
        
        # Create outfit combinations within budget
        outfit_combinations = self._create_budget_combinations(
            categorized_products, 
            max_budget, 
            must_have_pieces or []
        )
        
        # Find luxury inspiration pieces for comparison
        luxury_inspiration = await self._find_luxury_inspiration(target_look)
        
        # Generate money-saving tips
        saving_tips = self._generate_money_saving_tips(target_look, max_budget)
        
        return {
            "target_look": target_look,
            "budget_limit": max_budget,
            "budget_products": budget_products[:20],  # Top 20 budget options
            "outfit_combinations": outfit_combinations[:5],  # Top 5 combinations
            "luxury_inspiration": luxury_inspiration,
            "money_saved": sum([item.get("original_price", 0) - item.get("budget_price", 0) 
                               for combo in outfit_combinations[:1] 
                               for item in combo.get("items", [])]),
            "saving_tips": saving_tips,
            "style_alternatives": await self._get_style_alternatives(target_look, max_budget),
            "generated_at": datetime.now().isoformat()
        }
    
    async def sustainable_fashion_alternatives(
        self,
        search_query: str,
        sustainability_criteria: Optional[List[str]] = None,
        max_price_premium: float = 0.3  # 30% premium for sustainable options
    ) -> Dict[str, Any]:
        """
        Find eco-friendly alternatives to fashion items
        """
        logger.info(f"Finding sustainable alternatives for: {search_query}")
        
        # Search for regular products first
        regular_search = await self.search_service.search_by_text(
            query=search_query,
            limit=30,
            min_similarity=0.2
        )
        
        # Filter for sustainable products
        sustainability_keywords = (sustainability_criteria or []) + [
            "organic", "sustainable", "eco-friendly", "recycled", "ethical",
            "fair trade", "bamboo", "hemp", "GOTS certified"
        ]
        
        sustainable_products = []
        regular_products = []
        
        for product in regular_search.products:
            is_sustainable = any(
                keyword.lower() in product.description.lower() or 
                keyword.lower() in ' '.join(product.tags).lower() or
                product.brand in self.sustainable_brands
                for keyword in sustainability_keywords
            )
            
            if is_sustainable:
                sustainable_products.append(product)
            else:
                regular_products.append(product)
        
        # Calculate sustainability scores
        sustainability_analysis = []
        for product in sustainable_products:
            score = self._calculate_sustainability_score(product)
            sustainability_analysis.append({
                "product": product.__dict__,
                "sustainability_score": score["total_score"],
                "eco_features": score["features"],
                "certifications": score["certifications"],
                "environmental_impact": score["impact_reduction"]
            })
        
        # Sort by sustainability score
        sustainability_analysis.sort(key=lambda x: x["sustainability_score"], reverse=True)
        
        # Compare with regular alternatives
        price_comparison = self._compare_sustainable_vs_regular_prices(
            sustainable_products, regular_products
        )
        
        # Generate eco-impact information
        eco_impact = self._calculate_environmental_impact(sustainable_products[:10])
        
        return {
            "search_query": search_query,
            "sustainable_alternatives": sustainability_analysis[:15],
            "regular_alternatives": [p.__dict__ for p in regular_products[:10]],
            "price_comparison": price_comparison,
            "eco_impact_summary": eco_impact,
            "sustainability_tips": self._generate_sustainability_tips(),
            "sustainable_brands_featured": list(set([
                p["product"]["brand"] for p in sustainability_analysis
                if p["product"]["brand"] in self.sustainable_brands
            ])),
            "generated_at": datetime.now().isoformat()
        }
    
    async def size_inclusive_search(
        self,
        search_query: str,
        target_size: str,
        size_range: Optional[List[str]] = None,
        body_type_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Find products available in specific sizes with inclusive options
        """
        logger.info(f"Size-inclusive search for: {search_query}, size: {target_size}")
        
        # Search for products
        search_result = await self.search_service.search_by_text(
            query=search_query,
            limit=50,
            min_similarity=0.2
        )
        
        # Extended size ranges for inclusivity
        size_mappings = {
            "XS": ["XS", "XXS", "0", "2"],
            "S": ["S", "XS", "4", "6"],
            "M": ["M", "S", "8", "10"],
            "L": ["L", "M", "12", "14"],
            "XL": ["XL", "L", "16", "18"],
            "XXL": ["XXL", "XL", "20", "22"],
            "XXXL": ["XXXL", "XXL", "24", "26"],
            "XXXXL": ["XXXXL", "XXXL", "28", "30"]
        }
        
        # Include plus sizes and extended ranges
        extended_sizes = size_range or size_mappings.get(target_size.upper(), [target_size])
        
        # Filter products by size availability
        size_available_products = []
        size_unavailable_products = []
        
        for product in search_result.products:
            # Check if product has size information and matches target
            product_size = getattr(product, 'size', 'One Size')
            if (product_size in extended_sizes or 
                product_size == 'One Size' or 
                any(size.lower() in product.tags for size in extended_sizes)):
                size_available_products.append(product)
            else:
                size_unavailable_products.append(product)
        
        # Find inclusive brands and size-friendly alternatives
        inclusive_brands = await self._identify_size_inclusive_brands(search_query)
        
        # Generate fit recommendations based on body type
        fit_recommendations = self._generate_fit_recommendations(
            target_size, body_type_preferences
        )
        
        # Calculate size availability statistics
        size_stats = self._calculate_size_availability_stats(
            size_available_products, size_unavailable_products
        )
        
        # Find similar products in different sizes
        alternative_sizes = await self._find_alternative_sizes(
            search_query, target_size, extended_sizes
        )
        
        return {
            "search_query": search_query,
            "target_size": target_size,
            "available_products": [p.__dict__ for p in size_available_products],
            "unavailable_products": [p.__dict__ for p in size_unavailable_products[:10]],
            "size_availability_rate": len(size_available_products) / len(search_result.products) if search_result.products else 0,
            "inclusive_brands": inclusive_brands,
            "fit_recommendations": fit_recommendations,
            "size_statistics": size_stats,
            "alternative_sizes": alternative_sizes,
            "styling_tips_for_size": self._generate_size_specific_styling_tips(target_size),
            "generated_at": datetime.now().isoformat()
        }
    
    async def trend_forecasting(
        self,
        season: Optional[str] = None,
        year: Optional[int] = None,
        style_category: Optional[str] = None,
        demographic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict upcoming fashion trends and recommend products
        """
        logger.info(f"Trend forecasting for {season or 'upcoming'} {year or 2025}")
        
        current_year = datetime.now().year
        target_year = year or current_year + 1
        target_season = season or self._get_next_season()
        
        # Filter relevant trend forecasts
        relevant_trends = [
            trend for trend in self.trend_forecasts
            if (not season or trend.season.lower() == target_season.lower()) and
               (not year or trend.year == target_year)
        ]
        
        if not relevant_trends:
            relevant_trends = self.trend_forecasts  # Fallback to all trends
        
        # Analyze current product catalog for trend alignment
        trend_aligned_products = {}
        
        for trend in relevant_trends:
            # Search for products matching trend elements
            trend_query = " ".join(trend.key_elements + trend.color_trends[:2])
            
            try:
                search_result = await self.search_service.search_by_text(
                    query=trend_query,
                    limit=20,
                    min_similarity=0.2
                )
                
                # Score products for trend alignment
                scored_products = []
                for product in search_result.products:
                    alignment_score = self._calculate_trend_alignment(product, trend)
                    if alignment_score > 0.3:  # Minimum alignment threshold
                        scored_products.append({
                            "product": product.__dict__,
                            "trend_alignment_score": alignment_score,
                            "matching_elements": self._identify_matching_trend_elements(product, trend)
                        })
                
                trend_aligned_products[trend.trend_name] = sorted(
                    scored_products, 
                    key=lambda x: x["trend_alignment_score"], 
                    reverse=True
                )[:10]
                
            except Exception as e:
                logger.error(f"Error analyzing trend {trend.trend_name}: {e}")
                continue
        
        # Generate trend insights and predictions
        trend_insights = self._generate_trend_insights(relevant_trends, trend_aligned_products)
        
        # Create shopping recommendations based on trends
        trend_shopping_guide = self._create_trend_shopping_guide(relevant_trends)
        
        # Predict price movements and investment pieces
        investment_recommendations = self._identify_investment_pieces(relevant_trends, trend_aligned_products)
        
        return {
            "forecast_period": f"{target_season} {target_year}",
            "predicted_trends": [
                {
                    "name": trend.trend_name,
                    "confidence": trend.confidence_score,
                    "key_elements": trend.key_elements,
                    "colors": trend.color_trends,
                    "materials": trend.material_trends,
                    "influences": trend.style_influences,
                    "target_demographics": trend.target_demographics
                }
                for trend in relevant_trends
            ],
            "trend_aligned_products": trend_aligned_products,
            "trend_insights": trend_insights,
            "shopping_guide": trend_shopping_guide,
            "investment_pieces": investment_recommendations,
            "early_adopter_recommendations": self._get_early_adopter_recommendations(relevant_trends),
            "generated_at": datetime.now().isoformat(),
            "confidence_level": sum(t.confidence_score for t in relevant_trends) / len(relevant_trends) if relevant_trends else 0
        }
    
    # Helper methods
    
    def _generate_styling_tips(self, outfit, recreated_pieces):
        """Generate styling tips for celebrity outfit recreation"""
        tips = [
            f"To achieve {outfit.celebrity_name}'s look, focus on the key elements: {', '.join(outfit.style_tags[:3])}",
            f"The color palette ({', '.join(outfit.color_palette)}) is crucial for authenticity",
            "Consider accessories to complete the look - they make the biggest impact",
            "Fit is everything - ensure proper tailoring for a polished appearance"
        ]
        
        if len(recreated_pieces) < len(outfit.key_pieces):
            tips.append("Don't worry about finding exact matches - focus on capturing the overall vibe and silhouette")
        
        return tips
    
    async def _find_alternatives(self, recreated_pieces, budget_range):
        """Find alternative products for outfit pieces"""
        alternatives = []
        
        for piece in recreated_pieces:
            try:
                # Search for similar but different products
                alt_search = await self.search_service.search_by_text(
                    query=piece["original_piece"]["description"],
                    limit=3,
                    min_similarity=0.2
                )
                
                # Filter out the already selected product
                selected_id = piece["suggested_product"]["id"]
                alt_products = [p for p in alt_search.products if p.id != selected_id]
                
                if budget_range:
                    alt_products = [p for p in alt_products 
                                  if budget_range["min"] <= p.price <= budget_range["max"]]
                
                alternatives.append({
                    "piece_type": piece["original_piece"]["type"],
                    "alternatives": [p.__dict__ for p in alt_products[:2]]
                })
                
            except Exception as e:
                logger.error(f"Error finding alternatives: {e}")
                continue
        
        return alternatives
    
    def _categorize_products_by_type(self, products):
        """Categorize products by clothing type"""
        categories = {
            "tops": [], "bottoms": [], "dresses": [], "outerwear": [],
            "shoes": [], "accessories": [], "bags": [], "jewelry": []
        }
        
        for product in products:
            category = product.category.lower()
            subcategory = getattr(product, 'subcategory', '').lower()
            
            if 'dress' in subcategory or 'dress' in product.name.lower():
                categories["dresses"].append(product)
            elif category == 'shoes':
                categories["shoes"].append(product)
            elif category == 'accessories':
                if 'bag' in subcategory or 'purse' in subcategory:
                    categories["bags"].append(product)
                elif 'jewelry' in subcategory:
                    categories["jewelry"].append(product)
                else:
                    categories["accessories"].append(product)
            elif subcategory in ['shirt', 'blouse', 'top', 'sweater', 't-shirt']:
                categories["tops"].append(product)
            elif subcategory in ['pants', 'jeans', 'skirt', 'shorts']:
                categories["bottoms"].append(product)
            elif subcategory in ['jacket', 'coat', 'blazer']:
                categories["outerwear"].append(product)
            else:
                # Default categorization based on product name
                name_lower = product.name.lower()
                if any(word in name_lower for word in ['shirt', 'top', 'blouse', 'sweater']):
                    categories["tops"].append(product)
                elif any(word in name_lower for word in ['pants', 'jeans', 'skirt']):
                    categories["bottoms"].append(product)
                else:
                    categories["accessories"].append(product)
        
        return categories
    
    def _create_budget_combinations(self, categorized_products, max_budget, must_have_pieces):
        """Create outfit combinations within budget"""
        combinations = []
        
        # Try different combination strategies
        strategies = [
            {"dress": 0.6, "shoes": 0.2, "accessories": 0.2},  # Dress-focused
            {"tops": 0.3, "bottoms": 0.3, "shoes": 0.2, "accessories": 0.2},  # Separates
            {"outerwear": 0.4, "tops": 0.2, "bottoms": 0.2, "shoes": 0.2}  # Outerwear-focused
        ]
        
        for i, strategy in enumerate(strategies):
            combination = {"strategy": f"Option {i+1}", "items": [], "total_cost": 0}
            
            for category, budget_percentage in strategy.items():
                if category in categorized_products and categorized_products[category]:
                    category_budget = max_budget * budget_percentage
                    suitable_products = [
                        p for p in categorized_products[category] 
                        if p.price <= category_budget
                    ]
                    
                    if suitable_products:
                        selected = suitable_products[0]  # Pick the first suitable product
                        combination["items"].append({
                            "category": category,
                            "product": selected.__dict__,
                            "budget_allocation": category_budget,
                            "savings": category_budget - selected.price
                        })
                        combination["total_cost"] += selected.price
            
            if combination["items"] and combination["total_cost"] <= max_budget:
                combination["remaining_budget"] = max_budget - combination["total_cost"]
                combinations.append(combination)
        
        return combinations
    
    async def _find_luxury_inspiration(self, target_look):
        """Find luxury products for inspiration comparison"""
        luxury_brands = ["Gucci", "Prada", "Louis Vuitton", "Chanel", "Dior", "Versace", "Saint Laurent"]
        
        # Search with luxury brand names
        luxury_query = f"{target_look} " + " OR ".join(luxury_brands[:3])
        
        try:
            luxury_search = await self.search_service.search_by_text(
                query=luxury_query,
                limit=10,
                min_similarity=0.1
            )
            
            luxury_products = [
                p for p in luxury_search.products 
                if p.brand in luxury_brands or p.price > 500
            ]
            
            return [p.__dict__ for p in luxury_products[:5]]
        
        except Exception as e:
            logger.error(f"Error finding luxury inspiration: {e}")
            return []
    
    def _generate_money_saving_tips(self, target_look, max_budget):
        """Generate money-saving tips for budget shopping"""
        return [
            f"Shop off-season for {target_look} to save 30-50%",
            "Mix high and low pieces - invest in quality basics, save on trendy items",
            "Check outlet stores and sales sections first",
            "Consider renting accessories or special occasion pieces",
            f"Set a strict budget of ${max_budget} and stick to it",
            "Look for versatile pieces that work with multiple outfits",
            "Shop your closet first - you might already have key pieces",
            "Follow your favorite brands on social media for flash sales",
            "Use cashback apps and reward programs",
            "Consider second-hand or consignment options for designer pieces"
        ]
    
    async def _get_style_alternatives(self, target_look, max_budget):
        """Get alternative style interpretations within budget"""
        style_variations = [
            f"casual {target_look}",
            f"minimalist {target_look}",
            f"bohemian {target_look}",
            f"classic {target_look}"
        ]
        
        alternatives = []
        for variation in style_variations:
            try:
                search_result = await self.search_service.search_by_text(
                    query=variation,
                    limit=3,
                    min_similarity=0.2
                )
                
                budget_options = [p for p in search_result.products if p.price <= max_budget]
                if budget_options:
                    alternatives.append({
                        "style_variant": variation,
                        "products": [p.__dict__ for p in budget_options[:2]]
                    })
            except Exception:
                continue
        
        return alternatives
    
    def _calculate_sustainability_score(self, product):
        """Calculate sustainability score for a product"""
        score = 0
        features = []
        certifications = []
        
        # Check materials
        sustainable_materials = ["organic cotton", "recycled", "bamboo", "hemp", "tencel", "linen"]
        for material in sustainable_materials:
            if material.lower() in product.description.lower() or material.lower() in ' '.join(product.tags).lower():
                score += 20
                features.append(f"Made with {material}")
        
        # Check brand sustainability
        if product.brand in self.sustainable_brands:
            score += 30
            features.append("Sustainable brand")
        
        # Check certifications
        cert_keywords = ["GOTS", "OEKO-TEX", "Fair Trade", "B-Corp", "organic certified"]
        for cert in cert_keywords:
            if cert.lower() in product.description.lower():
                score += 15
                certifications.append(cert)
        
        # Check production claims
        production_keywords = ["locally made", "ethically produced", "zero waste", "carbon neutral"]
        for keyword in production_keywords:
            if keyword.lower() in product.description.lower():
                score += 10
                features.append(keyword.replace("_", " ").title())
        
        return {
            "total_score": min(score, 100),  # Cap at 100
            "features": features,
            "certifications": certifications,
            "impact_reduction": self._estimate_environmental_impact_reduction(features)
        }
    
    def _compare_sustainable_vs_regular_prices(self, sustainable_products, regular_products):
        """Compare prices between sustainable and regular products"""
        if not sustainable_products or not regular_products:
            return {"message": "Insufficient data for price comparison"}
        
        sustainable_avg = sum(p.price for p in sustainable_products) / len(sustainable_products)
        regular_avg = sum(p.price for p in regular_products) / len(regular_products)
        
        price_premium = ((sustainable_avg - regular_avg) / regular_avg) * 100 if regular_avg > 0 else 0
        
        return {
            "sustainable_average_price": round(sustainable_avg, 2),
            "regular_average_price": round(regular_avg, 2),
            "price_premium_percentage": round(price_premium, 1),
            "absolute_difference": round(sustainable_avg - regular_avg, 2),
            "value_proposition": "Higher upfront cost, lower long-term environmental impact" if price_premium > 0 else "Competitive pricing with environmental benefits"
        }
    
    def _calculate_environmental_impact(self, products):
        """Calculate estimated environmental impact of sustainable products"""
        total_water_saved = len(products) * 2700  # Liters saved per sustainable garment
        total_co2_reduced = len(products) * 8.5   # kg CO2 reduced per garment
        
        return {
            "products_analyzed": len(products),
            "estimated_water_savings_liters": total_water_saved,
            "estimated_co2_reduction_kg": total_co2_reduced,
            "equivalent_impact": {
                "water_saved": f"Equivalent to {total_water_saved // 200} days of drinking water",
                "co2_reduced": f"Equivalent to removing a car from road for {total_co2_reduced * 4:.0f} miles"
            },
            "sustainability_benefits": [
                "Reduced water consumption in production",
                "Lower carbon footprint",
                "Reduced chemical usage",
                "Support for ethical labor practices",
                "Decreased textile waste"
            ]
        }
    
    def _generate_sustainability_tips(self):
        """Generate sustainability tips for conscious shopping"""
        return [
            "Choose quality over quantity - buy fewer, better pieces",
            "Care for your clothes properly to extend their lifespan",
            "Consider the cost-per-wear when evaluating purchases",
            "Look for certifications like GOTS, OEKO-TEX, and Fair Trade",
            "Support brands with transparent supply chains",
            "Choose natural, organic, or recycled materials when possible",
            "Repair and upcycle existing items before buying new",
            "Shop secondhand or vintage for unique sustainable options",
            "Avoid fast fashion and trend-driven purchases",
            "Consider renting special occasion wear instead of buying"
        ]
    
    def _estimate_environmental_impact_reduction(self, features):
        """Estimate environmental impact reduction based on features"""
        impact_values = {
            "organic cotton": {"water_saved": 91, "co2_reduced": 46},
            "recycled": {"water_saved": 70, "co2_reduced": 60},
            "bamboo": {"water_saved": 75, "co2_reduced": 30},
            "hemp": {"water_saved": 80, "co2_reduced": 35}
        }
        
        total_water = sum(impact_values.get(feature.lower().split()[2] if len(feature.split()) > 2 else feature.lower(), {}).get("water_saved", 0) for feature in features)
        total_co2 = sum(impact_values.get(feature.lower().split()[2] if len(feature.split()) > 2 else feature.lower(), {}).get("co2_reduced", 0) for feature in features)
        
        return {
            "water_savings_percentage": min(total_water, 95),
            "co2_reduction_percentage": min(total_co2, 90),
            "overall_impact_score": min((total_water + total_co2) / 2, 95)
        }
    
    async def _identify_size_inclusive_brands(self, search_query):
        """Identify brands known for size inclusivity"""
        inclusive_brands = [
            "Universal Standard", "Eloquii", "Lane Bryant", "Torrid", "Ashley Stewart",
            "ASOS Curve", "Anthropologie", "Madewell", "Good American", "Savage X Fenty"
        ]
        
        # Search for products from inclusive brands
        found_brands = []
        try:
            search_result = await self.search_service.search_by_text(
                query=search_query,
                limit=50,
                min_similarity=0.1
            )
            
            for product in search_result.products:
                if product.brand in inclusive_brands:
                    found_brands.append({
                        "brand": product.brand,
                        "size_range": "XS-5XL",  # Assumed range for demo
                        "known_for": "Size inclusivity and extended size options"
                    })
        
        except Exception as e:
            logger.error(f"Error identifying inclusive brands: {e}")
        
        return list({b["brand"]: b for b in found_brands}.values())  # Remove duplicates
    
    def _generate_fit_recommendations(self, target_size, body_type_preferences):
        """Generate fit recommendations based on size and body type"""
        size_tips = {
            "XS": ["Look for adjustable features", "Consider petite sizing", "Check shoulder fit carefully"],
            "S": ["Standard fit should work well", "Consider petite lengths if needed"],
            "M": ["Most versatile size for fit", "Good range of style options"],
            "L": ["Look for relaxed or classic fits", "Consider tall sizes for length"],
            "XL": ["Seek out inclusive brands", "Look for stretchy, forgiving fabrics"],
            "XXL": ["Prioritize comfort and movement", "Look for strategic design details"],
            "XXXL": ["Focus on quality construction", "Seek professional styling advice"]
        }
        
        general_tips = [
            "Read size charts carefully - sizes vary by brand",
            "Check return/exchange policies before ordering",
            "Look for adjustable features like drawstrings or elastic",
            "Consider fabric stretch and drape",
            "Read reviews from customers with similar measurements"
        ]
        
        size_specific = size_tips.get(target_size.upper(), ["Check sizing guides carefully"])
        
        recommendations = {
            "size_specific_tips": size_specific,
            "general_fit_advice": general_tips,
            "recommended_features": ["Adjustable waistbands", "Stretch fabrics", "Flattering cuts"],
            "brands_to_try": ["Known for consistent sizing", "Size-inclusive options", "Good return policy"]
        }
        
        if body_type_preferences:
            recommendations["personalized_tips"] = self._get_body_type_specific_tips(body_type_preferences)
        
        return recommendations
    
    def _get_body_type_specific_tips(self, body_type_preferences):
        """Get tips specific to body type preferences"""
        return [
            "Choose cuts that enhance your natural silhouette",
            "Focus on fit in your priority areas",
            "Don't be afraid to tailor pieces for perfect fit",
            "Experiment with different brands to find your best fit"
        ]
    
    def _calculate_size_availability_stats(self, available_products, unavailable_products):
        """Calculate statistics about size availability"""
        total_products = len(available_products) + len(unavailable_products)
        
        if total_products == 0:
            return {"message": "No products found for analysis"}
        
        availability_rate = len(available_products) / total_products
        
        # Analyze by category
        category_stats = {}
        for product in available_products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {"available": 0, "total": 0}
            category_stats[category]["available"] += 1
        
        for product in unavailable_products:
            category = product.category
            if category not in category_stats:
                category_stats[category] = {"available": 0, "total": 0}
            category_stats[category]["total"] += 1
        
        # Calculate category rates
        for category in category_stats:
            total = category_stats[category]["available"] + category_stats[category]["total"]
            category_stats[category]["availability_rate"] = category_stats[category]["available"] / total if total > 0 else 0
        
        return {
            "overall_availability_rate": round(availability_rate * 100, 1),
            "products_available": len(available_products),
            "products_unavailable": len(unavailable_products),
            "category_breakdown": category_stats,
            "recommendation": "Excellent" if availability_rate > 0.8 else "Good" if availability_rate > 0.6 else "Limited" if availability_rate > 0.3 else "Poor"
        }
    
    async def _find_alternative_sizes(self, search_query, target_size, extended_sizes):
        """Find products in alternative sizes"""
        alternatives = {}
        
        size_alternatives = {
            "XS": ["S"], "S": ["XS", "M"], "M": ["S", "L"],
            "L": ["M", "XL"], "XL": ["L", "XXL"], "XXL": ["XL", "XXXL"]
        }
        
        alt_sizes = size_alternatives.get(target_size.upper(), [])
        
        for alt_size in alt_sizes:
            try:
                # Search for products in alternative size
                alt_search = await self.search_service.search_by_text(
                    query=f"{search_query} size {alt_size}",
                    limit=5,
                    min_similarity=0.2
                )
                
                if alt_search.products:
                    alternatives[alt_size] = [p.__dict__ for p in alt_search.products[:3]]
            
            except Exception:
                continue
        
        return alternatives
    
    def _generate_size_specific_styling_tips(self, target_size):
        """Generate styling tips specific to the target size"""
        styling_tips = {
            "XS": [
                "Layer pieces to add visual weight and dimension",
                "Choose fitted silhouettes to avoid being overwhelmed",
                "Use accessories to add proportion and interest",
                "Consider cropped and petite lengths"
            ],
            "S": [
                "Balance fitted and relaxed pieces",
                "Experiment with proportions",
                "Use belts to define your waist",
                "Try both regular and petite sizing"
            ],
            "M": [
                "Most styles will work well for you",
                "Experiment with different fits and cuts",
                "Focus on quality and personal style",
                "Mix different proportions confidently"
            ],
            "L": [
                "Choose pieces that skim rather than cling",
                "Use vertical lines to elongate",
                "Invest in well-fitted undergarments",
                "Consider tall sizes for better proportions"
            ],
            "XL": [
                "Look for pieces with strategic draping",
                "Choose quality fabrics with good structure",
                "Define your waist with belts or fitted pieces",
                "Embrace bold patterns and colors"
            ],
            "XXL": [
                "Focus on fit over size number",
                "Choose pieces that make you feel confident",
                "Invest in tailoring for perfect fit",
                "Don't shy away from trends you love"
            ]
        }
        
        return styling_tips.get(target_size.upper(), [
            "Focus on fit and comfort",
            "Choose styles that make you feel confident",
            "Don't be limited by size - fashion is for everyone"
        ])
    
    def _get_next_season(self):
        """Determine the next fashion season"""
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:
            return "Spring"
        elif current_month in [3, 4, 5]:
            return "Summer"
        elif current_month in [6, 7, 8]:
            return "Fall"
        else:
            return "Winter"
    
    def _calculate_trend_alignment(self, product, trend):
        """Calculate how well a product aligns with a trend"""
        score = 0
        
        # Check key elements
        for element in trend.key_elements:
            if element.lower() in product.description.lower() or element.lower() in ' '.join(product.tags).lower():
                score += 20
        
        # Check color trends
        for color in trend.color_trends:
            if color.lower() in product.tags or color.lower() == product.color.lower():
                score += 15
        
        # Check material trends
        for material in trend.material_trends:
            if material.lower() in product.description.lower() or material.lower() in ' '.join(product.tags).lower():
                score += 10
        
        # Check style influences
        for influence in trend.style_influences:
            if influence.lower() in product.description.lower() or influence.lower() in ' '.join(product.tags).lower():
                score += 10
        
        return min(score / 100, 1.0)  # Normalize to 0-1
    
    def _identify_matching_trend_elements(self, product, trend):
        """Identify which trend elements match the product"""
        matching = []
        
        # Check each trend component
        for element in trend.key_elements:
            if element.lower() in product.description.lower() or element.lower() in ' '.join(product.tags).lower():
                matching.append(f"Key element: {element}")
        
        for color in trend.color_trends:
            if color.lower() in product.tags or color.lower() == product.color.lower():
                matching.append(f"Trend color: {color}")
        
        for material in trend.material_trends:
            if material.lower() in product.description.lower():
                matching.append(f"Trend material: {material}")
        
        return matching
    
    def _generate_trend_insights(self, trends, trend_aligned_products):
        """Generate insights about fashion trends"""
        insights = []
        
        # Overall trend confidence
        avg_confidence = sum(t.confidence_score for t in trends) / len(trends) if trends else 0
        insights.append(f"Overall trend confidence is {avg_confidence:.1%} based on {len(trends)} analyzed trends")
        
        # Most popular elements
        all_elements = [element for trend in trends for element in trend.key_elements]
        element_counts = {}
        for element in all_elements:
            element_counts[element] = element_counts.get(element, 0) + 1
        
        top_elements = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_elements:
            insights.append(f"Most recurring trend elements: {', '.join([e[0] for e in top_elements])}")
        
        # Color trends
        all_colors = [color for trend in trends for color in trend.color_trends]
        color_counts = {}
        for color in all_colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_colors:
            insights.append(f"Trending colors: {', '.join([c[0] for c in top_colors])}")
        
        return insights
    
    def _create_trend_shopping_guide(self, trends):
        """Create a shopping guide based on trends"""
        guide = {
            "must_have_pieces": [],
            "investment_priorities": [],
            "color_palette": [],
            "shopping_strategy": []
        }
        
        for trend in trends:
            # Extract must-have pieces
            guide["must_have_pieces"].extend(trend.key_elements[:2])
            
            # Extract colors
            guide["color_palette"].extend(trend.color_trends[:2])
            
            # Add investment advice
            if trend.confidence_score > 0.8:
                guide["investment_priorities"].append({
                    "trend": trend.trend_name,
                    "reason": f"High confidence ({trend.confidence_score:.1%}) - likely to be widely adopted",
                    "pieces": trend.key_elements[:3]
                })
        
        # Remove duplicates
        guide["must_have_pieces"] = list(set(guide["must_have_pieces"]))
        guide["color_palette"] = list(set(guide["color_palette"]))
        
        # Add shopping strategy
        guide["shopping_strategy"] = [
            "Start with versatile trend pieces that work with your existing wardrobe",
            "Invest in quality for high-confidence trends",
            "Try trend colors in accessories first",
            "Look for pieces that incorporate multiple trend elements",
            "Don't completely overhaul your wardrobe - blend trends with classics"
        ]
        
        return guide
    
    def _identify_investment_pieces(self, trends, trend_aligned_products):
        """Identify investment-worthy pieces based on trends"""
        investments = []
        
        high_confidence_trends = [t for t in trends if t.confidence_score > 0.8]
        
        for trend in high_confidence_trends:
            if trend.trend_name in trend_aligned_products:
                products = trend_aligned_products[trend.trend_name]
                
                # Find higher-priced, high-quality pieces
                investment_candidates = [
                    p for p in products 
                    if p["product"]["price"] > 200 and p["trend_alignment_score"] > 0.7
                ]
                
                if investment_candidates:
                    investments.append({
                        "trend": trend.trend_name,
                        "confidence": trend.confidence_score,
                        "recommended_pieces": investment_candidates[:3],
                        "investment_rationale": f"High trend confidence with quality pieces that will remain relevant"
                    })
        
        return investments
    
    def _get_early_adopter_recommendations(self, trends):
        """Get recommendations for early trend adopters"""
        recommendations = []
        
        # Focus on newer, emerging trends
        emerging_trends = [t for t in trends if 0.6 <= t.confidence_score <= 0.8]
        
        for trend in emerging_trends:
            recommendations.append({
                "trend": trend.trend_name,
                "early_adopter_appeal": "Be ahead of the curve",
                "key_pieces_to_try": trend.key_elements[:3],
                "styling_tip": f"Incorporate {trend.key_elements[0]} into your existing style",
                "risk_level": "Medium" if trend.confidence_score > 0.7 else "Higher"
            })
        
        return recommendations
