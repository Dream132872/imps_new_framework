# Gunicorn Configuration Guide

This project is configured to use Gunicorn with Uvicorn workers for production deployment. Gunicorn provides process management while Uvicorn workers handle async requests efficiently.

## Quick Start

### Development Mode (with hot reload)

```bash
# Start with hot reload enabled
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or set reload manually
GUNICORN_RELOAD=true docker-compose up
```

### Production Mode

```bash
# Start with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Default Mode (current docker-compose.yml)

```bash
# Uses Gunicorn with 4 workers, no reload
docker-compose up
```

## Configuration Options

All Gunicorn settings can be configured via environment variables in `docker-compose.yml`:

### Worker Configuration

- `GUNICORN_WORKERS` - Number of worker processes (default: 4)
  - Development: 2-4 workers
  - Production: 8-16 workers (or `(CPU_COUNT * 2) + 1`)

- `GUNICORN_WORKER_CLASS` - Worker class (default: `uvicorn.workers.UvicornWorker`)
  - `uvicorn.workers.UvicornWorker` - For async/ASGI support (recommended)
  - `sync` - For sync WSGI only

- `GUNICORN_WORKER_CONNECTIONS` - Max concurrent connections per worker (default: 1000)

### Server Configuration

- `GUNICORN_BIND` - Address and port to bind (default: `0.0.0.0:8000`)
- `GUNICORN_TIMEOUT` - Worker timeout in seconds (default: 30)
- `GUNICORN_LOG_LEVEL` - Logging level (default: `info`)
  - Options: `debug`, `info`, `warning`, `error`, `critical`

### Development Features

- `GUNICORN_RELOAD` - Enable auto-reload on code changes (default: `false`)
  - Set to `true` for development
  - Automatically disables `preload_app` when enabled

## Performance Tuning

### For High Traffic (2000+ concurrent users)

```yaml
environment:
  - GUNICORN_WORKERS=12
  - GUNICORN_WORKER_CONNECTIONS=1000
  - GUNICORN_PRELOAD_APP=true
  - GUNICORN_MAX_REQUESTS=5000
```

### For Docker Containers

```yaml
environment:
  - GUNICORN_WORKERS=4  # Adjust based on container resources
  - GUNICORN_WORKER_CONNECTIONS=500
  - GUNICORN_TIMEOUT=30
```

## Worker Types

### Uvicorn Workers (Default)
- Supports async/ASGI applications
- Better for WebSocket and async views
- Recommended for Django with Channels

### Sync Workers
- Traditional WSGI workers
- Use if you don't need async support
- Set: `GUNICORN_WORKER_CLASS=sync`

## Monitoring

### View Gunicorn Logs

```bash
# All logs
docker-compose logs -f web

# Only Gunicorn logs
docker-compose logs -f web | grep gunicorn
```

### Check Worker Status

```bash
# Enter container
docker-compose exec web bash

# Check running processes
ps aux | grep gunicorn
```

## Troubleshooting

### Workers Not Starting

- Check CPU/memory limits in Docker
- Reduce `GUNICORN_WORKERS` if container is resource-limited
- Check logs: `docker-compose logs web`

### Hot Reload Not Working

- Ensure `GUNICORN_RELOAD=true` is set
- Verify volume mounts are correct: `./src:/app/src:rw`
- Check file permissions

### High Memory Usage

- Reduce `GUNICORN_WORKERS`
- Disable `GUNICORN_PRELOAD_APP` (set to `false`)
- Reduce `GUNICORN_WORKER_CONNECTIONS`

### Connection Timeouts

- Increase `GUNICORN_TIMEOUT` (default: 30 seconds)
- Check database/Redis connection timeouts
- Verify network connectivity

## Configuration Files

- `src/gunicorn_config.py` - Main Gunicorn configuration
- `src/start_gunicorn.py` - Startup script
- `docker-compose.yml` - Base configuration
- `docker-compose.dev.yml` - Development overrides
- `docker-compose.prod.yml` - Production overrides

## Example Configurations

### Minimal Development Setup

```yaml
environment:
  - GUNICORN_WORKERS=1
  - GUNICORN_RELOAD=true
  - GUNICORN_LOG_LEVEL=debug
```

### Production Setup

```yaml
environment:
  - GUNICORN_WORKERS=8
  - GUNICORN_RELOAD=false
  - GUNICORN_LOG_LEVEL=warning
  - GUNICORN_PRELOAD_APP=true
  - GUNICORN_MAX_REQUESTS=5000
```

### High-Performance Setup

```yaml
environment:
  - GUNICORN_WORKERS=16
  - GUNICORN_WORKER_CONNECTIONS=1000
  - GUNICORN_PRELOAD_APP=true
  - GUNICORN_MAX_REQUESTS=10000
  - GUNICORN_TIMEOUT=60
```

