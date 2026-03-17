# Unimind — Claude Memory System Plugin

Organizational memory for Claude. Three specialized sub-agents backed by a
centralized MCP server provide persistent knowledge across conversations.

## What's Included

- **Orchestrator** (`agents/orchestrator.md`) — Replaces the default Claude system prompt with a general-purpose assistant that knows when to delegate to memory agents. Keeps the main context lean.
- **Detective agent** (`agents/detective.md`) — Read-only retrieval across the knowledge vault and structured data layer. 13 MCP tools. Returns synthesized briefings with sources.
- **Archivist agent** (`agents/archivist.md`) — Write agent for cataloguing decisions, preferences, patterns, structured business data, and media files. 23 MCP tools.
- **Ingestion agent** (`agents/ingestion.md`) — All file imports — single files or bulk batches. Surveys sources, produces a manifest for user approval, then processes everything. Handles text docs, video, audio, images, and PDFs.

MCP servers are defined inline in each agent's frontmatter — no tool descriptions are loaded into the main conversation context.

## Installation

### 1. Install the plugin

```bash
/plugin marketplace add JimmyWigerstedt/Unimind
/plugin install unimind@revenue-aigency
```

### 2. Run setup

```
/setup
```

The setup skill walks you through:
- Setting your Memory System server URL
- Naming your organization
- Granting MCP tool permissions for the memory agents

### 3. Use

Once installed, Claude operates as a general-purpose assistant with organizational
memory. It will automatically delegate to memory agents when needed:

- **Retrieval**: "What do we know about vendor risk assessment?"
- **Storage**: "Remember that we decided to use Redis for session storage"
- **Bulk import**: "Ingest everything in /onboarding-docs/"
- **File import**: "Store this PDF in memory" or "Ingest path/to/video.mp4"

## Files

| File | Purpose |
|------|---------|
| `.claude-plugin/plugin.json` | Plugin metadata and version |
| `settings.json` | Activates the orchestrator as the main agent |
| `agents/orchestrator.md` | Main agent — general-purpose assistant with delegation rules |
| `agents/detective.md` | Detective sub-agent (read-only retrieval) |
| `agents/archivist.md` | Archivist sub-agent (write operations) |
| `agents/ingestion.md` | Ingestion sub-agent (single and bulk file import) |
| `skills/setup/SKILL.md` | First-time setup wizard |
| `scripts/upload_to_r2.py` | Shared R2 upload script (used by Ingestion agent) |

## Local Development

Point the environment variable to your local server:

```bash
export MEMORY_MCP_URL="http://localhost:8000"
```

The agents' inline MCP configs connect automatically.

## Updating

Bump the `version` in `.claude-plugin/plugin.json` for each release. Marketplace
auto-update will pick up new versions.
