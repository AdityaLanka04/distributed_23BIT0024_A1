#!/bin/bash

echo "📊 Nginx Status Monitor"
echo "======================="
echo ""

if [ "$1" == "logs" ]; then
    echo "📜 Nginx Access Logs (last 50 lines):"
    docker-compose logs nginx --tail=50
    
elif [ "$1" == "errors" ]; then
    echo "❌ Nginx Error Logs (last 50 lines):"
    docker-compose exec nginx cat /var/log/nginx/error.log | tail -50
    
elif [ "$1" == "status" ]; then
    echo "🔍 Nginx Status:"
    docker-compose exec nginx nginx -t
    echo ""
    echo "📊 Active Connections:"
    docker-compose exec nginx ps aux | grep nginx
    
elif [ "$1" == "reload" ]; then
    echo "🔄 Reloading Nginx configuration..."
    docker-compose exec nginx nginx -s reload
    echo "✅ Configuration reloaded!"
    
elif [ "$1" == "test" ]; then
    echo "🧪 Testing Nginx configuration..."
    docker-compose exec nginx nginx -t
    
else
    echo "Usage: ./nginx-monitor.sh [command]"
    echo ""
    echo "Commands:"
    echo "  logs    - View access logs"
    echo "  errors  - View error logs"
    echo "  status  - Check Nginx status"
    echo "  reload  - Reload configuration"
    echo "  test    - Test configuration"
fi
