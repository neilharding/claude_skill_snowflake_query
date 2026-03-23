#!/usr/bin/env python3
"""Standalone Snowflake query runner with externalbrowser SSO auth."""

import argparse
import contextlib
import json
import os
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    pass

import snowflake.connector
import pandas as pd


# ---------------------------------------------------------------------------
# Connection cache (within this process)
# ---------------------------------------------------------------------------
_conn_cache: dict[tuple, snowflake.connector.SnowflakeConnection] = {}


def _cache_key(account, user, warehouse, database, schema, authenticator):
    return (account, user, warehouse, database, schema or "", authenticator)


def get_connection(account, user, warehouse, database, schema=None, authenticator="externalbrowser"):
    key = _cache_key(account, user, warehouse, database, schema, authenticator)
    if key in _conn_cache:
        conn = _conn_cache[key]
        try:
            conn.cursor().execute("SELECT 1")
            return conn
        except Exception:
            del _conn_cache[key]

    params = dict(
        account=account,
        user=user,
        warehouse=warehouse,
        database=database,
        authenticator=authenticator,
    )
    if schema:
        params["schema"] = schema

    conn = snowflake.connector.connect(**params)
    _conn_cache[key] = conn
    return conn


def execute_query(conn, query, params=None):
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()


def main():
    parser = argparse.ArgumentParser(description="Run a Snowflake query")
    parser.add_argument("query", help="SQL query to execute")
    parser.add_argument("--account", default=os.environ.get("SNOWFLAKE_ACCOUNT"), help="Snowflake account")
    parser.add_argument("--user", default=os.environ.get("SNOWFLAKE_USER"), help="Snowflake user")
    parser.add_argument("--warehouse", default=os.environ.get("SNOWFLAKE_WAREHOUSE"), help="Snowflake warehouse")
    parser.add_argument("--database", default=os.environ.get("SNOWFLAKE_DATABASE"), help="Snowflake database")
    parser.add_argument("--schema", default=os.environ.get("SNOWFLAKE_SCHEMA"), help="Snowflake schema")
    parser.add_argument("--authenticator", default="externalbrowser", help="Auth method (default: externalbrowser)")
    parser.add_argument("--params", default=None, help='Query parameters as JSON object, e.g. \'{"id": 123}\'')
    parser.add_argument("--format", choices=["csv", "json", "table"], default="csv", help="Output format")
    parser.add_argument("--timeout", type=int, default=600, help="Query timeout in seconds")
    args = parser.parse_args()

    # Validate required connection params
    missing = []
    if not args.account:
        missing.append("account (SNOWFLAKE_ACCOUNT)")
    if not args.user:
        missing.append("user (SNOWFLAKE_USER)")
    if not args.warehouse:
        missing.append("warehouse (SNOWFLAKE_WAREHOUSE)")
    if not args.database:
        missing.append("database (SNOWFLAKE_DATABASE)")
    if missing:
        print(f"Error: Missing required parameters: {', '.join(missing)}", file=sys.stderr)
        print("Set them via CLI flags or environment variables. Run setup.sh to configure.", file=sys.stderr)
        sys.exit(1)

    # Parse query params
    query_params = None
    if args.params:
        query_params = json.loads(args.params)

    # Connect and run
    start = time.time()
    try:
        print("Connecting to Snowflake (browser auth may open)...", file=sys.stderr)
        conn = get_connection(
            account=args.account,
            user=args.user,
            warehouse=args.warehouse,
            database=args.database,
            schema=args.schema,
            authenticator=args.authenticator,
        )
        print("Connected.", file=sys.stderr)

        df = execute_query(conn, args.query, query_params)
        elapsed = time.time() - start

        print(f"Rows: {len(df)} | Time: {elapsed:.1f}s", file=sys.stderr)

        if args.format == "csv":
            print(df.to_csv(index=False))
        elif args.format == "json":
            print(df.to_json(orient="records", indent=2))
        elif args.format == "table":
            print(df.to_string(index=False))

    except Exception as e:
        elapsed = time.time() - start
        print(f"Error after {elapsed:.1f}s: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        for conn in _conn_cache.values():
            with contextlib.suppress(Exception):
                conn.close()


if __name__ == "__main__":
    main()
