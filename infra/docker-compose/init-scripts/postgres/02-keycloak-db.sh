#!/bin/bash
# Enable extensions in Keycloak database

set -e

echo "Enabling UUID extension in keycloak database..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "keycloak" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

echo "✅ Keycloak database extensions enabled!"
