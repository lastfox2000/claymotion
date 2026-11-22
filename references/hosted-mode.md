# Pack mode (hosted bots without a local renderer)

Doubao, Grok Bot and Kimi can run this skill in two ways:

1. **Full mode** — the host has Python, ffmpeg, and an image backend it can reach. Run the normal workflow and render `out/<name>.mp4`.
2. **Pack mode** — the host cannot run Python/ffmpeg, or cannot reach a local ComfyUI. Do not fake a rendered film. Produce a **production pack** the user can render on their own machine.

## What a pack contains

```
<pack>/
  production-log.md        story skeleton, beats, shot list, layered action table, image list
  prompts/
    char_hero.slots.txt
    char_hero.txt          full prompt built by animi.py prompt
    bg_wide.slots.txt
    bg_wide.txt
    sheet_toss.slots.txt
    sheet_toss.txt
    close_face.slots.txt
    close_face.txt
  src/                     images the host generated (if any)
  tools/film.py            copied from the skill's film_template.py, settings filled in
  sound.json               score/foley plan, no narration unless requested
  README.md                how to finish locally
```

Include `tools/film.py` only if `init_film.py` ran; otherwise include `film_template.py` and say it must be copied.

## How to build prompts without Python

The prompt templates are plain text:

- `styles/<id>/STYLE.md` — look, palette, light, camera.
- `styles/_common/<kind>.txt` — shared template for `character`, `sheet8`, `sheet4`, `prop`, `fx`, `bg`, `layer`, `texture`.
- `styles/<id>/prompts/<kind>.txt` — style-specific additions.
- `styles/_common/_rules.txt` — originality/no text rule.
- `styles/_common/_transparent.txt` — transparency sentence.

Assemble in this order: style anchor (`styles/<id>/prompts/anchor.txt`) → common kind template → style kind addition → rules. Fill `{character}`, `{action}`, `{scene}`, `{shot_size}`, `{margin}`, `{prop}`, `{fx}`, `{aspect}`. Keep the transparency sentence for transparent assets.

If Python is available, always prefer:

```bash
python scripts/claymotion.py prompt clay sheet8 prompts/toss.slots.txt -o prompts/toss.txt
```

## What the host should do

1. Ask the same intake questions.
2. Write `production-log.md` with the story skeleton and shot list.
3. Build the prompt files.
4. Generate each image with the host's own image tool (Doubao Seedream, Grok Aurora, Kimi image, etc.).
5. Save images to `src/` with the names in the image list.
6. If the host can run Python: slice, anchor, write `film.py`, build sound, render. If not: stop and deliver the pack.
7. Say clearly: “这是制作包，不是成片；在本机运行 `python tools/film.py` 出片。”

## Local finish

On a machine with Python + ffmpeg + an image backend:

```bash
python scripts/setup.py --check
python scripts/claymotion.py doctor
cd <pack>
python tools/film.py lint
python tools/film.py board
python scripts/claymotion.py sound build sound.json
python tools/film.py
```

If images are already in `src/`, skip generation. If not, use `scripts/claymotion.py image` with the saved prompts.

## What not to do

- Do not claim a film exists when only a pack exists.
- Do not use placeholder images in a delivered pack.
- Do not switch image backends or models without telling the user.
- Do not put API keys in prompts or files.
