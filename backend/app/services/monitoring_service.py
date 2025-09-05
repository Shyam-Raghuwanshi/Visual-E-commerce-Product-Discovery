"""
Advanced monitoring and logging service for performance optimization.
Includes Prometheus metrics, structured logging, performance tracking, and alerting.
"""

import time
import asyncio
import logging
import json
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
import threading
from contextlib import contextmanager

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    structlog = None
    STRUCTLOG_AVAILABLE = False

try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    jsonlogger = None
    JSON_LOGGER_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric: str
    condition: str  # "gt", "lt", "eq"
    threshold: float
    duration_seconds: int = 300  # 5 minutes
    severity: str = "warning"  # "info", "warning", "error", "critical"
    enabled: bool = True

class MetricsCollector:
    """High-performance metrics collection system"""
    
    def __init__(self):
        self.metrics: Dict[str, List[PerformanceMetric]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.max_metric_history = 10000
        
        # Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self.registry = CollectorRegistry()
            self.prom_counters = {}
            self.prom_gauges = {}
            self.prom_histograms = {}
            self.prom_summaries = {}
            self._init_prometheus_metrics()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        if not PROMETHEUS_AVAILABLE:
            return
        
        # HTTP metrics
        self.prom_counters['http_requests_total'] = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.prom_histograms['http_request_duration'] = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Search metrics
        self.prom_counters['search_requests_total'] = Counter(
            'search_requests_total',
            'Total search requests',
            ['search_type', 'status'],
            registry=self.registry
        )
        
        self.prom_histograms['search_duration'] = Histogram(
            'search_duration_seconds',
            'Search request duration',
            ['search_type'],
            registry=self.registry
        )
        
        # Cache metrics
        self.prom_counters['cache_operations_total'] = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.prom_gauges['cache_hit_rate'] = Gauge(
            'cache_hit_rate',
            'Cache hit rate',
            registry=self.registry
        )
        
        # Database metrics
        self.prom_gauges['db_connections_active'] = Gauge(
            'db_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.prom_histograms['db_query_duration'] = Histogram(
            'db_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            registry=self.registry
        )
        
        # Image processing metrics
        self.prom_counters['image_operations_total'] = Counter(
            'image_operations_total',
            'Total image operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        self.prom_histograms['image_processing_duration'] = Histogram(
            'image_processing_duration_seconds',
            'Image processing duration',
            ['operation'],
            registry=self.registry
        )
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        self.counters[name] += value
        
        # Add to metrics history
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self.metrics[name].append(metric)
        self._cleanup_metric_history(name)
        
        # Update Prometheus if available
        if PROMETHEUS_AVAILABLE and name in self.prom_counters:
            if labels:
                self.prom_counters[name].labels(**labels).inc(value)
            else:
                self.prom_counters[name].inc(value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        self.gauges[name] = value
        
        # Add to metrics history
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self.metrics[name].append(metric)
        self._cleanup_metric_history(name)
        
        # Update Prometheus if available
        if PROMETHEUS_AVAILABLE and name in self.prom_gauges:
            if labels:
                self.prom_gauges[name].labels(**labels).set(value)
            else:
                self.prom_gauges[name].set(value)
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Add observation to histogram"""
        self.histograms[name].append(value)
        
        # Keep only recent observations
        if len(self.histograms[name]) > self.max_metric_history:
            self.histograms[name] = self.histograms[name][-self.max_metric_history:]
        
        # Add to metrics history
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {}
        )
        self.metrics[name].append(metric)
        self._cleanup_metric_history(name)
        
        # Update Prometheus if available
        if PROMETHEUS_AVAILABLE and name in self.prom_histograms:
            if labels:
                self.prom_histograms[name].labels(**labels).observe(value)
            else:
                self.prom_histograms[name].observe(value)
    
    def _cleanup_metric_history(self, name: str):
        """Clean up old metric history"""
        if len(self.metrics[name]) > self.max_metric_history:
            self.metrics[name] = self.metrics[name][-self.max_metric_history:]
    
    def get_metric_summary(self, name: str, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics[name] if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {"count": 0, "message": "No recent data"}
        
        values = [m.value for m in recent_metrics]
        
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p50": sorted(values)[len(values) // 2] if values else 0,
            "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 5 else max(values),
            "p99": sorted(values)[int(len(values) * 0.99)] if len(values) > 10 else max(values),
            "latest": values[-1] if values else 0,
            "trend": "increasing" if len(values) > 1 and values[-1] > values[0] else "stable"
        }
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus not available\n"
        
        return generate_latest(self.registry).decode('utf-8')

class PerformanceProfiler:
    """Function and endpoint performance profiler"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.active_requests = {}
        self.request_counter = 0
        self.lock = threading.Lock()
    
    @contextmanager
    def profile_request(self, endpoint: str, method: str = "GET"):
        """Context manager for profiling HTTP requests"""
        request_id = None
        start_time = time.time()
        
        try:
            with self.lock:
                self.request_counter += 1
                request_id = f"{endpoint}_{self.request_counter}"
                self.active_requests[request_id] = {
                    "endpoint": endpoint,
                    "method": method,
                    "start_time": start_time
                }
            
            yield request_id
            
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics.observe_histogram(
                'http_request_duration',
                duration,
                {"method": method, "endpoint": endpoint}
            )
            
            self.metrics.increment_counter(
                'http_requests_total',
                labels={"method": method, "endpoint": endpoint, "status": "success"}
            )
            
            # Clean up
            with self.lock:
                if request_id in self.active_requests:
                    del self.active_requests[request_id]
    
    def profile_function(self, name: str, category: str = "general"):
        """Decorator for profiling function performance"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    status = "success"
                    return result
                except Exception as e:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    self.metrics.observe_histogram(
                        f'{category}_function_duration',
                        duration,
                        {"function": name}
                    )
                    self.metrics.increment_counter(
                        f'{category}_function_calls',
                        labels={"function": name, "status": status}
                    )
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    status = "success"
                    return result
                except Exception as e:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    self.metrics.observe_histogram(
                        f'{category}_function_duration',
                        duration,
                        {"function": name}
                    )
                    self.metrics.increment_counter(
                        f'{category}_function_calls',
                        labels={"function": name, "status": status}
                    )
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator

class AlertManager:
    """Alert management system"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def add_rule(self, rule: AlertRule):
        """Add alert rule"""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alert rules and return active alerts"""
        current_alerts = []
        now = datetime.now()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                # Get recent metric values
                recent_metrics = [
                    m for m in self.metrics.metrics[rule.metric]
                    if m.timestamp >= now - timedelta(seconds=rule.duration_seconds)
                ]
                
                if not recent_metrics:
                    continue
                
                # Calculate current value (average of recent metrics)
                current_value = sum(m.value for m in recent_metrics) / len(recent_metrics)
                
                # Check condition
                alert_triggered = False
                if rule.condition == "gt" and current_value > rule.threshold:
                    alert_triggered = True
                elif rule.condition == "lt" and current_value < rule.threshold:
                    alert_triggered = True
                elif rule.condition == "eq" and abs(current_value - rule.threshold) < 0.001:
                    alert_triggered = True
                
                if alert_triggered:
                    alert_key = f"{rule.name}_{rule.metric}"
                    
                    # Check if this is a new alert
                    if alert_key not in self.active_alerts:
                        self.active_alerts[alert_key] = now
                        
                        alert = {
                            "rule_name": rule.name,
                            "metric": rule.metric,
                            "current_value": current_value,
                            "threshold": rule.threshold,
                            "condition": rule.condition,
                            "severity": rule.severity,
                            "triggered_at": now,
                            "duration": rule.duration_seconds
                        }
                        
                        current_alerts.append(alert)
                        self.alert_history.append(alert)
                        
                        # Keep history size manageable
                        if len(self.alert_history) > self.max_history:
                            self.alert_history = self.alert_history[-self.max_history:]
                        
                        logger.warning(f"Alert triggered: {rule.name} - {current_value} {rule.condition} {rule.threshold}")
                
                else:
                    # Remove from active alerts if condition no longer met
                    alert_key = f"{rule.name}_{rule.metric}"
                    if alert_key in self.active_alerts:
                        del self.active_alerts[alert_key]
                        logger.info(f"Alert resolved: {rule.name}")
            
            except Exception as e:
                logger.error(f"Error checking alert rule {rule.name}: {e}")
        
        return current_alerts

class StructuredLogger:
    """Enhanced structured logging system"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup structured logging"""
        # Create logger
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logger = logging.getLogger("visual_ecommerce")
        logger.setLevel(getattr(logging, log_level))
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatter
        if JSON_LOGGER_AVAILABLE:
            formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = os.getenv("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(f"{log_dir}/app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_request(self, method: str, endpoint: str, duration: float, status_code: int, user_id: str = None):
        """Log HTTP request"""
        self.logger.info(
            "HTTP request",
            extra={
                "event_type": "http_request",
                "method": method,
                "endpoint": endpoint,
                "duration_ms": duration * 1000,
                "status_code": status_code,
                "user_id": user_id
            }
        )
    
    def log_search(self, search_type: str, query: str, results_count: int, duration: float, user_id: str = None):
        """Log search operation"""
        self.logger.info(
            "Search request",
            extra={
                "event_type": "search",
                "search_type": search_type,
                "query": query[:100],  # Truncate long queries
                "results_count": results_count,
                "duration_ms": duration * 1000,
                "user_id": user_id
            }
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context"""
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "event_type": "error",
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {}
            },
            exc_info=True
        )

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.profiler = PerformanceProfiler(self.metrics_collector)
        self.alert_manager = AlertManager(self.metrics_collector)
        self.structured_logger = StructuredLogger()
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default alert rules"""
        default_rules = [
            AlertRule(
                name="High Response Time",
                metric="http_request_duration",
                condition="gt",
                threshold=2.0,  # 2 seconds
                severity="warning"
            ),
            AlertRule(
                name="Low Cache Hit Rate",
                metric="cache_hit_rate",
                condition="lt",
                threshold=0.7,  # 70%
                severity="warning"
            ),
            AlertRule(
                name="High Error Rate",
                metric="error_rate",
                condition="gt",
                threshold=0.05,  # 5%
                severity="error"
            )
        ]
        
        for rule in default_rules:
            self.alert_manager.add_rule(rule)
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_summary": {
                "total_requests": self.metrics_collector.counters.get("http_requests_total", 0),
                "cache_hit_rate": self.metrics_collector.gauges.get("cache_hit_rate", 0),
                "active_connections": self.metrics_collector.gauges.get("db_connections_active", 0),
            },
            "performance_summary": {
                name: self.metrics_collector.get_metric_summary(name, hours=1)
                for name in ["http_request_duration", "search_duration", "db_query_duration"]
                if name in self.metrics_collector.metrics
            },
            "active_alerts": len(self.alert_manager.active_alerts),
            "recent_alerts": self.alert_manager.alert_history[-5:] if self.alert_manager.alert_history else [],
            "system_status": "healthy" if len(self.alert_manager.active_alerts) == 0 else "degraded"
        }

# Global monitoring instance
performance_monitor = PerformanceMonitor()

# Convenience functions
def track_metric(name: str, value: float, metric_type: str = "gauge", labels: Optional[Dict[str, str]] = None):
    """Track a metric"""
    if metric_type == "counter":
        performance_monitor.metrics_collector.increment_counter(name, int(value), labels)
    elif metric_type == "gauge":
        performance_monitor.metrics_collector.set_gauge(name, value, labels)
    elif metric_type == "histogram":
        performance_monitor.metrics_collector.observe_histogram(name, value, labels)

def profile_function(name: str, category: str = "general"):
    """Decorator for profiling functions"""
    return performance_monitor.profiler.profile_function(name, category)

def log_request(method: str, endpoint: str, duration: float, status_code: int, user_id: str = None):
    """Log HTTP request"""
    performance_monitor.structured_logger.log_request(method, endpoint, duration, status_code, user_id)

def log_search(search_type: str, query: str, results_count: int, duration: float, user_id: str = None):
    """Log search operation"""
    performance_monitor.structured_logger.log_search(search_type, query, results_count, duration, user_id)

def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context"""
    performance_monitor.structured_logger.log_error(error, context)
