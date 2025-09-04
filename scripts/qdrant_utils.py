#!/usr/bin/env python3
"""
Qdrant Database Utilities
Additional utility functions for database management and maintenance
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from datetime import datetime

from setup_qdrant import QdrantDatabaseManager, ProductData

logger = logging.getLogger(__name__)

class QdrantUtilities:
    """
    Utility functions for Qdrant database maintenance and operations
    """
    
    def __init__(self, db_manager: QdrantDatabaseManager):
        self.db_manager = db_manager
    
    async def backup_collection(self, backup_path: str) -> bool:
        """
        Backup collection data to JSON file
        
        Args:
            backup_path: Path to save backup file
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            if not self.db_manager.client:
                raise Exception("Not connected to Qdrant")
            
            logger.info(f"Starting backup to {backup_path}")
            
            # Get all points from collection
            points = []
            offset = None
            limit = 100
            
            while True:
                batch = self.db_manager.client.scroll(
                    collection_name=self.db_manager.collection_name,
                    limit=limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True
                )
                
                if not batch[0]:  # No more points
                    break
                
                for point in batch[0]:
                    points.append({
                        "id": point.id,
                        "vector": point.vector,
                        "payload": point.payload
                    })
                
                offset = batch[1]  # Next offset
            
            # Save to file
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "collection_name": self.db_manager.collection_name,
                "points_count": len(points),
                "vector_size": self.db_manager.vector_size,
                "points": points
            }
            
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Backup completed: {len(points)} points saved to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False
    
    async def restore_collection(self, backup_path: str, recreate: bool = True) -> bool:
        """
        Restore collection from backup file
        
        Args:
            backup_path: Path to backup file
            recreate: Whether to recreate the collection
            
        Returns:
            bool: True if restore successful, False otherwise
        """
        try:
            if not Path(backup_path).exists():
                raise Exception(f"Backup file not found: {backup_path}")
            
            logger.info(f"Starting restore from {backup_path}")
            
            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Recreate collection if requested
            if recreate:
                await self.db_manager.create_collection(recreate=True)
                await self.db_manager.setup_indexes()
            
            # Convert backup data to ProductData objects
            products = []
            for point_data in backup_data["points"]:
                payload = point_data["payload"]
                
                product = ProductData(
                    id=point_data["id"],
                    name=payload.get("name", ""),
                    description=payload.get("description", ""),
                    price=payload.get("price", 0.0),
                    category=payload.get("category", ""),
                    brand=payload.get("brand"),
                    image_url=payload.get("image_url", ""),
                    embedding=np.array(point_data["vector"], dtype=np.float32),
                    metadata={k: v for k, v in payload.items() 
                             if k not in ["name", "description", "price", "category", "brand", "image_url"]}
                )
                products.append(product)
            
            # Insert products
            success = await self.db_manager.bulk_insert_products(products)
            
            if success:
                logger.info(f"Restore completed: {len(products)} points restored")
            
            return success
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False
    
    async def clear_collection(self) -> bool:
        """
        Clear all data from the collection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.db_manager.client:
                raise Exception("Not connected to Qdrant")
            
            logger.info(f"Clearing collection: {self.db_manager.collection_name}")
            
            # Delete and recreate collection
            self.db_manager.client.delete_collection(self.db_manager.collection_name)
            await self.db_manager.create_collection()
            await self.db_manager.setup_indexes()
            
            logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get detailed collection statistics
        
        Returns:
            Dict with collection statistics
        """
        try:
            if not self.db_manager.client:
                raise Exception("Not connected to Qdrant")
            
            collection_info = self.db_manager.client.get_collection(self.db_manager.collection_name)
            
            # Get category distribution
            category_stats = {}
            brand_stats = {}
            
            # Scroll through all points to get statistics
            offset = None
            limit = 1000
            total_points = 0
            price_sum = 0
            prices = []
            
            while True:
                batch = self.db_manager.client.scroll(
                    collection_name=self.db_manager.collection_name,
                    limit=limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                if not batch[0]:
                    break
                
                for point in batch[0]:
                    total_points += 1
                    payload = point.payload
                    
                    # Category stats
                    category = payload.get("category", "unknown")
                    category_stats[category] = category_stats.get(category, 0) + 1
                    
                    # Brand stats
                    brand = payload.get("brand", "unknown")
                    brand_stats[brand] = brand_stats.get(brand, 0) + 1
                    
                    # Price stats
                    price = payload.get("price", 0)
                    if price > 0:
                        price_sum += price
                        prices.append(price)
                
                offset = batch[1]
            
            # Calculate price statistics
            price_stats = {}
            if prices:
                prices.sort()
                price_stats = {
                    "count": len(prices),
                    "min": min(prices),
                    "max": max(prices),
                    "average": price_sum / len(prices),
                    "median": prices[len(prices) // 2]
                }
            
            stats = {
                "collection_name": self.db_manager.collection_name,
                "total_points": total_points,
                "indexed_vectors": collection_info.indexed_vectors_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "status": collection_info.status.value,
                "category_distribution": category_stats,
                "brand_distribution": brand_stats,
                "price_statistics": price_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}
    
    async def optimize_collection(self) -> bool:
        """
        Optimize collection for better performance
        
        Returns:
            bool: True if optimization successful, False otherwise
        """
        try:
            if not self.db_manager.client:
                raise Exception("Not connected to Qdrant")
            
            logger.info("Starting collection optimization...")
            
            # Update collection to use optimal settings
            from qdrant_client.models import OptimizersConfigDiff, VectorParams
            
            # This is a placeholder for optimization settings
            # In practice, you might adjust:
            # - Indexing threshold
            # - Memory mapping
            # - Quantization settings
            
            logger.info("Collection optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            return False

async def main():
    """
    Demo of utility functions
    """
    print("🔧 Qdrant Database Utilities Demo")
    print("=" * 40)
    
    # Initialize database manager
    db_manager = QdrantDatabaseManager()
    
    # Connect
    if not await db_manager.connect():
        print("❌ Failed to connect to Qdrant")
        return
    
    # Initialize utilities
    utils = QdrantUtilities(db_manager)
    
    # Get collection stats
    print("\n📊 Collection Statistics:")
    stats = await utils.get_collection_stats()
    if stats:
        print(f"  Total Points: {stats.get('total_points', 0)}")
        print(f"  Categories: {len(stats.get('category_distribution', {}))}")
        print(f"  Brands: {len(stats.get('brand_distribution', {}))}")
        
        price_stats = stats.get('price_statistics', {})
        if price_stats:
            print(f"  Price Range: ${price_stats.get('min', 0):.2f} - ${price_stats.get('max', 0):.2f}")
            print(f"  Average Price: ${price_stats.get('average', 0):.2f}")
    
    # Health check
    print("\n🏥 Health Check:")
    health = await db_manager.health_check()
    print(f"  Status: {health.get('status', 'unknown')}")
    print(f"  Collections: {health.get('collections_count', 0)}")
    
    print("\n✅ Utilities demo completed!")

if __name__ == "__main__":
    asyncio.run(main())
