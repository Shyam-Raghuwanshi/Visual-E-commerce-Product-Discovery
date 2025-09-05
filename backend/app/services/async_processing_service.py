"""
Enhanced async processing service for batch operations and background tasks.
Supports job queues, task scheduling, progress tracking, and distributed processing.
"""

import asyncio
import time
import json
import logging
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from queue import Queue, PriorityQueue
import threading
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatchJob:
    """Batch processing job definition"""
    job_id: str
    tasks: List[Dict[str, Any]]
    batch_size: int = 10
    max_workers: int = 4
    retry_attempts: int = 3
    timeout_seconds: int = 300
    priority: TaskPriority = TaskPriority.NORMAL
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class TaskQueue:
    """High-performance task queue with priority support"""
    
    def __init__(self, max_size: int = 10000):
        self.queue = PriorityQueue(maxsize=max_size)
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.max_completed_history = 1000
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "avg_execution_time": 0.0
        }
        self.lock = threading.Lock()
    
    def add_task(self, task_id: str, func: Callable, args: tuple = (), kwargs: dict = None, 
                 priority: TaskPriority = TaskPriority.NORMAL, metadata: dict = None) -> bool:
        """Add task to queue"""
        try:
            task_data = {
                "task_id": task_id,
                "func": func,
                "args": args,
                "kwargs": kwargs or {},
                "priority": priority,
                "metadata": metadata or {},
                "created_at": datetime.now(),
                "retries": 0
            }
            
            # Use priority enum value for queue ordering
            self.queue.put((priority.value, time.time(), task_data))
            
            with self.lock:
                self.pending_tasks[task_id] = task_data
                self.stats["total_tasks"] += 1
            
            logger.debug(f"Added task {task_id} with priority {priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task {task_id}: {e}")
            return False
    
    def get_task(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Get next task from queue"""
        try:
            _, _, task_data = self.queue.get(timeout=timeout)
            
            with self.lock:
                if task_data["task_id"] in self.pending_tasks:
                    del self.pending_tasks[task_data["task_id"]]
            
            return task_data
            
        except:
            return None
    
    def complete_task(self, task_id: str, result: TaskResult):
        """Mark task as completed"""
        with self.lock:
            self.completed_tasks[task_id] = result
            
            # Update statistics
            if result.status == TaskStatus.COMPLETED:
                self.stats["completed_tasks"] += 1
            elif result.status == TaskStatus.FAILED:
                self.stats["failed_tasks"] += 1
            elif result.status == TaskStatus.CANCELLED:
                self.stats["cancelled_tasks"] += 1
            
            # Update average execution time
            if result.duration:
                completed = self.stats["completed_tasks"]
                if completed > 0:
                    current_avg = self.stats["avg_execution_time"]
                    self.stats["avg_execution_time"] = (
                        (current_avg * (completed - 1) + result.duration) / completed
                    )
            
            # Clean up old completed tasks
            if len(self.completed_tasks) > self.max_completed_history:
                oldest_tasks = sorted(
                    self.completed_tasks.items(),
                    key=lambda x: x[1].end_time or datetime.min
                )[:50]
                for old_task_id, _ in oldest_tasks:
                    del self.completed_tasks[old_task_id]
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get task status"""
        with self.lock:
            return self.completed_tasks.get(task_id)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                "queue_size": self.queue.qsize(),
                "pending_tasks": len(self.pending_tasks),
                "completed_tasks_history": len(self.completed_tasks),
                "stats": self.stats.copy()
            }

class AsyncTaskExecutor:
    """Async task execution engine"""
    
    def __init__(self, max_workers: int = 10, thread_pool_size: int = 4, process_pool_size: int = 2):
        self.max_workers = max_workers
        self.task_queue = TaskQueue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)
        self.process_pool = ProcessPoolExecutor(max_workers=process_pool_size)
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start the task executor"""
        if self.is_running:
            return
        
        self.is_running = True
        self.shutdown_event.clear()
        
        # Start worker coroutines
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Started async task executor with {self.max_workers} workers")
    
    async def stop(self):
        """Stop the task executor"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.shutdown_event.set()
        
        # Cancel running tasks
        for task_id, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled running task: {task_id}")
        
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        logger.info("Async task executor stopped")
    
    async def _worker(self, worker_name: str):
        """Worker coroutine"""
        logger.debug(f"Worker {worker_name} started")
        
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Get task from queue
                task_data = self.task_queue.get_task(timeout=1.0)
                
                if task_data is None:
                    continue
                
                task_id = task_data["task_id"]
                logger.debug(f"Worker {worker_name} processing task {task_id}")
                
                # Execute task
                result = await self._execute_task(task_data)
                
                # Store result
                self.task_queue.complete_task(task_id, result)
                
                # Clean up
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
        
        logger.debug(f"Worker {worker_name} stopped")
    
    async def _execute_task(self, task_data: Dict[str, Any]) -> TaskResult:
        """Execute a single task"""
        task_id = task_data["task_id"]
        func = task_data["func"]
        args = task_data["args"]
        kwargs = task_data["kwargs"]
        
        result = TaskResult(
            task_id=task_id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            start_time = time.time()
            
            # Determine execution method
            if asyncio.iscoroutinefunction(func):
                # Async function
                task_result = await func(*args, **kwargs)
            elif hasattr(func, '__call__') and not asyncio.iscoroutinefunction(func):
                # Sync function - run in thread pool
                loop = asyncio.get_event_loop()
                task_result = await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
            else:
                raise ValueError(f"Invalid function type for task {task_id}")
            
            duration = time.time() - start_time
            
            result.status = TaskStatus.COMPLETED
            result.result = task_result
            result.end_time = datetime.now()
            result.duration = duration
            
            logger.debug(f"Task {task_id} completed in {duration:.3f}s")
            
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            result.duration = time.time() - start_time if result.start_time else 0
            
            logger.error(f"Task {task_id} failed: {e}")
        
        return result
    
    async def submit_task(self, func: Callable, args: tuple = (), kwargs: dict = None,
                         priority: TaskPriority = TaskPriority.NORMAL, 
                         task_id: str = None, metadata: dict = None) -> str:
        """Submit a task for execution"""
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        success = self.task_queue.add_task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            metadata=metadata
        )
        
        if not success:
            raise RuntimeError(f"Failed to submit task {task_id}")
        
        return task_id
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result"""
        return self.task_queue.get_task_status(task_id)
    
    async def wait_for_task(self, task_id: str, timeout: float = None) -> TaskResult:
        """Wait for task completion"""
        start_time = time.time()
        
        while True:
            result = await self.get_task_result(task_id)
            
            if result and result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return result
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            await asyncio.sleep(0.1)

class BatchProcessor:
    """High-performance batch processing system"""
    
    def __init__(self, executor: AsyncTaskExecutor):
        self.executor = executor
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_results: Dict[str, Dict[str, TaskResult]] = {}
        self.job_stats: Dict[str, Dict[str, Any]] = {}
    
    async def submit_batch_job(self, tasks: List[Dict[str, Any]], batch_size: int = 10,
                              max_workers: int = 4, job_id: str = None,
                              priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Submit a batch processing job"""
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        job = BatchJob(
            job_id=job_id,
            tasks=tasks,
            batch_size=batch_size,
            max_workers=max_workers,
            priority=priority
        )
        
        self.active_jobs[job_id] = job
        self.job_results[job_id] = {}
        self.job_stats[job_id] = {
            "total_tasks": len(tasks),
            "completed_tasks": 0,
            "failed_tasks": 0,
            "start_time": datetime.now(),
            "status": "running"
        }
        
        # Process batches
        asyncio.create_task(self._process_batch_job(job))
        
        logger.info(f"Submitted batch job {job_id} with {len(tasks)} tasks")
        return job_id
    
    async def _process_batch_job(self, job: BatchJob):
        """Process a batch job"""
        job_id = job.job_id
        
        try:
            # Submit all tasks
            task_ids = []
            for i, task_data in enumerate(job.tasks):
                task_id = f"{job_id}_task_{i}"
                
                await self.executor.submit_task(
                    func=task_data["func"],
                    args=task_data.get("args", ()),
                    kwargs=task_data.get("kwargs", {}),
                    priority=job.priority,
                    task_id=task_id,
                    metadata={"job_id": job_id, "task_index": i}
                )
                
                task_ids.append(task_id)
            
            # Wait for all tasks to complete
            for task_id in task_ids:
                result = await self.executor.wait_for_task(task_id)
                self.job_results[job_id][task_id] = result
                
                # Update job stats
                stats = self.job_stats[job_id]
                if result.status == TaskStatus.COMPLETED:
                    stats["completed_tasks"] += 1
                elif result.status == TaskStatus.FAILED:
                    stats["failed_tasks"] += 1
            
            # Mark job as completed
            self.job_stats[job_id]["status"] = "completed"
            self.job_stats[job_id]["end_time"] = datetime.now()
            
            # Execute callback if provided
            if job.callback:
                try:
                    await job.callback(job_id, self.job_results[job_id])
                except Exception as e:
                    logger.error(f"Batch job {job_id} callback failed: {e}")
            
            logger.info(f"Batch job {job_id} completed")
            
        except Exception as e:
            self.job_stats[job_id]["status"] = "failed"
            self.job_stats[job_id]["error"] = str(e)
            logger.error(f"Batch job {job_id} failed: {e}")
        finally:
            # Clean up
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch job status"""
        if job_id not in self.job_stats:
            return {"status": "not_found"}
        
        stats = self.job_stats[job_id].copy()
        
        if job_id in self.job_results:
            results = self.job_results[job_id]
            stats["task_results"] = {
                task_id: {
                    "status": result.status.value,
                    "duration": result.duration,
                    "error": result.error
                }
                for task_id, result in results.items()
            }
        
        return stats
    
    def get_all_jobs_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all jobs"""
        return {
            job_id: self.get_job_status(job_id)
            for job_id in self.job_stats.keys()
        }

# Global async processing system
async_executor = AsyncTaskExecutor(max_workers=10)
batch_processor = BatchProcessor(async_executor)

# Utility functions
async def submit_async_task(func: Callable, *args, priority: TaskPriority = TaskPriority.NORMAL, **kwargs) -> str:
    """Submit an async task"""
    return await async_executor.submit_task(func, args, kwargs, priority)

async def submit_batch_tasks(tasks: List[Dict[str, Any]], batch_size: int = 10) -> str:
    """Submit batch tasks"""
    return await batch_processor.submit_batch_job(tasks, batch_size)

async def get_task_result(task_id: str) -> Optional[TaskResult]:
    """Get task result"""
    return await async_executor.get_task_result(task_id)

async def wait_for_task(task_id: str, timeout: float = None) -> TaskResult:
    """Wait for task completion"""
    return await async_executor.wait_for_task(task_id, timeout)

# Context manager for async processing
class AsyncProcessingContext:
    """Context manager for async processing lifecycle"""
    
    async def __aenter__(self):
        await async_executor.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await async_executor.stop()

# Decorators
def async_background_task(priority: TaskPriority = TaskPriority.NORMAL):
    """Decorator to make function run as background task"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            task_id = await submit_async_task(func, *args, priority=priority, **kwargs)
            return task_id
        return wrapper
    return decorator
