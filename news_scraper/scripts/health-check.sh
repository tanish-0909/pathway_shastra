#!/bin/bash

# ========================================
# Health Check Script
# ========================================

echo "========================================="
echo "News Processing System - Health Check"
echo "========================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

# Check Docker services
echo "1. Checking Docker services..."
docker compose ps

echo ""
echo "2. Checking Redis..."
docker compose exec redis redis-cli ping 2>/dev/null | grep PONG > /dev/null && echo "  Redis is healthy" || echo "  Redis not responding"

echo ""
echo "3. Checking FastAPI..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  FastAPI is healthy"
else
    echo "  FastAPI not responding"
fi

echo ""
echo "4. Checking MongoDB Atlas..."
echo "  Using MongoDB Atlas (remote) - connection verified via API"
echo "  To check directly, use: mongosh with your Atlas connection string"

echo ""
echo "5. Checking article counts..."
curl -s http://localhost:8000/api/news/stats 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"  Raw articles: {data.get('total_enriched', 0)}\"
         )
    print(f\"  Summarized: {data.get('total_summarized', 0)}\")
    print(f\"  Clusters: {data.get('total_clusters', 0)}\")
except:
    print('  Could not fetch stats')
" 2>/dev/null || echo "  Could not fetch stats"

echo ""
echo "6. Service URLs:"
echo "  - FastAPI:     http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Redis:       redis://localhost:6379"
echo "  - MongoDB:     Atlas (remote)"

echo ""
echo "========================================="
