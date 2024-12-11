#!/bin/bash

# Copy .env.default to .env if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.default .env
fi

# Execute the command passed to docker run
exec "$@"
