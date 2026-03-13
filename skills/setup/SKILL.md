---
name: setup
description: >
  First-time setup for the Claude Memory System plugin. Configures the server
  URL, grants MCP tool permissions, and stores organization name. Run this
  once after installing the plugin. Safe to re-run.
allowed-tools: Read, Write, Edit, Bash(python *)
---

# Memory System Setup

Walk the user through first-time configuration. This is idempotent — running
it again updates existing settings without harm.

## Step 1: Ask for server URL

Ask the user for their Memory System server URL. Example:
`https://your-app.up.railway.app`

If they don't have one yet, let them know they need to deploy the Memory System
server first and come back when they have a URL.

## Step 2: Ask for organization name

Ask what organization or team this memory system serves. This helps the
orchestrator and agents contextualize information. Example: "Acme Corp",
"Backend Team", "My Company".

## Step 3: Write environment variable

Help the user set the `MEMORY_MCP_URL` environment variable. Detect their
shell and suggest the right command:

```bash
# For bash (~/.bashrc or ~/.bash_profile):
echo 'export MEMORY_MCP_URL="<url>"' >> ~/.bashrc

# For zsh (~/.zshrc):
echo 'export MEMORY_MCP_URL="<url>"' >> ~/.zshrc

# For fish (~/.config/fish/config.fish):
set -Ux MEMORY_MCP_URL "<url>"
```

Ask the user which shell they use, then run the appropriate command. Also
export it in the current session so setup can continue without restarting:

```bash
export MEMORY_MCP_URL="<url>"
```

## Step 4: Grant MCP tool permissions

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

## Step 5: Update orchestrator with org name

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

## Step 6: Verify

Tell the user setup is complete. Summarize what was configured:
- Server URL set to: `<url>`
- Organization: `<name>`
- MCP permissions granted for `vault-read` and `vault-write`
- They may need to restart their Claude session for all changes to take effect

If anything failed, tell them what to fix manually.
