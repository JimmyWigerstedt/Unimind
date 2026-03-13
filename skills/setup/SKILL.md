---
name: setup
description: >
  First-time setup for the Unimind plugin. Configures the server URL, auth
  token, MCP permissions, and organization name. Run once after installing.
  Safe to re-run.
allowed-tools: Read, Write, Edit, Bash(python *)
---

# Unimind Setup

Walk the user through first-time configuration. This is idempotent — running
it again updates existing settings without harm.

## Step 1: Ask for server URL

Ask the user for their Memory System server URL. Example:
`https://your-app.up.railway.app`

If they don't have one yet, let them know they need to deploy the Unimind
server first and come back when they have a URL.

## Step 2: Ask for auth token

Ask the user for their MCP auth token. This is the Bearer token used to
authenticate against the Memory System server. It was generated when the
server was deployed (the `MCP_AUTH_TOKEN` env var on the server side, or
a per-user token from the `_users` table).

If they don't have one, explain they can find it in their server's Railway
environment variables (`MCP_AUTH_TOKEN`).

## Step 3: Ask for organization name

Ask what organization or team this memory system serves. This helps the
agents contextualize information. Example: "Acme Corp", "Backend Team".

## Step 4: Set environment variables

Ask the user what platform they're on:
- **Claude Code in an IDE** (VS Code, Cursor, etc.) — on Mac or Windows?
- **Claude Code CLI** (terminal) — on Mac, Linux, or Windows?
- **Claude Desktop app** — on Mac or Windows?

Then set `MEMORY_MCP_URL` and `MCP_AUTH_TOKEN` using the approach that fits:

**Mac/Linux (terminal or IDE):**
Append export lines to their shell profile (`~/.zshrc` for macOS, `~/.bashrc`
for Linux). Use the Bash tool to append if not already present.

**Windows (terminal or IDE):**
Use `setx` via the Bash tool to set persistent environment variables:
```bash
setx MEMORY_MCP_URL "<url>"
setx MCP_AUTH_TOKEN "<token>"
```

**Claude Desktop (any platform):**
Environment variables must be set in the Claude Desktop config file. Guide the
user to their settings and tell them to add `MEMORY_MCP_URL` and
`MCP_AUTH_TOKEN` there. If you can locate the config file, offer to edit it.

After persisting, also export both variables in the current session so setup
can continue without a restart.

## Step 5: Grant MCP tool permissions

Run this Python script to add MCP tool permissions to the user's Claude Code
settings. This allows the memory agents to call MCP tools without prompting:

```bash
python -c "
import json
from pathlib import Path

settings_path = Path.home() / '.claude' / 'settings.json'
settings_path.parent.mkdir(parents=True, exist_ok=True)

settings = {}
if settings_path.exists():
    settings = json.loads(settings_path.read_text())

perms = settings.setdefault('permissions', {})
allow = perms.setdefault('allow', [])

needed = ['mcp__vault-read__*', 'mcp__vault-write__*']
for pattern in needed:
    if pattern not in allow:
        allow.append(pattern)

settings_path.write_text(json.dumps(settings, indent=2) + '\n')
print('Permissions updated: ' + str(settings_path))
"
```

## Step 6: Update orchestrator with org name

Read the orchestrator agent file and update the first line to include the
organization name:

Change:
```
You are a general-purpose assistant backed by an organizational memory system.
```

To:
```
You are a general-purpose assistant for <ORG NAME>, backed by an organizational memory system.
```

Use the Edit tool to make this change in the orchestrator agent file.

## Step 7: Verify

Tell the user setup is complete. Summarize what was configured:
- Server URL: `<url>`
- Auth token: configured (don't echo the token back)
- Organization: `<name>`
- MCP permissions granted for `vault-read` and `vault-write`
- They need to restart their Claude session for environment variables to take effect

If anything failed, tell them what to fix manually.
