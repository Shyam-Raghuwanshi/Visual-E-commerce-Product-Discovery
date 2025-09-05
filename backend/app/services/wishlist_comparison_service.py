"""
Wishlist and Product Comparison Service

Manages user wishlists, product comparisons, and related features
for enhanced e-commerce shopping experience.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import statistics

from app.models.business_schemas import (
    WishlistItem, ProductComparison, ComparisonMetrics,
    WishlistRequest
)
from app.services.database_service import db_manager
from app.services.cache_service import CacheService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

class WishlistComparisonService:
    """Wishlist and product comparison service"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.vector_service = VectorService()
        self.wishlist_cache_ttl = 1800  # 30 minutes cache for wishlists
        self.comparison_cache_ttl = 900  # 15 minutes cache for comparisons
        
        logger.info("Wishlist and Comparison Service initialized")
    
    async def add_to_wishlist(
        self,
        request: WishlistRequest
    ) -> WishlistItem:
        """
        Add item to user's wishlist
        
        Args:
            request: Wishlist action request
            
        Returns:
            Wishlist item record
        """
        try:
            if request.action != "add":
                raise ValueError("This method only handles 'add' actions")
            
            # Check if item already in wishlist
            existing_item = await self._get_wishlist_item(request.user_id, request.product_id)
            if existing_item:
                raise ValueError("Product already in wishlist")
            
            # Get product details for price tracking
            product_price = await self._get_product_price(request.product_id)
            
            # Create wishlist item
            wishlist_item = WishlistItem(
                user_id=request.user_id,
                product_id=request.product_id,
                priority=request.priority or 1,
                notes=request.notes,
                price_at_addition=product_price
            )
            
            # Save to database
            await self._save_wishlist_item(wishlist_item)
            
            # Invalidate cache
            await self._invalidate_wishlist_cache(request.user_id)
            
            logger.info(f"Product {request.product_id} added to wishlist for user {request.user_id}")
            return wishlist_item
            
        except Exception as e:
            logger.error(f"Add to wishlist failed: {e}")
            raise RuntimeError(f"Add to wishlist failed: {str(e)}")
    
    async def remove_from_wishlist(
        self,
        request: WishlistRequest
    ) -> bool:
        """
        Remove item from user's wishlist
        
        Args:
            request: Wishlist action request
            
        Returns:
            True if removal successful
        """
        try:
            if request.action != "remove":
                raise ValueError("This method only handles 'remove' actions")
            
            # Remove from database
            query = "DELETE FROM wishlist WHERE user_id = %s AND product_id = %s"
            await db_manager.execute_query(query, [request.user_id, request.product_id])
            
            # Invalidate cache
            await self._invalidate_wishlist_cache(request.user_id)
            
            logger.info(f"Product {request.product_id} removed from wishlist for user {request.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Remove from wishlist failed: {e}")
            return False
    
    async def update_wishlist_item(
        self,
        request: WishlistRequest
    ) -> Optional[WishlistItem]:
        """
        Update wishlist item details
        
        Args:
            request: Wishlist action request
            
        Returns:
            Updated wishlist item or None if not found
        """
        try:
            if request.action != "update":
                raise ValueError("This method only handles 'update' actions")
            
            # Get existing item
            existing_item = await self._get_wishlist_item(request.user_id, request.product_id)
            if not existing_item:
                return None
            
            # Update fields
            updates = {}
            if request.priority is not None:
                updates["priority"] = request.priority
            if request.notes is not None:
                updates["notes"] = request.notes
            
            if updates:
                # Update in database
                set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
                values = list(updates.values()) + [existing_item.id]
                
                query = f"UPDATE wishlist SET {set_clause} WHERE id = %s"
                await db_manager.execute_query(query, values)
                
                # Update the item object
                for key, value in updates.items():
                    setattr(existing_item, key, value)
                
                # Invalidate cache
                await self._invalidate_wishlist_cache(request.user_id)
            
            logger.info(f"Wishlist item updated for user {request.user_id}, product {request.product_id}")
            return existing_item
            
        except Exception as e:
            logger.error(f"Update wishlist item failed: {e}")
            return None
    
    async def get_user_wishlist(
        self,
        user_id: str,
        sort_by: str = "added_at",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get user's complete wishlist with product details
        
        Args:
            user_id: User identifier
            sort_by: Sort field (added_at, priority, price_at_addition)
            sort_order: Sort order (asc, desc)
            
        Returns:
            List of wishlist items with product details
        """
        try:
            # Check cache first
            cache_key = f"wishlist:{user_id}:{sort_by}:{sort_order}"
            cached_wishlist = await self.cache_service.get(cache_key)
            
            if cached_wishlist:
                return json.loads(cached_wishlist)
            
            # Get wishlist items with product details
            sort_clause = f"w.{sort_by} {'DESC' if sort_order.lower() == 'desc' else 'ASC'}"
            
            query = f"""
                SELECT 
                    w.*,
                    p.name, p.description, p.price as current_price, p.image_url,
                    p.category, p.brand, p.rating, p.in_stock
                FROM wishlist w
                JOIN products p ON w.product_id = p.id
                WHERE w.user_id = %s
                ORDER BY {sort_clause}
            """
            
            results = await db_manager.execute_query(query, [user_id])
            
            # Enhance with additional information
            enhanced_wishlist = []
            for item in results:
                # Calculate price change
                price_change = 0
                price_change_percentage = 0
                if item["price_at_addition"] and item["current_price"]:
                    price_change = item["current_price"] - item["price_at_addition"]
                    price_change_percentage = (price_change / item["price_at_addition"]) * 100
                
                # Check if item is on sale
                is_on_sale = price_change < -0.01  # Price dropped by more than 1 cent
                
                enhanced_item = {
                    "wishlist_id": item["id"],
                    "product_id": item["product_id"],
                    "product_name": item["name"],
                    "product_description": item["description"],
                    "current_price": item["current_price"],
                    "price_at_addition": item["price_at_addition"],
                    "price_change": price_change,
                    "price_change_percentage": price_change_percentage,
                    "is_on_sale": is_on_sale,
                    "image_url": item["image_url"],
                    "category": item["category"],
                    "brand": item["brand"],
                    "rating": item["rating"],
                    "in_stock": item["in_stock"],
                    "priority": item["priority"],
                    "notes": item["notes"],
                    "added_at": item["added_at"].isoformat(),
                    "notify_on_sale": item["notify_on_sale"],
                    "notify_on_restock": item["notify_on_restock"]
                }
                
                enhanced_wishlist.append(enhanced_item)
            
            # Cache the result
            await self.cache_service.set(
                cache_key, 
                json.dumps(enhanced_wishlist, default=str), 
                self.wishlist_cache_ttl
            )
            
            return enhanced_wishlist
            
        except Exception as e:
            logger.error(f"Get user wishlist failed for {user_id}: {e}")
            raise RuntimeError(f"Wishlist retrieval failed: {str(e)}")
    
    async def get_wishlist_analytics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get analytics for user's wishlist
        
        Args:
            user_id: User identifier
            
        Returns:
            Wishlist analytics
        """
        try:
            wishlist = await self.get_user_wishlist(user_id)
            
            if not wishlist:
                return {
                    "total_items": 0,
                    "analysis": "empty_wishlist"
                }
            
            # Calculate analytics
            total_items = len(wishlist)
            total_value_at_addition = sum(item["price_at_addition"] or 0 for item in wishlist)
            total_current_value = sum(item["current_price"] or 0 for item in wishlist)
            total_savings = total_value_at_addition - total_current_value
            
            # Category distribution
            categories = [item["category"] for item in wishlist if item["category"]]
            category_counts = {}
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Brand distribution
            brands = [item["brand"] for item in wishlist if item["brand"]]
            brand_counts = {}
            for brand in brands:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
            
            # Price tier analysis
            price_tiers = {"budget": 0, "mid": 0, "premium": 0}
            for item in wishlist:
                price = item["current_price"] or 0
                if price < 25:
                    price_tiers["budget"] += 1
                elif price < 100:
                    price_tiers["mid"] += 1
                else:
                    price_tiers["premium"] += 1
            
            # Availability analysis
            in_stock_count = sum(1 for item in wishlist if item["in_stock"])
            out_of_stock_count = total_items - in_stock_count
            
            # Sale opportunities
            items_on_sale = [item for item in wishlist if item["is_on_sale"]]
            potential_savings = sum(abs(item["price_change"]) for item in items_on_sale)
            
            return {
                "total_items": total_items,
                "value_summary": {
                    "total_value_at_addition": total_value_at_addition,
                    "total_current_value": total_current_value,
                    "total_savings": total_savings,
                    "average_item_price": total_current_value / total_items if total_items > 0 else 0
                },
                "category_distribution": category_counts,
                "brand_distribution": brand_counts,
                "price_tier_distribution": price_tiers,
                "availability": {
                    "in_stock": in_stock_count,
                    "out_of_stock": out_of_stock_count,
                    "availability_rate": in_stock_count / total_items if total_items > 0 else 0
                },
                "sale_opportunities": {
                    "items_on_sale": len(items_on_sale),
                    "potential_savings": potential_savings,
                    "best_deals": sorted(items_on_sale, key=lambda x: x["price_change"])[:5]
                },
                "recommendations": await self._generate_wishlist_recommendations(user_id, wishlist)
            }
            
        except Exception as e:
            logger.error(f"Wishlist analytics failed for {user_id}: {e}")
            raise RuntimeError(f"Wishlist analytics failed: {str(e)}")
    
    async def create_product_comparison(
        self,
        user_id: str,
        product_ids: List[str],
        comparison_criteria: Optional[List[str]] = None
    ) -> ProductComparison:
        """
        Create a new product comparison session
        
        Args:
            user_id: User identifier
            product_ids: List of product IDs to compare
            comparison_criteria: Specific criteria for comparison
            
        Returns:
            Product comparison session
        """
        try:
            if len(product_ids) < 2:
                raise ValueError("At least 2 products required for comparison")
            
            if len(product_ids) > 5:
                raise ValueError("Maximum 5 products allowed for comparison")
            
            # Verify all products exist
            for product_id in product_ids:
                if not await self._product_exists(product_id):
                    raise ValueError(f"Product not found: {product_id}")
            
            comparison = ProductComparison(
                user_id=user_id,
                product_ids=product_ids,
                comparison_criteria=comparison_criteria or []
            )
            
            # Save to database
            await self._save_product_comparison(comparison)
            
            logger.info(f"Product comparison created for user {user_id} with {len(product_ids)} products")
            return comparison
            
        except Exception as e:
            logger.error(f"Product comparison creation failed: {e}")
            raise RuntimeError(f"Comparison creation failed: {str(e)}")
    
    async def get_comparison_details(
        self,
        comparison_id: str,
        user_id: str
    ) -> Optional[ComparisonMetrics]:
        """
        Get detailed comparison metrics for products
        
        Args:
            comparison_id: Comparison session identifier
            user_id: User identifier (for security)
            
        Returns:
            Detailed comparison metrics or None if not found
        """
        try:
            # Check cache first
            cache_key = f"comparison:{comparison_id}"
            cached_comparison = await self.cache_service.get(cache_key)
            
            if cached_comparison:
                return ComparisonMetrics(**json.loads(cached_comparison))
            
            # Get comparison from database
            comparison = await self._get_comparison_from_db(comparison_id, user_id)
            if not comparison:
                return None
            
            # Get detailed product information
            products = await self._get_products_details(comparison.product_ids)
            
            if not products:
                return None
            
            # Calculate similarity scores between products
            similarity_scores = await self._calculate_product_similarities(products)
            
            # Identify key differences
            key_differences = await self._identify_key_differences(products)
            
            # Generate recommendations
            recommendations = await self._generate_comparison_recommendations(products)
            
            # Perform price analysis
            price_analysis = await self._analyze_comparison_prices(products)
            
            comparison_metrics = ComparisonMetrics(
                comparison_id=comparison_id,
                products=products,
                similarity_scores=similarity_scores,
                key_differences=key_differences,
                recommendations=recommendations,
                price_analysis=price_analysis
            )
            
            # Cache the result
            await self.cache_service.set(
                cache_key, 
                comparison_metrics.json(), 
                self.comparison_cache_ttl
            )
            
            # Update last accessed time
            await self._update_comparison_access_time(comparison_id)
            
            return comparison_metrics
            
        except Exception as e:
            logger.error(f"Comparison details retrieval failed for {comparison_id}: {e}")
            return None
    
    async def get_user_comparisons(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[ProductComparison]:
        """
        Get user's comparison history
        
        Args:
            user_id: User identifier
            limit: Maximum number of comparisons to return
            
        Returns:
            List of user's comparisons
        """
        try:
            query = """
                SELECT * FROM product_comparisons 
                WHERE user_id = %s 
                ORDER BY last_accessed DESC
                LIMIT %s
            """
            
            results = await db_manager.execute_query(query, [user_id, limit])
            
            comparisons = []
            for row in results:
                comparison = ProductComparison(
                    id=row["id"],
                    user_id=row["user_id"],
                    product_ids=json.loads(row["product_ids"]),
                    comparison_criteria=json.loads(row["comparison_criteria"]) if row["comparison_criteria"] else [],
                    created_at=row["created_at"],
                    last_accessed=row["last_accessed"],
                    notes=row["notes"]
                )
                comparisons.append(comparison)
            
            return comparisons
            
        except Exception as e:
            logger.error(f"User comparisons retrieval failed for {user_id}: {e}")
            return []
    
    async def delete_comparison(
        self,
        comparison_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a product comparison
        
        Args:
            comparison_id: Comparison identifier
            user_id: User identifier (for security)
            
        Returns:
            True if deletion successful
        """
        try:
            query = "DELETE FROM product_comparisons WHERE id = %s AND user_id = %s"
            await db_manager.execute_query(query, [comparison_id, user_id])
            
            # Remove from cache
            cache_key = f"comparison:{comparison_id}"
            await self.cache_service.delete(cache_key)
            
            logger.info(f"Comparison {comparison_id} deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Comparison deletion failed: {e}")
            return False
    
    async def get_similar_products_for_wishlist(
        self,
        user_id: str,
        product_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get products similar to a wishlist item
        
        Args:
            user_id: User identifier
            product_id: Product ID from wishlist
            limit: Maximum number of similar products
            
        Returns:
            List of similar products
        """
        try:
            # Verify product is in user's wishlist
            wishlist_item = await self._get_wishlist_item(user_id, product_id)
            if not wishlist_item:
                raise ValueError("Product not found in user's wishlist")
            
            # Get product embedding for similarity search
            try:
                product_embedding = await self.vector_service.get_product_embedding(product_id)
                if product_embedding is None:
                    # Fallback to category-based similarity
                    return await self._get_category_based_similar_products(product_id, limit)
                
                # Search for similar products
                similar_products = await self.vector_service.search_similar(
                    query_vector=product_embedding,
                    collection_name="products",
                    limit=limit + 1,  # +1 to exclude the original product
                    score_threshold=0.5,
                    exclude_ids=[product_id]
                )
                
                return similar_products[:limit]
                
            except Exception as ve:
                logger.warning(f"Vector search failed, using fallback: {ve}")
                return await self._get_category_based_similar_products(product_id, limit)
            
        except Exception as e:
            logger.error(f"Similar products search failed: {e}")
            return []
    
    # Private helper methods
    
    async def _get_wishlist_item(self, user_id: str, product_id: str) -> Optional[WishlistItem]:
        """Get wishlist item from database"""
        try:
            query = "SELECT * FROM wishlist WHERE user_id = %s AND product_id = %s"
            results = await db_manager.execute_query(query, [user_id, product_id])
            
            if results:
                return WishlistItem(**results[0])
            return None
            
        except Exception as e:
            logger.error(f"Wishlist item retrieval failed: {e}")
            return None
    
    async def _get_product_price(self, product_id: str) -> Optional[float]:
        """Get current product price"""
        try:
            query = "SELECT price FROM products WHERE id = %s"
            results = await db_manager.execute_query(query, [product_id])
            
            if results:
                return float(results[0]["price"])
            return None
            
        except Exception as e:
            logger.error(f"Product price retrieval failed: {e}")
            return None
    
    async def _save_wishlist_item(self, item: WishlistItem):
        """Save wishlist item to database"""
        try:
            query = """
                INSERT INTO wishlist 
                (id, user_id, product_id, added_at, priority, notes, 
                 price_at_addition, notify_on_sale, notify_on_restock)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                item.id,
                item.user_id,
                item.product_id,
                item.added_at,
                item.priority,
                item.notes,
                item.price_at_addition,
                item.notify_on_sale,
                item.notify_on_restock
            ])
            
        except Exception as e:
            logger.error(f"Wishlist item save failed: {e}")
            raise
    
    async def _invalidate_wishlist_cache(self, user_id: str):
        """Invalidate wishlist cache for user"""
        try:
            # Remove all cached wishlist variations for this user
            cache_patterns = [
                f"wishlist:{user_id}:*"
            ]
            
            for pattern in cache_patterns:
                await self.cache_service.delete_pattern(pattern)
                
        except Exception as e:
            logger.error(f"Wishlist cache invalidation failed: {e}")
    
    async def _product_exists(self, product_id: str) -> bool:
        """Check if product exists"""
        try:
            query = "SELECT 1 FROM products WHERE id = %s"
            results = await db_manager.execute_query(query, [product_id])
            return len(results) > 0
        except Exception:
            return False
    
    async def _save_product_comparison(self, comparison: ProductComparison):
        """Save product comparison to database"""
        try:
            query = """
                INSERT INTO product_comparisons 
                (id, user_id, product_ids, comparison_criteria, created_at, last_accessed, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                comparison.id,
                comparison.user_id,
                json.dumps(comparison.product_ids),
                json.dumps(comparison.comparison_criteria),
                comparison.created_at,
                comparison.last_accessed,
                comparison.notes
            ])
            
        except Exception as e:
            logger.error(f"Product comparison save failed: {e}")
            raise
    
    async def _get_comparison_from_db(
        self, 
        comparison_id: str, 
        user_id: str
    ) -> Optional[ProductComparison]:
        """Get comparison from database"""
        try:
            query = "SELECT * FROM product_comparisons WHERE id = %s AND user_id = %s"
            results = await db_manager.execute_query(query, [comparison_id, user_id])
            
            if results:
                row = results[0]
                return ProductComparison(
                    id=row["id"],
                    user_id=row["user_id"],
                    product_ids=json.loads(row["product_ids"]),
                    comparison_criteria=json.loads(row["comparison_criteria"]) if row["comparison_criteria"] else [],
                    created_at=row["created_at"],
                    last_accessed=row["last_accessed"],
                    notes=row["notes"]
                )
            return None
            
        except Exception as e:
            logger.error(f"Comparison retrieval failed: {e}")
            return None
    
    async def _get_products_details(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed product information"""
        try:
            if not product_ids:
                return []
            
            placeholders = ",".join(["%s"] * len(product_ids))
            query = f"""
                SELECT * FROM products 
                WHERE id IN ({placeholders})
            """
            
            results = await db_manager.execute_query(query, product_ids)
            return results
            
        except Exception as e:
            logger.error(f"Product details retrieval failed: {e}")
            return []
    
    async def _calculate_product_similarities(
        self, 
        products: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate similarity scores between products"""
        try:
            similarities = {}
            
            for i, product1 in enumerate(products):
                for j, product2 in enumerate(products[i+1:], i+1):
                    product1_id = product1["id"]
                    product2_id = product2["id"]
                    
                    # Calculate similarity based on various factors
                    similarity = 0.0
                    
                    # Category similarity
                    if product1.get("category") == product2.get("category"):
                        similarity += 0.3
                    
                    # Brand similarity
                    if product1.get("brand") == product2.get("brand"):
                        similarity += 0.2
                    
                    # Price similarity (within 20% range)
                    price1 = product1.get("price", 0)
                    price2 = product2.get("price", 0)
                    if price1 > 0 and price2 > 0:
                        price_diff = abs(price1 - price2) / max(price1, price2)
                        if price_diff <= 0.2:
                            similarity += 0.2
                    
                    # Rating similarity
                    rating1 = product1.get("rating", 0)
                    rating2 = product2.get("rating", 0)
                    if rating1 > 0 and rating2 > 0:
                        rating_diff = abs(rating1 - rating2) / 5.0  # Ratings are 0-5
                        similarity += (1 - rating_diff) * 0.1
                    
                    # Description similarity (simple keyword overlap)
                    desc1 = set(product1.get("description", "").lower().split())
                    desc2 = set(product2.get("description", "").lower().split())
                    if desc1 and desc2:
                        overlap = len(desc1 & desc2) / len(desc1 | desc2)
                        similarity += overlap * 0.2
                    
                    key = f"{product1_id}_vs_{product2_id}"
                    similarities[key] = min(similarity, 1.0)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Product similarity calculation failed: {e}")
            return {}
    
    async def _identify_key_differences(
        self, 
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify key differences between products"""
        try:
            differences = []
            
            if len(products) < 2:
                return differences
            
            # Price differences
            prices = [(p["id"], p.get("price", 0)) for p in products]
            prices.sort(key=lambda x: x[1])
            
            if prices[-1][1] > prices[0][1]:
                differences.append({
                    "aspect": "price",
                    "description": f"Price range: ${prices[0][1]:.2f} to ${prices[-1][1]:.2f}",
                    "cheapest": prices[0][0],
                    "most_expensive": prices[-1][0],
                    "savings_potential": prices[-1][1] - prices[0][1]
                })
            
            # Rating differences
            ratings = [(p["id"], p.get("rating", 0)) for p in products if p.get("rating")]
            if ratings:
                ratings.sort(key=lambda x: x[1], reverse=True)
                if ratings[0][1] > ratings[-1][1]:
                    differences.append({
                        "aspect": "rating",
                        "description": f"Rating range: {ratings[-1][1]:.1f} to {ratings[0][1]:.1f}",
                        "highest_rated": ratings[0][0],
                        "lowest_rated": ratings[-1][0]
                    })
            
            # Brand differences
            brands = set(p.get("brand") for p in products if p.get("brand"))
            if len(brands) > 1:
                differences.append({
                    "aspect": "brands",
                    "description": f"Multiple brands: {', '.join(brands)}",
                    "brand_count": len(brands)
                })
            
            # Category differences
            categories = set(p.get("category") for p in products if p.get("category"))
            if len(categories) > 1:
                differences.append({
                    "aspect": "categories",
                    "description": f"Different categories: {', '.join(categories)}",
                    "category_count": len(categories)
                })
            
            return differences
            
        except Exception as e:
            logger.error(f"Key differences identification failed: {e}")
            return []
    
    async def _generate_comparison_recommendations(
        self, 
        products: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on product comparison"""
        try:
            recommendations = []
            
            if len(products) < 2:
                return recommendations
            
            # Find best value product
            value_scores = []
            for product in products:
                price = product.get("price", float('inf'))
                rating = product.get("rating", 0)
                # Simple value score: rating / price (higher is better)
                value_score = rating / price if price > 0 else 0
                value_scores.append((product["id"], value_score, product.get("name", "Unknown")))
            
            value_scores.sort(key=lambda x: x[1], reverse=True)
            
            if value_scores:
                best_value = value_scores[0]
                recommendations.append(f"Best value: {best_value[2]} offers the best rating-to-price ratio")
            
            # Find cheapest option
            cheapest = min(products, key=lambda p: p.get("price", float('inf')))
            recommendations.append(f"Budget option: {cheapest.get('name', 'Unknown')} at ${cheapest.get('price', 0):.2f}")
            
            # Find highest rated
            highest_rated = max(products, key=lambda p: p.get("rating", 0))
            if highest_rated.get("rating", 0) > 0:
                recommendations.append(f"Top rated: {highest_rated.get('name', 'Unknown')} with {highest_rated.get('rating', 0):.1f} stars")
            
            # Check for sales/discounts
            for product in products:
                if product.get("discount_percentage", 0) > 10:
                    recommendations.append(f"Sale opportunity: {product.get('name', 'Unknown')} is {product.get('discount_percentage', 0):.0f}% off")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Comparison recommendations generation failed: {e}")
            return []
    
    async def _analyze_comparison_prices(
        self, 
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze price patterns in comparison"""
        try:
            prices = [p.get("price", 0) for p in products if p.get("price", 0) > 0]
            
            if not prices:
                return {"error": "No price data available"}
            
            analysis = {
                "min_price": min(prices),
                "max_price": max(prices),
                "average_price": statistics.mean(prices),
                "median_price": statistics.median(prices),
                "price_spread": max(prices) - min(prices),
                "price_variance": statistics.variance(prices) if len(prices) > 1 else 0
            }
            
            # Price distribution
            budget_count = sum(1 for p in prices if p < 25)
            mid_count = sum(1 for p in prices if 25 <= p < 100)
            premium_count = sum(1 for p in prices if p >= 100)
            
            analysis["price_distribution"] = {
                "budget": budget_count,
                "mid_range": mid_count,
                "premium": premium_count
            }
            
            # Price insights
            insights = []
            if analysis["price_spread"] > 50:
                insights.append("Wide price range - consider your budget carefully")
            
            if len(set(prices)) == 1:
                insights.append("All products are similarly priced")
            
            analysis["insights"] = insights
            
            return analysis
            
        except Exception as e:
            logger.error(f"Price analysis failed: {e}")
            return {"error": "Price analysis failed"}
    
    async def _update_comparison_access_time(self, comparison_id: str):
        """Update last accessed time for comparison"""
        try:
            query = "UPDATE product_comparisons SET last_accessed = %s WHERE id = %s"
            await db_manager.execute_query(query, [datetime.now(), comparison_id])
        except Exception as e:
            logger.error(f"Comparison access time update failed: {e}")
    
    async def _generate_wishlist_recommendations(
        self, 
        user_id: str, 
        wishlist: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on wishlist analysis"""
        try:
            recommendations = []
            
            if not wishlist:
                return recommendations
            
            # Check for sale opportunities
            items_on_sale = [item for item in wishlist if item["is_on_sale"]]
            if items_on_sale:
                recommendations.append(f"{len(items_on_sale)} items in your wishlist are currently on sale!")
            
            # Check for out of stock items
            out_of_stock = [item for item in wishlist if not item["in_stock"]]
            if out_of_stock:
                recommendations.append(f"{len(out_of_stock)} items are currently out of stock - consider setting restock alerts")
            
            # Price diversity recommendations
            prices = [item["current_price"] for item in wishlist if item["current_price"]]
            if prices:
                avg_price = statistics.mean(prices)
                if avg_price > 100:
                    recommendations.append("Your wishlist contains mainly premium items - consider adding some budget alternatives")
                elif avg_price < 25:
                    recommendations.append("Great job keeping your wishlist budget-friendly!")
            
            # Category diversity
            categories = set(item["category"] for item in wishlist if item["category"])
            if len(categories) == 1:
                recommendations.append("Consider exploring products from other categories to diversify your wishlist")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Wishlist recommendations generation failed: {e}")
            return []
    
    async def _get_category_based_similar_products(
        self, 
        product_id: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fallback method to get similar products based on category"""
        try:
            # Get product category
            query = "SELECT category, subcategory, brand FROM products WHERE id = %s"
            results = await db_manager.execute_query(query, [product_id])
            
            if not results:
                return []
            
            product = results[0]
            
            # Find similar products in same category
            similar_query = """
                SELECT * FROM products 
                WHERE category = %s 
                AND id != %s
                ORDER BY 
                    CASE WHEN subcategory = %s THEN 0 ELSE 1 END,
                    CASE WHEN brand = %s THEN 0 ELSE 1 END,
                    rating DESC
                LIMIT %s
            """
            
            similar_results = await db_manager.execute_query(similar_query, [
                product["category"],
                product_id,
                product["subcategory"],
                product["brand"],
                limit
            ])
            
            return similar_results
            
        except Exception as e:
            logger.error(f"Category-based similar products search failed: {e}")
            return []
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            logger.info("Wishlist and Comparison Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during wishlist service cleanup: {e}")

# Global wishlist and comparison service instance
wishlist_comparison_service = WishlistComparisonService()
