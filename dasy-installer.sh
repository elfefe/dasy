#!/usr/bin/env bash
# install_dasy.sh
# Self-contained installer for Dasy MVP (Docker Compose)
# Downloads the repository, runs Docker Compose, then deletes the repo

set -e

# Variables
REPO_URL="https://github.com/elfefe/dasy"
TMP_DIR=$(mktemp -d)
DOCKER_COMPOSE_FILE="docker-compose.yaml"

echo "Temporary install directory: $TMP_DIR"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker before proceeding."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Clone repository
echo "Cloning Dasy repository..."
git clone --depth=1 "$REPO_URL" "$TMP_DIR/dasy-repo"

cd "$TMP_DIR/dasy-repo"

# Check for .env
if [ ! -f ".env" ]; then
    echo ".env file not found. Please create it with your API keys:"
    echo "DOCKPLOY_API_KEY=..."
    echo "CLOUDFLARE_TUNNEL_TOKEN=..."
    echo "OPENAI_API_KEY=..."
    echo "GEMINI_API_KEY=..."
    exit 1
fi
export $(grep -v '^#' .env | xargs)

# Optional: create Docker volumes (Compose will auto-create if missing)
docker volume create daisy_pgdata || true

# Build custom images (or pull if already built)
echo "Building Dasy images..."
docker-compose build

# Start all services
echo "Starting Dasy services..."
docker-compose up -d

# Wait a few seconds and show container status
echo "Waiting for services to initialize..."
sleep 5
docker-compose ps

# Go back and delete temp directory
cd ~
echo "Cleaning up temporary files..."
rm -rf "$TMP_DIR"

echo "Dasy MVP is up and running!"
echo "Orchestrator should be available on port 8000 (via Cloudflare tunnel if configured)."
echo "Use 'docker-compose logs -f' to follow logs."
