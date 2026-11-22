#!/usr/bin/env python3
"""ComfyUI + Qwen-Image 2.1 image backend for claymotion.

Usage:
    python scripts/comfy_qwen.py <prompt.txt> <out.png> [reference images...]

Environment:
    COMFYUI_URL             default http://127.0.0.1:8188
    QWEN_UNET               default qwen_image_2.1_int8_convrot.safetensors
    QWEN_CLIP               default qwen3vl_8b_int8_convrot.safetensors
    QWEN_VAE                default qwen_image_2.1_vae_bf16.safetensors
    QWEN_STEPS              default 25
    QWEN_CFG                default 1.0
    QWEN_WIDTH/QWEN_HEIGHT  override the inferred size
    QWEN_ALPHA_RETRIES      default 2 (only when transparent is requested)
    QWEN_TIMEOUT            default 600 seconds
    LEMO_ANIMI_TRANSPARENT  "1" forces transparent handling
    COMFYUI_INPUT_DIR       optional fallback when /upload/image is unavailable
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

COMFY = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
UNET = os.environ.get("QWEN_UNET", "qwen_image_2.1_int8_convrot.safetensors")
CLIP = os.environ.get("QWEN_CLIP", "qwen3vl_8b_int8_convrot.safetensors")
VAE = os.environ.get("QWEN_VAE", "qwen_image_2.1_vae_bf16.safetensors")
STEPS = int(os.environ.get("QWEN_STEPS", "25"))
CFG = float(os.environ.get("QWEN_CFG", "1.0"))
TIMEOUT = int(os.environ.get("QWEN_TIMEOUT", "600"))

NEG_TRANSPARENT = (
    "background, ground, cast shadow, scenery, text, letters, watermark, "
    "signature, blurry, low quality, extra limbs, grid lines"
)
NEG_OPAQUE = "text, letters, watermark, signature, blurry, low quality"


def log(msg: str) -> None:
    print(msg, flush=True)


def http_json(path: str, payload=None, timeout=30):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        COMFY + path, data=data, headers={"Content-Type": "application/json"} if data else {}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def upload_image(path: str) -> str:
    """Upload to ComfyUI's input dir over HTTP; returns the LoadImage name."""
    p = Path(path)
    boundary = "----claymotion" + uuid.uuid4().hex
    ctype = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(p.suffix.lower(), "application/octet-stream")
    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{p.name}"\r\n'.encode()
    body += f"Content-Type: {ctype}\r\n\r\n".encode()
    body += p.read_bytes()
    body += f"\r\n--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        COMFY + "/upload/image",
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.loads(r.read().decode("utf-8"))
    name = j.get("name", p.name)
    sub = j.get("subfolder", "")
    return f"{sub}/{name}" if sub else name


def stage_reference(path: str) -> str:
    try:
        return upload_image(path)
    except Exception as e:
        fallback = os.environ.get("COMFYUI_INPUT_DIR")
        if not fallback:
            raise SystemExit(f"reference upload failed ({e}); set COMFYUI_INPUT_DIR as a fallback")
        name = "claymotion_ref_" + uuid.uuid4().hex[:10] + Path(path).suffix.lower()
        Path(fallback).mkdir(parents=True, exist_ok=True)
        (Path(fallback) / name).write_bytes(Path(path).read_bytes())
        return name


def png_has_alpha(path: str) -> bool:
    with open(path, "rb") as f:
        head = f.read(26)
    return len(head) >= 26 and head[:8] == b"\x89PNG\r\n\x1a\n" and head[25] in (4, 6)


def alpha_coverage(path: str):
    try:
        from PIL import Image
        import numpy as np
    except Exception:
        return None
    with Image.open(path) as im:
        a = np.asarray(im.convert("RGBA"))[..., 3]
    return float((a < 10).mean())


def choose_size(prompt: str) -> tuple[int, int]:
    w, h = os.environ.get("QWEN_WIDTH"), os.environ.get("QWEN_HEIGHT")
    if w and h:
        return int(w), int(h)
    low = prompt.lower()
    if "portrait" in low or "9:16" in low:
        return 1024, 1536
    if "square" in low or "1:1" in low:
        return 1280, 1280
    return 1536, 1024


def build_workflow(prompt: str, width: int, height: int, refs: list[str], transparent: bool):
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "4": {
            "class_type": "TextEncodeQwenImage21",
            "inputs": {
                "clip": ["2", 0],
                "prompt": prompt,
                "negative_prompt": NEG_TRANSPARENT if transparent else NEG_OPAQUE,
                "vae": ["3", 0],
                "resolution": 1024,
            },
        },
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "seed": random.randint(0, 2**31 - 1),
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": "euler",
                "scheduler": "simple",
                "positive": ["4", 0],
                "negative": ["4", 1],
                "latent_image": ["5", 0],
                "denoise": 1.0,
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "claymotion"}},
    }
    if refs:
        images = {}
        for i, ref in enumerate(refs, 1):
            nid = str(10 + i)
            wf[nid] = {"class_type": "LoadImage", "inputs": {"image": stage_reference(ref)}}
            images[f"image_{i}"] = [nid, 0]
        wf["4"]["inputs"]["images"] = images
    return wf


def wait_for(pid: str):
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            hist = http_json(f"/history/{pid}", timeout=15)
        except Exception as e:
            log(f"history poll failed: {e}")
            time.sleep(2)
            continue
        if pid in hist:
            entry = hist[pid]
            if entry.get("status", {}).get("status_str") == "error":
                raise SystemExit("ComfyUI error: " + json.dumps(entry.get("status"))[:1500])
            return entry
        time.sleep(2)
    raise SystemExit(f"ComfyUI timed out after {TIMEOUT}s")


def generate(wf, out_path: str) -> int:
    try:
        r = http_json("/prompt", {"prompt": wf, "client_id": "claymotion"})
    except urllib.error.HTTPError as e:
        raise SystemExit("ComfyUI rejected the workflow: " + e.read().decode("utf-8", "replace")[:2000])
    pid = r["prompt_id"]
    log(f"prompt_id={pid}")
    entry = wait_for(pid)
    images = entry.get("outputs", {}).get("8", {}).get("images", [])
    if not images:
        raise SystemExit("ComfyUI produced no image: " + json.dumps(entry.get("outputs"))[:800])
    img = images[0]
    q = urllib.parse.urlencode(
        {"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")}
    )
    with urllib.request.urlopen(COMFY + "/view?" + q, timeout=60) as resp:
        data = resp.read()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(data)
    return len(data)


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("usage: comfy_qwen.py <prompt.txt> <out.png> [references...]")
    prompt_file, out_path = sys.argv[1], sys.argv[2]
    refs = sys.argv[3:]
    prompt = Path(prompt_file).read_text(encoding="utf-8").strip()
    if not prompt:
        raise SystemExit("empty prompt")
    width, height = choose_size(prompt)
    transparent = os.environ.get("LEMO_ANIMI_TRANSPARENT") == "1" or "transparent" in prompt.lower()
    retries = max(0, int(os.environ.get("QWEN_ALPHA_RETRIES", "2")))
    attempts = 1 + retries if transparent else 1
    log(f"qwen-image-2.1 {width}x{height} steps={STEPS} refs={len(refs)} transparent={transparent}")
    cov = None
    for attempt in range(1, attempts + 1):
        wf = build_workflow(prompt, width, height, refs, transparent)
        size = generate(wf, out_path)
        cov = alpha_coverage(out_path) if transparent else None
        log(f"attempt {attempt}/{attempts}: wrote {out_path} ({size} bytes, alpha={png_has_alpha(out_path)}, "
            f"transparent={None if cov is None else round(cov * 100, 1)}%)")
        if not transparent or cov is None or cov > 0.01:
            break
        if attempt < attempts:
            log("alpha is fully opaque; retrying with a new seed")
    if transparent and (not png_has_alpha(out_path) or (cov is not None and cov <= 0.01)):
        log("WARNING: no usable alpha; cut the white background with scripts/cut.py or slice --birefnet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
