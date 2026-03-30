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

echo "Starting Distributed Quiz Management System locally..."
echo "Using compose file: $COMPOSE_FILE"

"${COMPOSE_CMD[@]}" -f "$COMPOSE_FILE" up --build -d

echo ""
echo "Application is starting."
echo "Local URL: http://localhost:8080"
echo ""
echo "Useful commands:"
echo "  View logs: ${COMPOSE_CMD[*]} -f $COMPOSE_FILE logs -f"
echo "  Stop app : ${COMPOSE_CMD[*]} -f $COMPOSE_FILE down"
