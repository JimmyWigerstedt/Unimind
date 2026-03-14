---
name: setup
description: >
  First-time setup for the Unimind plugin. Configures the server URL, auth
  token, MCP permissions, and organization name. Run once after installing.
  Safe to re-run.
allowed-tools: Read, Write, Edit, Bash(python *), AskUserQuestion
---

# Unimind Setup

Walk the user through first-time configuration. This is idempotent — running
it again updates existing settings without harm.

IMPORTANT: For every question to the user, use the AskUserQuestion tool.
Do not use plain text output to ask questions.

## Step 1: Server URL

Use AskUserQuestion to ask for their Unimind server URL.
Example: `https://your-app.up.railway.app`

If they don't have one yet, let them know they need to deploy the Unimind
server first and come back when they have a URL.

## Step 2: Auth token

Use AskUserQuestion to ask for their auth token. Tell them:
"You should have received an auth token from your system administrator.
If you're the admin, it's the MCP_AUTH_TOKEN value in your server's
environment variables."

## Step 3: Organization name

Use AskUserQuestion to ask what organization or team this memory system
serves. Example: "Acme Corp", "Backend Team".

## Step 4: Platform

Use AskUserQuestion to ask what platform they're on:
- Claude Code in an IDE (VS Code, Cursor, etc.) — Mac or Windows?
- Claude Code CLI (terminal) — Mac, Linux, or Windows?
- Claude Desktop — Mac or Windows?

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
