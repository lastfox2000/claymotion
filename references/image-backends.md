# Image backends

The skill never generates video. It needs **still images** with transparent backgrounds for characters, action sheets, close-ups, props and fx, and opaque backgrounds for sets.

`scripts/claymotion.py image` chooses a backend with `CLAYMOTION_BACKEND` (default `comfy-qwen`).

## comfy-qwen (default)

Local or LAN ComfyUI with Qwen-Image 2.1.

```bash
export COMFYUI_URL=http://127.0.0.1:8188
export QWEN_UNET=qwen_image_2.1_int8_convrot.safetensors
export QWEN_CLIP=qwen3vl_8b_int8_convrot.safetensors
export QWEN_VAE=qwen_image_2.1_vae_bf16.safetensors
python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png
```

- Workflow: `UNETLoader → CLIPLoader → TextEncodeQwenImage21 → KSampler(25 steps, cfg 1, euler/simple) → VAEDecode → SaveImage`.
- Negative conditioning uses `ConditioningZeroOut` (Qwen 2.1 is tuned for cfg 1).
- References are uploaded to ComfyUI via `/upload/image` and wired to `TextEncodeQwenImage21.images`.
- Qwen 2.1 can return RGBA, but not for every prompt. The adapter retries `QWEN_ALPHA_RETRIES` times (default 2). If the alpha is still opaque, cut it out (`cut.py` / `slice --birefnet`).

## openai

Any OpenAI-compatible Images API: Doubao/Seedream gateways, OpenAI, or a local gateway.

```bash
export CLAYMOTION_BACKEND=openai
export IMAGE_API_BASE=https://api.openai.com/v1
export IMAGE_API_KEY=...
export IMAGE_MODEL=gpt-image-1
export IMAGE_SIZE=1536x1024
python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png
```

- With references it calls `/images/edits`; without, `/images/generations`.
- `IMAGE_BACKGROUND=transparent` asks for alpha; if the gateway ignores it, the PNG comes back white. The skill can still cut it out.
- Keep keys in the environment, never in the prompt or the repo.

## h3

MiniMax H3-Image on a local ComfyUI. It has no native alpha; use white background + matte.

```bash
export CLAYMOTION_BACKEND=h3
python scripts/claymotion.py image --prompt prompts/bg_wide.txt --out src/bg_wide.png
```

## command

For any other tool, provide a command that follows the adapter contract:

```bash
export CLAYMOTION_BACKEND=command
export IMAGE_CMD="/path/to/my-image-tool"
python scripts/claymotion.py image --prompt prompts/char.txt --out src/char_hero.png --ref src/char.png
```

The command receives:

```
<IMAGE_CMD> <prompt file> <out.png> [reference images...]
```

- Read the full prompt file; keep its meaning.
- Write exactly one PNG to `<out.png>`.
- `LEMO_ANIMI_TRANSPARENT=1` means the asset needs a transparent background.
- Exit 0 on success; non-zero with a message on stderr on failure.

## Transparent assets: the practical rule

1. Ask for transparent background in the prompt (the style templates already do).
2. Check the result: `python scripts/claymotion.py check src/sheet.png --n 8`.
3. If `no alpha channel` or `edges white`:
   - white/clean background: `slice --birefnet` + `cut.py` mask + 1px erode;
   - flat colour background: chroma key in your own adapter;
   - true scene: regenerate.
4. Never deliver a white rectangle behind the character.

## Troubleshooting

- `ComfyUI unreachable`: check `COMFYUI_URL`, that ComfyUI is running, and that it listens on the address you use. WSL needs IPv4 (`127.0.0.1`, not `localhost`, if IPv6 resolves first).
- `ComfyUI rejected the workflow`: the model names or node names differ. Run `python scripts/comfy_qwen.py` against `/object_info` or open the ComfyUI workflow template `image_qwen_image_2_1_t2i`.
- `no image in response`: check the API model name, quota, and whether the gateway returns `b64_json` or `url`.
- 429 / timeout: do work that needs no image, retry in a few minutes; do not deliver placeholders.
