"""
Database connection pooling and async database operations for performance optimization.
Supports multiple databases with connection pooling, health monitoring, and performance metrics.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager
import os
from datetime import datetime, timedelta

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    asyncpg = None
    ASYNCPG_AVAILABLE = False

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.pool import QueuePool, NullPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    from databases import Database
    DATABASES_AVAILABLE = True
except ImportError:
    Database = None
    DATABASES_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ConnectionPoolStats:
    """Connection pool performance statistics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_queries: int = 0
    failed_queries: int = 0
    avg_query_time: float = 0.0
    total_query_time: float = 0.0
    pool_exhausted_count: int = 0
    connection_errors: int = 0

class AsyncDatabasePool:
    """High-performance async database connection pool"""
    
    def __init__(self, database_url: str, pool_config: Optional[Dict[str, Any]] = None):
        self.database_url = database_url
        self.pool_config = pool_config or {}
        self.stats = ConnectionPoolStats()
        self.query_times = []
        self.max_query_history = 1000
        
        # Default pool configuration
        self.default_config = {
            "min_size": 5,
            "max_size": 20,
            "command_timeout": 30,
            "server_settings": {
                "application_name": "visual-ecommerce-api",
                "jit": "off"  # Disable JIT for faster connection times
            }
        }
        
        # Merge configurations
        self.config = {**self.default_config, **self.pool_config}
        self.pool = None
        self.database = None
        self.engine = None
        self.session_factory = None
    
    async def initialize(self):
        """Initialize database connections based on available drivers"""
        try:
            if ASYNCPG_AVAILABLE and "postgresql" in self.database_url:
                await self._init_asyncpg_pool()
            elif DATABASES_AVAILABLE:
                await self._init_databases_pool()
            elif SQLALCHEMY_AVAILABLE:
                await self._init_sqlalchemy_pool()
            else:
                raise RuntimeError("No suitable async database driver available")
                
            logger.info(f"Database pool initialized with {self.config['max_size']} max connections")
            
        except Exception as e:
            logger.error(f"Database pool initialization failed: {e}")
            raise
    
    async def _init_asyncpg_pool(self):
        """Initialize asyncpg connection pool"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.config["min_size"],
            max_size=self.config["max_size"],
            command_timeout=self.config["command_timeout"],
            server_settings=self.config["server_settings"]
        )
        logger.info("AsyncPG pool initialized")
    
    async def _init_databases_pool(self):
        """Initialize databases connection pool"""
        self.database = Database(
            self.database_url,
            min_size=self.config["min_size"],
            max_size=self.config["max_size"]
        )
        await self.database.connect()
        logger.info("Databases pool initialized")
    
    async def _init_sqlalchemy_pool(self):
        """Initialize SQLAlchemy async engine"""
        pool_class = QueuePool if "sqlite" not in self.database_url else NullPool
        
        self.engine = create_async_engine(
            self.database_url,
            poolclass=pool_class,
            pool_size=self.config["min_size"],
            max_overflow=self.config["max_size"] - self.config["min_size"],
            pool_timeout=30,
            pool_recycle=3600,  # Recycle connections every hour
            echo=False
        )
        
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("SQLAlchemy async engine initialized")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        connection = None
        start_time = time.time()
        
        try:
            if self.pool:  # AsyncPG
                connection = await self.pool.acquire()
                self.stats.active_connections += 1
            elif self.database:  # Databases
                yield self.database
                return
            elif self.session_factory:  # SQLAlchemy
                async with self.session_factory() as session:
                    yield session
                    return
            else:
                raise RuntimeError("No database pool available")
            
            yield connection
            
        except asyncpg.PoolError if ASYNCPG_AVAILABLE else Exception as e:
            self.stats.pool_exhausted_count += 1
            logger.error(f"Pool exhausted or connection error: {e}")
            raise
        except Exception as e:
            self.stats.connection_errors += 1
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and self.pool:
                await self.pool.release(connection)
                self.stats.active_connections -= 1
            
            # Record connection time
            connection_time = time.time() - start_time
            self._record_query_time(connection_time)
    
    async def execute_query(self, query: str, values: Optional[List] = None) -> List[Dict[str, Any]]:
        """Execute a query with performance tracking"""
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                if self.pool:  # AsyncPG
                    if values:
                        result = await conn.fetch(query, *values)
                    else:
                        result = await conn.fetch(query)
                    return [dict(record) for record in result]
                
                elif self.database:  # Databases
                    if values:
                        result = await conn.fetch_all(query=query, values=values)
                    else:
                        result = await conn.fetch_all(query=query)
                    return [dict(record) for record in result]
                
                else:  # SQLAlchemy
                    result = await conn.execute(query, values or {})
                    return [dict(row) for row in result.fetchall()]
        
        except Exception as e:
            self.stats.failed_queries += 1
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            query_time = time.time() - start_time
            self._record_query_time(query_time)
            self.stats.total_queries += 1
    
    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> bool:
        """Execute multiple queries in a transaction"""
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                if self.pool:  # AsyncPG
                    async with conn.transaction():
                        for query_data in queries:
                            query = query_data["query"]
                            values = query_data.get("values", [])
                            if values:
                                await conn.execute(query, *values)
                            else:
                                await conn.execute(query)
                
                elif self.database:  # Databases
                    async with self.database.transaction():
                        for query_data in queries:
                            query = query_data["query"]
                            values = query_data.get("values", {})
                            await conn.execute(query=query, values=values)
                
                else:  # SQLAlchemy
                    async with conn.begin():
                        for query_data in queries:
                            query = query_data["query"]
                            values = query_data.get("values", {})
                            await conn.execute(query, values)
                
                return True
                
        except Exception as e:
            self.stats.failed_queries += len(queries)
            logger.error(f"Transaction failed: {e}")
            return False
        finally:
            transaction_time = time.time() - start_time
            self._record_query_time(transaction_time)
            self.stats.total_queries += len(queries)
    
    async def batch_execute(self, query: str, batch_values: List[List]) -> bool:
        """Execute query with multiple value sets efficiently"""
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                if self.pool:  # AsyncPG
                    await conn.executemany(query, batch_values)
                elif self.database:  # Databases
                    await conn.execute_many(query=query, values=batch_values)
                else:  # SQLAlchemy
                    await conn.execute(query, batch_values)
                
                return True
                
        except Exception as e:
            self.stats.failed_queries += 1
            logger.error(f"Batch execute failed: {e}")
            return False
        finally:
            batch_time = time.time() - start_time
            self._record_query_time(batch_time)
            self.stats.total_queries += 1
    
    def _record_query_time(self, duration: float):
        """Record query execution time for performance monitoring"""
        self.query_times.append(duration)
        
        # Keep only recent query times
        if len(self.query_times) > self.max_query_history:
            self.query_times = self.query_times[-self.max_query_history:]
        
        # Update average
        self.stats.total_query_time += duration
        if self.stats.total_queries > 0:
            self.stats.avg_query_time = self.stats.total_query_time / self.stats.total_queries
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and statistics"""
        status = {
            "driver": "unknown",
            "total_connections": 0,
            "active_connections": self.stats.active_connections,
            "idle_connections": 0,
            "pool_exhausted": self.stats.pool_exhausted_count > 0,
            "health": "unknown"
        }
        
        try:
            if self.pool:  # AsyncPG
                status.update({
                    "driver": "asyncpg",
                    "total_connections": self.pool.get_size(),
                    "idle_connections": self.pool.get_idle_size(),
                    "health": "healthy" if self.pool.get_size() > 0 else "unhealthy"
                })
            elif self.database:  # Databases
                status.update({
                    "driver": "databases",
                    "total_connections": self.config["max_size"],
                    "health": "healthy" if self.database.is_connected else "unhealthy"
                })
            elif self.engine:  # SQLAlchemy
                pool = self.engine.pool
                status.update({
                    "driver": "sqlalchemy",
                    "total_connections": pool.size(),
                    "idle_connections": pool.checkedin(),
                    "health": "healthy"
                })
        
        except Exception as e:
            logger.error(f"Error getting pool status: {e}")
            status["health"] = "error"
        
        return status
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        recent_query_times = self.query_times[-100:] if self.query_times else []
        
        return {
            "total_queries": self.stats.total_queries,
            "failed_queries": self.stats.failed_queries,
            "success_rate": (self.stats.total_queries - self.stats.failed_queries) / self.stats.total_queries if self.stats.total_queries > 0 else 0,
            "avg_query_time_ms": self.stats.avg_query_time * 1000,
            "recent_avg_query_time_ms": (sum(recent_query_times) / len(recent_query_times) * 1000) if recent_query_times else 0,
            "p95_query_time_ms": sorted(recent_query_times)[int(len(recent_query_times) * 0.95)] * 1000 if len(recent_query_times) > 5 else 0,
            "pool_exhausted_count": self.stats.pool_exhausted_count,
            "connection_errors": self.stats.connection_errors,
            "total_query_time": self.stats.total_query_time
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        health = {
            "status": "unhealthy",
            "connection_test": False,
            "query_test": False,
            "latency_ms": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            # Test connection and simple query
            await self.execute_query("SELECT 1 as test")
            
            latency = (time.time() - start_time) * 1000
            
            health.update({
                "status": "healthy",
                "connection_test": True,
                "query_test": True,
                "latency_ms": round(latency, 2)
            })
            
        except Exception as e:
            health["error"] = str(e)
            logger.error(f"Database health check failed: {e}")
        
        return health
    
    async def close(self):
        """Close all database connections"""
        try:
            if self.pool:
                await self.pool.close()
            elif self.database:
                await self.database.disconnect()
            elif self.engine:
                await self.engine.dispose()
            
            logger.info("Database pool closed")
            
        except Exception as e:
            logger.error(f"Error closing database pool: {e}")

class DatabaseManager:
    """Manager for multiple database connections"""
    
    def __init__(self):
        self.pools: Dict[str, AsyncDatabasePool] = {}
        self.default_pool_name = "default"
    
    async def add_pool(self, name: str, database_url: str, pool_config: Optional[Dict[str, Any]] = None):
        """Add a new database pool"""
        if name in self.pools:
            await self.pools[name].close()
        
        pool = AsyncDatabasePool(database_url, pool_config)
        await pool.initialize()
        self.pools[name] = pool
        
        logger.info(f"Added database pool '{name}'")
    
    def get_pool(self, name: str = None) -> AsyncDatabasePool:
        """Get database pool by name"""
        pool_name = name or self.default_pool_name
        
        if pool_name not in self.pools:
            raise ValueError(f"Database pool '{pool_name}' not found")
        
        return self.pools[pool_name]
    
    async def execute_query(self, query: str, values: Optional[List] = None, pool_name: str = None) -> List[Dict[str, Any]]:
        """Execute query on specified pool"""
        pool = self.get_pool(pool_name)
        return await pool.execute_query(query, values)
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all pools"""
        stats = {}
        
        for name, pool in self.pools.items():
            stats[name] = {
                "pool_status": await pool.get_pool_status(),
                "performance": pool.get_performance_stats()
            }
        
        return stats
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check for all pools"""
        health_checks = {}
        
        for name, pool in self.pools.items():
            health_checks[name] = await pool.health_check()
        
        overall_health = all(check["status"] == "healthy" for check in health_checks.values())
        
        return {
            "overall_status": "healthy" if overall_health else "unhealthy",
            "pools": health_checks
        }
    
    async def close_all(self):
        """Close all database pools"""
        for name, pool in self.pools.items():
            await pool.close()
        
        self.pools.clear()
        logger.info("All database pools closed")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
async def get_db_connection(pool_name: str = None):
    """Get database connection from pool"""
    pool = db_manager.get_pool(pool_name)
    return pool.get_connection()

async def execute_db_query(query: str, values: Optional[List] = None, pool_name: str = None) -> List[Dict[str, Any]]:
    """Execute database query"""
    return await db_manager.execute_query(query, values, pool_name)
