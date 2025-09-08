#!/usr/bin/env python
"""
Production startup script for Uvicorn with static and media file serving.
"""

import os
import sys
import signal
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root) + "src")

# Import configuration
from uvicorn_config import UVICORN_CONFIG, DJANGO_SETTINGS_MODULE

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

# Global variable to track server instance
server = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}. Shutting down gracefully...")
    if server:
        server.should_exit = True
    sys.exit(0)


def main():
    """Start the production server."""
    global server

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Starting Uvicorn production server...")
    print(f"Host: {UVICORN_CONFIG['host']}")
    print(f"Port: {UVICORN_CONFIG['port']}")
    print(f"Workers: {UVICORN_CONFIG['workers']}")
    print(f"Log Level: {UVICORN_CONFIG['log_level']}")
    print(
        f"Static files: http://{UVICORN_CONFIG['host']}:{UVICORN_CONFIG['port']}/static/"
    )
    print(
        f"Media files: http://{UVICORN_CONFIG['host']}:{UVICORN_CONFIG['port']}/media/"
    )
    print("Press Ctrl+C to stop the server")
    print("Note: With multiple workers, shutdown may take a few seconds...")

    # Remove None values from config
    config = {k: v for k, v in UVICORN_CONFIG.items() if v is not None}

    # Reduce graceful shutdown timeout for faster stopping
    config["timeout_graceful_shutdown"] = 10

    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\nShutdown requested by user...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        print("Server stopped.")


if __name__ == "__main__":
    main()
