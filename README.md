# Snowflake Query Skill for Claude Code

A Claude Code skill that lets Claude execute SQL queries against Snowflake using browser-based SSO authentication.

## Installation

1. **Copy the skill into your Claude Code skills directory:**

   ```bash
   cp -r /path/to/claude-skill-snowflake-query ~/.claude/skills/snowflake-query
   ```

2. **Run the setup script:**

   ```bash
   cd ~/.claude/skills/snowflake-query && ./setup.sh
   ```

   This will:
   - Create a Python virtual environment (`.venv`)
   - Install `snowflake-connector-python`, `pandas`, and `python-dotenv`
   - Prompt you for your Snowflake connection details (account, user, warehouse, database, schema)
   - Save them to a `.env` file

3. **Verify the installation:**

   ```bash
   ~/.claude/skills/snowflake-query/.venv/bin/python ~/.claude/skills/snowflake-query/scripts/run_query.py "SELECT CURRENT_TIMESTAMP()"
   ```

   Your browser will open for SSO authentication on first run.

## Usage

Once installed, ask Claude to query Snowflake in natural language:

- "Query Snowflake for the top 10 patients"
- "Run this SQL on Snowflake: SELECT count(*) FROM events"
- "What tables are in the PUBLIC schema on Snowflake?"

Claude will automatically invoke the skill when it detects a Snowflake-related request.

## Authentication

This skill uses Snowflake's **externalbrowser** SSO authentication. The first query in each session opens your default browser for authentication. This works well in Claude Code (terminal) and Claude Desktop where a browser is available.

For headless or remote environments, consider switching to key-pair authentication by modifying the `--authenticator` flag and connection parameters.

## Configuration

Connection settings are stored in `~/.claude/skills/snowflake-query/.env`:

```
SNOWFLAKE_ACCOUNT=your-account.region
SNOWFLAKE_USER=your-username
SNOWFLAKE_WAREHOUSE=your-warehouse
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_SCHEMA=your-schema
```

Edit this file directly to update your settings, or delete it and re-run `./setup.sh`.
