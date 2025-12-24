"""
Production configuration for Gunicorn with Uvicorn workers.
Optimized for handling 2000+ concurrent users.
"""

import multiprocessing
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Django settings
DJANGO_SETTINGS_MODULE = "config.settings"

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = int(os.getenv("GUNICORN_BACKLOG", "2048"))

# Worker processes
# For Docker: Use 2-4 workers (can be overridden via env var)
# For production hosts: 12-16 workers recommended for 2000+ concurrent users
workers = int(os.getenv("GUNICORN_WORKERS", str((multiprocessing.cpu_count() * 2) + 1)))
# Worker class: uvicorn.workers.UvicornWorker for async, sync for sync workers
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", "1000"))

# Worker lifecycle
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "5000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))
# Disable preload_app if reload is enabled (for development)
reload_enabled = os.getenv("GUNICORN_RELOAD", "false").lower() == "true"
preload_app = not reload_enabled and os.getenv("GUNICORN_PRELOAD_APP", "true").lower() == "true"
reload = reload_enabled

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "15"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Logging
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "warning")
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # Log to stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")    # Log to stderr
access_log_format = os.getenv(
    "GUNICORN_ACCESS_LOG_FORMAT",
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
)

# Process naming
proc_name = os.getenv("GUNICORN_PROC_NAME", "imps_framework")

# Security
limit_request_line = int(os.getenv("GUNICORN_LIMIT_REQUEST_LINE", "4094"))
limit_request_fields = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELDS", "100"))
limit_request_field_size = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", "8190"))

# Performance tuning
# Use /tmp in Docker, /dev/shm on Linux hosts (shared memory)
worker_tmp_dir = os.getenv("GUNICORN_WORKER_TMP_DIR", "/tmp")

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE={DJANGO_SETTINGS_MODULE}",
]

# Server mechanics
daemon = os.getenv("GUNICORN_DAEMON", "false").lower() == "true"
pidfile = os.getenv("GUNICORN_PIDFILE", "/tmp/gunicorn.pid")
user = os.getenv("GUNICORN_USER", None)
group = os.getenv("GUNICORN_GROUP", None)
tmp_upload_dir = os.getenv("GUNICORN_TMP_UPLOAD_DIR", None)

# SSL (if needed)
keyfile = os.getenv("GUNICORN_KEYFILE", None)
certfile = os.getenv("GUNICORN_CERTFILE", None)

# Worker process configuration
def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

