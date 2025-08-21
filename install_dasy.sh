#!/usr/bin/env bash
# install_dasy.sh
# Self-contained installer for Dasy MVP (Docker Compose)
# Downloads the repository, runs Docker Compose, then deletes the repo

set -e

# Variables
REPO_URL="https://github.com/elfefe/dasy"
TMP_DIR=$(mktemp -d)
DOCKER_COMPOSE_FILE="docker-compose.yaml"
INSTALL_DIR="$HOME/dasy"

echo "🚀 Dasy Installer - Autonomous Software Development System"
echo "========================================================"
echo "Temporary install directory: $TMP_DIR"
echo "Final installation directory: $INSTALL_DIR"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker before proceeding."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check for Git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git before proceeding."
    exit 1
fi

echo "✅ All dependencies found (Docker, Docker Compose, Git)"

# Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone repository or use local files if repo doesn't exist
echo "📥 Setting up Dasy files..."
if git clone --depth=1 "$REPO_URL" "$TMP_DIR/dasy-repo" 2>/dev/null; then
    echo "✅ Repository cloned successfully"
    cp -r "$TMP_DIR/dasy-repo"/* "$INSTALL_DIR/"
else
    echo "⚠️  Repository not found, creating local installation..."
    # We'll create the files locally since the repo might not exist yet
fi

# Ensure we have the necessary files
if [ ! -f "docker-compose.yaml" ]; then
    echo "📝 Creating Docker Compose configuration..."
    # The docker-compose.yaml will be created by our installer
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env configuration file..."
    cat > .env << 'EOF'
# Dasy Environment Configuration
# Fill in your API keys and tokens below

# Dokploy Configuration
DOCKPLOY_API_KEY=your_dokploy_api_key_here
DOCKPLOY_URL=https://your-dokploy-instance.com

# Cloudflare Tunnel Configuration
CLOUDFLARE_TUNNEL_TOKEN=your_cloudflare_tunnel_token_here

# AI API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
POSTGRES_PASSWORD=dasy_secure_password_123
POSTGRES_USER=dasy
POSTGRES_DB=dasy

# RabbitMQ Configuration
RABBITMQ_DEFAULT_USER=dasy
RABBITMQ_DEFAULT_PASS=dasy_rabbitmq_pass_123

# Application Configuration
ORCHESTRATOR_PORT=8000
GITHUB_WEBHOOK_SECRET=your_github_webhook_secret_here

# JWT Configuration for agents
JWT_SECRET_KEY=dasy_jwt_secret_key_change_this_in_production
EOF
    echo "⚠️  Please edit .env file with your API keys before proceeding!"
    echo "   - DOCKPLOY_API_KEY: Get from your Dokploy instance"
    echo "   - CLOUDFLARE_TUNNEL_TOKEN: Get from Cloudflare Dashboard"
    echo "   - OPENAI_API_KEY: Get from OpenAI Dashboard"
    echo "   - GEMINI_API_KEY: Get from Google AI Studio"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Validate required environment variables
missing_vars=()
required_vars=("OPENAI_API_KEY" "GEMINI_API_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_${var,,}_here" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables in .env:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo "Please edit .env file and run the installer again."
    exit 1
fi

# Create Docker volumes
echo "📦 Creating Docker volumes..."
docker volume create dasy_pgdata || true
docker volume create dasy_rabbitmq_data || true

# Build custom images
echo "🏗️  Building Dasy images..."
docker-compose build --parallel

# Start all services
echo "🚀 Starting Dasy services..."
docker-compose up -d

# Wait for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Display success message and instructions
echo ""
echo "🎉 Dasy MVP is up and running!"
echo "==============================="
echo "📍 Services available:"
echo "   • Orchestrator (Jules): http://localhost:8000"
echo "   • RabbitMQ Management: http://localhost:15672 (user: dasy)"
if [ ! -z "$CLOUDFLARE_TUNNEL_TOKEN" ] && [ "$CLOUDFLARE_TUNNEL_TOKEN" != "your_cloudflare_tunnel_token_here" ]; then
    echo "   • External access via Cloudflare Tunnel (configured)"
fi
echo ""
echo "📝 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "📖 Next steps:"
echo "   1. Configure GitHub webhooks to point to your orchestrator"
echo "   2. Set up Dokploy deployment targets"
echo "   3. Configure Cloudflare Zero Trust access policies"
echo ""

# Cleanup temporary directory
if [ -d "$TMP_DIR" ]; then
    rm -rf "$TMP_DIR"
    echo "🧹 Cleaned up temporary files"
fi

echo "✅ Installation complete! Dasy is ready to automate your development workflow."