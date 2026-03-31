#!/bin/bash

echo "🌐 Starting localtunnel..."
echo ""

if ! command -v lt &> /dev/null; then
    echo "📥 Installing localtunnel..."
    npm install -g localtunnel
fi

echo "🚀 Creating public tunnel..."
echo ""

lt --port 80 --subdomain quiz-$(date +%s)
