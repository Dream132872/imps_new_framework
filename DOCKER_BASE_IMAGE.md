# Docker Base Image Setup

This project uses a custom base Docker image to speed up builds by pre-installing system dependencies that rarely change.

## Quick Start

### First Time Setup

1. **Build the base image** (only needed once or when system dependencies change):

   **Linux/Mac:**
   ```bash
   ./build-base.sh
   ```

   **Windows (PowerShell):**
   ```powershell
   .\build-base.ps1
   ```

   **Or manually:**
   ```bash
   docker build -f Dockerfile.base -t imps-framework-base:latest .
   ```

2. **Build and run your application:**
   ```bash
   docker-compose up --build
   ```

### Subsequent Builds

After the base image is built, running `docker-compose up --build` will:
- ✅ Use the cached base image (no system package installation)
- ✅ Only copy source code
- ✅ Only run `uv pip install` (much faster than pip, cached if requirements.txt hasn't changed)

This makes builds **much faster**!

## How It Works

1. **`Dockerfile.base`** - Contains system dependencies and tools:
   - System packages: postgresql-client, gcc, libpq-dev
   - **uv package manager** - Fast Python package installer (much faster than pip)
   - Built once and cached
   - Tagged as `imps-framework-base:latest`

2. **`Dockerfile`** - Uses the base image
   - Uses `uv` to install Python packages (faster than pip)
   - Copies your source code
   - Much faster builds

## When to Rebuild Base Image

Rebuild the base image only when:
- System dependencies change (adding/removing apt packages)
- Python version changes
- Base image needs updates

**To rebuild:**
```bash
docker build -f Dockerfile.base -t imps-framework-base:latest .
```

## Benefits

- ⚡ **Faster builds** - System packages are pre-installed
- 🚀 **uv package manager** - Installs Python packages 10-100x faster than pip
- 💾 **Better caching** - Base image is reused across builds
- 🔄 **Quick iterations** - Only code and package installs run on each build

## Troubleshooting

### Base image not found

If you see an error about `imps-framework-base:latest` not found:
```bash
# Build the base image first
docker build -f Dockerfile.base -t imps-framework-base:latest .
```

### Base image outdated

If system dependencies changed but base image wasn't rebuilt:
```bash
# Rebuild base image
docker build -f Dockerfile.base -t imps-framework-base:latest .

# Then rebuild your app
docker-compose build --no-cache
```

### Check if base image exists

```bash
docker images | grep imps-framework-base
```

## Using uv Package Manager

The base image includes **uv**, a fast Python package manager written in Rust. It's 10-100x faster than pip!

### Current Usage

The `Dockerfile` uses `uv pip install` which is compatible with pip but much faster:
```dockerfile
RUN uv pip install --system --no-cache -r requirements.txt
```

### Advanced: Using uv sync (even faster)

If you want even better performance, you can use `uv sync` with a `pyproject.toml`:

1. Create `pyproject.toml` with your dependencies
2. Use `uv sync` instead of `uv pip install`
3. This creates a lock file for reproducible builds

### Benefits of uv

- ⚡ **10-100x faster** than pip
- 🔒 **Better dependency resolution**
- 📦 **Smaller Docker images** (better caching)
- 🔄 **Compatible with pip** (can use requirements.txt)

## Advanced: Including Python Dependencies in Base Image

If your Python dependencies (`requirements.txt`) rarely change, you can also cache them in the base image:

1. Copy `requirements.txt` to `Dockerfile.base`
2. Run `uv pip install` in `Dockerfile.base`
3. This will cache Python packages too

However, this means you need to rebuild the base image whenever `requirements.txt` changes.

