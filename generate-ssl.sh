#!/bin/bash

set -e

echo "🔐 Generating SSL certificates..."

mkdir -p ssl

if [ "$1" == "letsencrypt" ]; then
    echo "📜 Using Let's Encrypt..."
    
    if ! command -v certbot &> /dev/null; then
        echo "❌ certbot not found. Install with: sudo apt-get install certbot"
        exit 1
    fi
    
    read -p "Enter your domain name: " DOMAIN
    read -p "Enter your email: " EMAIL
    
    sudo certbot certonly --standalone \
        -d $DOMAIN \
        --non-interactive \
        --agree-tos \
        --email $EMAIL
    
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
    sudo chown $USER:$USER ssl/*.pem
    
    echo "✅ Let's Encrypt certificates generated!"
    echo "📝 Update nginx-ssl.conf with your domain: $DOMAIN"
    
else
    echo "🔧 Generating self-signed certificate (for development only)..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    echo "✅ Self-signed certificate generated!"
    echo "⚠️  This is for development only. Use Let's Encrypt for production."
fi

echo ""
echo "📁 Certificates saved to: ./ssl/"
echo "🔑 cert.pem - Certificate"
echo "🔑 key.pem - Private key"
