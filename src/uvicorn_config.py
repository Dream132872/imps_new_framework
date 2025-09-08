"""
Production configuration for Uvicorn server.
"""

import math
import multiprocessing
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Django settings
DJANGO_SETTINGS_MODULE = "config.settings"

# Uvicorn configuration
UVICORN_CONFIG = {
    "app": "config.asgi:application",
    "host": os.getenv("UVICORN_HOST", "0.0.0.0"),
    "port": int(os.getenv("UVICORN_PORT", "8000")),
    # "workers": math.ceil(multiprocessing.cpu_count() / 2) + 1,
    "workers": int(os.getenv("UVICORN_WORKERS", "8")),
    "log_level": os.getenv("UVICORN_LOG_LEVEL", "warning"),
    "access_log": True,
    "reload": os.getenv("UVICORN_RELOAD", "false").lower() == "true",
    "reload_dirs": (
        [str(BASE_DIR)]
        if os.getenv("UVICORN_RELOAD", "false").lower() == "true"
        else None
    ),
    "reload_excludes": ["*.pyc", "*.pyo", "*.pyd", "__pycache__", "*.so"],
    "reload_includes": ["*.py"],
    "limit_concurrency": int(os.getenv("UVICORN_LIMIT_CONCURRENCY", "10000")),
    "limit_max_requests": int(os.getenv("UVICORN_LIMIT_MAX_REQUESTS", "10000")),
    "timeout_keep_alive": int(os.getenv("UVICORN_TIMEOUT_KEEP_ALIVE", "5")),
    "timeout_graceful_shutdown": int(
        os.getenv("UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", "50")
    ),
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
