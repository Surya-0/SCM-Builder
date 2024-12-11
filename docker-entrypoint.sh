#!/bin/sh
set -e

cd /app

# Copy .env.default to .env if .env doesn't exist
if [ ! -f .env ] && [ -f .env.default ]; then
    cp .env.default .env
fi

# Execute the command passed to docker run
exec "$@"
