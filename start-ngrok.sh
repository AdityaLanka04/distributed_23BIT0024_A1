#!/bin/bash

echo "🌐 Starting ngrok tunnel..."
echo ""

if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found!"
    echo ""
    echo "📥 Install ngrok:"
    echo "  brew install ngrok  (macOS)"
    echo "  Or download from: https://ngrok.com/download"
    echo ""
    exit 1
fi

echo "🚀 Creating public tunnel to localhost:80..."
echo ""
echo "Your public URL will appear below:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

ngrok http 80
