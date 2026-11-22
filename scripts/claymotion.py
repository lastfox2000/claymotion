#!/usr/bin/env python3
"""claymotion: one command surface for the stop-motion skill.

Run with the same Python that has the skill's dependencies installed:
    python scripts/claymotion.py doctor
    python scripts/claymotion.py styles --lang zh
    python scripts/claymotion.py init pancake --style clay --dur 20 --name pancake --lang zh
    python scripts/claymotion.py prompt clay sheet8 prompts/toss.slots.txt -o prompts/toss.txt
    python scripts/claymotion.py image --prompt prompts/toss.txt --out src/toss.png --ref src/char.png
    python scripts/claymotion.py slice src/toss.png work/cells toss --n 8
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

try:  # Windows consoles often default to GBK; keep child output UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def child_env() -> dict:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def run(script: str, args: list[str], cwd: Path | None = None) -> int:
    path = SCRIPTS / script
    if not path.exists():
        print(f"missing script: {path}", file=sys.stderr)
        return 2
    cmd = [sys.executable, str(path), *args]
    return subprocess.call(cmd, cwd=str(cwd) if cwd else None, env=child_env())


def run_module(script: str, args: list[str]) -> int:
    return run(script, args)


def doctor(args) -> int:
    problems = []
    warnings = []
    py = sys.version_info
    print(f"python: {py.major}.{py.minor}.{py.micro}  ({sys.executable})")
    if py < (3, 10):
        problems.append("Python 3.10+ is required")
    mods = {
        "numpy": "numpy",
        "cv2": "opencv-python-headless",
        "PIL": "pillow",
        "scipy": "scipy",
        "soundfile": "soundfile",
        "soxr": "soxr",
        "onnxruntime": "onnxruntime",
        "edge_tts": "edge-tts",
    }
    missing = []
    for mod, pip_name in mods.items():
        ok = importlib.util.find_spec(mod) is not None
        print(f"  {mod:12s} {'ok' if ok else 'MISSING'}")
        if not ok:
            missing.append(pip_name)
    if missing:
        problems.append("missing Python packages: " + " ".join(missing))
        print("  install: " + sys.executable + " -m pip install " + " ".join(missing))
    for exe in ("ffmpeg", "ffprobe"):
        found = shutil.which(exe)
        print(f"{exe}: {found or 'MISSING'}")
        if not found:
            problems.append(f"{exe} not on PATH")
    font = ROOT / "fonts" / "SourceHanSansCN-Bold.otf"
    print(f"font: {'ok' if font.exists() else 'MISSING'}  {font}")
    if not font.exists():
        warnings.append("CJK font missing: titles/subtitles will fall back or fail")
    if args.comfy or os.environ.get("CLAYMOTION_BACKEND", "comfy-qwen") in ("comfy-qwen", "h3"):
        url = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
        try:
            import urllib.request
            with urllib.request.urlopen(url + "/system_stats", timeout=4) as r:
                print(f"ComfyUI: ok  {url}  HTTP {r.status}")
        except Exception as e:
            print(f"ComfyUI: unreachable  {url}  ({e})")
            warnings.append("ComfyUI unreachable; use the openai backend or pack mode")
    print()
    if problems:
        print("NOT READY:")
        for p in problems:
            print("  -", p)
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print("  -", w)
    if not problems:
        print("READY: " + ("with warnings" if warnings else "all checks passed"))
    return 1 if problems else 0


def cmd_styles(args) -> int:
    return run("animi.py", ["styles", "--lang", args.lang])


def cmd_init(args) -> int:
    short = args.film_name or args.name
    tail = [args.name, "--style", args.style, "--dur", str(args.dur), "--size", args.size,
            "--name", short, "--lang", args.lang]
    return run("init_film.py", tail)


def cmd_prompt(args) -> int:
    tail = ["prompt", args.style, args.kind, args.slots, "-o", args.out]
    if args.size:
        tail += ["--size", args.size]
    return run("animi.py", tail)


def cmd_check(args) -> int:
    tail = ["check", args.png, "--n", str(args.n)]
    if args.rows:
        tail += ["--rows", str(args.rows)]
    if args.cols:
        tail += ["--cols", str(args.cols)]
    if args.out:
        tail += ["--out", args.out]
    if args.birefnet:
        tail += ["--birefnet"]
    if args.group:
        tail += ["--group", args.group]
    return run("animi.py", tail)


def cmd_slice(args) -> int:
    tail = ["slice", args.png, args.outdir, args.prefix, "--n", str(args.n)]
    if args.rows:
        tail += ["--rows", str(args.rows)]
    if args.cols:
        tail += ["--cols", str(args.cols)]
    if args.birefnet:
        tail += ["--birefnet"]
    if args.group:
        tail += ["--group", args.group]
    if args.clean:
        tail += ["--clean"]
    return run("animi.py", tail)


def cmd_anchors(args) -> int:
    tail = ["anchors", args.cells, "--prefix", args.prefix]
    if args.json:
        tail += ["--json", args.json]
    if args.preview:
        tail += ["--preview", args.preview]
    return run("animi.py", tail)


def cmd_sound(args) -> int:
    return run("sound.py", [args.action, *args.rest])


def cmd_image(args) -> int:
    backend = args.backend or os.environ.get("CLAYMOTION_BACKEND", "comfy-qwen")
    env = child_env()
    if args.width:
        env["QWEN_WIDTH"] = str(args.width)
        env["IMAGE_WIDTH"] = str(args.width)
    if args.height:
        env["QWEN_HEIGHT"] = str(args.height)
        env["IMAGE_HEIGHT"] = str(args.height)
    if backend in ("comfy-qwen", "qwen", "comfy"):
        script, argv = "comfy_qwen.py", [args.prompt, args.out, *args.ref]
    elif backend == "h3":
        script, argv = "h3_image.py", [args.prompt, args.out, str(args.width or 1536), str(args.height or 1024)]
    elif backend == "openai":
        script, argv = "openai_images.py", [args.prompt, args.out, *args.ref]
    elif backend == "command":
        cmd = os.environ.get("IMAGE_CMD")
        if not cmd:
            print("IMAGE_CMD is not set", file=sys.stderr)
            return 2
        argv = [args.prompt, args.out, *args.ref]
        return subprocess.call(cmd.split() + argv, env=env)
    else:
        print(f"unknown backend: {backend}", file=sys.stderr)
        return 2
    path = SCRIPTS / script
    if not path.exists():
        print(f"missing backend: {path}", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(path), *argv], env=env)


def cmd_render(args) -> int:
    film = Path.cwd() / "tools" / "film.py"
    if not film.exists():
        print(f"not a film folder (no {film})", file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, str(film), *args.rest], cwd=str(Path.cwd()), env=child_env())


def cmd_review(args) -> int:
    return run("review.py", [args.action, *args.rest])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="claymotion", description="Stop-motion short from one line")
    p.add_argument("--version", action="version", version="1.0.0")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="check python, ffmpeg, packages, ComfyUI")
    d.add_argument("--comfy", action="store_true", help="require/report ComfyUI")
    d.set_defaults(func=doctor)

    s = sub.add_parser("styles", help="list fixed styles")
    s.add_argument("--lang", default="zh")
    s.set_defaults(func=cmd_styles)

    i = sub.add_parser("init", help="create a film folder")
    i.add_argument("name")
    i.add_argument("--name", dest="film_name", help="short film name (default: folder name)")
    i.add_argument("--style", default="clay")
    i.add_argument("--dur", type=float, default=40.0)
    i.add_argument("--size", default="landscape", choices=["landscape", "portrait", "square"])
    i.add_argument("--lang", default="zh")
    i.set_defaults(func=cmd_init)

    pr = sub.add_parser("prompt", help="build one asset prompt from a slot file")
    pr.add_argument("style")
    pr.add_argument("kind", choices=["character", "sheet8", "sheet4", "prop", "fx", "bg", "layer", "texture"])
    pr.add_argument("slots")
    pr.add_argument("-o", "--out", required=True)
    pr.add_argument("--size", default="landscape")
    pr.set_defaults(func=cmd_prompt)

    im = sub.add_parser("image", help="generate one image")
    im.add_argument("--prompt", required=True)
    im.add_argument("--out", required=True)
    im.add_argument("--ref", action="append", default=[])
    im.add_argument("--backend", default=None, choices=["comfy-qwen", "openai", "h3", "command"])
    im.add_argument("--width", type=int)
    im.add_argument("--height", type=int)
    im.set_defaults(func=cmd_image)

    c = sub.add_parser("check", help="QC a sheet")
    c.add_argument("png")
    c.add_argument("--n", type=int, default=8)
    c.add_argument("--rows", type=int)
    c.add_argument("--cols", type=int)
    c.add_argument("--out")
    c.add_argument("--birefnet", action="store_true")
    c.add_argument("--group", choices=["subject", "grid"])
    c.set_defaults(func=cmd_check)

    sl = sub.add_parser("slice", help="slice a sheet into cells")
    sl.add_argument("png")
    sl.add_argument("outdir")
    sl.add_argument("prefix")
    sl.add_argument("--n", type=int, default=8)
    sl.add_argument("--rows", type=int)
    sl.add_argument("--cols", type=int)
    sl.add_argument("--birefnet", action="store_true")
    sl.add_argument("--group", choices=["subject", "grid"])
    sl.add_argument("--clean", action="store_true")
    sl.set_defaults(func=cmd_slice)

    a = sub.add_parser("anchors", help="compute cell anchors")
    a.add_argument("cells")
    a.add_argument("--prefix", required=True)
    a.add_argument("--json")
    a.add_argument("--preview")
    a.set_defaults(func=cmd_anchors)

    so = sub.add_parser("sound", help="sound.py lint/build/check/times")
    so.add_argument("action", choices=["lint", "build", "check", "times", "vo"])
    so.add_argument("rest", nargs=argparse.REMAINDER)
    so.set_defaults(func=cmd_sound)

    r = sub.add_parser("render", help="tools/film.py in the current film folder")
    r.add_argument("rest", nargs=argparse.REMAINDER)
    r.set_defaults(func=cmd_render)

    rv = sub.add_parser("review", help="review.py add/open/notes/wait")
    rv.add_argument("action", choices=["add", "open", "notes", "wait", "reply"])
    rv.add_argument("rest", nargs=argparse.REMAINDER)
    rv.set_defaults(func=cmd_review)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
