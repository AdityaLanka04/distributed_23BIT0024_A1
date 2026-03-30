#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$ROOT_DIR/ssl/docker-compose.yml"

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required but not installed."
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
else
    echo "Docker Compose is required but not installed."
    exit 1
fi

echo "Stopping Distributed Quiz Management System..."
"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" down

echo ""
echo "Application stopped."
