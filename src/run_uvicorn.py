#!/usr/bin/env python
"""
Script to run Uvicorn with proper configuration for serving static and media files.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if __name__ == "__main__":
    # Configuration for Uvicorn
    config = {
        "app": "config.asgi:application",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Enable auto-reload for development
        "workers": 1,  # Use 1 worker for development
        "log_level": "info",
        "access_log": True,
    }

    print("Starting Uvicorn server...")
    print(f"Server will be available at: http://{config['host']}:{config['port']}")
    print(
        f"Static files will be served at: http://{config['host']}:{config['port']}/static/"
    )
    print(
        f"Media files will be served at: http://{config['host']}:{config['port']}/media/"
    )
    print("Press Ctrl+C to stop the server")

    uvicorn.run(**config)
