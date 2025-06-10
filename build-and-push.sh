#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Your Docker Hub username
DOCKER_USER="crowbank"
# The name of the image on Docker Hub
IMAGE_NAME="crowbank-intranet"
# The tag for the image, 'latest' is a good default
TAG="latest"
# The name of the image created locally by docker compose (projectname-servicename)
LOCAL_IMAGE_NAME="crowbank-intranet-app"

# --- Script ---
echo "Building the Docker image..."
docker compose build

echo "Tagging image for Docker Hub..."
docker tag "${LOCAL_IMAGE_NAME}:${TAG}" "${DOCKER_USER}/${IMAGE_NAME}:${TAG}"

echo "Pushing image to Docker Hub..."
docker push "${DOCKER_USER}/${IMAGE_NAME}:${TAG}"

echo "✅ Successfully built and pushed ${DOCKER_USER}/${IMAGE_NAME}:${TAG}" 