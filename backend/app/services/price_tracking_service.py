"""
Price Tracking and Alert Service

Provides real-time price monitoring, historical price tracking,
and automated deal alerts for e-commerce customers.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import statistics

from app.models.business_schemas import (
    PriceHistory, PriceAlert, PriceAlertTrigger, AlertType,
    PriceAlertRequest
)
from app.services.database_service import db_manager
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class PriceTrackingService:
    """Price monitoring and alert service"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.price_cache_ttl = 3600  # 1 hour cache for price data
        self.alert_check_interval = 300  # 5 minutes between alert checks
        
        # Price change thresholds
        self.significant_change_threshold = 0.05  # 5% change
        self.major_change_threshold = 0.15  # 15% change
        
        logger.info("Price Tracking Service initialized")
    
    async def record_price_change(
        self,
        product_id: str,
        new_price: float,
        original_price: Optional[float] = None,
        currency: str = "USD",
        source: str = "system"
    ) -> PriceHistory:
        """
        Record a price change for a product
        
        Args:
            product_id: Product identifier
            new_price: New price value
            original_price: Original/MSRP price
            currency: Price currency
            source: Source of price data
            
        Returns:
            PriceHistory record
        """
        try:
            # Get current price for comparison
            current_price = await self._get_current_price(product_id)
            
            # Calculate discount percentage
            discount_percentage = None
            if original_price and original_price > new_price:
                discount_percentage = ((original_price - new_price) / original_price) * 100
            
            # Create price history record
            price_record = PriceHistory(
                product_id=product_id,
                price=new_price,
                original_price=original_price,
                discount_percentage=discount_percentage,
                currency=currency,
                source=source,
                recorded_at=datetime.now()
            )
            
            # Save to database
            await self._save_price_history(price_record)
            
            # Update current price in cache
            await self._update_current_price_cache(product_id, new_price)
            
            # Check for price alerts if price changed
            if current_price and abs(new_price - current_price) > 0.01:
                await self._check_price_alerts(product_id, current_price, new_price)
            
            # Update product price in main products table
            await self._update_product_price(product_id, new_price)
            
            logger.info(f"Price recorded for {product_id}: ${new_price:.2f}")
            return price_record
            
        except Exception as e:
            logger.error(f"Price recording failed for {product_id}: {e}")
            raise RuntimeError(f"Price recording failed: {str(e)}")
    
    async def get_price_history(
        self,
        product_id: str,
        days: int = 30,
        limit: Optional[int] = None
    ) -> List[PriceHistory]:
        """
        Get price history for a product
        
        Args:
            product_id: Product identifier
            days: Number of days of history to retrieve
            limit: Maximum number of records
            
        Returns:
            List of price history records
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT * FROM price_history 
                WHERE product_id = %s 
                AND recorded_at >= %s
                ORDER BY recorded_at DESC
            """
            
            params = [product_id, start_date]
            
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            results = await db_manager.execute_query(query, params)
            
            return [PriceHistory(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Price history retrieval failed for {product_id}: {e}")
            raise RuntimeError(f"Price history retrieval failed: {str(e)}")
    
    async def create_price_alert(
        self,
        request: PriceAlertRequest
    ) -> PriceAlert:
        """
        Create a new price alert for a user
        
        Args:
            request: Price alert request details
            
        Returns:
            Created price alert
        """
        try:
            # Validate alert parameters
            await self._validate_price_alert_request(request)
            
            # Create alert
            alert = PriceAlert(
                user_id=request.user_id,
                product_id=request.product_id,
                alert_type=request.alert_type,
                target_price=request.target_price,
                percentage_threshold=request.percentage_threshold
            )
            
            # Save to database
            await self._save_price_alert(alert)
            
            logger.info(f"Price alert created for user {request.user_id} on product {request.product_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Price alert creation failed: {e}")
            raise RuntimeError(f"Price alert creation failed: {str(e)}")
    
    async def get_user_alerts(
        self,
        user_id: str,
        active_only: bool = True
    ) -> List[PriceAlert]:
        """
        Get all price alerts for a user
        
        Args:
            user_id: User identifier
            active_only: Only return active alerts
            
        Returns:
            List of user's price alerts
        """
        try:
            query = "SELECT * FROM price_alerts WHERE user_id = %s"
            params = [user_id]
            
            if active_only:
                query += " AND is_active = TRUE"
            
            query += " ORDER BY created_at DESC"
            
            results = await db_manager.execute_query(query, params)
            
            return [PriceAlert(**row) for row in results]
            
        except Exception as e:
            logger.error(f"User alerts retrieval failed for {user_id}: {e}")
            raise RuntimeError(f"User alerts retrieval failed: {str(e)}")
    
    async def deactivate_alert(
        self,
        alert_id: str,
        user_id: str
    ) -> bool:
        """
        Deactivate a price alert
        
        Args:
            alert_id: Alert identifier
            user_id: User identifier (for security)
            
        Returns:
            True if deactivation successful
        """
        try:
            query = """
                UPDATE price_alerts 
                SET is_active = FALSE 
                WHERE id = %s AND user_id = %s
            """
            
            await db_manager.execute_query(query, [alert_id, user_id])
            
            logger.info(f"Price alert {alert_id} deactivated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Alert deactivation failed: {e}")
            return False
    
    async def get_price_analytics(
        self,
        product_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get price analytics for a product
        
        Args:
            product_id: Product identifier
            days: Analysis period in days
            
        Returns:
            Dictionary with price analytics
        """
        try:
            # Get price history
            price_history = await self.get_price_history(product_id, days)
            
            if not price_history:
                return {
                    "product_id": product_id,
                    "error": "No price history available",
                    "period_days": days
                }
            
            prices = [record.price for record in price_history]
            
            # Calculate analytics
            current_price = prices[0] if prices else 0
            min_price = min(prices)
            max_price = max(prices)
            avg_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            
            # Price trend analysis
            if len(prices) >= 2:
                price_change = prices[0] - prices[-1]
                price_change_percentage = (price_change / prices[-1]) * 100
                
                # Calculate trend
                if price_change_percentage > 5:
                    trend = "increasing"
                elif price_change_percentage < -5:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                price_change = 0
                price_change_percentage = 0
                trend = "insufficient_data"
            
            # Price volatility (standard deviation)
            volatility = statistics.stdev(prices) if len(prices) > 1 else 0
            
            # Best deal analysis
            best_price_record = min(price_history, key=lambda x: x.price)
            worst_price_record = max(price_history, key=lambda x: x.price)
            
            # Discount analysis
            discount_records = [r for r in price_history if r.discount_percentage]
            avg_discount = statistics.mean([r.discount_percentage for r in discount_records]) if discount_records else 0
            max_discount = max([r.discount_percentage for r in discount_records]) if discount_records else 0
            
            return {
                "product_id": product_id,
                "analysis_period_days": days,
                "price_summary": {
                    "current_price": current_price,
                    "min_price": min_price,
                    "max_price": max_price,
                    "average_price": round(avg_price, 2),
                    "median_price": round(median_price, 2),
                    "price_volatility": round(volatility, 2)
                },
                "trend_analysis": {
                    "trend": trend,
                    "price_change": round(price_change, 2),
                    "price_change_percentage": round(price_change_percentage, 2),
                    "is_good_time_to_buy": current_price <= avg_price * 0.95  # 5% below average
                },
                "discount_analysis": {
                    "average_discount_percentage": round(avg_discount, 2),
                    "maximum_discount_percentage": round(max_discount, 2),
                    "discount_frequency": len(discount_records) / len(price_history) if price_history else 0
                },
                "historical_extremes": {
                    "best_price": {
                        "price": best_price_record.price,
                        "date": best_price_record.recorded_at.isoformat(),
                        "discount_from_current": round(((current_price - best_price_record.price) / current_price) * 100, 2)
                    },
                    "worst_price": {
                        "price": worst_price_record.price,
                        "date": worst_price_record.recorded_at.isoformat(),
                        "premium_over_current": round(((worst_price_record.price - current_price) / current_price) * 100, 2)
                    }
                },
                "recommendations": await self._generate_price_recommendations(product_id, price_history),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Price analytics failed for {product_id}: {e}")
            raise RuntimeError(f"Price analytics failed: {str(e)}")
    
    async def check_all_alerts(self) -> List[PriceAlertTrigger]:
        """
        Check all active alerts for trigger conditions
        
        Returns:
            List of triggered alerts
        """
        try:
            # Get all active alerts
            query = "SELECT * FROM price_alerts WHERE is_active = TRUE"
            alerts = await db_manager.execute_query(query)
            
            triggered_alerts = []
            
            for alert_data in alerts:
                alert = PriceAlert(**alert_data)
                
                # Get current price
                current_price = await self._get_current_price(alert.product_id)
                
                if current_price is None:
                    continue
                
                # Check trigger conditions based on alert type
                triggered = await self._check_alert_trigger(alert, current_price)
                
                if triggered:
                    trigger = await self._create_alert_trigger(alert, current_price)
                    triggered_alerts.append(trigger)
                    
                    # Mark alert as triggered and send notification
                    await self._mark_alert_triggered(alert.id)
                    await self._send_alert_notification(trigger)
            
            logger.info(f"Alert check completed. {len(triggered_alerts)} alerts triggered.")
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Alert checking failed: {e}")
            raise RuntimeError(f"Alert checking failed: {str(e)}")
    
    async def get_market_trends(
        self,
        category: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get market price trends for a category or overall market
        
        Args:
            category: Product category to analyze
            days: Analysis period in days
            
        Returns:
            Market trend analysis
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Base query for price trends
            if category:
                query = """
                    SELECT 
                        p.category,
                        ph.recorded_at::date as date,
                        AVG(ph.price) as avg_price,
                        COUNT(*) as product_count,
                        AVG(ph.discount_percentage) as avg_discount
                    FROM price_history ph
                    JOIN products p ON ph.product_id = p.id
                    WHERE p.category = %s AND ph.recorded_at >= %s
                    GROUP BY p.category, ph.recorded_at::date
                    ORDER BY date
                """
                params = [category, start_date]
            else:
                query = """
                    SELECT 
                        ph.recorded_at::date as date,
                        AVG(ph.price) as avg_price,
                        COUNT(*) as product_count,
                        AVG(ph.discount_percentage) as avg_discount
                    FROM price_history ph
                    WHERE ph.recorded_at >= %s
                    GROUP BY ph.recorded_at::date
                    ORDER BY date
                """
                params = [start_date]
            
            results = await db_manager.execute_query(query, params)
            
            if not results:
                return {
                    "category": category or "all",
                    "error": "No trend data available",
                    "period_days": days
                }
            
            # Calculate trend metrics
            prices = [row["avg_price"] for row in results]
            dates = [row["date"] for row in results]
            
            price_trend = "stable"
            if len(prices) >= 2:
                price_change_pct = ((prices[-1] - prices[0]) / prices[0]) * 100
                if price_change_pct > 3:
                    price_trend = "increasing"
                elif price_change_pct < -3:
                    price_trend = "decreasing"
            
            # Volatility analysis
            price_volatility = statistics.stdev(prices) if len(prices) > 1 else 0
            
            return {
                "category": category or "all_categories",
                "analysis_period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "trend_summary": {
                    "direction": price_trend,
                    "average_price": round(statistics.mean(prices), 2),
                    "price_volatility": round(price_volatility, 2),
                    "total_products_tracked": sum(row["product_count"] for row in results)
                },
                "daily_trends": [
                    {
                        "date": row["date"].isoformat(),
                        "avg_price": round(row["avg_price"], 2),
                        "product_count": row["product_count"],
                        "avg_discount": round(row["avg_discount"] or 0, 2)
                    }
                    for row in results
                ],
                "market_insights": await self._generate_market_insights(results, category),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Market trends analysis failed: {e}")
            raise RuntimeError(f"Market trends analysis failed: {str(e)}")
    
    # Private helper methods
    
    async def _get_current_price(self, product_id: str) -> Optional[float]:
        """Get current price from cache or database"""
        try:
            # Check cache first
            cache_key = f"current_price:{product_id}"
            cached_price = await self.cache_service.get(cache_key)
            
            if cached_price:
                return float(cached_price)
            
            # Get from database
            query = "SELECT price FROM products WHERE id = %s"
            results = await db_manager.execute_query(query, [product_id])
            
            if results:
                price = float(results[0]["price"])
                # Cache the result
                await self.cache_service.set(cache_key, str(price), self.price_cache_ttl)
                return price
            
            return None
            
        except Exception as e:
            logger.error(f"Current price retrieval failed for {product_id}: {e}")
            return None
    
    async def _update_current_price_cache(self, product_id: str, price: float):
        """Update current price in cache"""
        try:
            cache_key = f"current_price:{product_id}"
            await self.cache_service.set(cache_key, str(price), self.price_cache_ttl)
        except Exception as e:
            logger.error(f"Price cache update failed for {product_id}: {e}")
    
    async def _save_price_history(self, price_record: PriceHistory):
        """Save price history record to database"""
        try:
            query = """
                INSERT INTO price_history 
                (product_id, price, original_price, discount_percentage, currency, recorded_at, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                price_record.product_id,
                price_record.price,
                price_record.original_price,
                price_record.discount_percentage,
                price_record.currency,
                price_record.recorded_at,
                price_record.source
            ])
            
        except Exception as e:
            logger.error(f"Price history save failed: {e}")
            raise
    
    async def _update_product_price(self, product_id: str, new_price: float):
        """Update product price in main products table"""
        try:
            query = "UPDATE products SET price = %s, updated_at = %s WHERE id = %s"
            await db_manager.execute_query(query, [new_price, datetime.now(), product_id])
        except Exception as e:
            logger.error(f"Product price update failed for {product_id}: {e}")
    
    async def _validate_price_alert_request(self, request: PriceAlertRequest):
        """Validate price alert request"""
        if request.alert_type in [AlertType.PRICE_DROP, AlertType.PRICE_TARGET]:
            if request.target_price is None:
                raise ValueError("target_price is required for price-based alerts")
            if request.target_price <= 0:
                raise ValueError("target_price must be positive")
        
        # Check if product exists
        current_price = await self._get_current_price(request.product_id)
        if current_price is None:
            raise ValueError(f"Product not found: {request.product_id}")
    
    async def _save_price_alert(self, alert: PriceAlert):
        """Save price alert to database"""
        try:
            query = """
                INSERT INTO price_alerts 
                (id, user_id, product_id, alert_type, target_price, percentage_threshold, 
                 is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                alert.id,
                alert.user_id,
                alert.product_id,
                alert.alert_type.value,
                alert.target_price,
                alert.percentage_threshold,
                alert.is_active,
                alert.created_at
            ])
            
        except Exception as e:
            logger.error(f"Price alert save failed: {e}")
            raise
    
    async def _check_price_alerts(self, product_id: str, old_price: float, new_price: float):
        """Check if any alerts should be triggered for this price change"""
        try:
            # Get active alerts for this product
            query = """
                SELECT * FROM price_alerts 
                WHERE product_id = %s AND is_active = TRUE
            """
            
            alerts = await db_manager.execute_query(query, [product_id])
            
            for alert_data in alerts:
                alert = PriceAlert(**alert_data)
                triggered = await self._check_alert_trigger(alert, new_price, old_price)
                
                if triggered:
                    trigger = await self._create_alert_trigger(alert, new_price, old_price)
                    await self._mark_alert_triggered(alert.id)
                    await self._send_alert_notification(trigger)
            
        except Exception as e:
            logger.error(f"Price alert checking failed for {product_id}: {e}")
    
    async def _check_alert_trigger(
        self, 
        alert: PriceAlert, 
        current_price: float, 
        previous_price: Optional[float] = None
    ) -> bool:
        """Check if alert should be triggered"""
        try:
            if alert.alert_type == AlertType.PRICE_TARGET:
                return current_price <= alert.target_price
            
            elif alert.alert_type == AlertType.PRICE_DROP:
                if previous_price:
                    if alert.percentage_threshold:
                        drop_percentage = ((previous_price - current_price) / previous_price) * 100
                        return drop_percentage >= alert.percentage_threshold
                    elif alert.target_price:
                        return current_price <= alert.target_price
                
            return False
            
        except Exception as e:
            logger.error(f"Alert trigger check failed: {e}")
            return False
    
    async def _create_alert_trigger(
        self, 
        alert: PriceAlert, 
        new_price: float, 
        old_price: Optional[float] = None
    ) -> PriceAlertTrigger:
        """Create alert trigger record"""
        if old_price is None:
            old_price = await self._get_previous_price(alert.product_id)
        
        price_change = new_price - old_price if old_price else 0
        percentage_change = (price_change / old_price * 100) if old_price and old_price > 0 else 0
        
        return PriceAlertTrigger(
            alert_id=alert.id,
            product_id=alert.product_id,
            user_id=alert.user_id,
            old_price=old_price or 0,
            new_price=new_price,
            price_change=price_change,
            percentage_change=percentage_change,
            alert_type=alert.alert_type
        )
    
    async def _get_previous_price(self, product_id: str) -> Optional[float]:
        """Get previous price from history"""
        try:
            query = """
                SELECT price FROM price_history 
                WHERE product_id = %s 
                ORDER BY recorded_at DESC 
                LIMIT 1 OFFSET 1
            """
            
            results = await db_manager.execute_query(query, [product_id])
            return float(results[0]["price"]) if results else None
            
        except Exception as e:
            logger.error(f"Previous price retrieval failed: {e}")
            return None
    
    async def _mark_alert_triggered(self, alert_id: str):
        """Mark alert as triggered"""
        try:
            query = """
                UPDATE price_alerts 
                SET triggered_at = %s, notification_sent = TRUE
                WHERE id = %s
            """
            
            await db_manager.execute_query(query, [datetime.now(), alert_id])
            
        except Exception as e:
            logger.error(f"Alert trigger marking failed: {e}")
    
    async def _send_alert_notification(self, trigger: PriceAlertTrigger):
        """Send alert notification to user"""
        try:
            # Log notification (in real implementation, send email/push notification)
            logger.info(
                f"PRICE ALERT: User {trigger.user_id} - "
                f"Product {trigger.product_id} price changed from "
                f"${trigger.old_price:.2f} to ${trigger.new_price:.2f} "
                f"({trigger.percentage_change:+.1f}%)"
            )
            
            # Save notification record
            await self._save_alert_trigger(trigger)
            
        except Exception as e:
            logger.error(f"Alert notification failed: {e}")
    
    async def _save_alert_trigger(self, trigger: PriceAlertTrigger):
        """Save alert trigger to database"""
        try:
            query = """
                INSERT INTO price_alert_triggers 
                (alert_id, product_id, user_id, old_price, new_price, 
                 price_change, percentage_change, alert_type, triggered_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                trigger.alert_id,
                trigger.product_id,
                trigger.user_id,
                trigger.old_price,
                trigger.new_price,
                trigger.price_change,
                trigger.percentage_change,
                trigger.alert_type.value,
                trigger.triggered_at
            ])
            
        except Exception as e:
            logger.error(f"Alert trigger save failed: {e}")
    
    async def _generate_price_recommendations(
        self, 
        product_id: str, 
        price_history: List[PriceHistory]
    ) -> List[str]:
        """Generate price-based recommendations"""
        try:
            recommendations = []
            
            if not price_history:
                return recommendations
            
            current_price = price_history[0].price
            prices = [record.price for record in price_history]
            avg_price = statistics.mean(prices)
            min_price = min(prices)
            
            # Generate recommendations based on price analysis
            if current_price <= min_price * 1.05:  # Within 5% of lowest price
                recommendations.append("This is near the lowest price recorded - great time to buy!")
            
            if current_price <= avg_price * 0.9:  # 10% below average
                recommendations.append("Price is significantly below average - consider purchasing")
            
            if current_price >= avg_price * 1.1:  # 10% above average
                recommendations.append("Price is above average - consider waiting for a better deal")
            
            # Check for discount patterns
            discount_records = [r for r in price_history if r.discount_percentage and r.discount_percentage > 0]
            if discount_records:
                avg_discount = statistics.mean([r.discount_percentage for r in discount_records])
                if avg_discount > 15:
                    recommendations.append("This product frequently goes on sale - consider setting a price alert")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Price recommendations generation failed: {e}")
            return []
    
    async def _generate_market_insights(
        self, 
        trend_data: List[Dict[str, Any]], 
        category: Optional[str]
    ) -> List[str]:
        """Generate market insights from trend data"""
        try:
            insights = []
            
            if not trend_data:
                return insights
            
            prices = [row["avg_price"] for row in trend_data]
            
            # Price stability analysis
            if len(prices) > 1:
                volatility = statistics.stdev(prices) / statistics.mean(prices)
                if volatility < 0.05:
                    insights.append("Market shows stable pricing with low volatility")
                elif volatility > 0.15:
                    insights.append("Market shows high price volatility - good for finding deals")
            
            # Seasonal patterns (simplified)
            current_month = datetime.now().month
            if current_month in [11, 12]:  # Holiday season
                insights.append("Holiday season - expect more frequent sales and promotions")
            elif current_month in [6, 7]:  # Summer
                insights.append("Summer season - good time for seasonal clearance deals")
            
            return insights
            
        except Exception as e:
            logger.error(f"Market insights generation failed: {e}")
            return []
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            logger.info("Price Tracking Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during price tracking service cleanup: {e}")

# Global price tracking service instance
price_tracking_service = PriceTrackingService()
