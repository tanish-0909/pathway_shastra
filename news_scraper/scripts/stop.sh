#!/bin/bash

# ========================================
# Stop Script for News Processing System
# ========================================

set -e

echo "========================================="
echo "News Processing System - Stopping"
echo "========================================="

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

echo ""
echo "Stopping all services..."
docker compose down

echo ""
echo "========================================="
echo "All Services Stopped!"
echo "========================================="
echo ""
echo "To start services again:"
echo "  ./scripts/start.sh"
echo ""
echo "To remove all data (volumes):"
echo "  docker compose down -v"
echo ""
