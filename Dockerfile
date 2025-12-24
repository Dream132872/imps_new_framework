# Use custom base image with system dependencies pre-installed
# Build base image first: docker build -f Dockerfile.base -t imps-framework-base:latest .
# Or run: ./build-base.sh (Linux/Mac) or .\build-base.ps1 (Windows)
FROM imps-framework-base:latest

# Set environment variables
ENV PYTHONPATH=/app/src \
    DJANGO_SETTINGS_MODULE=config.settings

# Copy the entire project (will be overridden by volume mount in development)
# Note: Python dependencies are already installed in the base image
COPY . .

# Create directories for media and static files
RUN mkdir -p /app/cdn/media /app/cdn/static /app/logs

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]

