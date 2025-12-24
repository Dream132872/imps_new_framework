# PowerShell script to build the base Docker image with system dependencies
# Run this once or when system dependencies change

Write-Host "Building base Docker image with system dependencies (no cache)..." -ForegroundColor Cyan
docker build --no-cache -f Dockerfile.base -t imps-framework-base:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Base image built successfully!" -ForegroundColor Green
    Write-Host "You can now run: docker-compose up --build" -ForegroundColor Yellow
} else {
    Write-Host "✗ Failed to build base image" -ForegroundColor Red
    exit 1
}

