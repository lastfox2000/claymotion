#!/usr/bin/env python3
"""MiniMax H3-Image backend for claymotion (local ComfyUI).

Usage: python scripts/h3_image.py <prompt.txt> <out.png> [width] [height]
Env: COMFYUI_URL, H3_UNET, H3_CLIP, H3_VAE, H3_STEPS
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

COMFY = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
UNET = os.environ.get("H3_UNET", "minimax_h3_image_pruned_int8_convrot.safetensors")
CLIP = os.environ.get("H3_CLIP", "qwen3vl_32b_minimax_h3_int8_convrot.safetensors")
VAE = os.environ.get("H3_VAE", "minimax_h3_image_vae_fp16.safetensors")
STEPS = int(os.environ.get("H3_STEPS", "6"))


def post(path, payload):
    req = urllib.request.Request(
        COMFY + path, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("usage: h3_image.py <prompt.txt> <out.png> [width] [height]")
    prompt = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    out = sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1536
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
    wf = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "4": {"class_type": "MiniMaxH3ImageConditioning", "inputs": {"clip": ["2", 0], "vae": ["3", 0], "prompt": prompt, "width": w, "height": h}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": 42, "steps": STEPS, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["4", 1], "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "claymotion_h3"}},
    }
    r = post("/prompt", {"prompt": wf, "client_id": "claymotion-h3"})
    pid = r["prompt_id"]
    print("prompt_id", pid, flush=True)
    for _ in range(120):
        with urllib.request.urlopen(COMFY + "/history/" + pid, timeout=15) as hh:
            hist = json.loads(hh.read())
        if pid in hist:
            entry = hist[pid]
            if entry.get("status", {}).get("status_str") == "error":
                raise SystemExit(json.dumps(entry.get("status"))[:2000])
            img = entry["outputs"]["8"]["images"][0]
            q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
            with urllib.request.urlopen(COMFY + "/view?" + q, timeout=60) as resp:
                data = resp.read()
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            Path(out).write_bytes(data)
            print("wrote", out, len(data), flush=True)
            return 0
        time.sleep(2)
    raise SystemExit("timeout")


if __name__ == "__main__":
    raise SystemExit(main())
