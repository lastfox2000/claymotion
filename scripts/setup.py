#!/usr/bin/env python3
"""Cross-platform setup for claymotion.

    python scripts/setup.py --check        # only check
    python scripts/setup.py --install      # pip install missing packages
    python scripts/setup.py --instruments  # download score samples (~1.4 GB)
    python scripts/setup.py --matte        # download BiRefNet (~0.97 GB)
    python scripts/setup.py --all          # install + instruments + matte
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("LEMO_ANIMI_HOME", Path.home() / "lemo-animi-env"))
PKGS = ["pillow", "numpy", "opencv-python-headless", "scipy", "soundfile", "soxr", "edge-tts", "onnxruntime"]
MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-general-epoch_244.onnx"
MODEL_SIZE = 972666916


def check() -> int:
    bad = 0
    print("python", sys.version.split()[0], sys.executable)
    if sys.version_info < (3, 10):
        print("! Python 3.10+ required")
        bad = 1
    missing = []
    for mod, pip_name in [
        ("PIL", "pillow"), ("numpy", "numpy"), ("cv2", "opencv-python-headless"),
        ("scipy", "scipy"), ("soundfile", "soundfile"), ("soxr", "soxr"),
        ("onnxruntime", "onnxruntime"), ("edge_tts", "edge-tts"),
    ]:
        try:
            __import__(mod)
            print(f"  {mod:12s} ok")
        except Exception:
            print(f"  {mod:12s} MISSING")
            missing.append(pip_name)
    if missing:
        print("! pip install " + " ".join(missing))
        bad = 1
    for exe in ("ffmpeg", "ffprobe"):
        p = shutil.which(exe)
        print(f"{exe}: {p or 'MISSING'}")
        if not p:
            bad = 1
    font = ROOT / "fonts" / "SourceHanSansCN-Bold.otf"
    print("font:", "ok" if font.exists() else "MISSING", font)
    model = HOME / "models" / "birefnet-general.onnx"
    print("matte model:", "ok" if model.exists() else "optional, not installed", model)
    instr = HOME / "instruments"
    print("instruments:", "ok" if instr.exists() else "MISSING (score will not build)", instr)
    return 1 if bad else 0


def install() -> int:
    return subprocess.call([sys.executable, "-m", "pip", "install", *PKGS])


def instruments() -> int:
    script = ROOT / "scripts" / "audio" / "fetch_instruments.py"
    if not script.exists():
        print("missing", script)
        return 2
    return subprocess.call([sys.executable, str(script)])


def matte() -> int:
    dst = HOME / "models" / "birefnet-general.onnx"
    if dst.exists() and dst.stat().st_size == MODEL_SIZE:
        print("already installed", dst)
        return 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    part = dst.with_suffix(".part")
    print("downloading", MODEL_URL, "->", dst)
    try:
        urllib.request.urlretrieve(MODEL_URL, part)
    except Exception as e:
        print("download failed:", e)
        return 1
    if part.stat().st_size != MODEL_SIZE:
        print(f"size {part.stat().st_size} != {MODEL_SIZE}; delete {part} and retry")
        return 1
    part.replace(dst)
    print("installed", dst)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--instruments", action="store_true")
    ap.add_argument("--matte", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.all:
        a.install = a.instruments = a.matte = True
    rc = 0
    if a.install:
        rc |= install()
    if a.instruments:
        rc |= instruments()
    if a.matte:
        rc |= matte()
    if not any([a.install, a.instruments, a.matte]):
        rc |= check()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
