FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git curl python3 make g++

# Copy package files
COPY package*.json ./
COPY yarn.lock* ./

# Install dependencies
RUN npm install --production

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/workspace /app/config

# Set permissions
RUN chmod +x /app/scripts/*.sh || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start command
CMD ["npm", "start"]