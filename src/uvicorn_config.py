"""
Production configuration for Uvicorn server.
"""

import math
import multiprocessing
import os
from pathlib import Path

from decouple import Csv, config

# Base directory
BASE_DIR = Path(__file__).parent

# Django settings
DJANGO_SETTINGS_MODULE = "config.settings"

# Uvicorn configuration optimized for 2000+ concurrent users
UVICORN_CONFIG = {
    "app": "config.asgi:application",
    "host": config("UVICORN_HOST", default="0.0.0.0"),
    "port": config("UVICORN_PORT", default=8000, cast=int),
    # Optimized worker count: (2 * CPU cores) + 1 for I/O bound workloads
    # For 2000 concurrent users, recommend 12-16 workers on 4-8 core systems
    "workers": config("UVICORN_WORKERS", default=12, cast=int),
    "log_level": config("UVICORN_LOG_LEVEL", default="warning"),
    "access_log": config("UVICORN_ACCESS_LOG", default="1", cast=bool),
    "reload": config("UVICORN_RELOAD", default="0", cast=bool),
    "reload_dirs": (
        [str(BASE_DIR)]
        if config("UVICORN_RELOAD", default="false").lower() == "true"
        else None
    ),
    "reload_excludes": ["*.pyc", "*.pyo", "*.pyd", "__pycache__", "*.so"],
    "reload_includes": ["*.py", "*.env"],
    # Optimized concurrency: ~200-300 per worker for 2000 total users
    "limit_concurrency": config("UVICORN_LIMIT_CONCURRENCY", default=300, cast=int),
    # Restart workers after processing many requests to prevent memory leaks
    "limit_max_requests": config("UVICORN_LIMIT_MAX_REQUESTS", default=5000, cast=int),
    # Increased keep-alive for better connection reuse
    "timeout_keep_alive": config("UVICORN_TIMEOUT_KEEP_ALIVE", default=15, cast=int),
    # Graceful shutdown timeout for high-load scenarios
    "timeout_graceful_shutdown": config(
        "UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", default=30, cast=int
    ),
    # Additional performance optimizations
    "backlog": config("UVICORN_BACKLOG", default=2048, cast=int),  # Connection backlog
}

# Static and Media file configuration
STATIC_CONFIG = {
    "static_url": "/static/",
    "static_root": str(BASE_DIR / "staticfiles"),
    "media_url": "/media/",
    "media_root": str(BASE_DIR / "media"),
}

# Cache configuration
CACHE_CONFIG = {
    "static_max_age": int(
        os.getenv("STATIC_CACHE_MAX_AGE", "31536000")
    ),  # 1 year in seconds
    "media_max_age": int(os.getenv("MEDIA_CACHE_MAX_AGE", "86400")),  # 1 day in seconds
    "static_immutable": os.getenv("STATIC_CACHE_IMMUTABLE", "true").lower() == "true",
    "enable_etag": os.getenv("ENABLE_ETAG", "true").lower() == "true",
}

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

# CORS configuration
CORS_CONFIG = {
    "allowed_origins": os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(","),
    "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allowed_headers": ["*"],
    "allow_credentials": True,
}
