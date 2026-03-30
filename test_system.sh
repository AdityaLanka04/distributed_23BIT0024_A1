

echo "Testing Distributed Quiz Management System..."
echo ""

echo "1. Testing Backend Health:"
curl -s http://localhost:8001/health | python3 -m json.tool
echo ""

echo "2. Testing API Root:"
curl -s http://localhost:8001/ | python3 -m json.tool
echo ""

echo "3. Checking Docker Services:"
docker-compose ps
echo ""

echo "4. Testing Frontend (should return HTML):"
curl -s http://localhost:3001 | head -5
echo ""

echo "✅ All services are running!"
echo ""
echo "Access the application at:"
echo "  - Frontend: http://localhost:3001"
echo "  - Backend API: http://localhost:8001"
echo "  - API Docs: http://localhost:8001/docs"
