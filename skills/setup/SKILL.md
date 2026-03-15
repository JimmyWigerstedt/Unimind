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

## Step 2: Grant MCP tool permissions

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

## Step 3: Configure agent and skill files

Edit ALL files with MCP placeholders to replace them with the actual values
from Step 1. The files are:

- `agents/detective.md`
- `agents/archivist.md`
- `agents/ingestion.md`
- `skills/upload-media/SKILL.md`

In each file, replace:
- `<SERVER_URL>` with the server URL (e.g., `https://mcpbrain.up.railway.app`)
- `<AUTH_TOKEN>` with the auth token

Use the Edit tool with `replace_all: true` for each placeholder across each
file. The files use `type: http` — do not change that.

Also update the orchestrator (`agents/orchestrator.md`). Find the line:
```
You are a general-purpose assistant backed by an organizational memory system.
```

Edit it to:
```
You are a general-purpose assistant for <ORG NAME>, backed by an organizational memory system.
```

## Step 4: Install agents

Copy all agent files from the plugin's `agents/` directory into the project's
`.claude/agents/` directory. This ensures Claude Code discovers and loads them
on session start (the plugin's own `settings.json` agent activation is
unreliable, especially on Windows and Claude Desktop).

This step MUST come after Step 3 so the credentials and org name are already
baked into the agents before they get copied.

After copying, ensure `.claude/agents/` is in `.gitignore` (the copied agent
files contain hardcoded credentials). Read `.gitignore` if it exists, check
if `.claude/agents/` is already listed. If not, append it. If `.gitignore`
doesn't exist, create it with `.claude/agents/` as the first entry.

Use this Python script:
```bash
python -c "
import shutil
from pathlib import Path
import os

plugin_dir = os.environ.get('CLAUDE_PLUGIN_DIR', '')
if not plugin_dir:
    for candidate in [Path('.'), Path('CLIENT')]:
        if (candidate / 'agents').is_dir():
            plugin_dir = str(candidate)
            break

agents_src = Path(plugin_dir) / 'agents'
agents_dst = Path('.claude') / 'agents'
agents_dst.mkdir(parents=True, exist_ok=True)

copied = []
for f in agents_src.glob('*.md'):
    shutil.copy2(f, agents_dst / f.name)
    copied.append(f.name)

print(f'Installed {len(copied)} agents to {agents_dst}: {", ".join(copied)}')
"
```

If the script can't find the plugin agents directory, fall back to using the
Read and Write tools to copy each agent file manually.

## Step 5: Confirm

Tell the user setup is complete. Summarize:
- Server URL: `<url>`
- Auth token: configured (do NOT echo the token)
- Organization: `<name>`
- MCP permissions: granted
- Agents installed to `.claude/agents/`
- `.gitignore` updated
- **Restart required:** Fully quit and reopen Claude for agents and MCP permissions to take effect. A new conversation is not enough — the app must be restarted. On Desktop, make sure to also quit from the system tray (the icon area near the clock) — closing the window may leave the app running in the background.
