"""
Async utilities for managing thread pools.
"""

import concurrent.futures
from typing import Any, Callable, Coroutine

from django.conf import settings

# Custom thread pool executor
_custom_executor = None


def get_custom_executor():
    """Get custom thread pool executor."""
    global _custom_executor
    if _custom_executor is None:
        max_workers = getattr(settings, "ASYNC_THREADS", 20)
        _custom_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="custom_sync_to_async"
        )
    return _custom_executor


def sync_to_async_custom(func: Callable) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Custom sync_to_async with custom executor."""
    from asgiref.sync import sync_to_async

    return sync_to_async(func, thread_sensitive=True, executor=get_custom_executor())
