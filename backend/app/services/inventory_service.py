"""
Real-time Inventory Management Service

Provides real-time inventory checking, stock level monitoring,
and automated reorder suggestions for e-commerce operations.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.models.business_schemas import (
    InventoryItem, InventoryUpdate, InventoryCheck, InventoryCheckResponse,
    InventoryStatus, InventoryCheckRequest
)
from app.services.database_service import db_manager
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class InventoryService:
    """Real-time inventory management service"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.cache_ttl = 300  # 5 minutes cache for inventory data
        self.low_stock_threshold = 10
        self.critical_stock_threshold = 5
        
        # In-memory cache for frequently accessed inventory
        self._inventory_cache = {}
        self._cache_timestamps = {}
        self._cache_max_age = 60  # 1 minute for in-memory cache
        
        logger.info("Inventory Service initialized")
    
    async def check_availability(
        self,
        product_id: str,
        requested_quantity: int = 1
    ) -> InventoryCheckResponse:
        """
        Check real-time availability for a single product
        
        Args:
            product_id: Product identifier
            requested_quantity: Requested quantity to check
            
        Returns:
            InventoryCheckResponse with availability details
        """
        try:
            # First check cache
            cached_inventory = await self._get_cached_inventory(product_id)
            
            if cached_inventory:
                inventory_item = InventoryItem(**cached_inventory)
            else:
                # Fetch from database
                inventory_item = await self._fetch_inventory_from_db(product_id)
                if inventory_item:
                    await self._cache_inventory(product_id, inventory_item.dict())
            
            if not inventory_item:
                # Product not found in inventory
                return InventoryCheckResponse(
                    product_id=product_id,
                    available=False,
                    available_quantity=0,
                    requested_quantity=requested_quantity,
                    status=InventoryStatus.DISCONTINUED,
                    alternative_products=await self._get_alternative_products(product_id)
                )
            
            available_qty = inventory_item.available_quantity
            is_available = available_qty >= requested_quantity
            
            # Determine status
            status = self._determine_inventory_status(inventory_item)
            
            # Get estimated restock date if out of stock
            restock_date = None
            if not is_available:
                restock_date = await self._estimate_restock_date(product_id)
            
            # Get alternative products if not available
            alternatives = []
            if not is_available:
                alternatives = await self._get_alternative_products(product_id)
            
            return InventoryCheckResponse(
                product_id=product_id,
                available=is_available,
                available_quantity=available_qty,
                requested_quantity=requested_quantity,
                estimated_restock_date=restock_date,
                alternative_products=alternatives,
                status=status
            )
            
        except Exception as e:
            logger.error(f"Inventory availability check failed for {product_id}: {e}")
            raise RuntimeError(f"Inventory check failed: {str(e)}")
    
    async def check_multiple_availability(
        self,
        request: InventoryCheckRequest
    ) -> List[InventoryCheckResponse]:
        """
        Check availability for multiple products efficiently
        
        Args:
            request: Batch inventory check request
            
        Returns:
            List of inventory check responses
        """
        try:
            # Process checks concurrently
            tasks = [
                self.check_availability(check.product_id, check.requested_quantity)
                for check in request.product_requests
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Inventory check failed for request {i}: {result}")
                    # Create error response
                    check = request.product_requests[i]
                    error_response = InventoryCheckResponse(
                        product_id=check.product_id,
                        available=False,
                        available_quantity=0,
                        requested_quantity=check.requested_quantity,
                        status=InventoryStatus.OUT_OF_STOCK
                    )
                    valid_results.append(error_response)
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Batch inventory check failed: {e}")
            raise RuntimeError(f"Batch inventory check failed: {str(e)}")
    
    async def update_inventory(
        self,
        product_id: str,
        quantity_change: int,
        reason: str,
        reference_id: Optional[str] = None,
        updated_by: str = "system"
    ) -> InventoryItem:
        """
        Update inventory quantity for a product
        
        Args:
            product_id: Product identifier
            quantity_change: Quantity change (positive or negative)
            reason: Reason for the change
            reference_id: Order or transaction reference
            updated_by: User or system making the update
            
        Returns:
            Updated inventory item
        """
        try:
            # Get current inventory
            current_inventory = await self._fetch_inventory_from_db(product_id)
            
            if not current_inventory:
                raise ValueError(f"Product not found in inventory: {product_id}")
            
            # Calculate new quantity
            new_quantity = max(0, current_inventory.quantity + quantity_change)
            
            # Update database
            await self._update_inventory_in_db(
                product_id, new_quantity, reason, reference_id, updated_by
            )
            
            # Update cache
            updated_inventory = InventoryItem(
                product_id=product_id,
                sku=current_inventory.sku,
                quantity=new_quantity,
                reserved_quantity=current_inventory.reserved_quantity,
                reorder_level=current_inventory.reorder_level,
                max_stock_level=current_inventory.max_stock_level,
                supplier_id=current_inventory.supplier_id,
                location=current_inventory.location,
                last_updated=datetime.now(),
                status=self._determine_inventory_status_from_quantity(new_quantity)
            )
            
            await self._cache_inventory(product_id, updated_inventory.dict())
            
            # Check if reorder is needed
            if updated_inventory.needs_reorder:
                await self._trigger_reorder_alert(updated_inventory)
            
            # Log inventory change
            await self._log_inventory_change(
                product_id, quantity_change, reason, reference_id, updated_by
            )
            
            return updated_inventory
            
        except Exception as e:
            logger.error(f"Inventory update failed for {product_id}: {e}")
            raise RuntimeError(f"Inventory update failed: {str(e)}")
    
    async def reserve_inventory(
        self,
        product_id: str,
        quantity: int,
        reservation_id: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """
        Reserve inventory for pending orders
        
        Args:
            product_id: Product identifier
            quantity: Quantity to reserve
            reservation_id: Unique reservation identifier
            expires_at: When reservation expires
            
        Returns:
            True if reservation successful, False otherwise
        """
        try:
            # Check if enough inventory is available
            availability = await self.check_availability(product_id, quantity)
            
            if not availability.available:
                return False
            
            # Create reservation in database
            success = await self._create_inventory_reservation(
                product_id, quantity, reservation_id, expires_at
            )
            
            if success:
                # Update cached inventory
                await self._invalidate_inventory_cache(product_id)
                logger.info(f"Reserved {quantity} units of {product_id} (reservation: {reservation_id})")
            
            return success
            
        except Exception as e:
            logger.error(f"Inventory reservation failed for {product_id}: {e}")
            return False
    
    async def release_reservation(
        self,
        reservation_id: str
    ) -> bool:
        """
        Release inventory reservation
        
        Args:
            reservation_id: Reservation identifier to release
            
        Returns:
            True if release successful, False otherwise
        """
        try:
            # Get reservation details
            reservation = await self._get_reservation_details(reservation_id)
            
            if not reservation:
                logger.warning(f"Reservation not found: {reservation_id}")
                return False
            
            # Release reservation in database
            success = await self._release_inventory_reservation(reservation_id)
            
            if success:
                # Update cached inventory
                await self._invalidate_inventory_cache(reservation["product_id"])
                logger.info(f"Released reservation {reservation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Reservation release failed for {reservation_id}: {e}")
            return False
    
    async def get_low_stock_items(
        self,
        threshold: Optional[int] = None
    ) -> List[InventoryItem]:
        """
        Get all items with low stock levels
        
        Args:
            threshold: Custom low stock threshold
            
        Returns:
            List of low stock inventory items
        """
        try:
            if threshold is None:
                threshold = self.low_stock_threshold
            
            query = """
                SELECT * FROM inventory 
                WHERE (quantity - reserved_quantity) <= %s 
                AND status != 'discontinued'
                ORDER BY (quantity - reserved_quantity) ASC
            """
            
            results = await db_manager.execute_query(query, [threshold])
            
            return [InventoryItem(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get low stock items: {e}")
            raise RuntimeError(f"Low stock query failed: {str(e)}")
    
    async def get_inventory_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get inventory analytics for a date range
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dictionary with inventory analytics
        """
        try:
            # Get inventory turnover data
            turnover_query = """
                SELECT 
                    product_id,
                    SUM(CASE WHEN quantity_change < 0 THEN ABS(quantity_change) ELSE 0 END) as units_sold,
                    SUM(CASE WHEN quantity_change > 0 THEN quantity_change ELSE 0 END) as units_restocked,
                    COUNT(*) as transaction_count
                FROM inventory_history 
                WHERE updated_at BETWEEN %s AND %s
                GROUP BY product_id
            """
            
            turnover_results = await db_manager.execute_query(
                turnover_query, [start_date, end_date]
            )
            
            # Get current stock levels
            stock_query = """
                SELECT 
                    status,
                    COUNT(*) as count,
                    SUM(quantity) as total_units,
                    AVG(quantity - reserved_quantity) as avg_available
                FROM inventory
                GROUP BY status
            """
            
            stock_results = await db_manager.execute_query(stock_query)
            
            # Calculate analytics
            total_products = len(turnover_results)
            total_units_sold = sum(item["units_sold"] for item in turnover_results)
            total_units_restocked = sum(item["units_restocked"] for item in turnover_results)
            
            # Top selling products
            top_selling = sorted(
                turnover_results, 
                key=lambda x: x["units_sold"], 
                reverse=True
            )[:10]
            
            # Products needing attention
            low_turnover = [
                item for item in turnover_results 
                if item["units_sold"] < 5 and item["transaction_count"] < 3
            ]
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_products_tracked": total_products,
                    "total_units_sold": total_units_sold,
                    "total_units_restocked": total_units_restocked,
                    "inventory_turnover_ratio": total_units_sold / total_units_restocked if total_units_restocked > 0 else 0
                },
                "stock_status_breakdown": {row["status"]: row for row in stock_results},
                "top_selling_products": top_selling,
                "low_turnover_products": low_turnover,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Inventory analytics failed: {e}")
            raise RuntimeError(f"Inventory analytics failed: {str(e)}")
    
    # Private helper methods
    
    async def _get_cached_inventory(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get inventory from cache"""
        try:
            # Check in-memory cache first
            if product_id in self._inventory_cache:
                timestamp = self._cache_timestamps.get(product_id, datetime.min)
                if (datetime.now() - timestamp).seconds < self._cache_max_age:
                    return self._inventory_cache[product_id]
                else:
                    # Remove stale cache entry
                    del self._inventory_cache[product_id]
                    del self._cache_timestamps[product_id]
            
            # Check Redis cache
            cache_key = f"inventory:{product_id}"
            cached_data = await self.cache_service.get(cache_key)
            
            if cached_data:
                inventory_data = json.loads(cached_data)
                # Update in-memory cache
                self._inventory_cache[product_id] = inventory_data
                self._cache_timestamps[product_id] = datetime.now()
                return inventory_data
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed for {product_id}: {e}")
            return None
    
    async def _cache_inventory(self, product_id: str, inventory_data: Dict[str, Any]):
        """Cache inventory data"""
        try:
            # Update in-memory cache
            self._inventory_cache[product_id] = inventory_data
            self._cache_timestamps[product_id] = datetime.now()
            
            # Update Redis cache
            cache_key = f"inventory:{product_id}"
            await self.cache_service.set(
                cache_key, 
                json.dumps(inventory_data, default=str), 
                self.cache_ttl
            )
            
        except Exception as e:
            logger.error(f"Cache update failed for {product_id}: {e}")
    
    async def _invalidate_inventory_cache(self, product_id: str):
        """Invalidate cached inventory data"""
        try:
            # Remove from in-memory cache
            if product_id in self._inventory_cache:
                del self._inventory_cache[product_id]
                del self._cache_timestamps[product_id]
            
            # Remove from Redis cache
            cache_key = f"inventory:{product_id}"
            await self.cache_service.delete(cache_key)
            
        except Exception as e:
            logger.error(f"Cache invalidation failed for {product_id}: {e}")
    
    async def _fetch_inventory_from_db(self, product_id: str) -> Optional[InventoryItem]:
        """Fetch inventory data from database"""
        try:
            query = "SELECT * FROM inventory WHERE product_id = %s"
            results = await db_manager.execute_query(query, [product_id])
            
            if results:
                return InventoryItem(**results[0])
            return None
            
        except Exception as e:
            logger.error(f"Database fetch failed for {product_id}: {e}")
            return None
    
    async def _update_inventory_in_db(
        self, 
        product_id: str, 
        new_quantity: int, 
        reason: str, 
        reference_id: Optional[str], 
        updated_by: str
    ):
        """Update inventory in database"""
        try:
            # Update inventory table
            update_query = """
                UPDATE inventory 
                SET quantity = %s, last_updated = %s, status = %s
                WHERE product_id = %s
            """
            
            status = self._determine_inventory_status_from_quantity(new_quantity)
            await db_manager.execute_query(
                update_query, 
                [new_quantity, datetime.now(), status.value, product_id]
            )
            
            # Insert into inventory history
            history_query = """
                INSERT INTO inventory_history 
                (product_id, quantity_change, reason, reference_id, updated_by, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Calculate quantity change for history
            current_inventory = await self._fetch_inventory_from_db(product_id)
            quantity_change = new_quantity - (current_inventory.quantity if current_inventory else 0)
            
            await db_manager.execute_query(
                history_query,
                [product_id, quantity_change, reason, reference_id, updated_by, datetime.now()]
            )
            
        except Exception as e:
            logger.error(f"Database update failed for {product_id}: {e}")
            raise
    
    def _determine_inventory_status(self, inventory_item: InventoryItem) -> InventoryStatus:
        """Determine inventory status based on item details"""
        available_qty = inventory_item.available_quantity
        
        if available_qty <= 0:
            return InventoryStatus.OUT_OF_STOCK
        elif available_qty <= self.critical_stock_threshold:
            return InventoryStatus.LOW_STOCK
        else:
            return InventoryStatus.IN_STOCK
    
    def _determine_inventory_status_from_quantity(self, quantity: int) -> InventoryStatus:
        """Determine inventory status from quantity alone"""
        if quantity <= 0:
            return InventoryStatus.OUT_OF_STOCK
        elif quantity <= self.critical_stock_threshold:
            return InventoryStatus.LOW_STOCK
        else:
            return InventoryStatus.IN_STOCK
    
    async def _estimate_restock_date(self, product_id: str) -> Optional[datetime]:
        """Estimate restock date based on historical data"""
        try:
            # Get historical restock patterns
            query = """
                SELECT updated_at 
                FROM inventory_history 
                WHERE product_id = %s 
                AND quantity_change > 0 
                AND reason LIKE '%restock%'
                ORDER BY updated_at DESC 
                LIMIT 5
            """
            
            results = await db_manager.execute_query(query, [product_id])
            
            if len(results) >= 2:
                # Calculate average restock interval
                intervals = []
                for i in range(1, len(results)):
                    interval = (results[i-1]["updated_at"] - results[i]["updated_at"]).days
                    intervals.append(interval)
                
                avg_interval = sum(intervals) / len(intervals)
                last_restock = results[0]["updated_at"]
                
                estimated_date = last_restock + timedelta(days=avg_interval)
                return estimated_date
            
            # Default estimate: 7 days
            return datetime.now() + timedelta(days=7)
            
        except Exception as e:
            logger.error(f"Restock estimation failed for {product_id}: {e}")
            return None
    
    async def _get_alternative_products(self, product_id: str) -> List[str]:
        """Get alternative products when item is out of stock"""
        try:
            # Get product details for similarity search
            product_query = "SELECT category, subcategory, brand FROM products WHERE id = %s"
            product_results = await db_manager.execute_query(product_query, [product_id])
            
            if not product_results:
                return []
            
            product = product_results[0]
            
            # Find similar products that are in stock
            alternatives_query = """
                SELECT p.id 
                FROM products p
                JOIN inventory i ON p.id = i.product_id
                WHERE p.category = %s 
                AND p.subcategory = %s
                AND p.id != %s
                AND i.quantity > 0
                ORDER BY 
                    CASE WHEN p.brand = %s THEN 0 ELSE 1 END,
                    i.quantity DESC
                LIMIT 5
            """
            
            results = await db_manager.execute_query(
                alternatives_query,
                [product["category"], product["subcategory"], product_id, product["brand"]]
            )
            
            return [row["id"] for row in results]
            
        except Exception as e:
            logger.error(f"Alternative products query failed for {product_id}: {e}")
            return []
    
    async def _trigger_reorder_alert(self, inventory_item: InventoryItem):
        """Trigger reorder alert for low stock items"""
        try:
            # Log reorder alert
            logger.warning(
                f"REORDER ALERT: Product {inventory_item.product_id} "
                f"has only {inventory_item.available_quantity} units available "
                f"(below reorder level of {inventory_item.reorder_level})"
            )
            
            # Could integrate with external systems here
            # e.g., send email, create purchase order, notify suppliers
            
        except Exception as e:
            logger.error(f"Reorder alert failed for {inventory_item.product_id}: {e}")
    
    async def _log_inventory_change(
        self, 
        product_id: str, 
        quantity_change: int, 
        reason: str, 
        reference_id: Optional[str], 
        updated_by: str
    ):
        """Log inventory change for audit trail"""
        try:
            logger.info(
                f"Inventory changed: {product_id} "
                f"quantity_change={quantity_change} "
                f"reason='{reason}' "
                f"reference={reference_id} "
                f"updated_by={updated_by}"
            )
            
        except Exception as e:
            logger.error(f"Inventory change logging failed: {e}")
    
    async def _create_inventory_reservation(
        self, 
        product_id: str, 
        quantity: int, 
        reservation_id: str, 
        expires_at: Optional[datetime]
    ) -> bool:
        """Create inventory reservation in database"""
        try:
            if expires_at is None:
                expires_at = datetime.now() + timedelta(hours=24)  # Default 24h expiry
            
            query = """
                INSERT INTO inventory_reservations 
                (id, product_id, quantity, expires_at, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(
                query,
                [reservation_id, product_id, quantity, expires_at, datetime.now()]
            )
            
            # Update reserved quantity in inventory
            update_query = """
                UPDATE inventory 
                SET reserved_quantity = reserved_quantity + %s
                WHERE product_id = %s
            """
            
            await db_manager.execute_query(update_query, [quantity, product_id])
            
            return True
            
        except Exception as e:
            logger.error(f"Reservation creation failed: {e}")
            return False
    
    async def _get_reservation_details(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        """Get reservation details from database"""
        try:
            query = "SELECT * FROM inventory_reservations WHERE id = %s"
            results = await db_manager.execute_query(query, [reservation_id])
            
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Reservation details query failed: {e}")
            return None
    
    async def _release_inventory_reservation(self, reservation_id: str) -> bool:
        """Release inventory reservation"""
        try:
            # Get reservation details
            reservation = await self._get_reservation_details(reservation_id)
            
            if not reservation:
                return False
            
            # Update reserved quantity in inventory
            update_query = """
                UPDATE inventory 
                SET reserved_quantity = reserved_quantity - %s
                WHERE product_id = %s
            """
            
            await db_manager.execute_query(
                update_query, 
                [reservation["quantity"], reservation["product_id"]]
            )
            
            # Delete reservation
            delete_query = "DELETE FROM inventory_reservations WHERE id = %s"
            await db_manager.execute_query(delete_query, [reservation_id])
            
            return True
            
        except Exception as e:
            logger.error(f"Reservation release failed: {e}")
            return False
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            self._inventory_cache.clear()
            self._cache_timestamps.clear()
            logger.info("Inventory Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during inventory service cleanup: {e}")

# Global inventory service instance
inventory_service = InventoryService()
