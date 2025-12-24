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
- ✅ Use the cached base image (no system package installation, no Python package installation)
- ✅ Only copy source code
- ✅ Much faster builds since everything is pre-installed!

This makes builds **much faster**!

## How It Works

1. **`Dockerfile.base`** - Contains system dependencies, tools, and Python packages:
   - System packages: postgresql-client, gcc, libpq-dev
   - **uv package manager** - Fast Python package installer (much faster than pip)
   - **Python dependencies** - All packages from requirements.txt are pre-installed
   - Built once and cached
   - Tagged as `imps-framework-base:latest`

2. **`Dockerfile`** - Uses the base image
   - Only copies your source code
   - Everything else is already installed in the base image
   - Much faster builds!

## When to Rebuild Base Image

Rebuild the base image when:
- System dependencies change (adding/removing apt packages)
- **Python dependencies change** (requirements.txt is updated)
- Python version changes
- Base image needs updates

**To rebuild:**
```bash
# Windows PowerShell
.\build-base.ps1

# Linux/Mac
./build-base.sh

# Or manually
docker build --no-cache -f Dockerfile.base -t imps-framework-base:latest .
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

## Python Dependencies in Base Image

Python dependencies from `requirements.txt` are **already included** in the base image! This means:

- ✅ **Faster builds** - Python packages are pre-installed and cached
- ✅ **No pip install on every build** - Only source code is copied
- ⚠️ **Rebuild base image** when `requirements.txt` changes

### When requirements.txt Changes

If you add/remove/update packages in `requirements.txt`:

1. Rebuild the base image:
   ```bash
   .\build-base.ps1  # Windows
   # or
   ./build-base.sh   # Linux/Mac
   ```

2. Then rebuild your app:
   ```bash
   docker-compose build
   ```

