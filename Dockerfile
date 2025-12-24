# Use custom base image with system dependencies pre-installed
# Build base image first: docker build -f Dockerfile.base -t imps-framework-base:latest .
# Or run: ./build-base.sh (Linux/Mac) or .\build-base.ps1 (Windows)
FROM imps-framework-base:latest

# Set environment variables
ENV PYTHONPATH=/app/src \
    DJANGO_SETTINGS_MODULE=config.settings

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies using uv (much faster than pip)
# uv sync is faster and uses better caching than pip
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the entire project (will be overridden by volume mount in development)
COPY . .

# Create directories for media and static files
RUN mkdir -p /app/cdn/media /app/cdn/static /app/logs

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]

