---
name: setup
description: >
  First-time setup for the Unimind plugin. Configures the server URL, auth
  token, MCP permissions, and organization name. Run once after installing.
  Safe to re-run.
allowed-tools: Read, Write, Edit, Bash(python *), Bash(setx *)
---

# Unimind Setup

Walk the user through first-time configuration. This is idempotent — running
it again updates existing settings without harm.

IMPORTANT: YOU do all the work. Do not give the user manual instructions and
ask them to do it themselves. You have the tools — read files, write files,
edit files, run scripts. Use them. The user should only need to answer your
questions and confirm the result.

## Step 1: Collect information

Ask the user three things (you can ask all at once):
1. **Server URL** — their Unimind server URL (e.g., `https://your-app.up.railway.app`)
2. **Auth token** — the MCP auth token from their server admin or Railway env vars
3. **Organization name** — what org/team this serves (e.g., "Acme Corp")

## Step 2: Set environment variables

You MUST set both `MEMORY_MCP_URL` and `MCP_AUTH_TOKEN` as persistent
environment variables. Do not tell the user how to do it — do it yourself.

**Detect the platform** from your environment (check `sys.platform`, look for
Claude Desktop config files, etc.) and act accordingly:

### Windows (any client):
Run via Bash:
```bash
setx MEMORY_MCP_URL "<url>"
setx MCP_AUTH_TOKEN "<token>"
```

### Mac/Linux (any client):
Detect the shell from `$SHELL`. Append to the correct profile file
(`~/.zshrc`, `~/.bashrc`, or fish config). Read the file first to avoid
duplicates — only append if the variable isn't already present:
```bash
echo 'export MEMORY_MCP_URL="<url>"' >> ~/.zshrc
echo 'export MCP_AUTH_TOKEN="<token>"' >> ~/.zshrc
```

### Claude Desktop (additional step — REQUIRED):
Claude Desktop does NOT support Streamable HTTP MCP transport directly. It
needs `mcp-remote` as a bridge. You MUST add MCP server entries to the
Claude Desktop config.

Find the config file:
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

READ it first. Then EDIT it to add `vault-read` and `vault-write` to the
`mcpServers` object. Do NOT overwrite existing servers — merge carefully.

The entries must use `mcp-remote` via npx:
```json
{
  "mcpServers": {
    "vault-read": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "<MEMORY_MCP_URL>/mcp/read/mcp",
        "--header",
        "Authorization: Bearer <MCP_AUTH_TOKEN>"
      ]
    },
    "vault-write": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "<MEMORY_MCP_URL>/mcp/write/mcp",
        "--header",
        "Authorization: Bearer <MCP_AUTH_TOKEN>"
      ]
    }
  }
}
```

Replace `<MEMORY_MCP_URL>` and `<MCP_AUTH_TOKEN>` with the actual values
(not env var references — Claude Desktop doesn't expand env vars in args).

After persisting, also export both variables in the current session so the
rest of setup works without a restart.

## Step 3: Grant MCP tool permissions

Read `~/.claude/settings.json` (create it if it doesn't exist). Add
`mcp__vault-read__*` and `mcp__vault-write__*` to `permissions.allow` if
not already present. Write the file back.

Use this Python script:
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

## Step 4: Update orchestrator with org name

Read the orchestrator agent file. Find the line:
```
You are a general-purpose assistant backed by an organizational memory system.
```

Edit it to:
```
You are a general-purpose assistant for <ORG NAME>, backed by an organizational memory system.
```

Use the Edit tool. Do not ask the user to do this.

## Step 5: Confirm

Tell the user setup is complete. Summarize:
- Server URL: `<url>`
- Auth token: set (do NOT echo the token)
- Organization: `<name>`
- MCP permissions: granted
- Note: restart the Claude session for env vars to take effect
