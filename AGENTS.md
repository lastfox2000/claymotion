# AGENTS

This repository is a single **Agent Skill**. The entry point is `SKILL.md`; read it before doing anything.

## Install

- **Grok Bot**: `sh scripts/install_grok.sh` (defaults to `~/agent-data/workflows/claymotion/`).
- **Codex**: symlink/copy this folder to `~/.agents/skills/claymotion`.
- **Claude Code**: symlink/copy to `~/.claude/skills/claymotion`.
- **Doubao / Kimi**: upload the release ZIP; `SKILL.md` must be at the ZIP root.

## Run

```bash
python scripts/claymotion.py doctor
python scripts/claymotion.py styles --lang zh
python scripts/claymotion.py init pancake --style clay --dur 20 --name pancake --lang zh
```

## Rules

- Do not claim a rendered film when only a pack exists.
- Do not put API keys in prompts, commits, or `SKILL.md`.
- Keep the lemo-animi attribution and the CC BY-NC / MIT split in `NOTICE`.
- The 8 styles are fixed; don't invent a new style inline. See `styles/`.
