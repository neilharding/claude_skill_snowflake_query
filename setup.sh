#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SKILL_DIR/.venv"
ENV_FILE="$SKILL_DIR/.env"

echo "=== Snowflake Query Skill Setup ==="

# Create venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q \
    "snowflake-connector-python[secure-local-storage]>=3.0.0" \
    "pandas>=2.0.0" \
    "python-dotenv>=1.0.0"

# Configure .env if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "Configuring Snowflake connection..."
    read -rp "Snowflake account (e.g. acme.us-east-1): " sf_account
    read -rp "Snowflake user (your email/username): " sf_user
    read -rp "Snowflake warehouse: " sf_warehouse
    read -rp "Snowflake database: " sf_database
    read -rp "Snowflake schema (optional, press enter to skip): " sf_schema

    cat > "$ENV_FILE" <<ENVEOF
SNOWFLAKE_ACCOUNT=$sf_account
SNOWFLAKE_USER=$sf_user
SNOWFLAKE_WAREHOUSE=$sf_warehouse
SNOWFLAKE_DATABASE=$sf_database
SNOWFLAKE_SCHEMA=$sf_schema
ENVEOF
    echo "Saved to $ENV_FILE"
else
    echo ".env already exists, skipping configuration."
fi

echo ""
echo "Setup complete! Test with:"
echo "  $VENV_DIR/bin/python $SKILL_DIR/scripts/run_query.py \"SELECT CURRENT_TIMESTAMP()\""
