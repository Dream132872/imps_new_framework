#!/usr/bin/env python
"""
Production startup script for Gunicorn with Uvicorn workers.
Optimized for handling 2000+ concurrent users.
"""

import os
import signal
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if __name__ == "__main__":
    # Import Gunicorn configuration
    from gunicorn_config import *

    # Import Gunicorn application
    from gunicorn.app.wsgiapp import WSGIApplication

    class StandaloneApplication(WSGIApplication):
        def init(self, parser, opts, args):
            """Initialize the application with our configuration."""
            self.cfg = self.make_config()
            self.cfg.set("default_proc_name", proc_name)
            self.cfg.set("bind", bind)
            self.cfg.set("backlog", backlog)
            self.cfg.set("workers", workers)
            self.cfg.set("worker_class", worker_class)
            self.cfg.set("worker_connections", worker_connections)
            self.cfg.set("max_requests", max_requests)
            self.cfg.set("max_requests_jitter", max_requests_jitter)
            self.cfg.set("preload_app", preload_app)
            self.cfg.set("timeout", timeout)
            self.cfg.set("keepalive", keepalive)
            self.cfg.set("graceful_timeout", graceful_timeout)
            self.cfg.set("loglevel", loglevel)
            self.cfg.set("accesslog", accesslog)
            self.cfg.set("errorlog", errorlog)
            self.cfg.set("access_log_format", access_log_format)
            self.cfg.set("limit_request_line", limit_request_line)
            self.cfg.set("limit_request_fields", limit_request_fields)
            self.cfg.set("limit_request_field_size", limit_request_field_size)
            self.cfg.set("worker_tmp_dir", worker_tmp_dir)
            self.cfg.set("raw_env", raw_env)

            if daemon:
                self.cfg.set("daemon", daemon)
            if pidfile:
                self.cfg.set("pidfile", pidfile)
            if user:
                self.cfg.set("user", user)
            if group:
                self.cfg.set("group", group)
            if tmp_upload_dir:
                self.cfg.set("tmp_upload_dir", tmp_upload_dir)
            if keyfile:
                self.cfg.set("keyfile", keyfile)
            if certfile:
                self.cfg.set("certfile", certfile)

        def load_config(self):
            """Load configuration from our config file."""
            pass

    # Create and run the application
    app = StandaloneApplication()

    print("Starting Gunicorn with Uvicorn workers...")
    print(f"Workers: {workers}")
    print(f"Worker connections: {worker_connections}")
    print(f"Total concurrent capacity: {workers * worker_connections}")
    print(f"Bind: {bind}")
    print(f"Log level: {loglevel}")
    print("Press Ctrl+C to stop the server")

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutdown requested by user...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        print("Server stopped.")

