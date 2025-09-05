"""
User Preferences and Behavior Analytics Service

Manages user preferences, search history, and behavioral analytics
for personalized e-commerce experiences.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter
import statistics

from app.models.business_schemas import (
    UserPreferences, SearchHistory, UserActivity, UserActivityType,
    UserBehaviorAnalytics
)
from app.services.database_service import db_manager
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class UserBehaviorService:
    """User preferences and behavior analytics service"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.preferences_cache_ttl = 3600  # 1 hour cache for user preferences
        self.behavior_cache_ttl = 1800  # 30 minutes for behavior data
        
        # Behavior analysis thresholds
        self.min_sessions_for_analysis = 5
        self.recent_activity_days = 30
        
        logger.info("User Behavior Service initialized")
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences with caching
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences or None if not found
        """
        try:
            # Check cache first
            cache_key = f"user_preferences:{user_id}"
            cached_prefs = await self.cache_service.get(cache_key)
            
            if cached_prefs:
                return UserPreferences(**json.loads(cached_prefs))
            
            # Get from database
            query = "SELECT * FROM user_preferences WHERE user_id = %s"
            results = await db_manager.execute_query(query, [user_id])
            
            if results:
                preferences = UserPreferences(**results[0])
                # Cache the result
                await self.cache_service.set(
                    cache_key, 
                    preferences.json(), 
                    self.preferences_cache_ttl
                )
                return preferences
            
            return None
            
        except Exception as e:
            logger.error(f"User preferences retrieval failed for {user_id}: {e}")
            return None
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences_update: Dict[str, Any]
    ) -> UserPreferences:
        """
        Update user preferences
        
        Args:
            user_id: User identifier
            preferences_update: Preferences to update
            
        Returns:
            Updated user preferences
        """
        try:
            # Get current preferences or create new
            current_prefs = await self.get_user_preferences(user_id)
            
            if current_prefs:
                # Update existing preferences
                prefs_dict = current_prefs.dict()
                prefs_dict.update(preferences_update)
                prefs_dict["updated_at"] = datetime.now()
                preferences = UserPreferences(**prefs_dict)
                
                # Update in database
                await self._update_preferences_in_db(preferences)
            else:
                # Create new preferences
                preferences_update["user_id"] = user_id
                preferences = UserPreferences(**preferences_update)
                
                # Insert into database
                await self._insert_preferences_in_db(preferences)
            
            # Update cache
            cache_key = f"user_preferences:{user_id}"
            await self.cache_service.set(
                cache_key, 
                preferences.json(), 
                self.preferences_cache_ttl
            )
            
            logger.info(f"User preferences updated for {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"User preferences update failed for {user_id}: {e}")
            raise RuntimeError(f"Preferences update failed: {str(e)}")
    
    async def track_search_activity(
        self,
        user_id: str,
        search_query: Optional[str],
        search_type: str,
        filters_applied: Dict[str, Any],
        results_count: int,
        session_id: Optional[str] = None,
        device_info: Optional[Dict[str, str]] = None
    ) -> SearchHistory:
        """
        Track user search activity
        
        Args:
            user_id: User identifier
            search_query: Search query text
            search_type: Type of search performed
            filters_applied: Applied search filters
            results_count: Number of results returned
            session_id: User session identifier
            device_info: Device and browser information
            
        Returns:
            Search history record
        """
        try:
            search_record = SearchHistory(
                user_id=user_id,
                search_query=search_query,
                search_type=search_type,
                filters_applied=filters_applied,
                results_count=results_count,
                session_id=session_id,
                device_info=device_info
            )
            
            # Save to database
            await self._save_search_history(search_record)
            
            # Update user preferences based on search behavior
            await self._update_preferences_from_search(user_id, search_record)
            
            logger.debug(f"Search activity tracked for user {user_id}")
            return search_record
            
        except Exception as e:
            logger.error(f"Search activity tracking failed for {user_id}: {e}")
            raise RuntimeError(f"Search tracking failed: {str(e)}")
    
    async def track_user_activity(
        self,
        user_id: str,
        activity_type: UserActivityType,
        product_id: Optional[str] = None,
        activity_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserActivity:
        """
        Track general user activity
        
        Args:
            user_id: User identifier
            activity_type: Type of activity
            product_id: Related product (if applicable)
            activity_data: Additional activity data
            session_id: User session identifier
            ip_address: User IP address
            user_agent: User agent string
            
        Returns:
            User activity record
        """
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                product_id=product_id,
                activity_data=activity_data or {},
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Save to database
            await self._save_user_activity(activity)
            
            # Update user preferences based on activity
            await self._update_preferences_from_activity(user_id, activity)
            
            logger.debug(f"User activity tracked: {user_id} - {activity_type.value}")
            return activity
            
        except Exception as e:
            logger.error(f"User activity tracking failed for {user_id}: {e}")
            raise RuntimeError(f"Activity tracking failed: {str(e)}")
    
    async def get_user_search_history(
        self,
        user_id: str,
        limit: int = 50,
        days: int = 30
    ) -> List[SearchHistory]:
        """
        Get user's search history
        
        Args:
            user_id: User identifier
            limit: Maximum number of records
            days: Number of days to look back
            
        Returns:
            List of search history records
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT * FROM search_history 
                WHERE user_id = %s AND search_timestamp >= %s
                ORDER BY search_timestamp DESC
                LIMIT %s
            """
            
            results = await db_manager.execute_query(query, [user_id, start_date, limit])
            
            return [SearchHistory(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Search history retrieval failed for {user_id}: {e}")
            raise RuntimeError(f"Search history retrieval failed: {str(e)}")
    
    async def analyze_user_behavior(
        self,
        user_id: str,
        analysis_period_days: int = 30
    ) -> UserBehaviorAnalytics:
        """
        Analyze user behavior patterns
        
        Args:
            user_id: User identifier
            analysis_period_days: Period for analysis
            
        Returns:
            User behavior analytics
        """
        try:
            start_date = datetime.now() - timedelta(days=analysis_period_days)
            
            # Get user activities
            activities = await self._get_user_activities(user_id, start_date)
            search_history = await self.get_user_search_history(user_id, 1000, analysis_period_days)
            
            if len(activities) < self.min_sessions_for_analysis:
                # Not enough data for meaningful analysis
                return UserBehaviorAnalytics(
                    user_id=user_id,
                    analysis_period=f"{analysis_period_days}_days",
                    browsing_patterns={"insufficient_data": True}
                )
            
            # Analyze session patterns
            sessions = self._group_activities_by_session(activities)
            
            # Calculate metrics
            total_sessions = len(sessions)
            total_page_views = len([a for a in activities if a.activity_type == UserActivityType.VIEW_PRODUCT])
            total_searches = len(search_history)
            products_viewed = len(set(a.product_id for a in activities if a.product_id))
            products_wishlisted = len([a for a in activities if a.activity_type == UserActivityType.ADD_TO_WISHLIST])
            products_purchased = len([a for a in activities if a.activity_type == UserActivityType.PURCHASE])
            
            # Session duration analysis
            session_durations = []
            for session_activities in sessions.values():
                if len(session_activities) > 1:
                    start_time = min(a.timestamp for a in session_activities)
                    end_time = max(a.timestamp for a in session_activities)
                    duration = (end_time - start_time).total_seconds() / 60  # minutes
                    session_durations.append(duration)
            
            avg_session_duration = statistics.mean(session_durations) if session_durations else 0
            
            # Category preferences
            category_counts = Counter()
            for activity in activities:
                if activity.product_id and activity.activity_type == UserActivityType.VIEW_PRODUCT:
                    # Get product category (would need to join with products table)
                    category = activity.activity_data.get("category", "unknown")
                    category_counts[category] += 1
            
            preferred_categories = [cat for cat, _ in category_counts.most_common(5)]
            
            # Browsing patterns
            browsing_patterns = await self._analyze_browsing_patterns(activities, search_history)
            
            # Purchase behavior
            purchase_history_summary = await self._analyze_purchase_behavior(user_id, start_date)
            
            return UserBehaviorAnalytics(
                user_id=user_id,
                analysis_period=f"{analysis_period_days}_days",
                total_sessions=total_sessions,
                total_page_views=total_page_views,
                total_searches=total_searches,
                products_viewed=products_viewed,
                products_wishlisted=products_wishlisted,
                products_purchased=products_purchased,
                average_session_duration=avg_session_duration,
                preferred_categories=preferred_categories,
                browsing_patterns=browsing_patterns,
                purchase_history_summary=purchase_history_summary
            )
            
        except Exception as e:
            logger.error(f"User behavior analysis failed for {user_id}: {e}")
            raise RuntimeError(f"Behavior analysis failed: {str(e)}")
    
    async def get_similar_users(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find users with similar behavior patterns
        
        Args:
            user_id: User identifier
            limit: Maximum number of similar users
            
        Returns:
            List of similar users with similarity scores
        """
        try:
            # Get user preferences
            user_prefs = await self.get_user_preferences(user_id)
            if not user_prefs:
                return []
            
            # Get user behavior
            user_behavior = await self.analyze_user_behavior(user_id)
            
            # Find users with similar preferences
            similar_users = await self._find_similar_users_by_preferences(user_prefs, limit * 2)
            
            # Calculate similarity scores
            similarity_results = []
            for similar_user in similar_users:
                if similar_user["user_id"] == user_id:
                    continue
                
                similarity_score = await self._calculate_user_similarity(
                    user_behavior, 
                    similar_user["user_id"]
                )
                
                if similarity_score > 0.3:  # Minimum similarity threshold
                    similarity_results.append({
                        "user_id": similar_user["user_id"],
                        "similarity_score": similarity_score,
                        "common_categories": similar_user.get("common_categories", []),
                        "common_brands": similar_user.get("common_brands", [])
                    })
            
            # Sort by similarity score
            similarity_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return similarity_results[:limit]
            
        except Exception as e:
            logger.error(f"Similar users search failed for {user_id}: {e}")
            return []
    
    async def update_search_click_through(
        self,
        search_id: str,
        clicked_product_ids: List[str]
    ):
        """
        Update search history with clicked products
        
        Args:
            search_id: Search history record ID
            clicked_product_ids: List of clicked product IDs
        """
        try:
            query = """
                UPDATE search_history 
                SET clicked_products = %s
                WHERE id = %s
            """
            
            await db_manager.execute_query(query, [json.dumps(clicked_product_ids), search_id])
            
            logger.debug(f"Search click-through updated for search {search_id}")
            
        except Exception as e:
            logger.error(f"Search click-through update failed: {e}")
    
    # Private helper methods
    
    async def _save_search_history(self, search_record: SearchHistory):
        """Save search history to database"""
        try:
            query = """
                INSERT INTO search_history 
                (id, user_id, search_query, search_type, filters_applied, 
                 results_count, clicked_products, search_timestamp, session_id, device_info)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                search_record.id,
                search_record.user_id,
                search_record.search_query,
                search_record.search_type,
                json.dumps(search_record.filters_applied),
                search_record.results_count,
                json.dumps(search_record.clicked_products),
                search_record.search_timestamp,
                search_record.session_id,
                json.dumps(search_record.device_info) if search_record.device_info else None
            ])
            
        except Exception as e:
            logger.error(f"Search history save failed: {e}")
            raise
    
    async def _save_user_activity(self, activity: UserActivity):
        """Save user activity to database"""
        try:
            query = """
                INSERT INTO user_activity 
                (id, user_id, activity_type, product_id, activity_data, 
                 timestamp, session_id, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                activity.id,
                activity.user_id,
                activity.activity_type.value,
                activity.product_id,
                json.dumps(activity.activity_data),
                activity.timestamp,
                activity.session_id,
                activity.ip_address,
                activity.user_agent
            ])
            
        except Exception as e:
            logger.error(f"User activity save failed: {e}")
            raise
    
    async def _update_preferences_from_search(
        self, 
        user_id: str, 
        search_record: SearchHistory
    ):
        """Update user preferences based on search behavior"""
        try:
            # Extract preferences from search filters
            filters = search_record.filters_applied
            
            updates = {}
            
            # Update preferred categories
            if "categories" in filters:
                current_prefs = await self.get_user_preferences(user_id)
                if current_prefs:
                    existing_categories = current_prefs.preferred_categories
                else:
                    existing_categories = []
                
                new_categories = list(set(existing_categories + filters["categories"]))
                updates["preferred_categories"] = new_categories[:10]  # Limit to 10
            
            # Update preferred brands
            if "brands" in filters:
                current_prefs = await self.get_user_preferences(user_id)
                if current_prefs:
                    existing_brands = current_prefs.preferred_brands
                else:
                    existing_brands = []
                
                new_brands = list(set(existing_brands + filters["brands"]))
                updates["preferred_brands"] = new_brands[:10]  # Limit to 10
            
            # Update price ranges
            if "min_price" in filters or "max_price" in filters:
                min_price = filters.get("min_price", 0)
                max_price = filters.get("max_price", float('inf'))
                
                # Determine category from search
                category = filters.get("category", "general")
                
                current_prefs = await self.get_user_preferences(user_id)
                if current_prefs:
                    price_ranges = current_prefs.price_ranges.copy()
                else:
                    price_ranges = {}
                
                price_ranges[category] = {"min": min_price, "max": max_price}
                updates["price_ranges"] = price_ranges
            
            if updates:
                await self.update_user_preferences(user_id, updates)
            
        except Exception as e:
            logger.error(f"Preferences update from search failed: {e}")
    
    async def _update_preferences_from_activity(
        self, 
        user_id: str, 
        activity: UserActivity
    ):
        """Update user preferences based on user activity"""
        try:
            if activity.activity_type not in [UserActivityType.VIEW_PRODUCT, UserActivityType.PURCHASE]:
                return
            
            if not activity.product_id:
                return
            
            # Get product details to extract preferences
            product_info = activity.activity_data
            
            updates = {}
            
            # Update preferred categories
            if "category" in product_info:
                current_prefs = await self.get_user_preferences(user_id)
                if current_prefs:
                    existing_categories = current_prefs.preferred_categories
                else:
                    existing_categories = []
                
                category = product_info["category"]
                if category not in existing_categories:
                    new_categories = existing_categories + [category]
                    updates["preferred_categories"] = new_categories[:10]
            
            # Update preferred brands
            if "brand" in product_info:
                current_prefs = await self.get_user_preferences(user_id)
                if current_prefs:
                    existing_brands = current_prefs.preferred_brands
                else:
                    existing_brands = []
                
                brand = product_info["brand"]
                if brand not in existing_brands:
                    new_brands = existing_brands + [brand]
                    updates["preferred_brands"] = new_brands[:10]
            
            if updates:
                await self.update_user_preferences(user_id, updates)
            
        except Exception as e:
            logger.error(f"Preferences update from activity failed: {e}")
    
    async def _insert_preferences_in_db(self, preferences: UserPreferences):
        """Insert new user preferences into database"""
        try:
            query = """
                INSERT INTO user_preferences 
                (user_id, preferred_categories, preferred_brands, preferred_colors,
                 preferred_styles, size_preferences, price_ranges, seasonal_preferences,
                 material_preferences, avoid_materials, lifestyle_tags, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                preferences.user_id,
                json.dumps(preferences.preferred_categories),
                json.dumps(preferences.preferred_brands),
                json.dumps(preferences.preferred_colors),
                json.dumps(preferences.preferred_styles),
                json.dumps(preferences.size_preferences),
                json.dumps(preferences.price_ranges),
                json.dumps(preferences.seasonal_preferences),
                json.dumps(preferences.material_preferences),
                json.dumps(preferences.avoid_materials),
                json.dumps(preferences.lifestyle_tags),
                preferences.updated_at
            ])
            
        except Exception as e:
            logger.error(f"User preferences insert failed: {e}")
            raise
    
    async def _update_preferences_in_db(self, preferences: UserPreferences):
        """Update existing user preferences in database"""
        try:
            query = """
                UPDATE user_preferences 
                SET preferred_categories = %s, preferred_brands = %s, preferred_colors = %s,
                    preferred_styles = %s, size_preferences = %s, price_ranges = %s,
                    seasonal_preferences = %s, material_preferences = %s, avoid_materials = %s,
                    lifestyle_tags = %s, updated_at = %s
                WHERE user_id = %s
            """
            
            await db_manager.execute_query(query, [
                json.dumps(preferences.preferred_categories),
                json.dumps(preferences.preferred_brands),
                json.dumps(preferences.preferred_colors),
                json.dumps(preferences.preferred_styles),
                json.dumps(preferences.size_preferences),
                json.dumps(preferences.price_ranges),
                json.dumps(preferences.seasonal_preferences),
                json.dumps(preferences.material_preferences),
                json.dumps(preferences.avoid_materials),
                json.dumps(preferences.lifestyle_tags),
                preferences.updated_at,
                preferences.user_id
            ])
            
        except Exception as e:
            logger.error(f"User preferences update failed: {e}")
            raise
    
    async def _get_user_activities(
        self, 
        user_id: str, 
        start_date: datetime
    ) -> List[UserActivity]:
        """Get user activities from database"""
        try:
            query = """
                SELECT * FROM user_activity 
                WHERE user_id = %s AND timestamp >= %s
                ORDER BY timestamp
            """
            
            results = await db_manager.execute_query(query, [user_id, start_date])
            
            activities = []
            for row in results:
                activity_data = json.loads(row["activity_data"]) if row["activity_data"] else {}
                activity = UserActivity(
                    id=row["id"],
                    user_id=row["user_id"],
                    activity_type=UserActivityType(row["activity_type"]),
                    product_id=row["product_id"],
                    activity_data=activity_data,
                    timestamp=row["timestamp"],
                    session_id=row["session_id"],
                    ip_address=row["ip_address"],
                    user_agent=row["user_agent"]
                )
                activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"User activities retrieval failed: {e}")
            return []
    
    def _group_activities_by_session(
        self, 
        activities: List[UserActivity]
    ) -> Dict[str, List[UserActivity]]:
        """Group activities by session"""
        sessions = defaultdict(list)
        
        for activity in activities:
            session_key = activity.session_id or "unknown"
            sessions[session_key].append(activity)
        
        return dict(sessions)
    
    async def _analyze_browsing_patterns(
        self, 
        activities: List[UserActivity], 
        search_history: List[SearchHistory]
    ) -> Dict[str, Any]:
        """Analyze user browsing patterns"""
        try:
            patterns = {}
            
            # Activity distribution
            activity_counts = Counter(a.activity_type.value for a in activities)
            patterns["activity_distribution"] = dict(activity_counts)
            
            # Time-based patterns
            hour_counts = Counter(a.timestamp.hour for a in activities)
            most_active_hours = [hour for hour, _ in hour_counts.most_common(3)]
            patterns["most_active_hours"] = most_active_hours
            
            # Search patterns
            search_types = Counter(s.search_type for s in search_history)
            patterns["search_type_distribution"] = dict(search_types)
            
            # Filter usage patterns
            filter_usage = defaultdict(int)
            for search in search_history:
                for filter_key in search.filters_applied.keys():
                    filter_usage[filter_key] += 1
            patterns["filter_usage"] = dict(filter_usage)
            
            # Conversion patterns
            views = len([a for a in activities if a.activity_type == UserActivityType.VIEW_PRODUCT])
            purchases = len([a for a in activities if a.activity_type == UserActivityType.PURCHASE])
            conversion_rate = (purchases / views) if views > 0 else 0
            patterns["conversion_rate"] = conversion_rate
            
            return patterns
            
        except Exception as e:
            logger.error(f"Browsing pattern analysis failed: {e}")
            return {}
    
    async def _analyze_purchase_behavior(
        self, 
        user_id: str, 
        start_date: datetime
    ) -> Dict[str, Any]:
        """Analyze user purchase behavior"""
        try:
            # Get purchase activities
            query = """
                SELECT * FROM user_activity 
                WHERE user_id = %s 
                AND activity_type = 'purchase'
                AND timestamp >= %s
                ORDER BY timestamp
            """
            
            results = await db_manager.execute_query(query, [user_id, start_date])
            
            if not results:
                return {"total_purchases": 0, "analysis": "insufficient_data"}
            
            purchases = []
            total_spent = 0
            
            for row in results:
                activity_data = json.loads(row["activity_data"]) if row["activity_data"] else {}
                purchases.append(activity_data)
                total_spent += activity_data.get("price", 0)
            
            # Calculate metrics
            avg_order_value = total_spent / len(purchases)
            
            # Category analysis
            categories = [p.get("category", "unknown") for p in purchases]
            category_counts = Counter(categories)
            
            # Price tier analysis
            price_tiers = []
            for purchase in purchases:
                price = purchase.get("price", 0)
                if price < 25:
                    price_tiers.append("budget")
                elif price < 100:
                    price_tiers.append("mid")
                else:
                    price_tiers.append("premium")
            
            price_tier_counts = Counter(price_tiers)
            
            return {
                "total_purchases": len(purchases),
                "total_spent": total_spent,
                "average_order_value": avg_order_value,
                "preferred_categories": [cat for cat, _ in category_counts.most_common(3)],
                "price_tier_preference": dict(price_tier_counts),
                "purchase_frequency": len(purchases) / 30,  # purchases per day (30-day period)
            }
            
        except Exception as e:
            logger.error(f"Purchase behavior analysis failed: {e}")
            return {}
    
    async def _find_similar_users_by_preferences(
        self, 
        user_prefs: UserPreferences, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Find users with similar preferences"""
        try:
            # Simple similarity based on overlapping categories and brands
            query = """
                SELECT user_id, preferred_categories, preferred_brands
                FROM user_preferences
                WHERE user_id != %s
                LIMIT %s
            """
            
            results = await db_manager.execute_query(query, [user_prefs.user_id, limit])
            
            similar_users = []
            for row in results:
                other_categories = json.loads(row["preferred_categories"]) if row["preferred_categories"] else []
                other_brands = json.loads(row["preferred_brands"]) if row["preferred_brands"] else []
                
                # Calculate overlap
                category_overlap = len(set(user_prefs.preferred_categories) & set(other_categories))
                brand_overlap = len(set(user_prefs.preferred_brands) & set(other_brands))
                
                if category_overlap > 0 or brand_overlap > 0:
                    similar_users.append({
                        "user_id": row["user_id"],
                        "common_categories": list(set(user_prefs.preferred_categories) & set(other_categories)),
                        "common_brands": list(set(user_prefs.preferred_brands) & set(other_brands)),
                        "category_overlap": category_overlap,
                        "brand_overlap": brand_overlap
                    })
            
            return similar_users
            
        except Exception as e:
            logger.error(f"Similar users search failed: {e}")
            return []
    
    async def _calculate_user_similarity(
        self, 
        user_behavior: UserBehaviorAnalytics, 
        other_user_id: str
    ) -> float:
        """Calculate similarity score between two users"""
        try:
            # Get other user's behavior
            other_behavior = await self.analyze_user_behavior(other_user_id)
            
            if not other_behavior or other_behavior.total_sessions < self.min_sessions_for_analysis:
                return 0.0
            
            # Calculate similarity based on various factors
            similarity_score = 0.0
            
            # Category preference similarity
            common_categories = set(user_behavior.preferred_categories) & set(other_behavior.preferred_categories)
            category_similarity = len(common_categories) / max(len(user_behavior.preferred_categories), len(other_behavior.preferred_categories), 1)
            similarity_score += category_similarity * 0.4
            
            # Behavior pattern similarity
            conversion_diff = abs(user_behavior.browsing_patterns.get("conversion_rate", 0) - 
                                other_behavior.browsing_patterns.get("conversion_rate", 0))
            conversion_similarity = max(0, 1 - conversion_diff)
            similarity_score += conversion_similarity * 0.3
            
            # Session pattern similarity
            session_duration_diff = abs(user_behavior.average_session_duration - other_behavior.average_session_duration)
            session_similarity = max(0, 1 - min(session_duration_diff / 60, 1))  # Normalize by hour
            similarity_score += session_similarity * 0.3
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"User similarity calculation failed: {e}")
            return 0.0
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            logger.info("User Behavior Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during user behavior service cleanup: {e}")

# Global user behavior service instance
user_behavior_service = UserBehaviorService()
