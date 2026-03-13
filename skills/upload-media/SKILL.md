---
name: upload-media
description: >
  Upload and ingest media files (images, video, audio, PDFs) into the memory
  system. Handles context extraction, R2 upload via presigned URL, and
  delegation to the Archivist for chunking, embedding, and vault note creation.
  Use when a user attaches a file and wants it stored in organizational memory.
argument-hint: <file-path>
allowed-tools: Read, Bash(python *upload_to_r2*), mcp__vault-write__get_upload_url
mcpServers:
  - vault-write:
      type: url
      url: "${MEMORY_MCP_URL}/mcp/write/mcp"
---

# Upload Media to Memory System

You are handling media ingestion for the Claude Memory System. A user has
attached a file or provided a file path. Your job is to extract context,
upload the file to R2, and delegate to the Archivist for full ingestion.

## Step 1: Identify the file and modality

Determine the modality from the file extension or MIME type:

| Extensions | Modality | MIME type |
|---|---|---|
| .png, .jpg, .jpeg, .gif, .webp | image | image/* |
| .mp4, .mov, .webm | video | video/* |
| .mp3, .wav, .ogg, .m4a | audio | audio/* |
| .pdf | pdf | application/pdf |

If the file is not one of these types, inform the user that only image, video,
audio, and PDF files are supported for media ingestion.

## Step 2: Extract context

### PDFs and documents
- **Do NOT ask for context.** PDFs are content-dense and self-describing.
- If the user has already volunteered context in the conversation, capture it.
  Otherwise, proceed silently.

### Video and audio
Context is critical — the embedding model sees/hears the content but doesn't
know *why it matters* to the organization.

1. Check if context is already clear from the conversation. If the user said
   "Here's the recording from Tuesday's sprint retro with the backend team"
   — that IS the context. Confirm and proceed. Don't interrogate redundantly.

2. If context is NOT clear, ask:
   - What is this? (event, meeting, presentation, demo, etc.)
   - When and where did this happen?
   - Who is involved?
   - Why are we keeping this? What future search would need to find it?

3. If the user gives vague answers ("it's a video from work"), push back once:
   "Without context, this media will only be findable by its visual/audio
   content. Can you tell me more about what this is and why it matters?"

4. Do not ask more than twice. If the user declines, proceed with what you have.

### Images
1. Same context extraction as video/audio (check conversation first, then ask).
2. **Additionally:** You can see the image. Generate a `content_description` —
   a detailed, factual description of what the image shows. This will be stored
   permanently and used by the Detective agent for reasoning.

   Example: "Five people in chef hats cooking at kitchen stations. Whiteboard
   in background reads 'Q1 Offsite - Cook-Off Challenge'. Two teams appear to
   be racing to plate dishes."

## Step 3: Get presigned upload URL

Call the MCP tool:
```
get_upload_url(
  filename="<original filename>",
  mime_type="<mime type>",
  metadata={"org_id": "<org if known, else 'default'>"}
)
```

This returns `{r2_key, upload_url, expires_in}`. Save the `r2_key` — you'll
pass it to the Archivist.

## Step 4: Upload to R2

Run the upload script with the file path and presigned URL:

```bash
python ${CLAUDE_PLUGIN_DIR}/scripts/upload_to_r2.py "<file_path>" "<upload_url>" "<mime_type>"
```

Verify the script exits with code 0. If it fails, report the error to the user.

## Step 5: Delegate to Archivist

Spawn the Archivist sub-agent with a **Media intent**:

```
**Media:** <title>
**Modality:** <image | video | audio | pdf>
**R2 Key:** <r2_key from step 3>
**Context:** <gathered context string, or empty for PDFs>
**Content Description:** <your image description from step 2, or empty>
**Department:** <department if known>
```

The Archivist will handle the rest: chunking, Flash Lite descriptions,
dual-vector embedding, vault note creation, and link weaving.

## Step 6: Confirm to user

Once the Archivist returns its status line, relay the outcome:
- What was ingested (title, modality, chunk count)
- Where the vault note was created (path)
- Any related notes that were linked

---

## Notes

- The presigned URL expires in 1 hour. Large files have plenty of time.
- For large video/audio files, the upload may take time. The script streams
  the upload — no need to load the entire file into memory.
- All media goes through R2. No base64 exceptions, no size-based branching.
- The `r2_key` is deterministic (based on slugified title) — uploading the
  same title twice will overwrite the previous file in R2.
