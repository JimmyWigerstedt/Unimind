#!/usr/bin/env python3
"""
upload_to_r2.py
Upload a local file to Cloudflare R2 via a presigned PUT URL.

Usage:
  python upload_to_r2.py <file_path> <presigned_url> <mime_type>

Exit codes:
  0 — success
  1 — upload failed (HTTP error or file not found)

The upload streams the file in 8MB chunks to avoid loading large
video/audio files entirely into memory.
"""

import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    # Fall back to urllib if httpx isn't available in the client env
    httpx = None


CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB


def upload_streaming_httpx(file_path: Path, url: str, mime_type: str) -> int:
    """Stream-upload via httpx (preferred — supports chunked transfer)."""
    with open(file_path, "rb") as f:
        resp = httpx.put(
            url,
            content=f,
            headers={"Content-Type": mime_type},
            timeout=600.0,  # 10 min for large files
        )
    return resp.status_code


def upload_streaming_urllib(file_path: Path, url: str, mime_type: str) -> int:
    """Stream-upload via urllib (fallback — no external deps)."""
    import urllib.request

    file_size = file_path.stat().st_size
    with open(file_path, "rb") as f:
        req = urllib.request.Request(
            url,
            data=f,
            method="PUT",
            headers={
                "Content-Type": mime_type,
                "Content-Length": str(file_size),
            },
        )
        resp = urllib.request.urlopen(req, timeout=600)
    return resp.status


def main():
    if len(sys.argv) != 4:
        print("Usage: upload_to_r2.py <file_path> <presigned_url> <mime_type>",
              file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    presigned_url = sys.argv[2]
    mime_type = sys.argv[3]

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"Uploading {file_path.name} ({file_size_mb:.1f} MB) to R2...")

    try:
        if httpx is not None:
            status = upload_streaming_httpx(file_path, presigned_url, mime_type)
        else:
            status = upload_streaming_urllib(file_path, presigned_url, mime_type)
    except Exception as e:
        print(f"Upload failed: {e}", file=sys.stderr)
        sys.exit(1)

    if 200 <= status < 300:
        print(f"Upload successful ({status})")
    else:
        print(f"Upload failed with status {status}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
