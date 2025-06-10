#!/bin/sh
set -e
CONN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
exec node dist/index.js "$CONN" 