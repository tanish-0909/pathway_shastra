#!/bin/bash

# ========================================
# View Logs for News Processing System
# ========================================

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1

SERVICE=${1:-all}

echo "========================================="
echo "Viewing logs for: $SERVICE"
echo "========================================="
echo ""

if [ "$SERVICE" = "all" ]; then
    docker compose logs -f --tail=100
else
    docker compose logs -f --tail=100 "$SERVICE"
fi
