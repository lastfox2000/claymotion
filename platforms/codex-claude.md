# Codex / Claude Code

The package is an Agent Skills folder: `SKILL.md` + `scripts/` + `styles/` + `references/`.

## Codex

```bash
mkdir -p ~/.agents/skills
ln -s /path/to/claymotion ~/.agents/skills/claymotion
```

Start a new chat and say:

> 用 claymotion 做一支 20 秒黏土定格动画：小企鹅学做煎饼

## Claude Code

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/claymotion ~/.claude/skills/claymotion
```

Claude Code needs the image adapter or Codex CLI. This package’s `scripts/claymotion.py image` is that adapter; set `CLAYMOTION_BACKEND` and `COMFYUI_URL`/`IMAGE_API_*`.

## Windows

Use a WSL shell or a Python 3.10+ environment with ffmpeg on PATH. The Python scripts are cross-platform; only the old `setup.sh` / `gen.sh` wrappers are POSIX. Prefer:

```powershell
python scripts\claymotion.py doctor
python scripts\claymotion.py init pancake --style clay --dur 20 --name pancake --lang zh
```

`claymotion.py` calls `sys.executable`, so use the venv Python that has `numpy`, `opencv-python-headless`, `pillow`, `scipy`, `soundfile`, `soxr`, `onnxruntime`, `edge-tts`.

## Install options

If the host supports the `codex plugin` / Claude plugin marketplace, publish this folder as a plugin repo with `plugin/skills/claymotion/` layout; otherwise symlink/copy the folder as above.
