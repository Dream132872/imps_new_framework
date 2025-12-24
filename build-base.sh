#!/bin/bash
# Script to build the base Docker image with system dependencies
# Run this once or when system dependencies change

echo "Building base Docker image with system dependencies (no cache)..."
docker build --no-cache -f Dockerfile.base -t imps-framework-base:latest .

if [ $? -eq 0 ]; then
    echo "✓ Base image built successfully!"
    echo "You can now run: docker-compose up --build"
else
    echo "✗ Failed to build base image"
    exit 1
fi

