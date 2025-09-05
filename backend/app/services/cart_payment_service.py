"""
Shopping Cart and Mock Payment Service

Manages shopping cart operations and mock payment processing
for e-commerce demonstration purposes.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import uuid
import random

from app.models.business_schemas import (
    CartItem, ShoppingCart, PaymentTransaction, Order,
    PaymentStatus, OrderStatus, CartActionRequest
)
from app.services.database_service import db_manager
from app.services.cache_service import CacheService
from app.services.inventory_service import inventory_service

logger = logging.getLogger(__name__)

class CartPaymentService:
    """Shopping cart and mock payment processing service"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.cart_cache_ttl = 1800  # 30 minutes cache for carts
        self.cart_expiry_hours = 24  # Carts expire after 24 hours
        
        # Mock payment settings
        self.payment_success_rate = 0.95  # 95% success rate for demo
        self.payment_processing_delay = 2  # 2 seconds simulation
        
        # Tax and shipping rates
        self.tax_rate = 0.08  # 8% tax rate
        self.free_shipping_threshold = 50.0
        self.standard_shipping_cost = 5.99
        
        logger.info("Cart and Payment Service initialized")
    
    async def get_user_cart(self, user_id: str) -> ShoppingCart:
        """
        Get or create user's shopping cart
        
        Args:
            user_id: User identifier
            
        Returns:
            User's shopping cart
        """
        try:
            # Check cache first
            cache_key = f"cart:{user_id}"
            cached_cart = await self.cache_service.get(cache_key)
            
            if cached_cart:
                cart_data = json.loads(cached_cart)
                cart = ShoppingCart(**cart_data)
                
                # Check if cart has expired
                if cart.expires_at and datetime.now() > cart.expires_at:
                    await self._clear_expired_cart(user_id)
                    return await self._create_new_cart(user_id)
                
                return cart
            
            # Get from database or create new
            cart = await self._get_cart_from_db(user_id)
            if not cart:
                cart = await self._create_new_cart(user_id)
            
            # Cache the cart
            await self._cache_cart(cart)
            
            return cart
            
        except Exception as e:
            logger.error(f"Get user cart failed for {user_id}: {e}")
            # Return empty cart as fallback
            return await self._create_new_cart(user_id)
    
    async def add_to_cart(
        self,
        request: CartActionRequest
    ) -> ShoppingCart:
        """
        Add item to shopping cart
        
        Args:
            request: Cart action request
            
        Returns:
            Updated shopping cart
        """
        try:
            if request.action != "add":
                raise ValueError("This method only handles 'add' actions")
            
            if not request.product_id or not request.quantity:
                raise ValueError("product_id and quantity are required for add action")
            
            # Check inventory availability
            inventory_check = await inventory_service.check_availability(
                request.product_id, 
                request.quantity
            )
            
            if not inventory_check.available:
                raise ValueError(f"Insufficient inventory. Available: {inventory_check.available_quantity}")
            
            # Get user's cart
            cart = await self.get_user_cart(request.user_id)
            
            # Get product details
            product_details = await self._get_product_details(request.product_id)
            if not product_details:
                raise ValueError(f"Product not found: {request.product_id}")
            
            # Check if item already in cart
            existing_item = None
            for item in cart.items:
                if (item.product_id == request.product_id and 
                    item.size == request.size and 
                    item.color == request.color):
                    existing_item = item
                    break
            
            if existing_item:
                # Update quantity
                new_quantity = existing_item.quantity + request.quantity
                
                # Check inventory for new total
                inventory_check = await inventory_service.check_availability(
                    request.product_id, 
                    new_quantity
                )
                
                if not inventory_check.available:
                    raise ValueError(f"Cannot add {request.quantity} more. Total would exceed available inventory.")
                
                existing_item.quantity = new_quantity
                existing_item.updated_at = datetime.now()
            else:
                # Add new item
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=request.product_id,
                    quantity=request.quantity,
                    size=request.size,
                    color=request.color,
                    price_at_addition=product_details["price"]
                )
                cart.items.append(cart_item)
            
            # Recalculate cart totals
            await self._recalculate_cart_totals(cart)
            
            # Save updated cart
            await self._save_cart_to_db(cart)
            await self._cache_cart(cart)
            
            logger.info(f"Added {request.quantity} of {request.product_id} to cart for user {request.user_id}")
            return cart
            
        except Exception as e:
            logger.error(f"Add to cart failed: {e}")
            raise RuntimeError(f"Add to cart failed: {str(e)}")
    
    async def update_cart_item(
        self,
        request: CartActionRequest
    ) -> ShoppingCart:
        """
        Update cart item quantity
        
        Args:
            request: Cart action request
            
        Returns:
            Updated shopping cart
        """
        try:
            if request.action != "update":
                raise ValueError("This method only handles 'update' actions")
            
            if not request.product_id or not request.quantity:
                raise ValueError("product_id and quantity are required for update action")
            
            # Get user's cart
            cart = await self.get_user_cart(request.user_id)
            
            # Find the item to update
            item_to_update = None
            for item in cart.items:
                if (item.product_id == request.product_id and 
                    item.size == request.size and 
                    item.color == request.color):
                    item_to_update = item
                    break
            
            if not item_to_update:
                raise ValueError("Item not found in cart")
            
            # Check inventory for new quantity
            inventory_check = await inventory_service.check_availability(
                request.product_id, 
                request.quantity
            )
            
            if not inventory_check.available:
                raise ValueError(f"Insufficient inventory. Available: {inventory_check.available_quantity}")
            
            # Update item
            item_to_update.quantity = request.quantity
            item_to_update.updated_at = datetime.now()
            
            # Recalculate cart totals
            await self._recalculate_cart_totals(cart)
            
            # Save updated cart
            await self._save_cart_to_db(cart)
            await self._cache_cart(cart)
            
            logger.info(f"Updated cart item {request.product_id} quantity to {request.quantity} for user {request.user_id}")
            return cart
            
        except Exception as e:
            logger.error(f"Update cart item failed: {e}")
            raise RuntimeError(f"Update cart item failed: {str(e)}")
    
    async def remove_from_cart(
        self,
        request: CartActionRequest
    ) -> ShoppingCart:
        """
        Remove item from shopping cart
        
        Args:
            request: Cart action request
            
        Returns:
            Updated shopping cart
        """
        try:
            if request.action != "remove":
                raise ValueError("This method only handles 'remove' actions")
            
            if not request.product_id:
                raise ValueError("product_id is required for remove action")
            
            # Get user's cart
            cart = await self.get_user_cart(request.user_id)
            
            # Find and remove the item
            item_removed = False
            for i, item in enumerate(cart.items):
                if (item.product_id == request.product_id and 
                    item.size == request.size and 
                    item.color == request.color):
                    cart.items.pop(i)
                    item_removed = True
                    break
            
            if not item_removed:
                raise ValueError("Item not found in cart")
            
            # Recalculate cart totals
            await self._recalculate_cart_totals(cart)
            
            # Save updated cart
            await self._save_cart_to_db(cart)
            await self._cache_cart(cart)
            
            logger.info(f"Removed {request.product_id} from cart for user {request.user_id}")
            return cart
            
        except Exception as e:
            logger.error(f"Remove from cart failed: {e}")
            raise RuntimeError(f"Remove from cart failed: {str(e)}")
    
    async def clear_cart(
        self,
        request: CartActionRequest
    ) -> ShoppingCart:
        """
        Clear all items from shopping cart
        
        Args:
            request: Cart action request
            
        Returns:
            Empty shopping cart
        """
        try:
            if request.action != "clear":
                raise ValueError("This method only handles 'clear' actions")
            
            # Get user's cart
            cart = await self.get_user_cart(request.user_id)
            
            # Clear all items
            cart.items = []
            
            # Reset totals
            await self._recalculate_cart_totals(cart)
            
            # Save updated cart
            await self._save_cart_to_db(cart)
            await self._cache_cart(cart)
            
            logger.info(f"Cleared cart for user {request.user_id}")
            return cart
            
        except Exception as e:
            logger.error(f"Clear cart failed: {e}")
            raise RuntimeError(f"Clear cart failed: {str(e)}")
    
    async def process_checkout(
        self,
        user_id: str,
        payment_method: str,
        shipping_address: Dict[str, str],
        billing_address: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process checkout and create order
        
        Args:
            user_id: User identifier
            payment_method: Payment method (mock)
            shipping_address: Shipping address details
            billing_address: Billing address details
            
        Returns:
            Checkout result with order and payment details
        """
        try:
            # Get user's cart
            cart = await self.get_user_cart(user_id)
            
            if not cart.items:
                raise ValueError("Cannot checkout with empty cart")
            
            # Validate inventory for all items
            inventory_issues = []
            for item in cart.items:
                inventory_check = await inventory_service.check_availability(
                    item.product_id, 
                    item.quantity
                )
                
                if not inventory_check.available:
                    inventory_issues.append({
                        "product_id": item.product_id,
                        "requested": item.quantity,
                        "available": inventory_check.available_quantity
                    })
            
            if inventory_issues:
                return {
                    "success": False,
                    "error": "Inventory issues found",
                    "inventory_issues": inventory_issues
                }
            
            # Reserve inventory
            reservations = []
            try:
                for item in cart.items:
                    reservation_id = str(uuid.uuid4())
                    success = await inventory_service.reserve_inventory(
                        item.product_id,
                        item.quantity,
                        reservation_id,
                        datetime.now() + timedelta(hours=1)  # 1 hour reservation
                    )
                    
                    if success:
                        reservations.append(reservation_id)
                    else:
                        # Release already made reservations
                        for res_id in reservations:
                            await inventory_service.release_reservation(res_id)
                        raise ValueError(f"Failed to reserve inventory for {item.product_id}")
                
                # Process mock payment
                payment_result = await self._process_mock_payment(cart, payment_method)
                
                if payment_result["success"]:
                    # Create order
                    order = await self._create_order(cart, payment_result["transaction"], shipping_address, billing_address)
                    
                    # Update inventory (reduce quantities)
                    for item in cart.items:
                        await inventory_service.update_inventory(
                            item.product_id,
                            -item.quantity,
                            "purchase",
                            order.id,
                            user_id
                        )
                    
                    # Release reservations (they're now fulfilled)
                    for res_id in reservations:
                        await inventory_service.release_reservation(res_id)
                    
                    # Clear cart
                    await self.clear_cart(CartActionRequest(user_id=user_id, action="clear"))
                    
                    return {
                        "success": True,
                        "order": order.dict(),
                        "payment": payment_result["transaction"].dict()
                    }
                else:
                    # Release reservations on payment failure
                    for res_id in reservations:
                        await inventory_service.release_reservation(res_id)
                    
                    return {
                        "success": False,
                        "error": "Payment failed",
                        "payment_error": payment_result.get("error")
                    }
                    
            except Exception as e:
                # Release any reservations made
                for res_id in reservations:
                    await inventory_service.release_reservation(res_id)
                raise e
            
        except Exception as e:
            logger.error(f"Checkout processing failed for user {user_id}: {e}")
            raise RuntimeError(f"Checkout failed: {str(e)}")
    
    async def get_user_orders(
        self,
        user_id: str,
        limit: int = 20,
        status_filter: Optional[OrderStatus] = None
    ) -> List[Order]:
        """
        Get user's order history
        
        Args:
            user_id: User identifier
            limit: Maximum number of orders
            status_filter: Filter by order status
            
        Returns:
            List of user orders
        """
        try:
            query = "SELECT * FROM orders WHERE user_id = %s"
            params = [user_id]
            
            if status_filter:
                query += " AND status = %s"
                params.append(status_filter.value)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            results = await db_manager.execute_query(query, params)
            
            orders = []
            for row in results:
                # Parse JSON fields
                items_data = json.loads(row["items"]) if row["items"] else []
                items = [CartItem(**item_data) for item_data in items_data]
                
                order = Order(
                    id=row["id"],
                    user_id=row["user_id"],
                    cart_id=row["cart_id"],
                    payment_id=row["payment_id"],
                    status=OrderStatus(row["status"]),
                    items=items,
                    total_amount=row["total_amount"],
                    shipping_address=json.loads(row["shipping_address"]),
                    billing_address=json.loads(row["billing_address"]),
                    estimated_delivery=row["estimated_delivery"],
                    tracking_number=row["tracking_number"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                orders.append(order)
            
            return orders
            
        except Exception as e:
            logger.error(f"Get user orders failed for {user_id}: {e}")
            return []
    
    async def get_order_details(
        self,
        order_id: str,
        user_id: str
    ) -> Optional[Order]:
        """
        Get detailed order information
        
        Args:
            order_id: Order identifier
            user_id: User identifier (for security)
            
        Returns:
            Order details or None if not found
        """
        try:
            query = "SELECT * FROM orders WHERE id = %s AND user_id = %s"
            results = await db_manager.execute_query(query, [order_id, user_id])
            
            if not results:
                return None
            
            row = results[0]
            
            # Parse JSON fields
            items_data = json.loads(row["items"]) if row["items"] else []
            items = [CartItem(**item_data) for item_data in items_data]
            
            return Order(
                id=row["id"],
                user_id=row["user_id"],
                cart_id=row["cart_id"],
                payment_id=row["payment_id"],
                status=OrderStatus(row["status"]),
                items=items,
                total_amount=row["total_amount"],
                shipping_address=json.loads(row["shipping_address"]),
                billing_address=json.loads(row["billing_address"]),
                estimated_delivery=row["estimated_delivery"],
                tracking_number=row["tracking_number"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Get order details failed for {order_id}: {e}")
            return None
    
    async def update_order_status(
        self,
        order_id: str,
        new_status: OrderStatus,
        tracking_number: Optional[str] = None
    ) -> bool:
        """
        Update order status (admin function)
        
        Args:
            order_id: Order identifier
            new_status: New order status
            tracking_number: Tracking number (for shipped status)
            
        Returns:
            True if update successful
        """
        try:
            update_fields = ["status = %s", "updated_at = %s"]
            params = [new_status.value, datetime.now()]
            
            if tracking_number:
                update_fields.append("tracking_number = %s")
                params.append(tracking_number)
            
            if new_status == OrderStatus.SHIPPED and not tracking_number:
                # Generate mock tracking number
                tracking_number = f"TRK{random.randint(100000, 999999)}"
                update_fields.append("tracking_number = %s")
                params.append(tracking_number)
            
            if new_status == OrderStatus.SHIPPED:
                # Set estimated delivery (3-7 business days)
                delivery_days = random.randint(3, 7)
                estimated_delivery = datetime.now() + timedelta(days=delivery_days)
                update_fields.append("estimated_delivery = %s")
                params.append(estimated_delivery)
            
            params.append(order_id)
            
            query = f"UPDATE orders SET {', '.join(update_fields)} WHERE id = %s"
            await db_manager.execute_query(query, params)
            
            logger.info(f"Order {order_id} status updated to {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Order status update failed for {order_id}: {e}")
            return False
    
    async def get_cart_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get shopping cart analytics for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Cart analytics data
        """
        try:
            # Get current cart
            cart = await self.get_user_cart(user_id)
            
            # Get user's order history for comparison
            orders = await self.get_user_orders(user_id, limit=50)
            
            analytics = {
                "current_cart": {
                    "item_count": len(cart.items),
                    "total_value": cart.total,
                    "average_item_price": cart.subtotal / len(cart.items) if cart.items else 0,
                    "categories": list(set(item.product_id for item in cart.items)),  # Simplified
                    "needs_attention": []
                },
                "purchase_history": {
                    "total_orders": len(orders),
                    "total_spent": sum(order.total_amount for order in orders),
                    "average_order_value": sum(order.total_amount for order in orders) / len(orders) if orders else 0,
                    "most_recent_order": orders[0].created_at.isoformat() if orders else None
                },
                "recommendations": []
            }
            
            # Add cart attention items
            if cart.total > 0 and cart.total < self.free_shipping_threshold:
                remaining = self.free_shipping_threshold - cart.total
                analytics["current_cart"]["needs_attention"].append(
                    f"Add ${remaining:.2f} more for free shipping"
                )
            
            # Add recommendations
            if cart.items:
                analytics["recommendations"].append("Ready to checkout? Don't forget to apply any promo codes!")
            else:
                analytics["recommendations"].append("Your cart is empty. Browse our latest products!")
            
            if len(orders) > 0:
                days_since_last_order = (datetime.now() - orders[0].created_at).days
                if days_since_last_order > 30:
                    analytics["recommendations"].append("It's been a while since your last order. Check out our new arrivals!")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Cart analytics failed for {user_id}: {e}")
            return {"error": "Analytics unavailable"}
    
    # Private helper methods
    
    async def _get_cart_from_db(self, user_id: str) -> Optional[ShoppingCart]:
        """Get cart from database"""
        try:
            query = "SELECT * FROM shopping_carts WHERE user_id = %s"
            results = await db_manager.execute_query(query, [user_id])
            
            if not results:
                return None
            
            row = results[0]
            
            # Get cart items
            items_query = "SELECT * FROM cart_items WHERE cart_id = %s"
            items_results = await db_manager.execute_query(items_query, [row["id"]])
            
            items = []
            for item_row in items_results:
                customizations = json.loads(item_row["customizations"]) if item_row["customizations"] else {}
                item = CartItem(
                    id=item_row["id"],
                    cart_id=item_row["cart_id"],
                    product_id=item_row["product_id"],
                    quantity=item_row["quantity"],
                    size=item_row["size"],
                    color=item_row["color"],
                    customizations=customizations,
                    price_at_addition=item_row["price_at_addition"],
                    added_at=item_row["added_at"],
                    updated_at=item_row["updated_at"]
                )
                items.append(item)
            
            return ShoppingCart(
                id=row["id"],
                user_id=row["user_id"],
                items=items,
                subtotal=row["subtotal"],
                tax_amount=row["tax_amount"],
                shipping_cost=row["shipping_cost"],
                discount_amount=row["discount_amount"],
                total=row["total"],
                currency=row["currency"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                expires_at=row["expires_at"]
            )
            
        except Exception as e:
            logger.error(f"Cart retrieval from DB failed: {e}")
            return None
    
    async def _create_new_cart(self, user_id: str) -> ShoppingCart:
        """Create new empty cart"""
        expires_at = datetime.now() + timedelta(hours=self.cart_expiry_hours)
        
        cart = ShoppingCart(
            user_id=user_id,
            expires_at=expires_at
        )
        
        await self._save_cart_to_db(cart)
        return cart
    
    async def _save_cart_to_db(self, cart: ShoppingCart):
        """Save cart to database"""
        try:
            # Upsert cart
            cart_query = """
                INSERT INTO shopping_carts 
                (id, user_id, subtotal, tax_amount, shipping_cost, discount_amount, 
                 total, currency, created_at, updated_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    subtotal = EXCLUDED.subtotal,
                    tax_amount = EXCLUDED.tax_amount,
                    shipping_cost = EXCLUDED.shipping_cost,
                    discount_amount = EXCLUDED.discount_amount,
                    total = EXCLUDED.total,
                    updated_at = EXCLUDED.updated_at
            """
            
            await db_manager.execute_query(cart_query, [
                cart.id, cart.user_id, cart.subtotal, cart.tax_amount,
                cart.shipping_cost, cart.discount_amount, cart.total,
                cart.currency, cart.created_at, cart.updated_at, cart.expires_at
            ])
            
            # Delete existing cart items
            await db_manager.execute_query("DELETE FROM cart_items WHERE cart_id = %s", [cart.id])
            
            # Insert current cart items
            for item in cart.items:
                item_query = """
                    INSERT INTO cart_items 
                    (id, cart_id, product_id, quantity, size, color, customizations,
                     price_at_addition, added_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                await db_manager.execute_query(item_query, [
                    item.id, item.cart_id, item.product_id, item.quantity,
                    item.size, item.color, json.dumps(item.customizations),
                    item.price_at_addition, item.added_at, item.updated_at
                ])
            
        except Exception as e:
            logger.error(f"Cart save to DB failed: {e}")
            raise
    
    async def _cache_cart(self, cart: ShoppingCart):
        """Cache cart data"""
        try:
            cache_key = f"cart:{cart.user_id}"
            cart_json = cart.json()
            await self.cache_service.set(cache_key, cart_json, self.cart_cache_ttl)
        except Exception as e:
            logger.error(f"Cart caching failed: {e}")
    
    async def _clear_expired_cart(self, user_id: str):
        """Clear expired cart"""
        try:
            # Delete from database
            query = "DELETE FROM shopping_carts WHERE user_id = %s"
            await db_manager.execute_query(query, [user_id])
            
            # Remove from cache
            cache_key = f"cart:{user_id}"
            await self.cache_service.delete(cache_key)
            
        except Exception as e:
            logger.error(f"Expired cart clearing failed: {e}")
    
    async def _get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product details for cart operations"""
        try:
            query = "SELECT * FROM products WHERE id = %s"
            results = await db_manager.execute_query(query, [product_id])
            
            return results[0] if results else None
            
        except Exception as e:
            logger.error(f"Product details retrieval failed: {e}")
            return None
    
    async def _recalculate_cart_totals(self, cart: ShoppingCart):
        """Recalculate cart totals"""
        try:
            # Calculate subtotal
            subtotal = 0
            for item in cart.items:
                subtotal += item.price_at_addition * item.quantity
            
            cart.subtotal = subtotal
            
            # Calculate shipping
            if subtotal >= self.free_shipping_threshold:
                cart.shipping_cost = 0
            else:
                cart.shipping_cost = self.standard_shipping_cost
            
            # Calculate tax
            cart.tax_amount = subtotal * self.tax_rate
            
            # Calculate total
            cart.total = cart.subtotal + cart.tax_amount + cart.shipping_cost - cart.discount_amount
            
            # Update timestamp
            cart.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Cart total recalculation failed: {e}")
            raise
    
    async def _process_mock_payment(
        self, 
        cart: ShoppingCart, 
        payment_method: str
    ) -> Dict[str, Any]:
        """Process mock payment transaction"""
        try:
            # Simulate processing delay
            await asyncio.sleep(self.payment_processing_delay)
            
            # Mock payment success/failure
            success = random.random() < self.payment_success_rate
            
            transaction = PaymentTransaction(
                cart_id=cart.id,
                user_id=cart.user_id,
                amount=cart.total,
                payment_method=payment_method,
                status=PaymentStatus.COMPLETED if success else PaymentStatus.FAILED,
                transaction_reference=f"TXN{random.randint(100000, 999999)}",
                processed_at=datetime.now() if success else None,
                failure_reason=None if success else "Mock payment failure for demonstration"
            )
            
            # Save transaction to database
            await self._save_payment_transaction(transaction)
            
            return {
                "success": success,
                "transaction": transaction,
                "error": transaction.failure_reason if not success else None
            }
            
        except Exception as e:
            logger.error(f"Mock payment processing failed: {e}")
            return {
                "success": False,
                "error": f"Payment processing error: {str(e)}"
            }
    
    async def _save_payment_transaction(self, transaction: PaymentTransaction):
        """Save payment transaction to database"""
        try:
            query = """
                INSERT INTO payment_transactions 
                (id, cart_id, user_id, amount, currency, payment_method, status,
                 transaction_reference, created_at, processed_at, failure_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            await db_manager.execute_query(query, [
                transaction.id, transaction.cart_id, transaction.user_id,
                transaction.amount, transaction.currency, transaction.payment_method,
                transaction.status.value, transaction.transaction_reference,
                transaction.created_at, transaction.processed_at, transaction.failure_reason
            ])
            
        except Exception as e:
            logger.error(f"Payment transaction save failed: {e}")
            raise
    
    async def _create_order(
        self,
        cart: ShoppingCart,
        payment: PaymentTransaction,
        shipping_address: Dict[str, str],
        billing_address: Dict[str, str]
    ) -> Order:
        """Create order from cart and payment"""
        try:
            order = Order(
                user_id=cart.user_id,
                cart_id=cart.id,
                payment_id=payment.id,
                status=OrderStatus.CONFIRMED,
                items=cart.items.copy(),
                total_amount=cart.total,
                shipping_address=shipping_address,
                billing_address=billing_address
            )
            
            # Save order to database
            await self._save_order_to_db(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            raise
    
    async def _save_order_to_db(self, order: Order):
        """Save order to database"""
        try:
            query = """
                INSERT INTO orders 
                (id, user_id, cart_id, payment_id, status, items, total_amount,
                 shipping_address, billing_address, estimated_delivery, tracking_number,
                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convert items to JSON
            items_json = json.dumps([item.dict() for item in order.items], default=str)
            
            await db_manager.execute_query(query, [
                order.id, order.user_id, order.cart_id, order.payment_id,
                order.status.value, items_json, order.total_amount,
                json.dumps(order.shipping_address), json.dumps(order.billing_address),
                order.estimated_delivery, order.tracking_number,
                order.created_at, order.updated_at
            ])
            
        except Exception as e:
            logger.error(f"Order save to DB failed: {e}")
            raise
    
    async def cleanup(self):
        """Clean up service resources"""
        try:
            logger.info("Cart and Payment Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during cart service cleanup: {e}")

# Global cart and payment service instance
cart_payment_service = CartPaymentService()
