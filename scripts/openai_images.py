#!/usr/bin/env python3
"""OpenAI-compatible image backend for claymotion.

Usage:
    python scripts/openai_images.py <prompt.txt> <out.png> [reference images...]

Environment:
    IMAGE_API_BASE   base URL before /images, e.g. https://api.openai.com/v1
    IMAGE_API_KEY    bearer token
    IMAGE_MODEL      model name, default gpt-image-1
    IMAGE_SIZE       default 1536x1024
    IMAGE_BACKGROUND auto | transparent | opaque  (default auto: transparent only if requested)
    LEMO_ANIMI_TRANSPARENT  1 forces transparent handling
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

BASE = os.environ.get("IMAGE_API_BASE", "").rstrip("/")
KEY = os.environ.get("IMAGE_API_KEY", "")
MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-1")
SIZE = os.environ.get("IMAGE_SIZE", "1536x1024")


def log(msg: str) -> None:
    print(msg, flush=True)


def multipart(fields: dict[str, str], files: list[tuple[str, str]]) -> tuple[bytes, str]:
    boundary = "----claymotion" + uuid.uuid4().hex
    body = bytearray()
    for k, v in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for field, path in files:
        p = Path(path)
        ctype = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
            p.suffix.lower(), "application/octet-stream"
        )
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{field}"; filename="{p.name}"\r\n'.encode()
        body += f"Content-Type: {ctype}\r\n\r\n".encode()
        body += p.read_bytes()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), boundary


def request(path: str, data: bytes, ctype: str):
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Authorization": f"Bearer {KEY}", "Content-Type": ctype}
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"image API error {e.code}: " + e.read().decode("utf-8", "replace")[:2000])


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("usage: openai_images.py <prompt.txt> <out.png> [references...]")
    if not BASE or not KEY:
        raise SystemExit("set IMAGE_API_BASE and IMAGE_API_KEY")
    prompt = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    out = sys.argv[2]
    refs = sys.argv[3:]
    transparent = os.environ.get("LEMO_ANIMI_TRANSPARENT") == "1" or "transparent" in prompt.lower()
    bg_mode = os.environ.get("IMAGE_BACKGROUND", "auto")
    bg = "transparent" if (bg_mode == "transparent" or (bg_mode == "auto" and transparent)) else "opaque"
    if refs:
        fields = {"model": MODEL, "size": SIZE, "background": bg, "prompt": prompt}
        body, boundary = multipart(fields, [("image[]", r) for r in refs])
        j = request("/images/edits", body, f"multipart/form-data; boundary={boundary}")
    else:
        payload = json.dumps({"model": MODEL, "size": SIZE, "background": bg, "prompt": prompt}).encode()
        j = request("/images/generations", payload, "application/json")
    try:
        item = j["data"][0]
    except Exception:
        raise SystemExit("no image in response: " + json.dumps(j)[:1200])
    if item.get("b64_json"):
        data = base64.b64decode(item["b64_json"])
    elif item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            data = r.read()
    else:
        raise SystemExit("response has neither b64_json nor url")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(data)
    log(f"wrote {out} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
