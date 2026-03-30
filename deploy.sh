#!/bin/bash

set -e

echo "🚀 Starting deployment..."

if [ "$1" == "prod" ]; then
    echo "📦 Building production images..."
    docker-compose -f docker-compose.prod.yml build
    
    echo "🔄 Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down
    
    echo "🚀 Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    echo "🔍 Checking service status..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo "✅ Production deployment complete!"
    echo "🌐 Application available at: http://localhost"
    
else
    echo "📦 Building development images..."
    docker-compose build
    
    echo "🔄 Stopping existing containers..."
    docker-compose down
    
    echo "🚀 Starting development services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    echo "🔍 Checking service status..."
    docker-compose ps
    
    echo "✅ Development deployment complete!"
    echo "🌐 Application available at: http://localhost"
fi

echo ""
echo "📊 View logs with:"
if [ "$1" == "prod" ]; then
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
else
    echo "  docker-compose logs -f"
fi

echo ""
echo "🛑 Stop services with:"
if [ "$1" == "prod" ]; then
    echo "  docker-compose -f docker-compose.prod.yml down"
else
    echo "  docker-compose down"
fi
