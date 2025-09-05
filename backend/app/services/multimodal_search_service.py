"""
Multi-modal Search Enhancement Service

This service provides advanced search capabilities that showcase vector search:
- Find items that match this outfit but in a different color
- Show me cheaper alternatives to this luxury item
- Find accessories that go with this dress
- Seasonal recommendations based on current trends
- Style evolution ("make this more casual/formal")
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, Union
import numpy as np
from PIL import Image
import io
import asyncio
from datetime import datetime, timedelta
import json
import re

from app.services.clip_service import CLIPService
from app.services.vector_service import VectorService
from app.services.enhanced_search_service import EnhancedSearchService
from app.models.schemas import Product, SearchResponse

logger = logging.getLogger(__name__)

class MultiModalSearchService:
    """
    Advanced multi-modal search service for sophisticated e-commerce queries
    """
    
    def __init__(self):
        """Initialize the multi-modal search service"""
        self.enhanced_search = EnhancedSearchService()
        self.clip_service = self.enhanced_search.clip_service
        self.vector_service = self.enhanced_search.vector_service
        
        # Color mapping for style variations
        self.color_mappings = {
            "red": ["burgundy", "crimson", "scarlet", "cherry", "wine"],
            "blue": ["navy", "royal", "sky", "teal", "azure"],
            "green": ["forest", "emerald", "olive", "sage", "mint"],
            "black": ["charcoal", "ebony", "onyx", "coal", "jet"],
            "white": ["ivory", "cream", "pearl", "snow", "vanilla"],
            "brown": ["tan", "beige", "coffee", "chocolate", "camel"],
            "gray": ["silver", "slate", "ash", "pewter", "smoke"],
            "yellow": ["gold", "amber", "honey", "lemon", "butter"],
            "purple": ["violet", "lavender", "plum", "mauve", "amethyst"],
            "pink": ["rose", "blush", "coral", "salmon", "magenta"]
        }
        
        # Style transformation mappings
        self.style_transforms = {
            "casual": {
                "keywords": ["casual", "relaxed", "comfortable", "everyday", "laid-back"],
                "avoid": ["formal", "dressy", "elegant", "sophisticated"]
            },
            "formal": {
                "keywords": ["formal", "elegant", "sophisticated", "dressy", "business"],
                "avoid": ["casual", "relaxed", "sporty", "athletic"]
            },
            "sporty": {
                "keywords": ["athletic", "sporty", "active", "performance", "gym"],
                "avoid": ["formal", "dressy", "elegant"]
            },
            "bohemian": {
                "keywords": ["boho", "bohemian", "free-spirited", "artistic", "flowy"],
                "avoid": ["structured", "tailored", "minimalist"]
            },
            "minimalist": {
                "keywords": ["minimal", "clean", "simple", "sleek", "understated"],
                "avoid": ["ornate", "busy", "decorative", "embellished"]
            }
        }
        
        # Seasonal mappings
        self.seasonal_keywords = {
            "spring": ["light", "fresh", "pastel", "floral", "breathable"],
            "summer": ["lightweight", "cool", "bright", "airy", "tropical"],
            "fall": ["warm", "cozy", "earth tones", "layering", "autumn"],
            "winter": ["warm", "heavy", "thick", "insulated", "holiday"]
        }
        
        logger.info("Multi-Modal Search Service initialized")
    
    async def find_color_variations(
        self,
        product_id: str,
        target_colors: List[str],
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Find items similar to the given product but in different colors.
        
        Args:
            product_id: Reference product ID
            target_colors: List of desired colors
            limit: Maximum number of results
            
        Returns:
            Dictionary with color variation results
        """
        try:
            logger.info(f"Finding color variations for product {product_id} in colors: {target_colors}")
            
            # Get the reference product
            ref_product = await self.vector_service.get_product_by_id(product_id)
            if not ref_product:
                raise ValueError(f"Product not found: {product_id}")
            
            # Get product embedding
            ref_embedding = await self.vector_service.get_product_embedding(product_id)
            if ref_embedding is None:
                raise ValueError(f"Product embedding not found: {product_id}")
            
            # Expand color terms using mappings
            expanded_colors = []
            for color in target_colors:
                expanded_colors.append(color.lower())
                if color.lower() in self.color_mappings:
                    expanded_colors.extend(self.color_mappings[color.lower()])
            
            # Create style-preserving query
            style_keywords = [
                ref_product.get("name", ""),
                ref_product.get("subcategory", ""),
                ref_product.get("material", ""),
                ref_product.get("brand", "")
            ]
            
            # Remove color words from style description
            color_words = set(self.color_mappings.keys()) | set([
                color for colors in self.color_mappings.values() for color in colors
            ])
            
            filtered_style = []
            for keyword in style_keywords:
                if keyword:
                    words = keyword.lower().split()
                    filtered_words = [w for w in words if w not in color_words]
                    if filtered_words:
                        filtered_style.append(" ".join(filtered_words))
            
            # Search for similar items
            similar_products = await self.vector_service.search_similar(
                query_vector=ref_embedding,
                collection_name="products",
                limit=limit * 3,  # Get more to filter by color
                score_threshold=0.3,
                exclude_ids=[product_id]
            )
            
            # Filter by target colors and style similarity
            color_variations = []
            for product in similar_products:
                # Check if product contains target colors
                product_text = f"{product.get('name', '')} {product.get('description', '')} {product.get('color', '')}".lower()
                
                color_match = any(color in product_text for color in expanded_colors)
                
                # Check style similarity (same category/subcategory)
                style_match = (
                    product.get("category") == ref_product.get("category") and
                    product.get("subcategory") == ref_product.get("subcategory")
                )
                
                if color_match and style_match:
                    product["color_match_reason"] = [color for color in expanded_colors if color in product_text]
                    color_variations.append(product)
                    
                    if len(color_variations) >= limit:
                        break
            
            return {
                "reference_product": ref_product,
                "target_colors": target_colors,
                "color_variations": color_variations[:limit],
                "total_found": len(color_variations),
                "search_strategy": "style_preserving_color_search"
            }
            
        except Exception as e:
            logger.error(f"Color variation search failed: {e}")
            raise RuntimeError(f"Color variation search failed: {str(e)}")
    
    async def find_cheaper_alternatives(
        self,
        product_id: str,
        max_price_ratio: float = 0.7,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Find cheaper alternatives to a luxury item while maintaining style similarity.
        
        Args:
            product_id: Reference luxury product ID
            max_price_ratio: Maximum price as ratio of original (0.7 = 70% of original price)
            limit: Maximum number of results
            
        Returns:
            Dictionary with cheaper alternatives
        """
        try:
            logger.info(f"Finding cheaper alternatives for product {product_id}")
            
            # Get the reference product
            ref_product = await self.vector_service.get_product_by_id(product_id)
            if not ref_product:
                raise ValueError(f"Product not found: {product_id}")
            
            ref_price = ref_product.get("price", 0)
            max_price = ref_price * max_price_ratio
            
            logger.info(f"Reference price: ${ref_price:.2f}, Max alternative price: ${max_price:.2f}")
            
            # Get product embedding for similarity search
            ref_embedding = await self.vector_service.get_product_embedding(product_id)
            if ref_embedding is None:
                raise ValueError(f"Product embedding not found: {product_id}")
            
            # Search for similar products
            similar_products = await self.vector_service.search_similar(
                query_vector=ref_embedding,
                collection_name="products",
                limit=limit * 4,  # Get more to filter by price
                score_threshold=0.2,
                exclude_ids=[product_id]
            )
            
            # Filter by price and calculate savings
            cheaper_alternatives = []
            for product in similar_products:
                product_price = product.get("price", float('inf'))
                
                if product_price <= max_price and product_price > 0:
                    savings = ref_price - product_price
                    savings_percentage = (savings / ref_price) * 100
                    
                    product["savings"] = savings
                    product["savings_percentage"] = savings_percentage
                    product["price_ratio"] = product_price / ref_price
                    
                    # Add style similarity score
                    product["style_similarity"] = product.get("score", 0.0)
                    
                    cheaper_alternatives.append(product)
            
            # Sort by best value (combination of savings and similarity)
            cheaper_alternatives.sort(
                key=lambda x: (x["savings_percentage"] * 0.6 + x["style_similarity"] * 0.4),
                reverse=True
            )
            
            return {
                "reference_product": ref_product,
                "reference_price": ref_price,
                "max_target_price": max_price,
                "cheaper_alternatives": cheaper_alternatives[:limit],
                "total_found": len(cheaper_alternatives),
                "average_savings": sum(p["savings_percentage"] for p in cheaper_alternatives[:limit]) / len(cheaper_alternatives[:limit]) if cheaper_alternatives else 0,
                "search_strategy": "price_conscious_similarity_search"
            }
            
        except Exception as e:
            logger.error(f"Cheaper alternatives search failed: {e}")
            raise RuntimeError(f"Cheaper alternatives search failed: {str(e)}")
    
    async def find_matching_accessories(
        self,
        clothing_product_id: str,
        accessory_types: Optional[List[str]] = None,
        limit: int = 15
    ) -> Dict[str, Any]:
        """
        Find accessories that complement a clothing item.
        
        Args:
            clothing_product_id: ID of the clothing item
            accessory_types: Specific accessory types to find (bags, shoes, jewelry, etc.)
            limit: Maximum number of results per accessory type
            
        Returns:
            Dictionary with matching accessories grouped by type
        """
        try:
            logger.info(f"Finding matching accessories for product {clothing_product_id}")
            
            # Get the reference clothing item
            ref_product = await self.vector_service.get_product_by_id(clothing_product_id)
            if not ref_product:
                raise ValueError(f"Product not found: {clothing_product_id}")
            
            # Default accessory types if not specified
            if not accessory_types:
                accessory_types = ["bags", "shoes", "jewelry", "scarves", "belts", "hats"]
            
            # Get clothing item details for matching
            clothing_style = ref_product.get("description", "").lower()
            clothing_color = ref_product.get("color", "").lower()
            clothing_season = ref_product.get("season", "").lower()
            clothing_gender = ref_product.get("gender", "").lower()
            
            # Create style-based search query
            style_keywords = [
                ref_product.get("name", ""),
                clothing_color,
                clothing_season,
                "complement",
                "match"
            ]
            
            style_query = " ".join(filter(None, style_keywords))
            
            # Encode the style query
            style_embedding = await self.clip_service.encode_text(style_query)
            
            matching_accessories = {}
            
            for accessory_type in accessory_types:
                logger.info(f"Searching for {accessory_type} accessories")
                
                # Search for accessories of this type
                accessories = await self.vector_service.search_similar(
                    query_vector=style_embedding,
                    collection_name="products",
                    limit=limit * 2,
                    score_threshold=0.1,
                    filter_conditions={
                        "category": "accessories",
                        "subcategory": accessory_type
                    }
                )
                
                # Filter and score accessories based on compatibility
                compatible_accessories = []
                for accessory in accessories:
                    compatibility_score = self._calculate_accessory_compatibility(
                        ref_product, accessory
                    )
                    
                    if compatibility_score > 0.3:  # Minimum compatibility threshold
                        accessory["compatibility_score"] = compatibility_score
                        accessory["match_reasons"] = self._get_match_reasons(ref_product, accessory)
                        compatible_accessories.append(accessory)
                
                # Sort by compatibility score
                compatible_accessories.sort(
                    key=lambda x: x["compatibility_score"],
                    reverse=True
                )
                
                if compatible_accessories:
                    matching_accessories[accessory_type] = compatible_accessories[:limit]
            
            return {
                "clothing_item": ref_product,
                "matching_accessories": matching_accessories,
                "total_accessories_found": sum(len(accessories) for accessories in matching_accessories.values()),
                "accessory_types_searched": accessory_types,
                "search_strategy": "style_compatibility_matching"
            }
            
        except Exception as e:
            logger.error(f"Accessory matching search failed: {e}")
            raise RuntimeError(f"Accessory matching search failed: {str(e)}")
    
    async def get_seasonal_recommendations(
        self,
        season: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get seasonal product recommendations based on current trends.
        
        Args:
            season: Target season (spring, summer, fall, winter)
            user_preferences: User style preferences and history
            limit: Maximum number of recommendations
            
        Returns:
            Dictionary with seasonal recommendations
        """
        try:
            logger.info(f"Getting seasonal recommendations for {season}")
            
            if season.lower() not in self.seasonal_keywords:
                raise ValueError(f"Invalid season: {season}. Must be one of: spring, summer, fall, winter")
            
            # Get seasonal keywords
            seasonal_terms = self.seasonal_keywords[season.lower()]
            
            # Incorporate user preferences
            style_preferences = []
            if user_preferences:
                style_preferences.extend(user_preferences.get("preferred_styles", []))
                style_preferences.extend(user_preferences.get("favorite_colors", []))
                style_preferences.extend(user_preferences.get("preferred_brands", []))
            
            # Create seasonal search query
            query_terms = seasonal_terms + style_preferences + [season, "trending", "fashion"]
            seasonal_query = " ".join(query_terms)
            
            # Encode the seasonal query
            query_embedding = await self.clip_service.encode_text(seasonal_query)
            
            # Search for seasonal products
            seasonal_products = await self.vector_service.search_similar(
                query_vector=query_embedding,
                collection_name="products",
                limit=limit * 2,
                score_threshold=0.1
            )
            
            # Group recommendations by category
            categorized_recommendations = {}
            trend_scores = {}
            
            for product in seasonal_products:
                category = product.get("category", "other")
                
                # Calculate trend score based on seasonal relevance
                trend_score = self._calculate_seasonal_relevance(product, season)
                product["trend_score"] = trend_score
                product["seasonal_reasons"] = self._get_seasonal_reasons(product, season)
                
                if category not in categorized_recommendations:
                    categorized_recommendations[category] = []
                    trend_scores[category] = []
                
                categorized_recommendations[category].append(product)
                trend_scores[category].append(trend_score)
            
            # Sort each category by trend score and limit results
            for category in categorized_recommendations:
                categorized_recommendations[category].sort(
                    key=lambda x: x["trend_score"],
                    reverse=True
                )
                # Keep top items per category
                category_limit = min(limit // len(categorized_recommendations), 10)
                categorized_recommendations[category] = categorized_recommendations[category][:category_limit]
            
            # Get overall top recommendations
            all_products = []
            for products in categorized_recommendations.values():
                all_products.extend(products)
            
            all_products.sort(key=lambda x: x["trend_score"], reverse=True)
            top_recommendations = all_products[:limit]
            
            return {
                "season": season,
                "seasonal_keywords": seasonal_terms,
                "user_preferences": user_preferences or {},
                "top_recommendations": top_recommendations,
                "categorized_recommendations": categorized_recommendations,
                "total_found": len(all_products),
                "average_trend_score": sum(p["trend_score"] for p in top_recommendations) / len(top_recommendations) if top_recommendations else 0,
                "search_strategy": "seasonal_trend_analysis"
            }
            
        except Exception as e:
            logger.error(f"Seasonal recommendations failed: {e}")
            raise RuntimeError(f"Seasonal recommendations failed: {str(e)}")
    
    async def style_evolution_search(
        self,
        product_id: str,
        target_style: str,
        intensity: float = 0.5,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Transform a product's style (make it more casual/formal/sporty/etc.).
        
        Args:
            product_id: Reference product ID
            target_style: Target style (casual, formal, sporty, bohemian, minimalist)
            intensity: How much to transform (0.0 = minimal, 1.0 = maximum)
            limit: Maximum number of results
            
        Returns:
            Dictionary with style evolution results
        """
        try:
            logger.info(f"Style evolution for product {product_id} to {target_style} (intensity: {intensity})")
            
            if target_style.lower() not in self.style_transforms:
                raise ValueError(f"Invalid target style: {target_style}")
            
            # Get the reference product
            ref_product = await self.vector_service.get_product_by_id(product_id)
            if not ref_product:
                raise ValueError(f"Product not found: {product_id}")
            
            # Get style transformation rules
            style_rules = self.style_transforms[target_style.lower()]
            target_keywords = style_rules["keywords"]
            avoid_keywords = style_rules["avoid"]
            
            # Create style evolution query
            base_description = f"{ref_product.get('name', '')} {ref_product.get('description', '')}"
            
            # Add target style keywords with intensity weighting
            style_query_parts = [base_description]
            
            # Add target style keywords
            weighted_style_keywords = []
            for keyword in target_keywords:
                # Repeat keywords based on intensity for stronger weighting
                repeat_count = max(1, int(intensity * 3))
                weighted_style_keywords.extend([keyword] * repeat_count)
            
            style_query = " ".join(style_query_parts + weighted_style_keywords)
            
            # Encode the style evolution query
            query_embedding = await self.clip_service.encode_text(style_query)
            
            # Search for style-evolved products
            evolved_products = await self.vector_service.search_similar(
                query_vector=query_embedding,
                collection_name="products",
                limit=limit * 3,
                score_threshold=0.1,
                exclude_ids=[product_id]
            )
            
            # Filter and score products based on style transformation
            style_evolved_results = []
            
            for product in evolved_products:
                product_text = f"{product.get('name', '')} {product.get('description', '')}".lower()
                
                # Calculate style alignment score
                style_score = self._calculate_style_alignment(
                    product_text, target_keywords, avoid_keywords
                )
                
                # Check if it's the same category (for meaningful comparison)
                category_match = product.get("category") == ref_product.get("category")
                
                if style_score > 0.3 and category_match:  # Minimum style alignment
                    product["style_score"] = style_score
                    product["style_transformation"] = target_style
                    product["transformation_intensity"] = intensity
                    product["style_reasons"] = self._get_style_transformation_reasons(
                        product_text, target_keywords
                    )
                    
                    style_evolved_results.append(product)
            
            # Sort by style alignment score
            style_evolved_results.sort(
                key=lambda x: x["style_score"],
                reverse=True
            )
            
            return {
                "original_product": ref_product,
                "target_style": target_style,
                "transformation_intensity": intensity,
                "style_evolved_products": style_evolved_results[:limit],
                "total_found": len(style_evolved_results),
                "average_style_score": sum(p["style_score"] for p in style_evolved_results[:limit]) / len(style_evolved_results[:limit]) if style_evolved_results else 0,
                "search_strategy": "style_transformation_search"
            }
            
        except Exception as e:
            logger.error(f"Style evolution search failed: {e}")
            raise RuntimeError(f"Style evolution search failed: {str(e)}")
    
    def _calculate_accessory_compatibility(
        self,
        clothing_item: Dict[str, Any],
        accessory: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score between clothing item and accessory"""
        score = 0.0
        
        # Color compatibility
        clothing_color = clothing_item.get("color", "").lower()
        accessory_color = accessory.get("color", "").lower()
        
        if clothing_color and accessory_color:
            if clothing_color == accessory_color:
                score += 0.3  # Exact color match
            elif self._colors_complement(clothing_color, accessory_color):
                score += 0.2  # Complementary colors
        
        # Season compatibility
        clothing_season = clothing_item.get("season", "").lower()
        accessory_season = accessory.get("season", "").lower()
        
        if clothing_season == accessory_season:
            score += 0.2
        
        # Gender compatibility
        clothing_gender = clothing_item.get("gender", "").lower()
        accessory_gender = accessory.get("gender", "").lower()
        
        if clothing_gender == accessory_gender or accessory_gender == "unisex":
            score += 0.2
        
        # Style/material compatibility
        clothing_desc = clothing_item.get("description", "").lower()
        accessory_desc = accessory.get("description", "").lower()
        
        style_keywords = ["casual", "formal", "elegant", "sporty", "vintage", "modern"]
        for keyword in style_keywords:
            if keyword in clothing_desc and keyword in accessory_desc:
                score += 0.1
        
        # Vector similarity score
        vector_similarity = accessory.get("score", 0.0)
        score += vector_similarity * 0.2
        
        return min(score, 1.0)
    
    def _colors_complement(self, color1: str, color2: str) -> bool:
        """Check if two colors complement each other"""
        # Define complementary color pairs
        complementary_pairs = [
            ("black", "white"), ("navy", "white"), ("brown", "cream"),
            ("red", "black"), ("blue", "brown"), ("green", "brown"),
            ("gray", "navy"), ("beige", "navy")
        ]
        
        for pair in complementary_pairs:
            if (color1 in pair[0] and color2 in pair[1]) or (color1 in pair[1] and color2 in pair[0]):
                return True
        
        return False
    
    def _get_match_reasons(
        self,
        clothing_item: Dict[str, Any],
        accessory: Dict[str, Any]
    ) -> List[str]:
        """Get reasons why an accessory matches the clothing item"""
        reasons = []
        
        if clothing_item.get("color") == accessory.get("color"):
            reasons.append(f"Matching {clothing_item.get('color')} color")
        
        if clothing_item.get("season") == accessory.get("season"):
            reasons.append(f"Perfect for {clothing_item.get('season')} season")
        
        if clothing_item.get("gender") == accessory.get("gender"):
            reasons.append("Gender-appropriate styling")
        
        return reasons
    
    def _calculate_seasonal_relevance(self, product: Dict[str, Any], season: str) -> float:
        """Calculate how relevant a product is for the given season"""
        score = 0.0
        
        product_text = f"{product.get('name', '')} {product.get('description', '')}".lower()
        seasonal_keywords = self.seasonal_keywords.get(season.lower(), [])
        
        # Check for seasonal keywords
        for keyword in seasonal_keywords:
            if keyword in product_text:
                score += 0.2
        
        # Check product season
        product_season = product.get("season", "").lower()
        if product_season == season.lower():
            score += 0.4
        
        # Vector similarity score
        vector_similarity = product.get("score", 0.0)
        score += vector_similarity * 0.4
        
        return min(score, 1.0)
    
    def _get_seasonal_reasons(self, product: Dict[str, Any], season: str) -> List[str]:
        """Get reasons why a product is recommended for the season"""
        reasons = []
        
        product_text = f"{product.get('name', '')} {product.get('description', '')}".lower()
        seasonal_keywords = self.seasonal_keywords.get(season.lower(), [])
        
        matched_keywords = [kw for kw in seasonal_keywords if kw in product_text]
        if matched_keywords:
            reasons.append(f"Features {season}-appropriate qualities: {', '.join(matched_keywords)}")
        
        if product.get("season", "").lower() == season.lower():
            reasons.append(f"Designed specifically for {season}")
        
        return reasons
    
    def _calculate_style_alignment(
        self,
        product_text: str,
        target_keywords: List[str],
        avoid_keywords: List[str]
    ) -> float:
        """Calculate how well a product aligns with target style"""
        score = 0.0
        
        # Positive score for target keywords
        for keyword in target_keywords:
            if keyword in product_text:
                score += 0.3
        
        # Negative score for avoided keywords
        for keyword in avoid_keywords:
            if keyword in product_text:
                score -= 0.2
        
        return max(0.0, min(score, 1.0))
    
    def _get_style_transformation_reasons(
        self,
        product_text: str,
        target_keywords: List[str]
    ) -> List[str]:
        """Get reasons for style transformation"""
        reasons = []
        
        matched_keywords = [kw for kw in target_keywords if kw in product_text]
        if matched_keywords:
            reasons.append(f"Embodies {', '.join(matched_keywords)} style elements")
        
        return reasons

    async def cleanup(self):
        """Clean up service resources"""
        try:
            await self.enhanced_search.cleanup()
            logger.info("Multi-Modal Search Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during multi-modal search service cleanup: {e}")
