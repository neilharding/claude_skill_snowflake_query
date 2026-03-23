---
name: snowflake-query
description: Use when the user asks to query Snowflake, run Snowflake SQL, explore Snowflake tables or schemas, or fetch data from Snowflake
---

# Snowflake Query Skill

Execute SQL queries against Snowflake using browser-based SSO authentication.

## Prerequisites

Run `./setup.sh` in this skill's directory to install dependencies and configure connection settings. If queries fail with configuration errors, tell the user:

```bash
cd ~/.claude/skills/snowflake-query && ./setup.sh
```

## How to Run Queries

**IMPORTANT:** NEVER run destructive queries (e.g. `DELETE`, `DROP`) unless explicitly requested by the user and confirmed. Always ask the user to confirm and warn them in ALL CAPS before executing any query that modifies data or schema.

```bash
~/.claude/skills/snowflake-query/.venv/bin/python ~/.claude/skills/snowflake-query/scripts/run_query.py "YOUR SQL QUERY HERE"
```

**IMPORTANT:** The first query in a session opens the user's browser for SSO authentication. This is expected — the user must complete the browser auth flow before results return. Warn the user before running the first query so they aren't surprised.

### CLI Options

- `--database DB` — Override the default database
- `--schema SCHEMA` — Override the default schema
- `--params '{"key": "value"}'` — Query parameters for `%(key)s` placeholders
- `--format csv|json|table` — Output format (default: csv). Use `table` for display, `json` for structured parsing
- `--timeout SECONDS` — Query timeout (default: 600)

### Examples

Simple query:

```bash
~/.claude/skills/snowflake-query/.venv/bin/python ~/.claude/skills/snowflake-query/scripts/run_query.py "SELECT * FROM my_table LIMIT 10"
```

Different database/schema:

```bash
~/.claude/skills/snowflake-query/.venv/bin/python ~/.claude/skills/snowflake-query/scripts/run_query.py "SELECT count(*) FROM patients" --database PROD_DB --schema PUBLIC
```

Parameterized query:

```bash
~/.claude/skills/snowflake-query/.venv/bin/python ~/.claude/skills/snowflake-query/scripts/run_query.py "SELECT * FROM events WHERE status = %(status)s" --params '{"status": "active"}'
```

## Browser Auth Notes

- First query per session opens browser for SSO — warn the user
- If running in a headless/remote context, browser auth will fail. Consider switching to key-pair auth (modify `--authenticator` and connection params)
- The connection is cached within a single script invocation but not across separate calls

## SQL Dialect Notes

Snowflake SQL:

- **Parameters:** Use `%(key)s` for named placeholders, pass via `--params` as JSON object
- **String functions:** `LOWER()`, `UPPER()`, `TRIM()`, `SUBSTR()`, `REGEXP_LIKE()`
- **Date functions:** `DATEADD()`, `DATEDIFF()`, `CURRENT_DATE()`, `CURRENT_TIMESTAMP()`
- **Semi-structured:** `PARSE_JSON()`, `FLATTEN()`, `col:path` dot notation
- **LIMIT:** `LIMIT N` at end of query
- **Case sensitivity:** Identifiers are uppercase by default; use double quotes for case-sensitive names

## Presenting Results

- Small results (< 20 rows): show full table
- Medium results (20-100 rows): show first 10 rows, summarize totals and patterns
- Large results (100+ rows): show first 5 rows, summarize, offer to save to file
- Always mention row count and execution time (printed to stderr)

## Error Handling

- **"Run ./setup.sh to configure"** — skill not set up, guide the user
- **Browser auth timeout** — user didn't complete SSO in browser, ask them to retry
- **Connection errors** — check .env file settings in `~/.claude/skills/snowflake-query/.env`
- **SQL errors** — Snowflake returns clear messages, relay them to the user
